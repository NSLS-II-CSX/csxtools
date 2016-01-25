import numpy as np
from lmfit import Model
from lmfit.models import index_of, fwhm_expr, _validate_1d, update_param_vals


def fwhm_expr_2D(model, parameter='sigma'):
    "return constraint expression for fwhm"
    return "%.7f*%s%s" % (model.fwhm_factor, model.prefix, parameter)


def guess_from_peak(model, y, x, negative, ampscale=1.0, sigscale=1.0, area=True):
    "estimate amp, cen, sigma for a peak, create params"
    if x is None:
        return 1.0, 0.0, 1.0
    maxy, miny = max(y), min(y)
    maxx, minx = max(x), min(x)
    imaxy = index_of(y, maxy)

    #amp = (maxy - miny)
    amp = maxy - (y[0]+y[-1])/2.0
    cen = x[imaxy]
    sig = (maxx-minx)/6.0

    halfmax_vals = np.where(y > (maxy+miny)/2.0)[0]
    if negative:
        imaxy = index_of(y, miny)
        amp = -(maxy - miny)*2.0
        halfmax_vals = np.where(y < (maxy+miny)/2.0)[0]
    if len(halfmax_vals) > 2:
        sig = (x[halfmax_vals[-1]] - x[halfmax_vals[0]])/2.0
        cen = x[halfmax_vals].mean()
    amp = amp*ampscale
    if area:
        amp *= sig*2.0
    sig = sig*sigscale

    pars = model.make_params(amplitude=amp, center=cen, sigma=sig)
    pars['%ssigma' % model.prefix].set(min=0.0)
    return pars


def guess_from_peak_2D(model, y, x, negative, ampscale=1.0, sigscale=1.0, amp_area=True):
    "estimate amp, cen_x, cen_y, sigma_x, sigma_y for a 2D peak, create params"
    if x is None:
        return 1.0, 0.0, 0.0, 1.0, 1.0
    x0 = x[0]
    x1 = x[1]

    maxy, miny = np.nanmax(y), np.nanmin(y)
    maxx0, minx0 = max(x0), min(x0)
    maxx1, minx1 = max(x1), min(x1)
    imaxy = index_of(y, maxy)

    #amp = (maxy - miny)
    amp = maxy - (y[0]+y[-1])/2.0
    cen_x = x0[imaxy]
    cen_y = x1[imaxy]
    sig_x = (maxx0-minx0)/6.0
    sig_y = (maxx1-minx1)/6.0

    halfmax_vals = np.where(y > (maxy+miny)/2.0)[0]
    if negative:
        imaxy = index_of(y, miny)
        amp = -(maxy - miny)*2.0
        halfmax_vals = np.where(y < (maxy+miny)/2.0)[0]

    if len(halfmax_vals) > 2:
        sig_x = abs((x0[halfmax_vals[-1]] - x0[halfmax_vals[0]])/2.0)
        sig_y = abs((x1[halfmax_vals[-1]] - x1[halfmax_vals[0]])/2.0)
        cen_x = x0[halfmax_vals].mean()
        cen_y = x1[halfmax_vals].mean()

    amp = amp*ampscale
    if amp_area:
        amp *= sig_x*sig_y*4.0
    sig_x = sig_x*sigscale
    sig_y = sig_y*sigscale

    pars = model.make_params(amplitude=amp,
                             center_x=cen_x, center_y=cen_y,
                             sigma_x=sig_x,  sigma_y=sig_y)
    pars['%ssigma_x' % model.prefix].set(min=0.0)
    pars['%ssigma_y' % model.prefix].set(min=0.0)
    return pars


def lorentzian_squared(x, amplitude=1.0, center=0.0, sigma=1.0):
    """Lorentzian squared defined by amplitude
      amplitude*(1/(1 +((x[0] - x_center)/sigma_x)**2)**2

    The HWHM is related to the parameter :math:`\Gamma` by the relation:
      :math:`\kappa = \sqrt{\sqrt{2} - 1}\sigma`

    """
    return amplitude * (1 / (1 + ((x - center) / sigma)**2) )**2


def plane(x, intercept, slope_x, slope_y):
    """2D plane
    Function:
       :math:`f(x) = p_0 + p_1x + p_2y`
    """
    return intercept + slope_x * x[0] + slope_y * x[1]


def lor2_2D(x, amplitude=1.0, center_x=0.0, center_y=0.0, sigma_x=1.0, sigma_y=1.0):
    """2D Lorentzian squared defined by amplitude
    amplitude*(1/(1 +((x[0] - x_center)/sigma_x)**2 + ((x[1] - y_center)/sigma_y)**2))**2

    The HWHM is related to the parameter :math:`\Gamma` by the relation:
      :math:`\kappa = \sqrt{\sqrt{2} - 1}\Gamma`
    """
    return amplitude * ( 1 / (1 + ((x[0] - center_x) / sigma_x)**2 +
                                  ((x[1] - center_y) / sigma_y)**2) )**2


def gauss_2D(x, amplitude=1.0, center_x=0.0, center_y=0.0, sigma_x=1.0, sigma_y=1.0):
    """2D Gaussian defined by amplitide
    out = amplitude * ( exp( -1.0 * (x[0] - center_x)**2 / (2 * sigma_x**2) +
                             -1.0 * (x[1] - center_y)**2 / (2 * sigma_y**2) ) )
    """
    out = amplitude * ( np.exp( -1.0 * (x[0] - center_x)**2 / (2 * sigma_x**2) +
                                -1.0 * (x[1] - center_y)**2 / (2 * sigma_y**2) ) )


COMMON_DOC = """

Parameters
----------
independent_vars: list of strings to be set as variable names
missing: None, 'drop', or 'raise'
    None: Do not check for null or missing values.
    'drop': Drop null or missing observations in data.
        Use pandas.isnull if pandas is available; otherwise,
        silently fall back to numpy.isnan.
    'raise': Raise a (more helpful) exception when data contains null
        or missing values.
prefix: string to prepend to paramter names, needed to add two Models that
    have parameter names in common. None by default.
"""

class LorentzianSquaredModel(Model):
    __doc__ = lorentzian_squared.__doc__ + COMMON_DOC if lorentzian_squared.__doc__ else ""
    fwhm_factor = 2.0*np.sqrt(np.sqrt(2)-1)
    def __init__(self, *args, **kwargs):
        super(LorentzianSquaredModel, self).__init__(lorentzian_squared, *args, **kwargs)
        self.set_param_hint('sigma', min=0)
        self.set_param_hint('fwhm', expr=fwhm_expr(self))

    def guess(self, data, x=None, negative=False, **kwargs):
        pars = guess_from_peak(self, data, x, negative, ampscale=0.5)
        return update_param_vals(pars, self.prefix, **kwargs)


class PlaneModel(Model):
    __doc__ = plane.__doc__ + COMMON_DOC if plane.__doc__ else ""
    def __init__(self, *args, **kwargs):
        super(PlaneModel, self).__init__(plane, *args, **kwargs)

    def guess(self, data, x=None, **kwargs):
        sxval, syval, oval = 0., 0., 0.
        if x is not None:
            not_nan_inds = ~np.isnan(data)
            sxval, oval = np.polyfit(x[0][not_nan_inds], data[not_nan_inds], 1)
            syval, oval = np.polyfit(x[1][not_nan_inds], data[not_nan_inds], 1)
        pars = self.make_params(intercept=oval, slope_x=sxval, slope_y=syval)
        return update_param_vals(pars, self.prefix, **kwargs)


class LorentzianSquared2DModel(Model):
    __doc__ = lor2_2D.__doc__ + COMMON_DOC if lor2_2D.__doc__ else ""
    fwhm_factor = 2.0*np.sqrt(np.sqrt(2)-1)
    def __init__(self, *args, **kwargs):
        super(LorentzianSquared2DModel, self).__init__(lor2_2D, *args, **kwargs)
        self.set_param_hint('sigma_x', min=0)
        self.set_param_hint('sigma_y', min=0)

        self.set_param_hint('fwhm_x', expr=fwhm_expr_2D(self, parameter='sigma_x'))
        self.set_param_hint('fwhm_y', expr=fwhm_expr_2D(self, parameter='sigma_y'))
        #self.set_param_hint('fwhm_x', expr='self.fwhm_factor*sigma_x')
        #self.set_param_hint('fwhm_y', expr='self.fwhm_factor*sigma_y')

    def guess(self, data, x=None, negative=False, **kwargs):
        pars = guess_from_peak_2D(self, data, x, negative, ampscale=1.25, amp_area=False)
        return update_param_vals(pars, self.prefix, **kwargs)


class Gaussian2DModel(Model):
    __doc__ = gauss_2D.__doc__ + COMMON_DOC if gauss_2D.__doc__ else ""
    fwhm_factor = 2.354820
    def __init__(self, *args, **kwargs):
        super(Gaussian2DModel, self).__init__(gauss_2D, *args, **kwargs)
        self.set_param_hint('sigma_x', min=0)
        self.set_param_hint('sigma_y', min=0)
        self.set_param_hint('fwhm_x', expr=fwhm_expr_2D(self, parameter='sigma_x'))
        self.set_param_hint('fwhm_y', expr=fwhm_expr_2D(self, parameter='sigma_y'))

    def guess(self, data, x=None, negative=False, **kwargs):
        pars = guess_from_peak_2D(self, data, x, negative, ampscale=1., amp_area=False)
        return update_param_vals(pars, self.prefix, **kwargs)
