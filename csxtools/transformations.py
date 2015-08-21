#
# transformations.py (c) Stuart B. Wilkins 2010 and (c) Sven Partzsch 2010
#
# $Id: transformations.py 238 2012-10-16 13:15:42Z stuwilkins $
# $HeadURL: https://pyspec.svn.sourceforge.net/svnroot/pyspec/trunk/pyspec/ccd/transformations.py $
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Part of the "pyspec" package
#

import gc
import time
import numpy as np
import numpy.ma as ma

try:
    import ctrans
except:
    import ctrans2 as ctrans


gc.enable()

__version__   = "$Revision: 238 $"
__author__    = "Stuart B. Wilkins <stuwilkins@mac.com>, Sven Partzsch <SvenPartzsch@gmx.de>"
__date__      = "$LastChangedDate: 2012-10-16 09:15:42 -0400 (Tue, 16 Oct 2012) $"
__id__        = "$Id: transformations.py 238 2012-10-16 13:15:42Z stuwilkins $"

#
# image processor class
#

class ImageProcessor():
    """Image Processor class

    This class provides the processing of single and sets of CCD-images
    in more detail: each pixel is transformed into reciprocal space
    the set of reciprocal vectors and intensities is gridded on a regular cuboid
    the needed informations can be provided by a spec scan from the pyspec package"""

    hc_over_e = 12398.4
    def __init__(self, sP = None):
        """Initialize the image processor

        sP         : ScanProcessor Instance
                     Scan processor object for getting the images
        """

        # set parameters to configure the CCD setup
        self.setDetectorProp(0.030, 0.030, 960, 960, 480, 480)
        self.setDetectorPos(320, 0.0)
        self.setDetectorMask()

        # Default to frame mode 1
        self.setFrameMode(4)

        self.totSet   = None

        self.gridData   = None
        self.gridOccu   = None
        self.gridOut    = None
        self.gridStdErr = None

        self.Qmin  = None
        self.Qmax  = None
        self.dQN   = None

        self._mask = None

        if sP is not None:
            self.setScanProcessor(fP)


    def getGrid(self):
        """Convinience function to return useful grid values

        This function returns the X, Y and Z coordinates of the grid
        along with the intensity and standard error grids. For example::

            >>>X, Y, Z, I, E, N = ip.getGrid()

        """
        X, Y, Z = self.getGridMesh()
        I = self.getGridData()
        E = self.getGridStdErr()
        N = self.getGridOccu()
        return X, Y, Z, I, E, N

    def getImageData(self):
        """Get the totat image data, transformed into Q"""
        return self.totSet

    def getGridData(self):
        """Return the intensity grid

        This function will mask the data if previously
        set to be masked"""
        # Here we check for mask
        if self._mask is not None:
            return ma.masked_array(self.gridData, mask = self._mask)
        else:
            return self.gridData

    def getGridStdErr(self):
        """Return the standard error grid"""
        if self._mask is not None:
            return ma.masked_array(self.gridStdErr, mask = self._mask)
        else:
            return self.gridStdErr

    def getGridStdDev(self):
        """Return the standard deviation grid"""
        st = self.gridStdErr * sqrt(self.gridOccu)
        if self._mask is not None:
            return ma.masked_array(st, mask = self._mask)
        else:
            return st

    def getGridOccu(self):
        """Return the occupation of the grid"""
        return self.gridOccu

    def setGridMaskOnOccu(self, thresh = 10):
        """Set grid mask from bin occupation

        thresh : int
            Threshold for grid occupation"""

        self._mask = self.gridOccu <= thresh

    def setDetectorProp(self, detPixSizeX, detPixSizeY, detSizeX, detSizeY, detX0, detY0):
        """Set properties of used detector

        detPixSizeX : float (mm)
             Detector pixel size in detector X-direction.
        detPixSizeY : float (mm)
             Detector pixel size in detector Y-direction.
        detSizeX    : integer
             Detector no. of pixels (size) in detector X-direction.
        detSizeY    : integer
             Detector no. of pixels (size) in detector Y-direction.
        detX0       : float
             Detector X-coordinate of center for reference.
        detY0       : float
             Detector Y-coordinate of center for reference."""

        self.detPixSizeX = detPixSizeX
        self.detPixSizeY = detPixSizeY
        self.detSizeX    = detSizeX
        self.detSizeY    = detSizeY
        self.detX0       = detX0
        self.detY0       = detY0

    def getDetectorProp(self):
        """Get properties of used detector returned as a tuple

        detPixSizeX : float (mm)
             Detector pixel size in detector X-direction.
        detPixSizeY : float (mm)
             Detector pixel size in detector Y-direction.
        detSizeX    : integer
             Detector no. of pixels (size) in detector X-direction.
        detSizeY    : integer
             Detector no. of pixels (size) in detector Y-direction.
        detX0       : float
             Detector X-coordinate of center for reference.
        detY0       : float
             Detector Y-coordinate of center for reference."""

        return self.detPixSizeX, self.detPixSizeY, self.detSizeX, self.detSizeY, self.detX0, self.detY0

    def setDetectorPos(self, detDis = 300.0, detAng = 0.0):
        """Set the detector position

        detDis : float (mm)
           Detector distance from sample.
        detAng : float (deg)
           Detector miss alignement angle (rotation around incident beam)"""

        self.detDis = detDis
        self.detAngle = detAng

    def getDetectorPos(self, detDis = 30.0, detAng = 0.0):
        """Get the detector position

        detDis : float (mm)
           Detector distance from sample.
        detAng : float (deg)
           Detector miss alignement angle (rotation around incident beam)"""

        return self.detDis, self.detAngle

    def setDetectorMask(self, mask = None):
        """Set the detector mask, to exclude data points

        mask : ndarray
           Array of same form as CCD images, with 1's for valid data points

        """
        self.detMask = mask

    def setBins(self, binX = 1, binY = 1):
        """Set detector binning.

        This function sets the detector binning, and modifies the detector paremeters accordingly.

        binX : integer
           Binning in x-direction.
        binY : integer
           Binning in y-direction.

        """

        # try to get old bins
        try:
            oldBinX = self.binX
        except:
            oldBinX = 1
        try:
            oldBinY = self.binY
        except:
            oldBinY = 1

        # scaling ratios
        ratX = 1.0*binX/oldBinX
        ratY = 1.0*binY/oldBinY

        # apply changes to detector probperties
        self.detPixSizeX *= ratX
        self.detPixSizeY *= ratY
        self.detSizeX     = int(self.detSizeX / ratX)
        self.detSizeY     = int(self.detSizeY / ratY)
        self.detX0       /= ratX
        self.detY0       /= ratY

        self.binX = binX
        self.binY = binY


    def getBins(self, binX, binY):
        """Set no. of bins. Takes them into acount for pixel size, detector size and detector center

        binX : no. of pixels along detector X-direction which are bined
        binY : no. of pixels along detector Y-direction which are bined"""

        return self.binX, self.binY


    def setSetSettings(self, waveLen, settingAngles, UBmat):
        """Set the settings for the set

        The set settings are:
        waveLen       : float
           Wavelength of the X-rays (Angstroms).
        settingAngles : setting angles of the diffractometer at each image (data point)
        UBmat         : UB matrix (orientation matrix) to transform the HKL-values into the sample-frame (phi-frame)
        """

        self.waveLen       = waveLen
        self.settingAngles = settingAngles
        self.UBmat         = UBmat


    def setFrameMode(self, mode):
        """Set the mode of the output frame for (Qx, Qy, Qz)

        mode : Integer
           Mode (see below)

        The image processor uses a number of modes which defile the
        coordinates of the final grid. These are:

        mode 1 : 'theta'    : Theta axis frame.
        mode 2 : 'phi'      : Phi axis frame.
        mode 3 : 'cart'     : Crystal cartesian frame.
        mode 4 : 'hkl'      : Reciproal lattice units frame."""

        if mode == 'theta':
            self.frameMode = 1
        elif mode == 'phi':
            self.frameMode = 2
        elif mode == 'cart':
            self.frameMode = 3
        elif mode == 'hkl':
            self.frameMode = 4
        else:
            self.frameMode = mode


    def getFrameMode(self):
        """Get the mode of the output frame for (Qx, Qy, Qz)

        mode 1 : 'theta'    : Theta axis frame.
        mode 2 : 'phi'      : Phi axis frame.
        mode 3 : 'cart'     : Crystal cartesian frame.
        mode 4 : 'hkl'      : Reciproal lattice units frame."""

        return self.frameMode


    def setGridSize(self, Qmin = None, Qmax = None, dQN = None):
        """Set the options for the gridding of the dataset

        Qmin : ndarray
           Minimum values of the cuboid [Qx, Qy, Qz]_min
        Qmax : ndarray
           Maximum values of the cuboid [Qx, Qy, Qz]_max
        dQN  : ndarray
           No. of grid parts (bins)     [Nqx, Nqy, Nqz]"""

        if Qmin is not None:
            self.Qmin = np.array(Qmin)
        if Qmax is not None:
            self.Qmax = np.array(Qmax)
        if dQN is not None:
            self.dQN  = np.array(dQN)


    def getGridSize(self):
        """Get the options for the gridding of the dataset

        returns tuple of (Qmin, Qmax, dQN)"""

        return self.Qmin, self.Qmax, self.dQN


    def getGridMesh(self):
        """Return the grid vectors as a mesh.

        This function returns the X, Y and Z coordinates of the grid as 3d
        arrays.

        Example:

        X, Y, Z = ip.getGridMesh()

        These values can be used for obtaining the coordinates of each voxel.
        For instance, the position of the (0,0,0) voxel is given by

        x = X[0,0,0]
        y = Y[0,0,0]
        z = Z[0,0,0]"""

        grid = np.mgrid[0:self.dQN[0], 0:self.dQN[1], 0:self.dQN[2]]
        r = (self.Qmax - self.Qmin) / self.dQN

        X = grid[0] * r[0] + self.Qmin[0]
        Y = grid[1] * r[1] + self.Qmin[1]
        Z = grid[2] * r[2] + self.Qmin[2]

        return X, Y, Z


    def _calcBMatrix(self, angles):
        """Calculate the B matrix from reciprocal space angles

        anges: ndarray
           Array of real space values, [a, b, c, alpha, beta, gamma]

        returns B matrix as (3x3) ndarray.
        """
        B = np.ones((3,3))
        B[0,0] = angles[0]
        B[1,0] = 0
        B[2,0] = 0
        B[0,1] = angles[1] * cos(angles[5])
        B[1,1] = angles[1] * sin(angles[5])
        B[2,1] = 0
        B[0,2] = angles[2] * cos(angles[4])
        B[1,2] = -1.0 * angles[2] * sin(angles[4]) * cos(angles[3])
        B[2,2] = 2 * np.pi / angles[2]

        return B


# Added by Vivek ----- Start

    def setScanProcessor(self, sp):
        """Set Values from  ImageProcessor"""
        self.scanProcessor = sp

    def getScanProcessor(self):
        """Get the ScanProcessor object for treating the CCD images

        fp : ScanProcessor object with the CCD images"""

        return self.scanProcessor

    def setFromScanProcessor(self):
        """Set Values from  ImageProcessor"""
        self.energy = self.scanProcessor.get_energy()
        self.waveLen = self.hc_over_e / self.energy.mean()
        self.settingAngles = self.scanProcessor.getSIXCAngles()


    def setUB(self, UBmat=None):
        self.UBmat = UBmat


    def setEnergy(self, energy):
        self.energy = energy

# Added by Vivek ----- End

    def _XYCorrect(self, xVal, yVal):
        """Correct the miss alignement of the CCD camera

        xVal : measured X-values of the detector
        yVal : measured Y-values of the detector

        return
        xNew : corrected X-values of the detector
        yNew : corrected Y-values of the detector"""

        # detetoc angle in rad
        detAn = self.detAngle /180.0 * np.pi

        xNew = np.cos(detAn) * xVal - np.sin(detAn) * yVal
        yNew = np.sin(detAn) * xVal + np.cos(detAn) * yVal

        return xNew, yNew

    #
    # help functions for input / output
    #

    def __str__(self):
        """Create the information about the grid process"""

        _s = "Detector Parameters:\n\n"

        _s += "Detector size        :%d x %d [pixels]\n" % (self.detSizeX, self.detSizeY)
        _s += "Detector pixel size  :%f x %f [mm]\n" % (self.detPixSizeX, self.detPixSizeY)
        _s += "Zero (center) of CCD :(%f, %f) [pixels]\n" % (self.detX0, self.detY0)
        _s += "Sample Detector dist.:%f [mm]\n" % self.detDis
        _s += "Detector rot. ang.   :%f [deg]\n" % self.detAngle

        if self.totSet is not None:
            _s += "\n\nData Set:\n"

            _s += "Number of Pixels : %.2e\n" % self.totSet.shape[0]
            _s += 'Q_min            : [%.3e %.3e %.3e]\n' % (self.totSet[:,0].min(),
                                                             self.totSet[:,1].min(),
                                                             self.totSet[:,2].min())
            _s += 'Q_max            : [%.3e %.3e %.3e]\n' % (self.totSet[:,0].max(),
                                                             self.totSet[:,1].max(),
                                                             self.totSet[:,2].max())
            _s += 'I_min            : %.3e\n' % self.totSet[:,3].min()
            _s += 'I_max            : %.3e\n' % self.totSet[:,3].max()
            _s += 'I_ave            : %.3e\n' % self.totSet[:,3].mean()

        _s += "\n\nGrid Parameters:\n\n"
        mode = self.frameMode
        if mode == 1:
            _s += 'Frame Mode 1: (Qx, Qy, Qz) in theta-frame and (1/Angstrom)\n'
        elif mode == 2:
            _s += 'Frame Mode 2: (Qx, Qy, Qz) in phi-frame and (1/Angstrom)\n'
        elif mode == 3:
            _s += 'Frame Mode 3: (Qx, Qy, Qz) in cartesian-frame and (1/Angstrom)\n'
        elif mode == 4:
            _s += 'Frame Mode 4: (H, K, L) in hkl-frame and (reciprocal lattice units)\n'

        _s += '\n\nGrid Vectors:\n\n'
        if self.Qmin is not None:
            _s += 'Q_min     : [%.3e %.3e %.3e]\n' % (self.Qmin[0], self.Qmin[1], self.Qmin[2])
        if self.Qmax is not None:
            _s += 'Q_max     : [%.3e %.3e %.3e]\n' % (self.Qmax[0], self.Qmax[1], self.Qmax[2])
        if self.dQN is not None:
            _s += 'Grid Size : [%.3e %.3e %.3e]\n' % (self.dQN[0], self.dQN[1], self.dQN[2])

        if self.gridData is not None:
            _s += '\n\nGrid Statistics:\n\n'
            _s += 'No. of voxels in grid           : \t %.2e\n' % (self.gridData.size)
            _s += 'No. of data points outside grid : \t %.2e\n' % (self.gridOut)
            _s += 'No. of empty voxels             : \t %.2e\n' % ((self.gridOccu == 0).sum())

        return _s

    #
    # process part
    #

    def processToQ(self):
        """Process selcted images of the full set into (Qx, Qy, Qz, I)

        This function takes the images provided by a FileProcessor instance, and
        converts them to a set of (Qx, Qy, Qz, I) values in the frame mode which
        is set prevously in this class.

        """
        ccdToQkwArgs = {}
        if self.totSet is not None:
            del self.totSet
            gc.collect()

        if not self.scanProcessor:
            raise Exception("No ScanProcessor specified.")

        if not self.scanProcessor.processed:       #VT
            self.scanProcessor.process()

        if self.settingAngles is None:
            raise Exception("No setting angles specified.")

        print("\n")
        print("---- Setting angle size :", self.settingAngles.shape)
        print("---- CCD Size :", (self.detSizeX, self.detSizeY))
        print("**** Converting to Q")
        t1 = time.time()
        self.totSet = ctrans.ccdToQ(angles      = self.settingAngles * np.pi / 180.0,
                                    mode        = self.frameMode,
                                    ccd_size    = (self.detSizeX, self.detSizeY),
                                    ccd_pixsize = (self.detPixSizeX, self.detPixSizeY),
                                    ccd_cen     = (self.detX0, self.detY0),
                                    dist        = self.detDis,
                                    wavelength  = self.waveLen,
                                    UBinv       = np.matrix(self.UBmat).I,
                                    **ccdToQkwArgs)
        t2 = time.time()
        print("---- DONE (Processed in %f seconds)" % (t2 - t1))
        print("---- Setsize is %d" % self.totSet.shape[0])
        self.totSet[:,3] = np.ravel(self.scanProcessor.get_images())  #VT

        self.images_q = ma.masked_array(self.totSet)
        #if self.detMask is None:
            #m = self.fileProcessor.getMask()
            #m = self.scanProcessor.mask          #VT
            #if m is not None:
                #if m.sum():
                    #self.detMask = m

        if self.detMask is not None:
            print("---- Masking data")
            totMask = self.detMask.ravel()
            self.totSet = self.totSet[totMask == False,:]

            print("---- New setsize is %d " % self.totSet.shape[0])


    def processGrid(self):
        """Process imageset of (Qx, Qy, Qz, I) into grid

        This function, process the set of (Qx, Qy, Qz, I) values and grid the data."""
        print("---- Total data is %f MBytes\n" % (self.totSet.nbytes / 1024.0**2))

        if self.totSet is None:
            raise Exception("No set of (Qx, Qy, Qz, I). Cannot process grid.")

        # prepare min, max,... from defaults if not set
        if self.Qmin is None:
            self.Qmin = np.array([ self.totSet[:,0].min(), self.totSet[:,1].min(), self.totSet[:,2].min() ])
        if self.Qmax is None:
            self.Qmax = np.array([ self.totSet[:,0].max(), self.totSet[:,1].max(), self.totSet[:,2].max() ])
        if self.dQN is None:
            self.dQN = [100, 100, 100]

        # 3D grid of the data set
        print("**** Gridding Data.")
        t1 = time.time()
        gridData, gridOccu, gridStdErr, gridOut = ctrans.grid3d(self.totSet, self.Qmin, self.Qmax, self.dQN, norm = 1)
        t2 = time.time()
        print("---- DONE (Processed in %f seconds)" % (t2 - t1))
        emptNb = (gridOccu == 0).sum()
        if gridOut != 0:
            print("---- Warning : There are %.2e points outside the grid (%.2e bins in the grid)" % (gridOut, gridData.size))
        if emptNb:
            print("---- Warning : There are %.2e values zero in the grid" % emptNb)

       # store intensity, occupation and no. of outside data points of the grid
        self.gridData   = gridData
        self.gridOccu   = gridOccu
        self.gridOut    = gridOut
        self.gridStdErr = gridStdErr


    def process(self):
        """Convinience function to perform all processing"""
        self.processToQ()
        self.processGrid()
