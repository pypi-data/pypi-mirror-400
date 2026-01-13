'''Utility for constructing a hypercube in n-dimensions'''

__author__ = "Vera Del Favero"

def hypercube(limits, res):
    '''Generate a hypercube within some limits as a grid of points

    Parameters
    ----------
    limits: array like, shape = (ndim, 2)
        List of [min,max] pairs for each dimension
    res: array like (or int)
        Resolution in each (all) dimensions

    Returns
    -------
    sample: `~numpy.ndarray`, shape = (npts, ndim)
        Output hypercube samples

    '''

    #### Imports ####
    import numpy as np

    #### Check inputs ####
    ## Check limits ##
    limits = np.asarray(limits)
    assert len(limits.shape) == 2
    assert limits.shape[1] == 2

    ## Exctract ndim ##
    ndim = limits.shape[0]

    # Check resolution
    res = np.asarray(res, dtype=int)
    if res.size == 1:
        res = np.ones((ndim,)).astype(int) * res
    else:
        assert len(res.shape) == 1
        assert res.size == ndim

    #### Generate slices ####
    slices = []
    for i in range(ndim):
        slices.append(slice(limits[i,0], limits[i,1], res[i] * 1j))

    #### Generate grid ####
    grid = np.mgrid[slices]

    #### Reshape the sample space ####
    sample = grid.reshape(ndim, np.prod(res))
    sample = sample.T

    return sample
