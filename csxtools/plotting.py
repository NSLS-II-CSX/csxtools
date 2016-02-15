import numpy as np
from matplotlib import pyplot as plt

golden_mean = (np.sqrt(5)-1.0)/2.0


def make_panel_plot(n, fig=None,
                    xlmargin=0.15, ytmargin=0.10,
                    xrmargin=0.05, ybmargin=0.10):
    """Make a multi panel plot using matplotlib

    This function, makes a typical panel plot and returns a list
    of the axes objects for plotting later.

    Parameters
    ----------
    n : int
       Number of panels
    fig : figure object, optional
       Figure object to use (If None creates new figure)
    xmargin : float, optional
       Margin at x-axis
    ymargin : float, optional
       Margin at y-axis

    Returns
    -------
    tuple
        tuple of matplotlib axes objects for the panel plot

    """

    if fig is None:
        fig = plt.figure(figsize=[6, 6 * golden_mean * n])

    xsize = (1. - (xlmargin + xrmargin))
    ysize = (1. - (ybmargin + ytmargin)) / n

    pos = np.array([xlmargin, ybmargin, xsize, ysize])

    allax = []
    for x in range(n):
        ax = fig.add_axes(pos + np.array([0, ysize * x, 0, 0]))
        if x > 0:
            # Remove ticklabels
            ax.xaxis.set_ticklabels("")
        allax.append(ax)

    return allax
