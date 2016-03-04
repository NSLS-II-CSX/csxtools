import numpy as np
import exceptions


class Diffractometer():
    """Diffractometer class

    This class provides various functions to perform calculations to
    and from the sample and instrument frames

    used lab frame:
    Z up, Y along X-ray beam, X = Y x Z;
    sample rotations:
    mu    : along +Z     -> S'    (mu-frame),
    theta : along +X'    -> S''   (theta-frame),
    chi   : along +Y''   -> S'''  (chi-frame),
    phi   : along +X'''  -> S'''' (phi-frame);
    detector rotations:
    mu    : along +Z     -> S'    (mu-frame),
    delta : along +X'    -> S*    (delta-frame),
    gamma : along +Z*    -> S**   (gamma-frame)"""

    # HC_OVER_E to convert from E to Lambda
    hc_over_e = 12398.4
    # transformation from sixc to fourc (tardis)
    sixcToFourc = np.array([[0, 0, -1],
                            [0, 1, 0],
                            [1, 0, 0]])

    def __init__(self, mode='sixc'):
        """Initialize the class
        'mode' defines the type of diffractometer"""
        self.mode = mode
        self.Qtheta = None

    def setAllAngles(self, angles, mode='deg'):
        """Sets angles for calculation.
        Angles are expected in spec 'sixc' order:
        Delta     Theta       Chi       Phi        Mu     Gamma"""
        self._settingAngles = angles
        if mode == 'deg':
            self._settingAngles = self._settingAngles / 180.0 * np.pi

    def setAngles(self, delta=None, theta=None, chi=None,
                  phi=None, mu=None, gamma=None, mode='deg'):
        """Set the angles for calculation"""

        # Internally angles are stored in sixc (spec) order
        # Delta     Theta       Chi       Phi        Mu     Gamma

        maxlen = 1

        for aa in [delta, theta, chi, phi, mu, gamma]:
            if type(aa) == np.ndarray:
                if maxlen == 1:
                    maxlen = aa.size
                elif maxlen != aa.size:
                    raise exceptions.ValueError("Values must be numpy array"
                                                " of same size or scalar"
                                                " (float).")

        self._settingAngles = np.zeros((maxlen, 6))
        for aa, i in zip([delta, theta, chi, phi, mu, gamma], range(6)):
            if type(aa) == float:
                self._settingAngles[:, i] = np.ones(maxlen) * aa
            else:
                self._settingAngles[:, i] = aa

        if mode == 'deg':
            self._settingAngles = self._settingAngles / 180.0 * np.pi

    def setEnergy(self, energy):
        """Set the energy (in eV) for calculations"""
        self._waveLen = self.hc_over_e / energy

    def setLambda(self, waveLen):
        """Set the wavelength (in Angstroms) for calculations"""
        self._waveLen = waveLen

    def setUbMatrix(self, UBmat):
        """Sets the UB matrix"""
        self.UBmat = np.matrix(UBmat)
        self.UBinv = self.UBmat.I

    def _calc_QTheta(self):
        """Calculate (Qx, Qy, Qz) set in theta-frame from angles

        k0      = (0, kl, 0), kl: wave vector length,
        ki''    = rotX(-theta)*rotZ(-mu)*k0,
        kf''    = rotX(-theta+delta)*rotZ(gamma)*k0,
        QTheta = Q'' = kf'' - ki'' """

        # wave vector length in 1/A
        kl = 2 * np.pi / self._waveLen
        # wave vector for all diffractometer angles zero
        # k0 = [0, kl, 0]

        # alias for used angles
        mu = self._settingAngles[:, 4]
        theta = self._settingAngles[:, 1]
        delta = self._settingAngles[:, 0]
        gamma = self._settingAngles[:, 5]

        ki = np.zeros((self._settingAngles.shape[0], 3))
        kf = np.zeros(ki.shape)

        # initial wave vector in theta-frame
        # ki'' = rotX(-theta)*rotZ(-mu)*k0
        ki[:, 0] = np.sin(mu) * kl
        ki[:, 1] = np.cos(theta) * np.cos(mu) * kl
        ki[:, 2] = -np.sin(theta) * np.cos(mu) * kl

        # final   wave vector in theta-frame
        # kf'' = rotX(-theta+delta)*rotZ(gamma)*k0

        kf[:, 0] = -np.sin(gamma) * kl
        kf[:, 1] = np.cos(delta-theta) * np.cos(gamma) * kl
        kf[:, 2] = np.sin(delta-theta) * np.cos(gamma) * kl

        #   scattering vector in theta-frame
        q = kf - ki

        self.QTheta = q

    def calc(self):
        self._calc_QTheta()

    def getQTheta(self):
        """Return transformed coordinates"""
        return self.QTheta

    def getQPhi(self):
        """Calculate (Qx, Qy, Qz) set in phi-frame from (Qx, Qy, Qz) set in theta-frame

        QPhi = rotZ(-phi) rotY(-chi) QTheta """

        # alias for used angles
        chi = self._settingAngles[:, 2]
        phi = self._settingAngles[:, 3]
        # alias for q-vector in theta-frame
        QTh = self.QTheta

        # QPhi = rotZ(-phi) rotY(-chi) QTheta
        # matrix coefficients are calculated by hand for convenience
        r11 = np.cos(chi)
        r12 = 0.0
        r13 = -np.sin(chi)
        r21 = np.sin(phi) * np.sin(chi)
        r22 = np.cos(phi)
        r23 = np.sin(phi) * np.cos(chi)
        r31 = np.cos(phi) * np.sin(chi)
        r32 = -np.sin(phi)
        r33 = np.cos(phi) * np.cos(chi)

        QPhi = np.zeros(QTh.shape)
        QPhi[:, 0] = r11*QTh[:, 0] + r12*QTh[:, 1] + r13*QTh[:, 2]
        QPhi[:, 1] = r21*QTh[:, 0] + r22*QTh[:, 1] + r23*QTh[:, 2]
        QPhi[:, 2] = r31*QTh[:, 0] + r32*QTh[:, 1] + r33*QTh[:, 2]

        return QPhi

    def getQCart(self):
        """Calculate (Qx, Qy, Qz) set in cartesian reciprocal space from
        (Qx, Qy, Qz) set in theta-frame

        still under construction """

        # still under construction

        # return (np.dot( self.sixcToFourc.T, self.getQPhi().T ) ).T

    def getQHKL(self):
        """Calc HKL values from (Qx, Qy, Qz) set in theta-frame with UB-matrix

        QHKL = UB^-1 sixcToFourc^T QPhi"""

        return (self.UBinv * np.dot(self.sixcToFourc.T, self.getQPhi().T)).T
