#
# fitfuncs.py (c) Stuart B. Wilkins 2008
#
# $Id: fitfuncs.py 235 2012-08-08 17:07:54Z tombeale $
# $HeadURL: https://pyspec.svn.sourceforge.net/svnroot/pyspec/trunk/pyspec/fitfuncs.py $
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

import numpy
import time as _time

try:
    import wx as _wx
except ImportError:
    pass
try:
    import pylab as _pylab
except ImportError:
    pass

__version__   = "$Revision: 235 $"
__author__    = "Stuart B. Wilkins <stuwilkins@mac.com>"
__date__      = "$LastChangedDate: 2012-08-08 13:07:54 -0400 (Wed, 08 Aug 2012) $"
__id__        = "$Id: fitfuncs.py 235 2012-08-08 17:07:54Z tombeale $"

def peakguess(x,y):
    """Guess the "vital statistics" of a peak.

    This function guesses the peak's center
    width, integral, height and linear background
    (m, c) from the x and y data passed to it.
    """

    # Calculate linear background

    m = (y[-1] - y[0]) / (x[-1] - x[0])
    c = y[0] - x[0] * m

    # Now subtract this background

    ty = y - (m * x) - c

    # Calculate integral of background
    # subtracted data

    integral = abs(x[1] - x[0]) / 2
    dsum = ty[1:-1].sum()

    integral = integral * (ty[0] + ty[-1] + (2 * dsum))

    xmax = 0
    ymax = 0
    for i in range(len(x)):
        # find max
        if ty[i] > ymax:
            ymax = ty[i]
            xmax = i

    centre = x[xmax]

    lxmax = 0
    rxmax = len(x)

    i = xmax - 1
    while (i >= 0):
        if ty[i] < (ymax / 2):
            lxmax = i
            break
        i -= 1

    i = xmax + 1
    while (i <= len(x)):
        if ty[i] < (ymax / 2):
            rxmax = i
            break
        i += 1

    width = abs(x[rxmax] - x[lxmax])

    height = ty.max()

    out = [centre, width, integral, height, m, c]

    return out

def lor2a(x, p, mode='eval'):
    """Lorentzian squared function defined by area"""
    if mode == 'eval':
        out = ((numpy.sqrt(2)*p[2])/(numpy.pi*p[1]) / (1 + 0.5*((x - p[0])/p[1])**2)**2);
    elif mode == 'params':
        out = ['cent', 'width', 'area']
    elif mode == 'name':
        out = "Lorentzian Squared"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = g[0:3]
    else:
        out = []

    return out

def lor2(x, p, mode='eval'):
    """Lorentzian squared defined by amplitude

    Function:
      :math:`f(x) = p_2\left(\\frac{1}{1 + \left(\\frac{x - p_0}{p_1}\\right)^2}\\right)^2`

    The HWHM is related to the parameter :math:`\Gamma` by the relation:
      :math:`\kappa = \sqrt{\sqrt{2} - 1}\Gamma`

    """
    if mode == 'eval':
        out = p[2] * (1 / (1 + ((x - p[0]) / p[1])**2))**2
    elif mode == 'params':
        out = ['Cent', 'Gamma', 'Height']
    elif mode == 'name':
        out = "Lorentzian Squared"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = g[0:3]
    elif mode == 'graphguess':
        x = GetGraphInput()
        print "Click on (in order)"
        print "\tPeak center"
        print "\tPeak width (left)"
        print "\tPeak width (right)"
        print "\tBackground at center"
        c = x(4, 0)
        width = abs(c[1][0] - c[2][0])
        area = abs(c[0][1] - c[3][1])
        out = [c[0][0], width, area]
    else:
        out = []

    return out

def two_lor2_eqW(x, p, mode='eval'):
    """Two Lorentzian squared defined by amplitude

    Function:
      :math:`f(x) = p_2\left(\\frac{1}{1 + \left(\\frac{x - p_0}{p_1}\\right)^2}\\right)^2`

    The HWHM is related to the parameter :math:`\Gamma` by the relation:
      :math:`\kappa = \sqrt{\sqrt{2} - 1}\Gamma`

    """
    if mode == 'eval':
        out = (p[1] * (1 / (1 + ((x - p[0]) / p[4])**2))**2 +
               p[3] * (1 / (1 + ((x - p[2]) / p[4])**2))**2)
    elif mode == 'params':
        out = ['Cent1', 'Height1', 'Cent2', 'Height2', 'Gamma']
    elif mode == 'name':
        out = " Two Lorentzian Squared Functions with Equal Width"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = g[0:5]
    elif mode == 'graphguess':
        x = GetGraphInput()
        print "Click on (in order)"
        print "\tPeak center"
        print "\tPeak width (left)"
        print "\tPeak width (right)"
        print "\tBackground at center"
        c = x(4, 0)
        width = abs(c[1][0] - c[2][0])
        area = abs(c[0][1] - c[3][1])
        out = [c[0][0], width, area]
    else:
        out = []

    return out

def three_lor2_eqW(x, p, mode='eval'):
    """Three Lorentzian squared defined by amplitude

    Function:
      :math:`f(x) = p_2\left(\\frac{1}{1 + \left(\\frac{x - p_0}{p_1}\\right)^2}\\right)^2`

    The HWHM is related to the parameter :math:`\Gamma` by the relation:
      :math:`\kappa = \sqrt{\sqrt{2} - 1}\Gamma`

    """
    if mode == 'eval':
        out = (p[1] * (1 / (1 + ((x - p[0]) / p[6])**2))**2 +
               p[3] * (1 / (1 + ((x - p[2]) / p[6])**2))**2 +
               p[5] * (1 / (1 + ((x - p[4]) / p[6])**2))**2)
    elif mode == 'params':
        out = ['Cent1', 'Height1', 'Cent2', 'Height2', 'Cent3', 'Height3', 'Gamma']
    elif mode == 'name':
        out = " Three Lorentzian Squared Functions with Equal Width"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = g[0:7]
    elif mode == 'graphguess':
        x = GetGraphInput()
        print "Click on (in order)"
        print "\tPeak center"
        print "\tPeak width (left)"
        print "\tPeak width (right)"
        print "\tBackground at center"
        c = x(4, 0)
        width = abs(c[1][0] - c[2][0])
        area = abs(c[0][1] - c[3][1])
        out = [c[0][0], width, area]
    else:
        out = []

    return out

def lor2_2d(x, p, mode='eval'):
    """2D Lorentzian squared defined by amplitude

    Function:
      :math:`f(x) = p_0\left(\\frac{1}{1 + \left(\\frac{x - p_1}{p_3}\\right)^2 + \left(\\frac{y - p_2}{p_4}\\right)^2}\\right)^2`

    The HWHM is related to the parameter :math:`\Gamma` by the relation:
      :math:`\kappa = \sqrt{\sqrt{2} - 1}\Gamma`

    """
    if mode == 'eval':
        amp = p[0]; cent_x = p[1]; cent_y = p[2]; gam_x = p[3]; gam_y = p[4]
        out = amp * ( 1 / (1 + ((x[0] - cent_x) / gam_x)**2 + ((x[1] - cent_y) / gam_y)**2) )**2
    elif mode == 'params':
        out = ['amp', 'X cent', 'Y cent', 'X Gamma', 'Y Gamma']
    elif mode == 'name':
        out = "Lorentzian Squared"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = g[0:3]
    elif mode == 'graphguess':
        x = GetGraphInput()
        print "Click on (in order)"
        print "\tPeak center"
        print "\tPeak width (left)"
        print "\tPeak width (right)"
        print "\tBackground at center"
        c = x(4, 0)
        width = abs(c[1][0] - c[2][0])
        area = abs(c[0][1] - c[3][1])
        out = [c[0][0], width, area]
    else:
        out = []

    return out

def lor2_2d_eqW(x, p, mode='eval'):
    """2D Lorentzian squared defined by amplitude with equal widths

    Function:
      :math:`f(x) = p_0\left(\\frac{1}{1 + \left(\\frac{x - p_1}{p_3}\\right)^2 + \left(\\frac{y - p_2}{p_3}\\right)^2}\\right)^2`

    The HWHM is related to the parameter :math:`\Gamma` by the relation:
      :math:`\kappa = \sqrt{\sqrt{2} - 1}\Gamma`

    """
    if mode == 'eval':
        amp = p[0]; cent_x = p[1]; cent_y = p[2]; gam = p[3]
        out = amp * ( 1 / (1 + ((x[0] - cent_x) / gam)**2 + ((x[1] - cent_y) / gam)**2) )**2
    elif mode == 'params':
        out = ['amp', 'X cent', 'Y cent', 'Gamma']
    elif mode == 'name':
        out = "Lorentzian Squared with Equal Width in X and Y"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = g[0:3]
    elif mode == 'graphguess':
        x = GetGraphInput()
        print "Click on (in order)"
        print "\tPeak center"
        print "\tPeak width (left)"
        print "\tPeak width (right)"
        print "\tBackground at center"
        c = x(4, 0)
        width = abs(c[1][0] - c[2][0])
        area = abs(c[0][1] - c[3][1])
        out = [c[0][0], width, area]
    else:
        out = []

    return out

def two_lor2_2d_eqW(x, p, mode='eval'):
    """Two 2D Lorentzian squared defined by amplitude with equal widths

    Function:
      :math:`f(x) = p_0\left(\\frac{1}{1 + \left(\\frac{x - p_1}{p_3}\\right)^2 + \left(\\frac{y - p_2}{p_3}\\right)^2}\\right)^2`

    The HWHM is related to the parameter :math:`\Gamma` by the relation:
      :math:`\kappa = \sqrt{\sqrt{2} - 1}\Gamma`

    """
    if mode == 'eval':
        amp1 = p[0]; cent_x1 = p[1]; cent_y1 = p[2]; amp2 = p[3]; cent_x2 = p[4]; cent_y2 = p[5]; gam = p[6]
        out = ( amp1 * ( 1 / (1 + ((x[0] - cent_x1) / gam)**2 + ((x[1] - cent_y1) / gam)**2) )**2 +
                amp2 * ( 1 / (1 + ((x[0] - cent_x2) / gam)**2 + ((x[1] - cent_y2) / gam)**2) )**2 )
    elif mode == 'params':
        out = ['amp1', 'X cent1', 'Y cent1', 'amp2', 'X cent2', 'Y cent2', 'Gamma']
    elif mode == 'name':
        out = "Lorentzian Squared with Equal Width in X and Y"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = g[0:7]
    elif mode == 'graphguess':
        x = GetGraphInput()
        print "Click on (in order)"
        print "\tPeak center"
        print "\tPeak width (left)"
        print "\tPeak width (right)"
        print "\tBackground at center"
        c = x(4, 0)
        width = abs(c[1][0] - c[2][0])
        area = abs(c[0][1] - c[3][1])
        out = [c[0][0], width, area]
    else:
        out = []

    return out

def two_lor2_2d_eqW_eqX(x, p, mode='eval'):
    """Two 2D Lorentzian squared defined by amplitude with equal widths

    Function:
      :math:`f(x) = p_0\left(\\frac{1}{1 + \left(\\frac{x - p_1}{p_3}\\right)^2 + \left(\\frac{y - p_2}{p_3}\\right)^2}\\right)^2`

    The HWHM is related to the parameter :math:`\Gamma` by the relation:
      :math:`\kappa = \sqrt{\sqrt{2} - 1}\Gamma`

    """
    if mode == 'eval':
        amp1 = p[0]; cent_y1 = p[1]; amp2 = p[2]; cent_y2 = p[3]; cent_x = p[4]; gam = p[5]
        out = ( amp1 * ( 1 / (1 + ((x[0] - cent_x) / gam)**2 + ((x[1] - cent_y1) / gam)**2) )**2 +
                amp2 * ( 1 / (1 + ((x[0] - cent_x) / gam)**2 + ((x[1] - cent_y2) / gam)**2) )**2 )
    elif mode == 'params':
        out = ['amp1', 'Y cent1', 'amp2', 'Y cent2', 'X cent', 'Gamma']
    elif mode == 'name':
        out = "2 2D Lorentzian Squared with Equal Widths in X and Y and same center in X"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = g[0:7]
    elif mode == 'graphguess':
        x = GetGraphInput()
        print "Click on (in order)"
        print "\tPeak center"
        print "\tPeak width (left)"
        print "\tPeak width (right)"
        print "\tBackground at center"
        c = x(4, 0)
        width = abs(c[1][0] - c[2][0])
        area = abs(c[0][1] - c[3][1])
        out = [c[0][0], width, area]
    else:
        out = []

    return out

def two_lor2_2d_eqX_eqY(x, p, mode='eval'):
    """Two 2D Lorentzian squared defined by amplitude with equal widths

    Function:
      :math:`f(x) = p_0\left(\\frac{1}{1 + \left(\\frac{x - p_1}{p_3}\\right)^2 + \left(\\frac{y - p_2}{p_3}\\right)^2}\\right)^2`

    The HWHM is related to the parameter :math:`\Gamma` by the relation:
      :math:`\kappa = \sqrt{\sqrt{2} - 1}\Gamma`

    """
    if mode == 'eval':
        amp1 = p[0]; amp2 = p[1]; cent_x = p[2]; cent_y = p[3]; gam_x = p[4]; gam_y = p[5]
        out = ( amp1 * ( 1 / (1 + ((x[0] - cent_x) / gam_x)**2 + ((x[1] - cent_y) / gam_y)**2) )**2 +
                amp2 * ( 1 / (1 + ((x[0] - cent_x) / gam_x)**2 + ((x[1] + cent_y) / gam_y)**2) )**2 )
    elif mode == 'params':
        out = ['amp1', 'amp2', 'X cent', 'Y cent', 'X Gamma', 'Y Gamma']
    elif mode == 'name':
        out = "2 2D Lorentzian Squared with equal X and mirror Y"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = g[0:6]
    elif mode == 'graphguess':
        x = GetGraphInput()
        print "Click on (in order)"
        print "\tPeak center"
        print "\tPeak width (left)"
        print "\tPeak width (right)"
        print "\tBackground at center"
        c = x(4, 0)
        width = abs(c[1][0] - c[2][0])
        area = abs(c[0][1] - c[3][1])
        out = [c[0][0], width, area]
    else:
        out = []

    return out

def two_lor2_2d_eqA_eqX_eqY(x, p, mode='eval'):
    """Two 2D Lorentzian squared defined by amplitude with equal widths and equal amplitudes

    Function:
      :math:`f(x) = p_0\left(\\frac{1}{1 + \left(\\frac{x - p_1}{p_3}\\right)^2 + \left(\\frac{y - p_2}{p_3}\\right)^2}\\right)^2`

    The HWHM is related to the parameter :math:`\Gamma` by the relation:
      :math:`\kappa = \sqrt{\sqrt{2} - 1}\Gamma`

    """
    if mode == 'eval':
        amp = p[0]; cent_x = p[1]; cent_y = p[2]; gam_x = p[3]; gam_y = p[4]
        out = ( amp * ( 1 / (1 + ((x[0] - cent_x) / gam_x)**2 + ((x[1] - cent_y) / gam_y)**2) )**2 +
                amp * ( 1 / (1 + ((x[0] - cent_x) / gam_x)**2 + ((x[1] + cent_y) / gam_y)**2) )**2 )
    elif mode == 'params':
        out = ['amp', 'X cent', 'Y cent', 'X Gamma', 'Y Gamma']
    elif mode == 'name':
        out = "2 2D Lorentzian Squared with equal X and mirror Y and equal Amp"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = g[0:7]
    elif mode == 'graphguess':
        x = GetGraphInput()
        print "Click on (in order)"
        print "\tPeak center"
        print "\tPeak width (left)"
        print "\tPeak width (right)"
        print "\tBackground at center"
        c = x(4, 0)
        width = abs(c[1][0] - c[2][0])
        area = abs(c[0][1] - c[3][1])
        out = [c[0][0], width, area]
    else:
        out = []

    return out

def two_lor2_2d_eqW_eqX_eqY(x, p, mode='eval'):
    """Two 2D Lorentzian squared defined by amplitude with equal widths

    Function:
      :math:`f(x) = p_0\left(\\frac{1}{1 + \left(\\frac{x - p_1}{p_3}\\right)^2 + \left(\\frac{y - p_2}{p_3}\\right)^2}\\right)^2`

    The HWHM is related to the parameter :math:`\Gamma` by the relation:
      :math:`\kappa = \sqrt{\sqrt{2} - 1}\Gamma`

    """
    if mode == 'eval':
        amp1 = p[0]; amp2 = p[1]; cent_x = p[2]; cent_y = p[3]; gam = p[4]
        out = ( amp1 * ( 1 / (1 + ((x[0] - cent_x) / gam)**2 + ((x[1] - cent_y) / gam)**2) )**2 +
                amp2 * ( 1 / (1 + ((x[0] - cent_x) / gam)**2 + ((x[1] + cent_y) / gam)**2) )**2 )
    elif mode == 'params':
        out = ['amp1', 'amp2', 'X cent', 'Y cent', 'Gamma']
    elif mode == 'name':
        out = "2 2D Lorentzian Squared with Equal Widths in X and Y"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = g[0:7]
    elif mode == 'graphguess':
        x = GetGraphInput()
        print "Click on (in order)"
        print "\tPeak center"
        print "\tPeak width (left)"
        print "\tPeak width (right)"
        print "\tBackground at center"
        c = x(4, 0)
        width = abs(c[1][0] - c[2][0])
        area = abs(c[0][1] - c[3][1])
        out = [c[0][0], width, area]
    else:
        out = []

    return out

def three_lor2_2d_eqW_eqX(x, p, mode='eval'):
    """Two 2D Lorentzian squared defined by amplitude with equal widths

    Function:
      :math:`f(x) = p_0\left(\\frac{1}{1 + \left(\\frac{x - p_1}{p_3}\\right)^2 + \left(\\frac{y - p_2}{p_3}\\right)^2}\\right)^2`

    The HWHM is related to the parameter :math:`\Gamma` by the relation:
      :math:`\kappa = \sqrt{\sqrt{2} - 1}\Gamma`

    """
    if mode == 'eval':
        amp1 = p[0]; cent_x = p[1]; cent_y = p[2]; gam = p[3]; amp3 = p[4]; cent_y3 = p[5]
        out = ( amp1 * ( 1 / (1 + ((x[0] - cent_x) / gam)**2 + ((x[1] - cent_y)  / gam)**2) )**2 +
                amp1 * ( 1 / (1 + ((x[0] - cent_x) / gam)**2 + ((x[1] + cent_y)  / gam)**2) )**2 +
                amp3 * ( 1 / (1 + ((x[0] - cent_x) / gam)**2 + ((x[1] - cent_y3) / gam)**2) )**2 )
    elif mode == 'params':
        out = ['amp', 'X cent', 'Y cent', 'Gamma', 'amp3', 'Y Cent3']
    elif mode == 'name':
        out = "2 2D Lorentzian Squared with Equal Widths in X and Y"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = g[0:7]
    elif mode == 'graphguess':
        x = GetGraphInput()
        print "Click on (in order)"
        print "\tPeak center"
        print "\tPeak width (left)"
        print "\tPeak width (right)"
        print "\tBackground at center"
        c = x(4, 0)
        width = abs(c[1][0] - c[2][0])
        area = abs(c[0][1] - c[3][1])
        out = [c[0][0], width, area]
    else:
        out = []

    return out

def linear(x, p, mode='eval'):
    """Linear (strait line)

    Function:
       :math:`f(x) = p_0 x + p_1`

    """
    if mode == 'eval':
        out = (p[0] * x) + p[1]
    elif mode == 'params':
        out = ['grad','offset']
    elif mode == 'name':
        out = "Linear"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = g[4:6]
    else:
        out = []

    return out

def sinSq(x, p, mode='eval'):
    """Sin squared

    Function:
       :math:`f(x) = p_0 * (sin x)**2`

    """
    if mode == 'eval':
        out = p[0] * (numpy.sin((x)*numpy.pi/180))**2
    elif mode == 'params':
        out = ['Amp']
    elif mode == 'name':
        out = "Sin Squared"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = g[0:1]
    else:
        out = []

    return out

def constant(x, p, mode='eval'):
    """Single constant value

    Function:
       :math:`f(x) = p_0`

    """
    if mode == 'eval':
        out = p[0]
    elif mode == 'params':
        out = ['value']
    elif mode == 'name':
        out = "Constant"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = [(g[4] * (x[0] + x[-1]) + 2*g[5]) / 2]
    else:
        out = []

    return out

def lor(x, p, mode='eval'):
    """Lorentzian defined by amplitude

    Function:
       :math:`f(x) = p_2\left(\\frac{1}{1 + \\left(\\frac{x - p_0}{p_1}\\right)^2}\\right)`

    """
    if mode == 'eval':
        out = p[2] / (1 + ((x - p[0]) / p[1])**2)
    elif mode == 'params':
        out = ['Center', 'Gamma', 'Height']
    elif mode == 'name':
        out = "Lorentzian"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = g[0:3]
    else:
        out = []

    return out

def lorr(x, p, mode='eval'):
    """Lorentzian defined by area

    Function:
       :math:`f(x) = \\frac{p_2}{p_1\pi} \left(\\frac{1}{1 + 4\left(\\frac{x - p_0}{p_1}\\right)^2}\\right)`

    """
    if mode == 'eval':
        out = (2*p[2]/p[1]/numpy.pi) / (1 + 4*((x-p[0])/p[1])**2)
    elif mode == 'params':
        out = ['Center', 'width', 'area']
    elif mode == 'name':
        out = "Lorentzian"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = g[0:3]
    else:
        out = []

    return out

def pvoight(x, p, mode='eval'):
    """Pseudo Voight function

    Function:
       :math:'f(x) = '

    """
    if mode == 'eval':
        cent=p[0];wid=p[1];area=p[2];lfrac=p[3];
        out = area / wid / ( lfrac*numpy.pi/2 + (1-lfrac)*numpy.sqrt(numpy.pi/4/numpy.log(2)) ) * ( lfrac / (1 + 4*((x-cent)/wid)**2) + (1-lfrac)*numpy.exp(-4*numpy.log(2)*((x-cent)/wid)**2) );
    elif mode == 'params':
        out = ['cent', 'FWHM', 'area', 'Lorr. Fac.']
    elif mode == 'name':
        out = "Pseudo Voight"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = g[0:4]
        out[3] = 1.0
    else:
        out = []

    return out

def gauss(x, p, mode='eval'):
    """Gaussian defined by amplitide

    Function:
       :math:`f(x) = p_2 \exp\left(\\frac{-(x - p_0)^2}{2p_1^2}\\right)`

    """
    if mode == 'eval':
        cent=p[0];wid=p[1];amp=p[2];
        out = amp * numpy.exp(-1.0 * (x - cent)**2 / (2 * wid**2))
    elif mode == 'params':
        out = ['cent', 'sigma', 'amp']
    elif mode == 'name':
        out = "Gaussian"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = [g[0], g[1] / (4 * numpy.log(2)), g[3]]
    else:
        out = []

    return out

def gauss2d(x, p, mode='eval'):
    """2D Gaussian defined by amplitide

    Function:
       :math:`f(x) = p_0 \exp\left(\\frac{-(x - p_1)^2}{2p_3^2} + \\frac{-(y - p_2)^2}{2p_4^2}\\right)`

    """
    if mode == 'eval':
        amp = p[0]; cent_x = p[1]; cent_y = p[2]; wid_x = p[3]; wid_y = p[4]
        out = amp * ( numpy.exp( -1.0 * (x[0] - cent_x)**2 / (2 * wid_x**2) +
                                 -1.0 * (x[1] - cent_y)**2 / (2 * wid_y**2) ) )
    elif mode == 'params':
        out = ['amp', 'X cent', 'Y cent', 'X sigma', 'Y sigma']
    elif mode == 'name':
        out = "2D Gaussian"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = [g[0], g[1] / (4 * numpy.log(2)), g[3]]
    else:
        out = []

    return out


def gauss2d_eqW(x, p, mode='eval'):
    """2D Gaussian defined by amplitide with equal width in X and Y

    Function:
       :math:`f(x) = p_0 \exp\left(\\frac{-(x - p_1)^2}{2p_3^2} + \\frac{-(y - p_2)^2}{2p_3^2}\\right)`

    """
    if mode == 'eval':
        amp = p[0]; cent_x = p[1]; cent_y = p[2]; wid = p[3]
        out = amp * ( numpy.exp( -1.0 * (x[0] - cent_x)**2 / (2 * wid**2) -1.0 * (x[1] - cent_y)**2 / (2 * wid**2) ) )
    elif mode == 'params':
        out = ['amp', 'X cent', 'Y cent', 'sigma']
    elif mode == 'name':
        out = "2D Gaussian with Equal Widths"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = [g[0], g[1] / (4 * numpy.log(2)), g[3]]
    else:
        out = []

    return out


def two_gauss2d_eqA_eqW_eqX(x, p, mode='eval'):
    """2D Gaussian defined by amplitide with equal width in X and Y

    Function:
       :math:`f(x) = p_0 \exp\left(\\frac{-(x - p_1)^2}{2p_3^2} + \\frac{-(y - p_2)^2}{2p_3^2}\\right)`

    """
    if mode == 'eval':
        amp = p[0]; cent_x = p[1]; cent_y = p[2]; wid = p[3]
        out = amp * ( ( numpy.exp( - (x[0] - cent_x)**2 / (2 * wid**2) - (x[1] - cent_y)**2 / (2 * wid**2) ) ) +
                      ( numpy.exp( - (x[0] - cent_x)**2 / (2 * wid**2) - (x[1] + cent_y)**2 / (2 * wid**2) ) ) )
    elif mode == 'params':
        out = ['amp', 'X cent', 'Y cent', 'sigma']
    elif mode == 'name':
        out = "2D Gaussian with Equal Widths"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = [g[0], g[1] / (4 * numpy.log(2)), g[3]]
    else:
        out = []

    return out

def poly2D(x, p, mode='eval'):
    """2 Degree polynomial
    """
    if mode == 'eval':
        out = p[0] + p[1]*x + p[2]*x**2
    elif mode == 'params':
        out = ['a0', 'a1', 'a2']
    elif mode == 'name':
        out = "2nd Degree Polynomial"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = [g[0], g[1], g[2]]
    else:
        out = []

    return out

def poly3D(x, p, mode='eval'):
    """3 Degree polynomial
    """
    if mode == 'eval':
        out = p[0] + p[1]*x + p[2]*x**2 + p[3]*x**3
    elif mode == 'params':
        out = ['a0', 'a1', 'a2', 'a3']
    elif mode == 'name':
        out = "3rd Degree Polynomial"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = [g[0], g[1], g[2], g[3]]
    else:
        out = []

    return out

def plane(x, p, mode='eval'):
    """2D plane

    Function:
       :math:`f(x) = p_0 + p_1x + p_2y`

    """
    if mode == 'eval':
        offset = p[0]; grad_x = p[1]; grad_y = p[2]
        out = p[0] + p[1] * x[0] + p[2] * x[1]
    elif mode == 'params':
        out = ['offset', 'X grad', 'Y grad']
    elif mode == 'name':
        out = "Plane w Sloping Background"
    elif mode == 'guess':
        g = peakguess(x, p)
        out = [g[0], g[1], g[3]]
    else:
        out = []

    return out

def power(x, p, mode = 'eval'):
    """Power function

    Function:
       :math:`f(x) = p_0 p_1^x`

    """
    if mode == 'eval':
        out = p[0] * pow(p[1], x)
    elif mode == 'params':
        out = ['A', 'B']
    elif mode == 'name':
        out = "Power"
    elif mode == 'guess':
        out = [1, 1]
    else:
        out = []

    return out

def stokes(x, p, mode='eval'):
	if mode == 'eval':
		out = p[0] * 0.5 * (1 + (p[1]*numpy.cos(x*numpy.pi/90)) + (p[2]*numpy.sin(x*numpy.pi/90)))
	elif mode == 'params':
		out = ['int', 'P1', 'P2']
	elif mode == 'name':
		out = "Stokes"
	elif mode == 'guess':
		g = peakguess(x, p)
		out = g[0:3]
	else:
		out = []

	return out


def stokes_rot(x, p, mode='eval'):
	# ASSUMES COMPLETELY LINEAR LIGHT! (P1^2+P2^2 = 1)
	if mode == 'eval':
		out = p[1]*(1+numpy.cos((x-p[0])*numpy.pi/90))
	elif mode == 'params':
		out = ['Rotation','S0']
	elif mode == 'name':
		out = "Stokes (assuming entirely linear)"
	elif mode == 'guess':
		out = [1,2]
	else:
		out = []
	return out

def sin_beam(x, p, mode='eval'):
	# ASSUMES COMPLETELY LINEAR LIGHT! (P1^2+P2^2 = 1)
	if mode == 'eval':
		out = p[1]*(numpy.cos((x-p[0])*numpy.pi/90))
	elif mode == 'params':
		out = ['Rotation','S0']
	elif mode == 'name':
		out = "Stokes (assuming entirely linear)"
	elif mode == 'guess':
		out = [1,2]
	else:
		out = []
	return out
