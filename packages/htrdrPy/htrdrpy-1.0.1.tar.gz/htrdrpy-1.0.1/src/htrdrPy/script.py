import numpy as np
import time
import pickle
import warnings

from htrdrPy.helperFunctions import *
from htrdrPy.data import *
from htrdrPy.geometry import *


class Script:
    '''
    The ``htrdrPy.Script`` module aims at creating a callable (a function)
    taking as input a ``htrdrPy.Data`` object.

    Examples
    --------
    The first step is to create an instance of ``htrdrPy.Script``:

    >>> script = htrdrPy.script(case="caseName")

    The second step is to define the kind of script to be executed (see the
    documentation for all possibilities). If none of the predefined script suits
    your use, you can use the ``htrdrPy.Script.startMultipleObsGeometry``
    method.

    >>> script.startMultipleObsGeometry(...)
    
    Finally, you can call the script on an already defined ``htrdrPy.Data``
    object:

    >>> script(data)

    '''
    _count = 0

    def __init__(self, case="", threadFlag = '', MPIcmd = '', verbose = True):
        '''
        The Script module aims at creating a callable (a function) to be called on a Data object.

        Parameters
        ----------
        case : str, optional
            String to identify the script. This is mostly usefull in case
            different scripts are used on the same ``htrdrPy.Data`` instance.
            The output files being stored in the same folder (see
            ``htrdrPy.Data`` documentation), the case name is used to
            differentiate the output files of the different scripts.
        threadFlag : str, optional
            Thread option to use in the htrdr command. Should take the form "-t
            <num>" where <num> is the number of threads to be used. If left
            empty, the maximum number of threads (corresponding to the number of
            virtual cores on the computer) will be used.
        MPIcmd : str, optional
            MPI command to pass before the call to htrdr-planets, depending on
            the MPI runner on your system. For insatnce, it could be an 'mpirun'
            command on many computers, or a 'srun' command on a slurm-based
            supercalculator.
        verbose : bool, default True
            Whether or not activate the verbose of htrdr-planets.
        '''
        self.outputFiles = []
        self.predefinedScript = None
        self.verbose = verbose
        Script._count += 1
        if case:
            self.name = case
        else:
            self.name = str(Geometry._count)
        self.threadFlag = threadFlag
        self.MPIcmd = MPIcmd
        return

    def __call__(self, data: Data):
        self.data = data

        if self.predefinedScript == "image":
            self.__run(self.wavelengths, self.geometry)

        elif (self.predefinedScript == "reflectanceSpectrum" or
              self.predefinedScript == "spectrum"):
            for i,case in enumerate(tqdm.tqdm(self.cases)):
                self.__run(case, self.geometry, case=i)

        elif self.predefinedScript == "startMultipleObsGeometry":
            for i,obs in enumerate(self.obsList):
                self.__run( self.wavelengths, obs, case=obs.case)

        elif self.predefinedScript == "imageRatio":
            self.__run({"type":self.kind, "low":self.wavelengths[0], "up":self.wavelengths[0]}, 
                self.geometry, case="numerator")
            self.__run({"type":self.kind, "low":self.wavelengths[1], "up":self.wavelengths[1]}, 
                self.geometry, case="denominator")

        elif self.predefinedScript == "compositeRGB":
            self.__run({"type":self.kind, "low":self.wavelengths[0], "up":self.wavelengths[0]}, 
                self.geometry, case="red")
            self.__run({"type":self.kind, "low":self.wavelengths[1], "up":self.wavelengths[1]}, 
                self.geometry, case="green")
            self.__run({"type":self.kind, "low":self.wavelengths[1], "up":self.wavelengths[2]}, 
                self.geometry, case="blue")

        elif self.predefinedScript == "twoStream":
            for (i,j) in np.ndindex(self.data.latitudes.shape[0], self.data.longitudes.shape[0]):
                # i, j = 18, 16 # test at 22.5°N 0°E (near sub-solar point)
                print(i,j)
                if      self.method==1: self.__twoStreamInColumnV1(i,j)
                elif    self.method==2: self.__twoStreamInColumnV2(i,j)
                elif    self.method==3: self.__twoStreamInColumnV3(i,j)
                else:   raise ValueError("This method is not defined")
                # break # to test on a single column for starting

            wavelengths = {
                "type": self.kind,
                "low": self.data.atmosphere["bands low"][0] * cst.nano,
                "up": self.data.atmosphere["bands up"][-1] * cst.nano
            }

            threads = []
            for i,obs in enumerate(self.obsList):
                threads.append(Thread(target=self.__run, args=(wavelengths, obs, obs.case)))
            
            maxThread = os.cpu_count()
            for th in threads:
                while active_count() >= maxThread: 
                    time.sleep(1)
                th.start()

            for th in threads: th.join()

        elif self.predefinedScript == "radiativeBudget":
            wavelengths = {
                "type": self.kind,
                "low": self.data.atmosphere["bands low"][0] * cst.nano,
                "up": self.data.atmosphere["bands up"][-1] * cst.nano
            }
            self.__runRadBudget(wavelengths, self.geometry)

        else: raise ValueError("You have not provided the script procedure to be used")

        fileName = f"{self.data.outputPath}{self.predefinedScript}_{self.data.name}_{self.name}.bin"
        print(f"The script data is saved as: {fileName} \
                \n The object can be reconstructed in an independant script with: \
                \n script = htrdr.loadScript('{fileName}')")
        with open(fileName, "bw") as file:
            pickle.dump(self, file)

    def __testNoScript(self):
        if self.predefinedScript:
            print("A script is already defined, please start a new instance")
            return True

    def __run(self, wavelengths,
              geometry: Geometry,
              case=""):
        '''
        Start a htrdr run.
        # Input
        - wavelengths: dictionnary containing the spectral information with the following items:
            - "type": type of calculation ("cie_xyz", "sw", "lw")
            - "low": (optional: not required for "cie_xyz") lower bound of integration band in nm
            - "up": (optional: not required for "cie_xyz") upper bound of integration band in nm (if monochromatic calculation, "up" = "low")
        - geometry: Geometry object containing the observation geometry data
        - threadFlag: thread option to use in the htrdr command. Should take the form "-t <num>" where <num> is the number of threads to be used. If left empty, the maximum number of threads (corresponding to the number of virtual cores on the computer) will be used.
        - MPIcmd: command (MPI) to pass before call to htrdr-planets
        - case (optional): string to rename the different output (usefull when multiple runs are started in the same directory)
        '''

        if not case: case = self.name

        # Define string variables
        gas = f"mesh={self.data.atmosphereGeometry}"
        gas += f":ck={self.data.gasOpticalProperties}"
        gas += f":temp={self.data.gasTempearture}"

        haze = "name=haze"
        haze += f":mesh={self.data.atmosphereGeometry}"
        haze += f":radprop={self.data.particleOpticalProperties}"
        haze += f":phasefn={self.data.phaseFunctionList}"
        haze += f":phaseids={self.data.phaseFunctionFile}"

        ground = "name=surface"
        ground += f":mesh={self.data.groundGeometry}"
        ground += f":prop={self.data.groundSurfaceProperties}"
        ground += f":brdf={self.data.groundMaterialList}"

        ##############

        camera = f"pos={geometry.camera['position'][0]},{geometry.camera['position'][1]},{geometry.camera['position'][2]}"
        camera += f":tgt={geometry.camera['target'][0]},{geometry.camera['target'][1]},{geometry.camera['target'][2]}"
        camera += f":up={geometry.camera['roll'][0]},{geometry.camera['roll'][1]},{geometry.camera['roll'][2]}"
        camera += f":fov={geometry.camera['field of view']}"
        ##############

        image = f"def={geometry.image['definition'][0]}x{geometry.image['definition'][1]}:spp={geometry.image['sampling']}"

        if wavelengths["type"] == "cie_xyz":
            spectral = f"{wavelengths['type']}"
        else:
            spectral = f"{wavelengths['type']}={wavelengths['low'] / cst.nano},{wavelengths['up'] / cst.nano}"

        octree = f"def={self.data.octreeDef}"
        octree += f":nthreads={self.data.nthOctree}"
        octree += f":tau={self.data.opthick}"
        if self.data.octreeFile:
            octree += f":storage={self.data.octreeFile}"
            octree += f":proc={self.data.procOctree}"

        output = f"{self.data.outputPath}output_{case}.txt"
        self.outputFiles.append(output)
        try:
            os.remove(output)
        except:
            pass

        if self.verbose: verb = "-v"
        else: verb = ""

        if wavelengths["type"] == "lw":
            command = f"{self.MPIcmd} htrdr-planets {verb} -N \
                        -a {haze} \
                        -G {ground} \
                        -g {gas} \
                        -s {spectral} \
                        -C {camera} \
                        -i {image} \
                        -b {octree} \
                        -o {output} \
                        {self.threadFlag} "
        else:
            source = f"lon={geometry.source['longitude']}:lat={geometry.source['latitude']}"
            source += f":dst={geometry.source['distance'] / cst.kilo}"
            source += f":radius={geometry.source['radius'] / cst.kilo}"
            if "radiance" in geometry.source.keys():
                source += f":rad={geometry.source['radiance']}"
            elif "temperature" in geometry.source.keys():
                source += f":temp={geometry.source['temperature']}"
            else:
                raise KeyError("error in source keys \
                                must be one of ('radiance', 'temperature')")
        
            command = f"{self.MPIcmd} htrdr-planets {verb} -N \
                        -a {haze} \
                        -G {ground} \
                        -g {gas} \
                        -S {source} \
                        -s {spectral} \
                        -C {camera} \
                        -i {image} \
                        -b {octree} \
                        -o {output} \
                        {self.threadFlag} "

        # print(command)
        subprocess.run(command, shell=True, check=True)
        return

    def __runRadBudget(self, wavelengths,
                       geometry: Geometry,
                       case=""):
        '''
        Start a htrdr run.
        # Input
        - wavelengths: dictionnary containing the spectral information with the following items:
            - "type": type of calculation ("sw", "lw")
            - "low": (optional: not required for "cie_xyz") lower bound of integration band in nm
            - "up": (optional: not required for "cie_xyz") upper bound of integration band in nm (if monochromatic calculation, "up" = "low")
        - geometry: Geometry object containing the observation geometry data
        - threadFlag: thread option to use in the htrdr command. Should take the form "-t <num>" where <num> is the number of threads to be used. If left empty, the maximum number of threads (corresponding to the number of virtual cores on the computer) will be used.
        - MPIcmd: command (MPI) to pass before call to htrdr-planets
        - case (optional): string to rename the different output (usefull when multiple runs are started in the same directory)
        '''
        
        if not case: case = self.data.name

        # Define string variables
        gas = f"mesh={self.data.atmosphereGeometry}"
        gas += f":ck={self.data.gasOpticalProperties}"
        gas += f":temp={self.data.gasTempearture}"
        
        haze = "name=haze"
        haze += f":mesh={self.data.atmosphereGeometry}"
        haze += f":radprop={self.data.particleOpticalProperties}"
        haze += f":phasefn={self.data.phaseFunctionList}"
        haze += f":phaseids={self.data.phaseFunctionFile}"
        
        ground = "name=surface"
        ground += f":mesh={self.data.groundGeometry}"
        ground += f":prop={self.data.groundSurfaceProperties}"
        ground += f":brdf={self.data.groundMaterialList}"
        
        ##############
        volrad_budget_opt = f"spt={geometry.volrad['sampling']}"
        if geometry.volrad["mesh"] == "origin": 
            volrad_budget_opt += f":mesh={self.data.atmosphereGeometry}"
        else: volrad_budget_opt += f":mesh={geometry.volrad['mesh']}"
        if "PDF" in geometry.volrad.keys(): 
            volrad_budget_opt += f":pdf={geometry.volrad['PDF']}"

        
        spectral = f"{wavelengths['type']}={wavelengths['low'] / cst.nano},{wavelengths['up'] / cst.nano}"

        octree = f"def={self.data.octreeDef}"
        octree += f":nthreads={self.data.nthOctree}"
        octree += f":tau={self.data.opthick}"
        if self.data.octreeFile: 
            octree += f":storage={self.data.octreeFile}"
            octree += f":proc={self.data.procOctree}"

        output = f"{self.data.outputPath}output_{case}.txt"
        self.outputFiles.append(output)
        try:
            os.remove(output)
        except:
            pass

        if self.verbose: verb = "-v"
        else: verb = ""

        if wavelengths["type"] == "lw":
            command = f"{self.MPIcmd} htrdr-planets {verb} -N \
                        -a {haze} \
                        -G {ground} \
                        -g {gas} \
                        -s {spectral} \
                        -r {volrad_budget_opt} \
                        -b {octree} \
                        -o {output} \
                        {self.threadFlag} "
        else:
            source = f"lon={geometry.source['longitude']}:lat={geometry.source['latitude']}"
            source += f":dst={geometry.source['distance'] / cst.kilo}"
            source += f":radius={geometry.source['radius'] / cst.kilo}"
            if "radiance" in geometry.source.keys():
                source += f":rad={geometry.source['radiance']}"
            elif "temperature" in geometry.source.keys():
                source += f":temp={geometry.source['temperature']}"
            else:
                raise KeyError("error in source keys \
                                must be one of ('radiance', 'temperature')")
        
            command = f"{self.MPIcmd} htrdr-planets {verb} -N \
                    -a {haze} \
                    -G {ground} \
                    -g {gas} \
                    -S {source} \
                    -s {spectral} \
                    -r {volrad_budget_opt} \
                    -b {octree} \
                    -o {output} \
                    {self.threadFlag} "

        print(command)
        subprocess.run(command, shell=True, check=True)
        return

    def visibleImage(self, geometry: Geometry):
        '''
        Set up the script to calculate a visible (RGB) image.

        Parameters
        ----------
        geometry : ``htrdrPy.Geometry``
            A ``htrdrPy.Geometry`` object previously created and set up.
        '''
        if self.__testNoScript(): return

        self.predefinedScript = "image"
        self.wavelengths = {"type": 'cie_xyz'}
        self.geometry = geometry
        return

    def monochromaticImage(self, geometry: Geometry, kind, wavelength):
        '''
        Set up the script to calculate a monochromatic image.

        Parameters
        ----------
        geometry : ``htrdrPy.Geometry``
            A ``htrdrPy.Geometry`` object previously created and set up.
        kind : {"sw", "lw"}
            Type of calculation. "sw" for a calculation with an external source,
            and "lw" to use the atmosphere emission as source.
        wavelength : float
            Wavelength to use for the calculation [m].
        '''
        if self.__testNoScript(): return

        self.predefinedScript = "image"
        self.wavelengths = {"type": kind, "low": wavelength, "up": wavelength}
        self.geometry = geometry
        return

    def bandIntegratedImage(self, geometry: Geometry, kind, wavelengthLow,
                            wavelengthUp):
        '''
        Set up the script to calculate an image integrated over a given spectral
        range.

        Parameters
        ----------
        geometry : ``htrdrPy.Geometry``
            A ``htrdrPy.Geometry`` object previously created and set up.
        kind : {"sw", "lw"}
            Type of calculation. "sw" for a calculation with an external source,
            and "lw" to use the atmosphere emission as source.
        wavelengthLow : float
            Lower boundary wavelength [m].
        wavelengthUp : float
            Upper boundary wavelength [m].
        '''
        if self.__testNoScript(): return

        self.predefinedScript = "image"
        self.wavelengths = {"type": kind, "low": wavelengthUp, "up": wavelengthLow}
        self.geometry = geometry
        return

    def spectrum(self, geometry: Geometry, kind, wavelengths, bandWidths=None):
        '''
        Start mutliple runs of htrdr-planets to calculate a spectrum, producing
        an output for each wavelength.

        Parameters
        ----------
        geometry : ``htrdrPy.Geometry``
            A ``htrdrPy.Geometry`` object previously created and set up.
        kind : {"sw", "lw"}
            Type of calculation. "sw" for a calculation with an external source,
            and "lw" to use the atmosphere emission as source.
        wavelength : float
            Wavelength to use for the calculation [m].
        bandWidths : ``numpy.ndarray`` 
            Integration band around each wavelength. If not provided, the
            calculation is monochromatic (shape=(nWavelength), [m]).
        '''
        if self.__testNoScript(): return

        self.predefinedScript = "spectrum"
        self.wavelengths = np.array(wavelengths)
        self.geometry = geometry
        self.cases = []
        if bandWidths is not None:
            self.bandWidths = np.array(bandWidths)
            for wvl,band in zip(wavelengths,bandWidths):
                self.cases.append({
                    "type": kind,
                    "low": (wvl - band/2),  # m
                    "up": (wvl + band/2)    # m 
                })
        else:
            for wvl in wavelengths:
                self.cases.append({
                    "type": kind,
                    "low": wvl,     # m
                    "up": wvl       # m 
                })
        return

    def reflectanceSpectrum(self, geometry: Geometry, kind, wavelengths, bandWidths=None):
        '''
        Start mutliple runs of htrdr-planets to calculate a reflectance
        spectrum, producing an output for each wavelength.

        Parameters
        ----------
        geometry : ``htrdrPy.Geometry``
            A ``htrdrPy.Geometry`` object previously created and set up.
        kind : {"sw", "lw"}
            Type of calculation. "sw" for a calculation with an external source,
            and "lw" to use the atmosphere emission as source.
        wavelength : float
            Wavelength to use for the calculation [m].
        bandWidths : ``numpy.ndarray`` 
            Integration band around each wavelength. If not provided, the
            calculation is monochromatic (shape=(nWavelength), [m]).
        '''
        if self.__testNoScript(): return

        self.predefinedScript = "reflectanceSpectrum"
        self.wavelengths = np.array(wavelengths)
        self.geometry = geometry
        self.cases = []
        if bandWidths is not None:
            self.bandWidths = np.array(bandWidths)
            for wvl,band in zip(wavelengths,bandWidths):
                self.cases.append({
                    "type": kind,
                    "low": (wvl - band/2),  # m
                    "up": (wvl + band/2)    # m 
                })
        else:
            for wvl in wavelengths:
                self.cases.append({
                    "type": kind,
                    "low": wvl,     # m
                    "up": wvl       # m 
                })
        return

    def imageRatio(self, geometry: Geometry, kind, wavelengthNum, wavelengthDen):
        '''
        Set up the script to calculate the ratio of 2 monochromatic images.

        Parameters
        ----------
        geometry : ``htrdrPy.Geometry``
            A ``htrdrPy.Geometry`` object previously created and set up.
        kind : {"sw", "lw"}
            Type of calculation. "sw" for a calculation with an external source,
            and "lw" to use the atmosphere emission as source.
        wavelengthNum : float
            Wavelength for numerator image [m].
        wavelengthDen : float
            Wavelength for denominator image [m].
        ''' 
        if self.__testNoScript(): return

        self.predefinedScript = "imageRatio"
        self.geometry = geometry
        self.wavelengths = [wavelengthNum, wavelengthDen]
        self.kind = kind
        return

    def compositeRBG(self, geometry: Geometry, kind, wavelengthRed,
                      wavelengthGreen, wavelengthBlue):
        '''
        Set up the script to calculate the composite image from 3 monochromatic
        images.

        Parameters
        ----------
        geometry : ``htrdrPy.Geometry``
            A ``htrdrPy.Geometry`` object previously created and set up.
        kind : {"sw", "lw"}
            Type of calculation. "sw" for a calculation with an external source,
            and "lw" to use the atmosphere emission as source.
        wavelengthRed : float
            Wavelength for red chanel image [m].
        wavelengthGreen : float
            Wavelength for green chanel image [m].
        wavelengthBlue : float
            Wavelength for red chanel image [m].

        Warning
        -------
        This script has not bee tested yet and may not work correctly. This
        should be treated in future versions.
        '''
        if self.__testNoScript(): return

        warnings.warn("This mode has not been tested yet and may crash")

        self.predefinedScript = "compositeRGB"
        self.geometry = geometry
        self.wavelengths = [wavelengthRed, wavelengthGreen, wavelengthBlue]
        self.kind = kind
        return

    def startMultipleObsGeometry(self,  obsList: list[Geometry], wavelength):
        '''
        Start multiple runs with different observation geometries but the same planet inputs

        Parameters
        ----------
        obsList : array-like
            List of ``htrdrPy.Geometry`` instances.
        wavelength : dict
            Dictionnary containing the spectral information with the following
            items:

            - "type" : {"cie_xyz", "sw", "lw"}
                Type of calculation.
            - "low" : float
                Lower bound of integration band [m].
            - "up" : float
                Upper bound of integration band [m] (if monochromatic
                calculation, "up" = "low").
        '''
        if self.__testNoScript(): return

        self.predefinedScript = "startMultipleObsGeometry"
        self.obsList = obsList
        self.wavelengths = wavelength
        return

    def startRadBudgetGCM(self, geometry: Geometry, kind):
        '''
        Set up the script to calculate athe radiative budget of each GCM cell.

        Parameters
        ----------
        geometry : ``htrdrPy.Geometry``
            A ``htrdrPy.Geometry`` object previously created and set up.
        kind : {"sw", "lw"}
            Type of calculation. "sw" for a calculation with an external source,
            and "lw" to use the atmosphere emission as source.
        '''
        if self.__testNoScript(): return

        self.predefinedScript = "radiativeBudget"
        self.geometry = geometry
        self.kind = kind
        return

    def __startThermalTwoStream(self, source, kind, method=3, nAngle=4, angle=30, sampling=1e4,
                                        verbose=False):
        '''Under developement ...'''
        if self.__testNoScript(): return

        self.predefinedScript = "twoStream"
        if method==3: self.angle = 179.99
        elif method==1: raise NotImplementedError("Method 1 is deprecated, use method 2 or 3")
        else: self.angle = angle #np.arccos(3**(-0.5)) / cst.degree
        self.source = source
        self.threadFlag = "-t 1" #threadFlag
        self.MPIcmd = "" #MPIcmd
        self.kind = kind
        self.method = method
        self.nAngle = nAngle
        self.verbose = verbose
        self.sampling = sampling
        self.obsList = []
        return

    def __twoStreamInColumnV1(self, i, j):
        column  = self.data.atmosphereCellCoord[:,i,j,0]
        latitude = self.data.atmosphereCellCoord[0,i,j,1]
        longitude = self.data.atmosphereCellCoord[0,i,j,2]
        nPlans = column.shape[0] + 1
        plans = np.zeros(nPlans)
        plans[1:-1] = (column[1:] + column[:-1]) * 0.5
        plans[0] = self.data.topoMap[self.data.latitudes.shape[0]-i-1,j] + self.data.radius + 1  # +1 serves to make sure the camera is not bellow the surface...
        plans[-1] = 2*plans[-2] - plans[-3] # plans[-1] + (plans[-1]-plans[-2])

        # print(plans)
        # dlat = np.pi / len(self.data.latitudes)
        # dlon = 2*np.pi / len(self.data.longitudes)
        # ''' 
        # surfaces considering trapezes with:
        #   a   
        #  ___
        # /   \  | b
        # -----
        #   c
        # b is along the latitudes: b = z * dlat
        # a and c are along longitudes, i.e. on circles of radii z * cos( lat +\- dlat/2 )
        # so: 
        #   a = z * dlon * cos( lat + dlat/2 )
        #   c = z * dlon * cos( lat - dlat/2 )
        # The surface is given by the mean of the inner and outer rectangle ((a * b) + (c * b))/2
        # '''
        # areasInner = (plans**2) * dlat * dlon * np.cos(latitude + dlat/2)
        # areasOuter = (plans**2) * dlat * dlon * np.cos(latitude - dlat/2)
        # areas = 0.5 * ( areasInner + areasOuter )

        image = {"definition": [1,1], "sampling":1000}
        for k, plan in enumerate(plans):
            position = sphere2cart(np.array([plan, latitude, longitude]))
            targetUp = sphere2cart(np.array([2*plans[-1], latitude, longitude]))
            geomTop1 = Geometry(source=self.source, image=image, case=f"{k}_{i}_{j}_top1")
            geomTop1.setCamera(position, targetUp, self.angle)
            geomTop2 = Geometry(source=self.source, image=image, case=f"{k}_{i}_{j}_top2")
            geomTop2.setCamera(position, targetUp, self.angle * 0.99)
            geomDown1 = Geometry(source=self.source, image=image, case=f"{k}_{i}_{j}_down1")
            geomDown1.setCamera(position, [0.,0.,0.], self.angle)
            geomDown2 = Geometry(source=self.source, image=image, case=f"{k}_{i}_{j}_down2")
            geomDown2.setCamera(position, [0.,0.,0.], self.angle * 0.99)
            self.obsList.append(geomTop1)
            self.obsList.append(geomDown1)
            self.obsList.append(geomTop2)
            self.obsList.append(geomDown2)

        return

    def __twoStreamInColumnV2(self, i, j):
        column  = self.data.atmosphereCellCoord[:,i,j,0]
        latitude = self.data.atmosphereCellCoord[0,i,j,1]
        longitude = self.data.atmosphereCellCoord[0,i,j,2]
        nPlans = column.shape[0] + 1
        plans = np.zeros(nPlans)
        plans[1:-1] = (column[1:] + column[:-1]) * 0.5
        plans[0] = self.data.topoMap[self.data.latitudes.shape[0]-i-1,j] + self.data.radius + 1e-3 # +1e-3 serves to make sure the camera is not bellow the surface...
        plans[-1] = 2*plans[-2] - plans[-3] # plans[-1] + (plans[-1]-plans[-2])


        # rotation matrix
        # defining the unitary vectors of the camera referential
        ez = sphere2cart(np.array([1, latitude, longitude]))        # ez is normal to the surface
        if abs(abs(latitude)-90) < 1e-5:    # if we are at either pole,
            ey = np.array([0.,1.,0.])   # ey is parallel to y in Titan referential
            ex = np.array([1.,0.,0.])   # ex is parallel to x in Titan referential
        else:
            ey = np.cross(np.array([0.,0.,1.]),ez) # ey is perpendicular to the plan formed by the camera and the Titan z axis
            ex = np.cross(ey,ez)
        ex /= np.linalg.norm(ex)
        ey /= np.linalg.norm(ey)
        ez /= np.linalg.norm(ez)
        M = np.array([ex, ey, ez]).T

        theta = 90 - self.angle # degree
        phis = np.arange(0,360,360/(self.nAngle))

        image = {"definition": [1,1], "sampling":int(self.sampling)}
        for k, plan in enumerate(plans):
            position = sphere2cart(np.array([plan, latitude, longitude]))
            zenith = sphere2cart(np.array([self.source['distance'], self.source['latitude'], self.source['longitude']]))
            geomDirect = Geometry(source=self.source, image=image, case=f"{self.name}_{k}_{i}_{j}_zenith")
            self.FOVzenith = 0.2
            geomDirect.setCamera(position, zenith, self.FOVzenith)
            self.obsList.append(geomDirect)
            # print(f"{k}_{i}_{j}")
            for l,phi in enumerate(phis):
                los = M @ sphere2cart(np.array([1., theta, phi]))
                # print( f"top{l}: ",  np.arccos( np.dot( los, position ) / ( np.linalg.norm(los)*np.linalg.norm(position) ) )/cst.degree   )
                targetUp = los + position
                geomTop = Geometry(source=self.source, image=image, case=f"{self.name}_{k}_{i}_{j}_top{l}")
                geomTop.setCamera(position, targetUp, 0.001)

                los = M @ sphere2cart(np.array([1., -theta, phi]))
                targetDown = los + position
                # print( f"down{l}: ",  180 - np.arccos( np.dot( los, position ) / ( np.linalg.norm(los)*np.linalg.norm(position) ) )/cst.degree   )
                geomDown = Geometry(source=self.source, image=image, case=f"{self.name}_{k}_{i}_{j}_down{l}")
                geomDown.setCamera(position, targetDown, 0.001)

                self.obsList.append(geomTop)
                self.obsList.append(geomDown)
        # raise
        return

    def __twoStreamInColumnV3(self, i, j):
        column  = self.data.atmosphereCellCoord[:,i,j,0]
        latitude = self.data.atmosphereCellCoord[0,i,j,1]
        longitude = self.data.atmosphereCellCoord[0,i,j,2]
        nPlans = column.shape[0] + 1
        plans = np.zeros(nPlans)
        plans[1:-1] = (column[1:] + column[:-1]) * 0.5
        plans[0] = self.data.topoMap[self.data.latitudes.shape[0]-i-1,j] + self.data.radius + 1  # +1 serves to make sure the camera is not bellow the surface...
        plans[-1] = 2*plans[-2] - plans[-3] # plans[-1] + (plans[-1]-plans[-2])

        image = {"definition": [1,1], "sampling":100000}
        for k, plan in enumerate(plans):
            position = sphere2cart(np.array([plan, latitude, longitude]))
            targetUp = sphere2cart(np.array([2*plans[-1], latitude, longitude]))
            geomTop = Geometry(source=self.source, image=image, case=f"{k}_{i}_{j}_top")
            geomTop.setCamera(position, targetUp, self.angle)
            geomDown = Geometry(source=self.source, image=image, case=f"{k}_{i}_{j}_down")
            geomDown.setCamera(position, np.array([0.,0.,0.]), self.angle)
            self.obsList.append(geomTop)
            self.obsList.append(geomDown)

        return


def loadScript(filename):
    '''
    Load a ``htrdrPy.Script`` object from the binary file where it is saved
    (generated after the call on a ``htrdrPy.Data`` object).

    Parameters
    ----------
    filename : str
        Path to the binary file to be loaded.
    '''
    with open(filename, 'br') as file:
        script = pickle.load(file)
    for i,file in enumerate(script.outputFiles):
        if not os.path.exists(script.data.workingDirectory):
            script.data.workingDirectory = f"{pathlib.Path().resolve()}/"
        if not os.path.exists(file):
            script.outputFiles[i] = f"{pathlib.Path().resolve()}/{'/'.join( file.split('/')[-2:] )}"
    return script
