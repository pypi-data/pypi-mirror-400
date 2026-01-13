'''Corner plot utilities by Vera Delfavero

I still stubornly refuse to use corner.py because it's not pretty enough
'''
######## General things ########

def percentile_levels(x,y,z, levels, nbins = 1000):
    '''Generate percentile levels
    Inspired by https://stackoverflow.com/questions/37890550/python-plotting-percentile-contour-lines-of-a-probability-distribution

    x,y,z should already be a meshgrid
    '''
    import numpy as np
    from scipy import interpolate

    # Define space for integral
    t = np.linspace(0, z.max(), nbins)

    # Create a mask for the integral
    mask = z <= t[:, None, None]

    # Perform the integral
    integral = (mask * z).sum(axis = (1,2))

    # Interpolate
    f = interpolate.interp1d(integral, t)
    # Return the function evaluated on the levels
    return f(levels)

def bivariate_normal(x, y, xscale, yscale, xloc, yloc):
    import numpy as np
    from scipy.stats import multivariate_normal
    mean = [xloc, yloc]
    cov = [[xscale, 0], [0, yscale]]
    rv = multivariate_normal(mean, cov)
    X = np.stack((x,y)).T
    return rv.pdf(X)

def example():
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt
    x = np.linspace(-3,3,100)
    y = np.linspace(-3,3,100)
    X, Y = np.meshgrid(x, y)

    #z1 = bivariate_normal(X, Y, .5, .5, 0., 0.)
    z2 = bivariate_normal(X, Y, .4, .4, .5, .5)
    z3 = bivariate_normal(X, Y, .6, .2, -1.5, 0.)
    z = z3 + z2
    #z = z1 + z2 + z3
    z = z / z.sum()

    t_contours = percentile_levels(X,Y,z,np.arange(0.,1.,0.1))
    plt.imshow(z.T, origin='lower', extent=[-3,3,-3,3], cmap="gray")
    plt.contour(z.T, t_contours, extent=[-3,3,-3,3])
    plt.show()

def bin_centers(xmin, xmax, bins):
    '''Get the bin centers for a histogram'''
    import numpy as np
    edges = np.linspace(xmin, xmax, bins+1)
    centers = 0.5*(edges[1:] + edges[:-1])
    return centers
