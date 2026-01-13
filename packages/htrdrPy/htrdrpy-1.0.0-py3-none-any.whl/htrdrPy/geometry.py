import numpy as np
import matplotlib.pyplot as plt
import json
from matplotlib.colors import LightSource

from htrdrPy.include.meshgen import *
from htrdrPy.include.meshvisual import *
from htrdrPy.include.write import *
from htrdrPy.include.read import *

from htrdrPy.helperFunctions import *
from htrdrPy.data import *


class Geometry:
    """
    ``htrdrPy.Geometry`` is a class that aims at managing all information
    related to the observation geometry. It handles the camera, source and image
    properties as well as the mesh on which running the volumic radiative budget
    calculations, if running on this mode.
    """
    _count = 0

    def __init__(self, source=None, camera=None, image=None, volrad=None, case=None):
        '''
        The Geometry module handles the positioning, orientation and properties
        of the camera and source.  The data can be provided directly when
        creating an instance as distinct dictionnaries for the source, the
        camera and the image, with the following keys:

        Parameters
        ----------
        source : dict, optional 
            Dictionnary containing the information on the source, with the
            following keys: 
            - "longitude" : float 
                Longitude of the source [°].
            - "latitude" : float
                Latitude of the source [°].
            - "distance" : 
                Distance of the source [m].
            - "radius" : float
                Radius of the source [m].
            - "temperature" : float, optional
                Surface temperature of the source [K] (used to calculate
                the Planck's function)
            - "radiance" : str, optional
                Path to a radiance file in htrdr readable format.
            - "spectrum" : ``numpy.ndarray``, optional
                2-D array containing the spectrum (shape=(nWavelength,2)).
                The first column contains the wavelength [nm] and the second
                contains the radiance [W/m2/sr/nm]) at the surface of the
                source.
        camera : dict, optional
            Dictionnary containing the information on the camera, with the
            following keys: 
            - "position" : ``numpy.ndarray``
                Position of the camera in cartesian coordinates (shape=(3),
                [m]). The origin corresponds to the center of the observed
                target.
            - "target" : ``numpy.ndarray``
                Position of the target in cartesian coordinates (shape=(3),
                [m]). The origin corresponds to the center of the observed
                target. This is NOT the line of sight but the position
                vector of the target.
            - "field of view" : float
                Vertical field of view of the camera [°] (the horizontal
                field of view is calculated via scaling by the image aspect
                ratio, assuming square pixels).
            - "roll" : ``numpy.ndarray``, optional
                Vector setting the upward direction of the camera (shape=(3),
                [m]) i.e. a vector in the pixel plane to turn the camera
                around the line of sight. If not provided, it is calculated
                as perpendicular to the line of sight and to z axis (or x
                axis if the z axis corresponds to the line of sight).
        image : dict, optional
            Dictionnary containing the information on the image, with the
            following keys: 
            - "definition" : array-like 
                Definition (number of pixels) of the image (shape=(2), the
                first value is the horizontal number of pixel and the second
                value is the vertical pixel count).
            - "sampling" : int
                Number of rays to sample for each pixel.
        '''
        Geometry._count += 1
        if case:
            self.case = case
        else:
            self.case = str(Geometry._count)
        if source:
            self.source = source
        else:
            self.source = {}
        if volrad:
            self.volrad = volrad
        else:
            self.volrad = {}
        if camera:
            self.camera = camera
            self.__lineOfSight()
            if not "roll" in self.camera.keys(): self.camera['roll'] = self.__calculateRoll()
        else:
            self.camera = {}
        if image:
            self.image = image
        else:
            self.image = {}

        self.radianceFolder = f"{pathlib.Path().resolve()}/radiances/"
        try:
            os.mkdir(self.radianceFolder)
        except FileExistsError:
            pass

        self.geometryFolder = f"{pathlib.Path().resolve()}/geometries/"
        try:
            os.mkdir(self.geometryFolder)
        except FileExistsError:
            pass

        if 'spectrum' in self.source.keys():
            self.radianceFile = f"{self.radianceFolder}radiance_{self.case}.bin"
            self.__writeRadiance(*self.source['spectrum'])
            self.source["radiance"] = self.radianceFile
        return

    def setSource(self, longitude, latitude, distance, radius, temperature=None, radianceFile=None, spectrum=None):
        '''
        Setup the source properties.

        Parameters
        ----------
        longitude : float 
           Longitude of the source [°].
        latitude : float
           Latitude of the source [°].
        distance : 
           Distance of the source [m].
        radius : float
           Radius of the source [m].
        temperature : float, optional
           Surface temperature of the source [K] (used to calculate
           the Planck's function)
        radianceFile : str, optional
           Path to a radiance file in htrdr readable format.
        spectrum : ``numpy.ndarray``, optional
           2-D array containing the spectrum (shape=(nWavelength,2)).
           The first column contains the wavelength [nm] and the second
           contains the radiance [W/m2/sr/nm]) at the surface of the
           source.

        Notes
        -----
        Whereas ``temperature``, ``radianceFile`` and ``spectrum`` are optional,
        at least one of those must be provided. If more than one is provided,
        the ``spectrum`` is taken in priority, then the ``radianceFile`` and
        finally the ``temperature``.
        '''

        self.source["longitude"] = longitude
        self.source["latitude"] = latitude
        self.source["distance"] = distance
        self.source["radius"] = radius
        if spectrum:
            self.radianceFile = f"{pathlib.Path().resolve()}/radiance_{self.case}.bin"
            self.source["radiance"] = self.radianceFile
            self.__writeRadiance(*spectrum)
        elif radianceFile:
            self.source["radiance"] = radianceFile
        elif temperature:
            self.source["temperature"] = temperature
        else:
            raise TypeError("Missing argument, either one of temperature or radiance must be given")
        return

    def setCamera(self, position, targetPosition, fieldOfView, roll=None):
        '''
        Setup the camera position, orientation and field of view

        Parameters
        ----------
        position : ``numpy.ndarray``
           Position of the camera in cartesian coordinates (shape=(3),
           [m]). The origin corresponds to the center of the observed
           target.
        targetPosition : ``numpy.ndarray``
           Position of the target in cartesian coordinates (shape=(3),
           [m]). The origin corresponds to the center of the observed
           target. This is NOT the line of sight but the position
           vector of the target.
        fieldOfView : float
           Vertical field of view of the camera [°] (the horizontal
           field of view is calculated via scaling by the image aspect
           ratio, assuming square pixels).
        roll : ``numpy.ndarray``, optional
           Vector setting the upward direction of the camera (shape=(3),
           [m]) i.e. a vector in the pixel plane to turn the camera
           around the line of sight. If not provided, it is calculated
           as perpendicular to the line of sight and to z axis (or x
           axis if the z axis corresponds to the line of sight).
        '''
        self.camera["position"] = position
        self.camera["target"] = targetPosition
        self.__lineOfSight()
        if roll:
            self.camera["roll"] = roll
        else:
            self.camera["roll"] = self.__calculateRoll()
        self.camera["field of view"] = fieldOfView
        return

    def setImage(self, definition, sampling):
        '''
        Setup the image properties
        
        Parameters
        ----------
        definition" : array-like 
           Definition (number of pixels) of the image (shape=(2), the
           first value is the horizontal number of pixel and the second
           value is the vertical pixel count).
        sampling" : int
           Number of rays to sample for each pixel.
        '''
        self.image["definition"] = definition
        self.image["sampling"] = sampling
        return

    def setVolrad(self, sampling, mesh="origin", args=None):
        '''
        Setup the volumic radiative budget properties.
        The volumic radiative budget mode evaluate the divergence of the flux
        within each provided tetrahedron. This method handles the generation of
        the mesh on which the calulation will be conducted.

        Parameters
        ----------
        sampling : int
            Number of ray to sample for each tetrahedron.
        mesh : {"origin", "makeColumnPP", "makeFromCellCoord", "makeSliceAltLat", "extractFromData"}, default "origin"
            Method to build the mesh on which the radiative budget calculation
            is realized. 

            .. list-table:: Building method
                :widths: 25 75
                :header-rows: 0
                
                * - "origin"
                  - Use the original atmosphere mesh.
                * - "makeColumnPP"
                  - Generate one plane-parallel column.
                * - "makeFromCellCoord"
                  - Generate a complete sphere from a table of coordinates.
                * - "makeSliceAltLat"
                  - Generate a slice in altitude / latitude from a table of
                    coordinates.
                * - "extractFromData"
                  - Extract a list of cells from an already generated mesh.
        args : tuple
            Tuple containing the arguments required by the chosen mesh
            generation method.
    
            .. list-table:: Arguments
                :widths: 25 75
                :header-rows: 1
                
                * - Method
                  - Required arguments
                * - "origin"
                  - 
                * - "makeColumnPP"
                  - 
                    altitudes : ``numpy.ndarray``
                        Array continaing the altitudes [m], either at the center
                        of the cells or at the boundaries (shape = nLevel or
                        nLayer).
                    hwidth : float
                        Horizontal dimension of the squared base column [m].
                    center : bool, default: True
                        True if the altitudes represent the cell centers and
                        False if they correspond to the boundaries of the cells.
                * - "makeFromCellCoord"
                  - 
                    cellCoord : ``numpy.ndarray``
                        Coordinates of the cells centers or cell interface
                        centers (c.f. ``onLevels``,
                        shape=(nAltitudes,nLatitudes,nLongitudes,3), [m])
                    radius : float
                        Radius of the planet [m].
                    poles : bool, default False
                        Whether or not the first and last latitudes correspond
                        to the poles in the given array of coordinates.
                    onLevels  : bool, default False
                        Whether or not the altitudes provided in the coordinates
                        are given on the levels or in the center of the cells.
                * - "makeSliceAltLat"
                  - 
                    cellCoord : ``numpy.ndarray``
                        Coordinates of the cells centers or cell interface
                        centers (c.f. ``onLevels``,
                        shape=(nAltitudes,nLatitudes,3), [m])
                    radius : float
                        Radius of the planet [m].
                    dLongitude : float
                        Longitude width of the slice [°].
                    poles : bool, default False
                        Whether or not the first and last latitudes correspond
                        to the poles in the given array of coordinates.
                    onLevels  : bool, default False
                        Whether or not the altitudes provided in the coordinates
                        are given on the levels or in the center of the cells.
                * - "extractFromData"
                  - 
                    data : ``htrdrPy.Data`` or ``htrdrPy.Geometry``
                        Object instance containing an already generated mesh
                        from which extracting the list of cells. This is
                        non-desctructive for the original ``htrdrPy.Data`` or
                        ``htrdrPy.Geometry`` and only affects the current
                        instance that "steals" the wanted cells.
                    cells : ``numpy.ndarray``
                        Array of the cells to be extracted (shape=(nCell,3))
                        with the altitude, latitude and longitude indices.
        '''
        self.volrad["sampling"] = sampling
        self.GCMmesh = False
        if mesh == "origin":
            self.GCMmesh = True
            self.volrad["mesh"] = "origin"
        elif mesh == "extractFromData": self.__makeMeshExtractFromData(*args)
        elif mesh == "makeFromCellCoord": self.__makeMeshFromCellCoord(*args)
        elif mesh == "makeSliceAltLat": self.__makeMeshSliceAltLat(*args)
        elif mesh == "makeColumnPP": self.__makeColumnPP(*args)
        return

    def geometryFromAPIE(self, observation, distance, radius, cameraFOV,
                         sourceDist, sourceRad, sourceTemp=None,
                         radianceFile=None, spectrum=None):
        '''
        Calulate the observation geometry from Azimut, Phase, Incident and
        Emergent angles.

        Parameters
        ----------
        observation : dict
            Dictionnary containing the geometry of the observation with the
            following items:
            - "azimut" : float
                Angle between the projected incidence and the projected
                emergence [°].
            - "phase" : float
                Angle between incident rays (directly from the source) and
                the line of sight [°].
            - "incidence" : float
                Angle between the incident rays (directly from the source)
                and the normal to the ground at the observed loaction [°].
            - "emergence" : float
                Angle between the normal to the line of sight and the normal
                to the ground at the observed loaction [°].
        distance : float
            Distance from the camera to the target [m].
        radius : float
            Radius of the planet to locate the target on the surface [m].
        cameraFOV : float
            Field of view of the camera (c.f. ``htrdrPy.Geometry.setCamera``).
        sourceDist : float 
            Distance of the source [m] (c.f. ``htrdrPy.Geometry.setSource``).
        sourceRad : float
            Radius of the source [m] (c.f. ``htrdrPy.Geometry.setSource``).
        spectrum : float, optional
            Spectrum of the source (c.f. ``htrdrpy.geometry.setsource``).
        radianceFile : float, optional
            Path to the radiance file of the source (c.f.
            `htrdrpy.geometry.setsource`).
        sourcetemp : float, optional
            Temperature of the source (c.f. ``htrdrpy.geometry.setsource``).
        '''

        '''we fix the source at (0°N,0°E)'''
        self.setSource(0, 0, sourceDist, sourceRad, temperature=sourceTemp,
                       radianceFile=radianceFile, spectrum=spectrum)

        ''' 
        we fix the target position in the equatorial plan 
        the longitude corresponds to the incident angle
        '''
        targetLon = observation["incidence"] * cst.degree
        target = np.array([
            0.,
            np.sin(targetLon),
            np.cos(targetLon)
        ]) * radius

        '''
        considering the target and source in the equator plan, in the target space
        '''
        incident = np.array([
            0,
            - np.sin(observation["incidence"] * cst.degree),
            np.cos(observation["incidence"] * cst.degree)
        ])

        emergent = np.array([
            np.sin(observation["emergence"] * cst.degree) * np.sin(observation["azimut"] * cst.degree),
            np.sin(observation["emergence"] * cst.degree) * np.cos(observation["azimut"] * cst.degree),
            np.cos(observation["emergence"] * cst.degree)
        ]) * distance

        if abs( np.arccos(np.dot(emergent,incident) / (np.linalg.norm(emergent) * np.linalg.norm(incident)) ) - observation["phase"] * cst.degree ) > 1e-5 * observation["phase"] * cst.degree:
            raise ValueError("error in observation geometry: calculated phase does not match real phase")

        matRot = np.array([ [1.,  0.,                   0.                  ],
                            [0.,  np.cos(targetLon),    np.sin(targetLon)   ],
                            [0., - np.sin(targetLon),   np.cos(targetLon)   ]]
                        )
        
        camPos = matRot @ emergent + target

        self.setCamera(np.array([camPos[2], camPos[1], -camPos[0]]), np.array([target[2], target[1], -target[0]]), cameraFOV)
        return

    def exportGeometry(self):
        '''
        Export the geometry (source, camera and image data) in a
        geometry_{case}.json file stored in the "geometries/" repository
        '''
        file = f"{self.geometryFolder}geometry_{self.case}.json"
        with open(file, 'w') as f:
            f.write(json.dumps({
                "source": self.source,
                "camera": {key: val.tolist() if (isinstance(val,np.ndarray)) else val for key,val in self.camera.items()},
                "image": self.image
            }, indent=4))
        print(f"Geometry saved in {file}")
        return

    def plotGeometry(self, ax, radius):
        '''
        Plot the gometry: the observed planet, the line of sight (blue vector),
        the source direction (red vector), the camera plan (black vectors) and
        the field of view (green vectors).

        Parameters
        ----------
        ax : matplotlib.pyplot.Axes
            Axe on which draxing the plot. It must be a 3D axe.
        radius: float
            Radius of the planet [m].

        Warning
        -------
        matplotlib.pyplot 3d projection has some issues with vector orientation.
        If they have the right direction, they may not have the right sens.
        '''

        ax.set_title(self.case)

        warnings.warn("matplotlib.pyplot 3d projection has some issues with vector orientation. If they have the right direction, they may not have the right sens.")

        theta = self.source["longitude"] * cst.degree
        phi = self.source["latitude"] * cst.degree
        sourcePos = np.array([
                np.cos(phi) * np.cos(theta),
                np.cos(phi) * np.sin(theta),
                np.sin(phi)
        ]) * self.source["distance"]


        cameraPos = np.array(self.camera["position"])

        targetPos = np.array(self.camera["target"])

        up = np.array(self.camera["roll"])

        lineOfSight = targetPos - cameraPos

        # planet
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x = np.outer(np.cos(u), np.sin(v)) * radius
        y = np.outer(np.sin(u), np.sin(v)) * radius
        z = np.outer(np.ones(np.size(u)), np.cos(v)) * radius

        light = LightSource(theta, phi)
        illuminated_surface = light.shade(z, cmap=plt.get_cmap('autumn'))
        ax.plot_surface(x, y, z, color="orange", facecolors=illuminated_surface, alpha=0.5, zorder=10)

        if abs(np.dot(up,lineOfSight) / (np.linalg.norm(up) * np.linalg.norm(lineOfSight))) > 1e-10:
            print("error: line of sight is not perpandicular to the camera")
            # print(abs(np.dot(up,lineOfSight) / (np.linalg.norm(up) * np.linalg.norm(lineOfSight))))
            # print(up, lineOfSight)

        cros = np.cross(lineOfSight,up)

        origin = np.array([0., 0., 0.])

        plotVector(ax, cameraPos, lineOfSight, color="blue")
        plotVector(ax, cameraPos, up*10*radius)
        plotVector(ax, cameraPos, cros * 10 * radius/np.linalg.norm(cros))
        plotVector(ax, origin, sourcePos, color='red')

        ## field of view
        # rotation matrix

        M = np.array([lineOfSight/np.linalg.norm(lineOfSight), up/np.linalg.norm(up), cros/np.linalg.norm(cros)])
        M = np.linalg.inv(M)


        definition = self.image['definition']
        alpahx = self.camera['field of view'] * (definition[0]/definition[1]) * 0.5 * cst.degree
        alpahy = self.camera['field of view'] * 0.5 * cst.degree
        nrm = np.linalg.norm(cameraPos) / (np.cos(alpahx) * np.cos(alpahy))
        v1 = M @ np.array([
            np.cos(alpahx) * np.cos(alpahy),
            np.cos(alpahx) * np.sin(alpahy),
            np.sin(alpahx)
        ]) * nrm
        v2 = M @ np.array([
            np.cos(-alpahx) * np.cos(alpahy),
            np.cos(-alpahx) * np.sin(alpahy),
            np.sin(-alpahx)
        ]) * nrm
        v3 = M @ np.array([
            np.cos(alpahx) * np.cos(-alpahy),
            np.cos(alpahx) * np.sin(-alpahy),
            np.sin(alpahx)
        ]) * nrm
        v4 = M @ np.array([
            np.cos(-alpahx) * np.cos(-alpahy),
            np.cos(-alpahx) * np.sin(-alpahy),
            np.sin(-alpahx)
        ]) * nrm

        plotVector(ax, cameraPos, v1, color="green", arrow_length_ratio=0., zorder=0)
        plotVector(ax, cameraPos, v2, color="green", arrow_length_ratio=0., zorder=0)
        plotVector(ax, cameraPos, v3, color="green", arrow_length_ratio=0., zorder=0)
        plotVector(ax, cameraPos, v4, color="green", arrow_length_ratio=0., zorder=0)

        plotVector(ax, cameraPos+v1, v2-v1, color="green", arrow_length_ratio=0., zorder=0)
        plotVector(ax, cameraPos+v1, v3-v1, color="green", arrow_length_ratio=0., zorder=0)
        plotVector(ax, cameraPos+v4, v2-v4, color="green", arrow_length_ratio=0., zorder=0)
        plotVector(ax, cameraPos+v4, v3-v4, color="green", arrow_length_ratio=0., zorder=0)

        points = cameraPos[None,:] + np.array([v1, v2, v3, v4])
        x = points[:,0]
        y = points[:,1]
        z = points[:,2]

        triangles = [[0, 1, 2],[3, 1, 2]]
        ax.plot_trisurf(x, y, triangles, z, color='green', alpha=0.3, zorder=0)


        # mat = np.array([
        #   [cameraPos[0],          cameraPos[1],           cameraPos[2],           1],
        #   [cameraPos[0]+up[0],    cameraPos[1]+up[1],     cameraPos[2]+up[2],     1],
        #   [cameraPos[0]-up[0],    cameraPos[1]-up[1],     cameraPos[2]-up[2],     1],
        #   [cameraPos[0]+cros[0],  cameraPos[1]+cros[1],   cameraPos[2]+cros[2],   1]
        # ])

        size = np.linalg.norm(cameraPos)

        ax.set_xlim(-size, size)
        ax.set_ylim(-size, size)
        ax.set_zlim(-size, size)

        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')

        set_axes_equal(ax)
        return

    def setSpectralCumulDist(self, pdf, data=None):
        '''
        Setup the probability density function to used for sampling the
        wavelength and correlated-k coefficient.

        Parameters
        ----------
        pdf : ``numpy.ndarray``
          Table containing the cumulative distribution used to sample the
          wavelength and k-coefficient
          (shape=(nAltitudes,nLatitudes,nLongitudes,nSpectralElements)).
          nSpectralElements correspond to nWavelength * nCoeff.
        '''

        if self.volrad.keys() == []: 
            raise ValueError("You should setup the mesh before setting the \
                    cumulative distribution")

        if self.volrad['mesh'] == 'origin':
            if data is None:
                raise ValueError("The mesh type is set to 'origin', \
                            please provide the data object")
            cellInd = data.tetraALL
        else:
            cellInd = self.tetraALL

        atmSize = cellInd.max(axis=0) + 1

        if not np.array_equal(atmSize, pdf.shape[:3]):
            print(atmSize, pdf.shape[:3])
            raise ValueError("Shape mismatch between \
                    cumulative distribution and grid")

        self.cumulDist = np.array([pdf[i,j,k,:] for (i,j,k) in cellInd])
        self.volrad["PDF"] = f"{self.geometryFolder}volrad_pdf_{self.case}.bin"
        print('generating spectral sampling distribution bin file \
                for radiative budget calculation...')
        write_binary_file_spectral_pdf(self.volrad["PDF"], 4096,
                                       self.cumulDist .shape[0], self.cumulDist)
        print('bin generation completed.')
        return

    def __makeMeshFromCellCoord(self, cellCoord, radius, poles=False,
                                onLevels=False):
        '''
        Make the mesh from the cell coordinates
        # Input
        - cellCoord (numpy 4-D array (shape=(nAltitudes,nLatitudes,nLongitudes,3), float [m])): coordinates of the cells centers in the atmosphere
        - radius (float [m]): radius of the planet
        - poles (optional, default=False, bool): whether or not the first and
          last latitudes correspond to the poles in the given coordinates
        - onLevels (optional, default=False, bool): whether or not the altitudes
          provided in the coordinates are given on the levels or in the center
          of the cells
        '''

        self.latitudes = np.unique(cellCoord[:,:,:,1])
        self.longitudes = np.unique(cellCoord[:,:,:,2])
        self.latitudes = self.latitudes[::-1]
        # print(self.latitudes, self.longitudes)

        nLay, nLat, nLon = cellCoord.shape[:-1]

        if onLevels:
            altitudesLev = cellCoord[:,:,:,0]

            altSup = altitudesLev[1:,:,:]
            altInf = altitudesLev[:-1,:,:]

            self.altitudes = 0.5 * (altitudesLev[1:,:,:] + altitudesLev[:-1,:,:])
            nLay -= 1
        else:
            altitudesLay = cellCoord[:,:,:,0]
            self.altitudes = altitudesLay

            altSup = np.zeros_like(altitudesLay)
            altInf = np.zeros_like(altitudesLay)
            altSup[:-1,:,:] = altInf[1:,:,:] = 0.5 * (altitudesLay[1:,:,:] + altitudesLay[:-1,:,:])
            altSup[-1,:,:] = 2 * altitudesLay[-1,:,:] - altitudesLay[-2,:,:]
            altInf[0,:,:] = radius

        latN = np.zeros_like(self.latitudes)
        latS = np.zeros_like(self.latitudes)
        latN[1:] = latS[:-1] = 0.5 * (self.latitudes[1:] + self.latitudes[:-1])
        latN[0] = 90
        latS[-1] = -90

        lonE = np.zeros_like(self.longitudes)
        lonW = np.zeros_like(self.longitudes)
        lonW[1:] = lonE[:-1] = 0.5 * (self.longitudes[1:] + self.longitudes[:-1])
        lonW[0] = lonE[-1] = 0.5 * (self.longitudes[-1] - self.longitudes[0])

        nodeCoord = []      # contains nodes cartesian coordinates
        tetraIds = []       # contains the ids of the nodes of each tetrahedron
        cellIds = []        # contains the ids of the tetrahedrons forming each PCM cell
        cellIndexALL = []   # contains the Altitude, Latitude and Longitude indices of each cell
        tetraALL = []

        tetraInds = []
        tetraInds.append(np.array([0,1,2,5]))
        tetraInds.append(np.array([0,2,3,7]))
        tetraInds.append(np.array([0,4,5,7]))
        tetraInds.append(np.array([2,5,6,7]))
        tetraInds.append(np.array([0,2,5,7]))

        polarTobs = np.arange(0, self.longitudes.shape[0])
        tetraIndsPoles = []
        tetraIndsPoles.append(np.array([0,2,3,4]))
        tetraIndsPoles.append(np.array([1,3,4,5]))
        tetraIndsPoles.append(np.array([0,1,3,4]))

        if poles:
            for k in range(nLay):
                # north pole
                cellId = []
                for n in polarTobs:
                    start = len(nodeCoord)
                    nodeCoord.append(sphere2cart([altInf[k,0,n], 90, 0]))
                    nodeCoord.append(sphere2cart([altSup[k,0,n], 90, 0]))
                    nodeCoord.append(sphere2cart([altInf[k,0,n], latS[0], lonW[n]]))
                    nodeCoord.append(sphere2cart([altSup[k,0,n], latS[0], lonW[n]]))
                    nodeCoord.append(sphere2cart([altInf[k,0,n], latS[0], lonE[n]]))
                    nodeCoord.append(sphere2cart([altSup[k,0,n], latS[0], lonE[n]]))
                    for tetraIndsPole in tetraIndsPoles:
                        cellId.append(len(tetraIds))
                        tetraIds.append(start + tetraIndsPole)
                        tetraALL.append(np.array([k,0,0]))
                cellIds.append(np.array(cellId))
                cellIndexALL.append(np.array([k,0,0]))

                # south pole
                cellId = []
                for n in polarTobs:
                    start = len(nodeCoord)
                    nodeCoord.append(sphere2cart([altInf[k,-1,n], -90, 0]))
                    nodeCoord.append(sphere2cart([altSup[k,-1,n], -90, 0]))
                    nodeCoord.append(sphere2cart([altInf[k,-1,n], latN[-1], lonW[n]]))
                    nodeCoord.append(sphere2cart([altSup[k,-1,n], latN[-1], lonW[n]]))
                    nodeCoord.append(sphere2cart([altInf[k,-1,n], latN[-1], lonE[n]]))
                    nodeCoord.append(sphere2cart([altSup[k,-1,n], latN[-1], lonE[n]]))

                    for tetraIndsPole in tetraIndsPoles:
                        cellId.append(len(tetraIds))
                        tetraIds.append(start + tetraIndsPole)
                        tetraALL.append(np.array([k,len(self.latitudes)-1,0]))
                cellIds.append(np.array(cellId))
                cellIndexALL.append(np.array([k,len(self.latitudes)-1,0]))

        for k,i,j in np.ndindex(nLay,nLat,nLon):
            start = len(nodeCoord)
            if i == 0 and poles: continue # north pole already done
            elif i == len(self.latitudes)-1 and poles: continue # south pole already done
            nodeCoord.append(sphere2cart([altInf[k,i,j], latN[i], lonW[j]]))
            nodeCoord.append(sphere2cart([altInf[k,i,j], latN[i], lonE[j]]))
            nodeCoord.append(sphere2cart([altInf[k,i,j], latS[i], lonE[j]]))
            nodeCoord.append(sphere2cart([altInf[k,i,j], latS[i], lonW[j]]))
            nodeCoord.append(sphere2cart([altSup[k,i,j], latN[i], lonW[j]]))
            nodeCoord.append(sphere2cart([altSup[k,i,j], latN[i], lonE[j]]))
            nodeCoord.append(sphere2cart([altSup[k,i,j], latS[i], lonE[j]]))
            nodeCoord.append(sphere2cart([altSup[k,i,j], latS[i], lonW[j]]))

            cellId = []
            for tetraInd in tetraInds:
                cellId.append(len(tetraIds))
                tetraIds.append(start + tetraInd)
                tetraALL.append(np.array([k,i,j]))
            cellIds.append(np.array(cellId))
            cellIndexALL.append(np.array([k,i,j]))

        self.nodeCoord = np.array(nodeCoord)
        self.tetraIds = np.array(tetraIds, dtype=int)       
        self.cellIndices = np.array(cellIndexALL, dtype=int)
        self.cellIds = cellIds
        self.tetraALL = np.array(tetraALL)

        self.calculationGeometry = f"{self.geometryFolder}volrad_geometry_{self.case}.bin"
        self.calculationGeometryObj = f"{self.geometryFolder}volrad_geometry_{self.case}.vtk"
        print('generating atmosphere mesh bin file for radiative budget calculation...')
        write_binary_file_grid(self.calculationGeometry,4096,self.nodeCoord,self.tetraIds)
        print('bin generation completed.')
        print("generating Atmosphere geometry VTK file ...")
        write_vtk_tetr(self.nodeCoord,self.tetraIds, self.calculationGeometryObj)
        print("VTK file written.")
        self.volrad["mesh"] = self.calculationGeometry
        return

    def __makeMeshSliceAltLat(self, cellCoord, radius, dLongitude, poles=False,
                              onLevels=False):
        '''
        Make the mesh from the cell coordinates
        # Input
        - cellCoord (numpy 3-D array (shape=(nAltitudes,nLatitudes,3), float [m])): coordinates of the cells centers in the atmosphere
        - radius (float [m]): radius of the planet
        - dLongitude (float [°]): longitude width of the slice
        - poles (optional, bool): wether the poles are included in the mesh or not
        - onLevels (optional, default=False, bool): whether or not the altitudes
          provided in the coordinates are given on the levels or in the center
          of the cells
        '''

        self.latitudes = np.unique(cellCoord[:,:,1])
        self.longitudes = np.unique(cellCoord[:,:,2])
        if len(self.longitudes) > 1: raise ValueError("makeMeshSliceAltLat only works for 1 longitude")
        self.longitude = self.longitudes[0]
        self.latitudes = self.latitudes[::-1]
        # print(self.latitudes, self.longitudes)

        nLay, nLat = cellCoord.shape[:-1]

        if onLevels:
            altitudesLev = cellCoord[:,:,0]

            altSup = altitudesLev[1:,:]
            altInf = altitudesLev[:-1,:]

            self.altitudes = 0.5 * (altitudesLev[1:,:] + altitudesLev[:-1,:])
            nLay -= 1
        else:
            altitudesLay = cellCoord[:,:,0]
            self.altitudes = altitudesLay

            altSup = np.zeros_like(altitudesLay)
            altInf = np.zeros_like(altitudesLay)
            altSup[:-1,:] = altInf[1:,:] = 0.5 * (altitudesLay[1:,:] + altitudesLay[:-1,:])
            altSup[-1,:] = 2 * altitudesLay[-1,:] - altitudesLay[-2,:]
            altInf[0,:] = radius

        # altitudesLay = cellCoord[:,:,0]
        # self.altitudes = altitudesLay

        # altSup = np.zeros_like(altitudesLay)
        # altInf = np.zeros_like(altitudesLay)
        # altSup[:-1,:] = altInf[1:,:] = 0.5 * (altitudesLay[1:,:] + altitudesLay[:-1,:])
        # altSup[-1,:] = 2 * altitudesLay[-1,:] - altitudesLay[-2,:]
        # altInf[0,:] = radius

        latN = np.zeros_like(self.latitudes)
        latS = np.zeros_like(self.latitudes)
        latN[1:] = latS[:-1] = 0.5 * (self.latitudes[1:] + self.latitudes[:-1])
        latN[0] = latN[1]
        latS[-1] = latS[-2]

        lonE = self.longitude + dLongitude / 2
        lonW = self.longitude - dLongitude / 2

        nodeCoord = []      # contains nodes cartesian coordinates                                      shape=(nNodes,3)
        tetraIds = []       # contains the ids of the nodes of each tetrahedron                         shape=(nTetra,4)
        cellIds = []        # contains the ids of the tetrahedrons forming each PCM cell                shape=(nPCMcell,?)
        cellIndexALL = []   # contains the Altitude, Latitude and Longitude indices of each cell        shape=(nPCMcell,3)
        tetraALL = []       # contains the Altitude, Latitude and Longitude indices of each tetrahedron shape=(nPCMcell,3)

        tetraInds = []
        tetraInds.append(np.array([0,1,2,5]))
        tetraInds.append(np.array([0,2,3,7]))
        tetraInds.append(np.array([0,4,5,7]))
        tetraInds.append(np.array([2,5,6,7]))
        tetraInds.append(np.array([0,2,5,7]))

        if poles:
            warnings.warn("poles implementation has not been tested yet")
            polarTobs = np.arange(0, 360//dLongitude + 1)
            tetraIndsPoles = []
            tetraIndsPoles.append(np.array([0,2,3,4]))
            tetraIndsPoles.append(np.array([1,3,4,5]))
            tetraIndsPoles.append(np.array([0,1,3,4]))

            for k in range(nLay):
                # north pole
                cellId = []
                for n in polarTobs:
                    start = len(nodeCoord)
                    nodeCoord.append(sphere2cart([altInf[k,0], 90, 0]))
                    nodeCoord.append(sphere2cart([altSup[k,0], 90, 0]))
                    nodeCoord.append(sphere2cart([altInf[k,0], latS[0], lonW]))
                    nodeCoord.append(sphere2cart([altSup[k,0], latS[0], lonW]))
                    nodeCoord.append(sphere2cart([altInf[k,0], latS[0], lonE]))
                    nodeCoord.append(sphere2cart([altSup[k,0], latS[0], lonE]))
                    for tetraIndsPole in tetraIndsPoles:
                        cellId.append(len(tetraIds))
                        tetraIds.append(start + tetraIndsPole)
                        tetraALL.append(np.array([k,0,0]))
                cellIds.append(np.array(cellId))
                cellIndexALL.append(np.array([k,0,0]))

                # south pole
                cellId = []
                for n in polarTobs:
                    start = len(nodeCoord)
                    nodeCoord.append(sphere2cart([altInf[k,-1], -90, 0]))
                    nodeCoord.append(sphere2cart([altSup[k,-1], -90, 0]))
                    nodeCoord.append(sphere2cart([altInf[k,-1], latN[-1], lonW]))
                    nodeCoord.append(sphere2cart([altSup[k,-1], latN[-1], lonW]))
                    nodeCoord.append(sphere2cart([altInf[k,-1], latN[-1], lonE]))
                    nodeCoord.append(sphere2cart([altSup[k,-1], latN[-1], lonE]))

                    for tetraIndsPole in tetraIndsPoles:
                        cellId.append(len(tetraIds))
                        tetraIds.append(start + tetraIndsPole)
                        tetraALL.append(np.array([k,len(self.latitudes)-1,0]))
                cellIds.append(np.array(cellId))
                cellIndexALL.append(np.array([k,len(self.latitudes)-1,0]))

        for k,i in np.ndindex(nLay, nLat):
            start = len(nodeCoord)
            if i == 0 and poles: continue # north pole already done
            elif i == len(self.latitudes)-1 and poles: continue # south pole already done
            nodeCoord.append(sphere2cart([altInf[k,i], latN[i], lonW]))
            nodeCoord.append(sphere2cart([altInf[k,i], latN[i], lonE]))
            nodeCoord.append(sphere2cart([altInf[k,i], latS[i], lonE]))
            nodeCoord.append(sphere2cart([altInf[k,i], latS[i], lonW]))
            nodeCoord.append(sphere2cart([altSup[k,i], latN[i], lonW]))
            nodeCoord.append(sphere2cart([altSup[k,i], latN[i], lonE]))
            nodeCoord.append(sphere2cart([altSup[k,i], latS[i], lonE]))
            nodeCoord.append(sphere2cart([altSup[k,i], latS[i], lonW]))

            cellId = []
            for tetraInd in tetraInds:
                cellId.append(len(tetraIds))
                tetraIds.append(start + tetraInd)
                tetraALL.append(np.array([k,i,0]))
            cellIds.append(np.array(cellId))
            cellIndexALL.append(np.array([k,i,0]))

        self.nodeCoord = np.array(nodeCoord)
        self.tetraIds = np.array(tetraIds, dtype=int)       
        self.cellIndices = np.array(cellIndexALL, dtype=int)
        self.cellIds = cellIds
        self.tetraALL = np.array(tetraALL)

        self.calculationGeometry = f"{self.geometryFolder}volrad_geometry_{self.case}.bin"
        self.calculationGeometryObj = f"{self.geometryFolder}volrad_geometry_{self.case}.vtk"
        print('generating atmosphere mesh bin file for radiative budget calculation...')
        write_binary_file_grid(self.calculationGeometry,4096,self.nodeCoord,self.tetraIds)
        print('bin generation completed.')
        print("generating Atmosphere geometry VTK file ...")
        write_vtk_tetr(self.nodeCoord,self.tetraIds, self.calculationGeometryObj)
        print("VTK file written.")
        self.volrad["mesh"] = self.calculationGeometry
        return

    def __makeColumnPP(self, altitudes, hwidth, center=True):
        '''
        Generate a mesh of a squared based column.
        # Inputs:
        - altitudes (1-D array, shape = nLevel or nLayer, float [m]): array of
          altitudes, either at the center of the cells or at the boundaries.
        - hwidth (flaot [m]): dimension of the squared base of the column.
        - center (optional, default: True, bool): tru if the altitudes
          correspond tho the cell centers and false if they correspond to the
          boundaries of the cells.
        '''

        if center:
            altSup = np.zeros_like(altitudes)
            altInf = np.zeros_like(altitudes)
            altSup[:-1] = altInf[1:] = 0.5 * (altitudes[1:] + altitudes[:-1])
            altSup[-1,:] = 2 * altitudes[-1] - altitudes[-2]
            altInf[0,:] = 0
        else:
            altInf = np.zeros(len(altitudes)-1)
            altSup = np.zeros(len(altitudes)-1)
            altInf = altitudes[:-1]
            altSup = altitudes[1:]

        nodeCoord = []      # contains nodes cartesian coordinates                                      shape=(nNodes,3)
        tetraIds = []       # contains the ids of the nodes of each tetrahedron                         shape=(nTetra,4)
        cellIds = []        # contains the ids of the tetrahedrons forming each PCM cell                shape=(nPCMcell,?)
        cellIndexALL = []   # contains the Altitude, Latitude and Longitude indices of each cell        shape=(nPCMcell,3)
        tetraALL = []       # contains the Altitude, Latitude and Longitude indices of each tetrahedron shape=(nPCMcell,3)

        tetraInds = []
        tetraInds.append(np.array([0,1,2,5]))
        tetraInds.append(np.array([0,2,3,7]))
        tetraInds.append(np.array([0,4,5,7]))
        tetraInds.append(np.array([2,5,6,7]))
        tetraInds.append(np.array([0,2,5,7]))

        for k in range(len(altSup)):
            start = len(nodeCoord)
            nodeCoord.append([altInf[k],  hwidth, -hwidth])
            nodeCoord.append([altInf[k],  hwidth,  hwidth])
            nodeCoord.append([altInf[k], -hwidth,  hwidth])
            nodeCoord.append([altInf[k], -hwidth, -hwidth])
            nodeCoord.append([altSup[k],  hwidth, -hwidth])
            nodeCoord.append([altSup[k],  hwidth,  hwidth])
            nodeCoord.append([altSup[k], -hwidth,  hwidth])
            nodeCoord.append([altSup[k], -hwidth, -hwidth])

            cellId = []
            for tetraInd in tetraInds:
                cellId.append(len(tetraIds))
                tetraIds.append(start + tetraInd)
                tetraALL.append(np.array([k,0,0]))
            cellIds.append(np.array(cellId))
            cellIndexALL.append(np.array([k,0,0]))

        self.nodeCoord = np.array(nodeCoord)
        self.tetraIds = np.array(tetraIds, dtype=int)
        self.cellIndices = np.array(cellIndexALL, dtype=int)
        self.cellIds = cellIds
        self.tetraALL = np.array(tetraALL)

        self.calculationGeometry = f"{self.geometryFolder}volrad_geometry_{self.case}.bin"
        self.calculationGeometryObj = f"{self.geometryFolder}volrad_geometry_{self.case}.vtk"
        print('generating atmosphere mesh bin file for radiative budget calculation...')
        write_binary_file_grid(self.calculationGeometry,4096,self.nodeCoord,self.tetraIds)
        print('bin generation completed.')
        print("generating Atmosphere geometry VTK file ...")
        write_vtk_tetr(self.nodeCoord,self.tetraIds, self.calculationGeometryObj)
        print("VTK file written.")
        self.volrad["mesh"] = self.calculationGeometry
        return

    def __makeMeshExtractFromData(self, data, cells):
        '''
        Generate a mesh from the data object.
        # Input
        - cells (2-D array, shape=(nCell,3)): list of the cells to be extracted with the altitude, latitude and longitude indices
        '''
        self.nodeCoord = []
        self.tetraIds = []
        self.cellIds = []
        self.cellIndices = []
        cumul = []

        for cell in cells:
            self.cellIndices.append(cell)
            coord, ids, pdf = self.__extractSingleCell(data, *cell)
            startNode = len(self.nodeCoord)
            startTetra = len(self.tetraIds)
            for c in coord:
                self.nodeCoord.append(c)
            for id in ids:
                self.tetraIds.append(np.array(id)+startNode)
            endTetra = len(self.tetraIds)
            self.cellIds.append(np.arange(startTetra, endTetra))

            if pdf is not None:
                for val in pdf: cumul.append(val)

        self.nodeCoord = np.array(self.nodeCoord)
        self.tetraIds = np.array(self.tetraIds)
        self.cellIndices = np.array(self.cellIndices)


        self.calculationGeometry = f"{self.geometryFolder}volrad_geometry_{self.case}.bin"
        self.calculationGeometryObj = f"{self.geometryFolder}volrad_geometry_{self.case}.vtk"
        print('generating atmosphere mesh bin file for radiative budget calculation...')
        write_binary_file_grid(self.calculationGeometry,4096,self.nodeCoord,self.tetraIds)
        print('bin generation completed.')
        print("generating Atmosphere geometry VTK file ...")
        write_vtk_tetr(self.nodeCoord,self.tetraIds, self.calculationGeometryObj)
        print("VTK file written.")
        self.volrad["mesh"] = self.calculationGeometry

        if cumul:
            self.volrad["PDF"] = f"{self.geometryFolder}volrad_pdf_{self.case}.bin"
            self.cumulDist = np.array(cumul) 
            print('generating spectral sampling distribution bin file \
                    for radiative budget calculation...')
            write_binary_file_spectral_pdf(self.volrad["PDF"], 4096,
                                           self.cumulDist.shape[0], self.cumulDist)
            print('bin generation completed.')
        return

    def __extractSingleCell(self, data, altitude, latitude, longitude):
        '''
        # Input
        - Data: data object
        - altitude: (integer) altitude index of the cell
        - latitude: (integer) latitude index of the cell
        - longitude: (integer) longitude index of the cell
        '''
        cellNum = data.cellIndices.tolist().index([altitude, latitude, longitude])
        tetrahedrons = data.cellIds[cellNum]  # we get the tetrahedrons ids for the cell
        if isinstance(data, Data):
            nodeIds = data.atmosphere["cells ids"]
            nodeCoordOG = data.atmosphere["nodes coordinates"]
            pdfOG = None
        elif isinstance(data,Geometry):
            nodeIds = data.tetraIds
            nodeCoordOG = data.nodeCoord
            if "PDF" in data.volrad.keys():
                pdfOG = data.cumulDist
            else:
                pdfOG = None
        else: raise TypeError(f"Should be of type {Data} or {Geometry}, not {type(data)}")

        nodeCoord = []
        cellIds = []
        for tetra in tetrahedrons:
            nodes = nodeIds[tetra]
            tetraId = []
            for node in nodes:
                tetraId.append(len(nodeCoord))
                nodeCoord.append(nodeCoordOG[node,:])
            cellIds.append(tetraId)

        if pdfOG is not None:
            return nodeCoord, cellIds, pdfOG[tetrahedrons,:]
        else:
            return nodeCoord, cellIds, None

    def __calculateRoll(self):
        '''
        Calculate the roll as perpendicular to both the line of sight and the z axis.
        In case the LOS is aligned with z, there are infinite possibilities and we arbitrary chose to fix the roll along x
        '''
        cros = np.cross(self.lineOfSight, np.array([0., 0., 1.]))
        if np.linalg.norm(cros) < 1e-10: return np.array([1., 0., 0.])  # if the line of sight is along z, we place the roll along x
        else: return cros/np.linalg.norm(cros)          # esle, the roll is defined as perpendicular to both z and the line of sight

    def __lineOfSight(self):
        ''' Calculate the line of sight and target to camera vectors'''
        self.lineOfSight = self.camera["target"] - self.camera["position"]
        self.tagtToCamera = - self.lineOfSight

    def __writeRadiance(self, wavelength, spectrum):
        '''Write the radiance file'''
        writeSourceRadiance(self.radianceFile, wavelength, spectrum, 4096)
        return


if __name__ == "__main__":
    print("Module loaded")
