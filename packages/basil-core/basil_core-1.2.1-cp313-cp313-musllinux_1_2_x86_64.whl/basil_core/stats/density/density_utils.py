'''Utilities for density function methods

I have developed some rather baroque methods of constructing
    histogram-based density estimates, and they require utility functions
    provided here.
'''

######## Imports ########
import numpy as np
from scipy.stats import multivariate_normal

######## Sample functions ########

def prune_samples(x_sample, limits):
    '''Prune samples not within limits

    Parameters
    ----------
    x_sample: array like, shape = (nsamples, ndim)
        Array of points [x_i,y_i,z_i,...]
    limits: array like, shape = (ndim, 2)
        Array of [min,max] pairs for each dimension

    Returns
    -------
    mask: np.ndarray, shape = (nsamples,), dtype=bool
        Array of T/F values for a point being inside limits
    '''
    # Grab information
    npts, ndim = x_sample.shape
    # Check limits
    limits = np.asarray(limits)
    assert len(limits.shape) == 2
    assert limits.shape[0] == ndim
    assert limits.shape[1] == 2

    # Initialize boolean array
    mask = np.ones((npts,),dtype=bool)
    # Loop the dimensions
    for i in range(ndim):
        mask &= x_sample[:,i] > limits[i][0]
        mask &= x_sample[:,i] < limits[i][1]
    return mask

def multigauss_samples(ndim, ngauss, nsample, seed=None):
    '''Generate samples from multiple gaussians in a bounded region

    For better ways of doing this, see my other package
    https://gitlab.com/xevra/gwalk

    Parameters
    ----------
    ndim: int
        Number of dimensions
    ngauss: int
        Number of Gaussians
    nsample: int
        Number of samples to draw (total)
    seed: Nonetype, int, or numpy.random.RandomState
        Seed for random numbers

    Returns
    -------
    samples: np.ndarray
        Samples drawn from multiple gaussians
    '''
    ## Check inputs ##
    assert isinstance(ndim, int)
    assert isinstance(ngauss, int)
    assert isinstance(nsample, int)
    assert nsample > ngauss
    
    # Check seed
    if seed is None:
        rs = np.random.RandomState()
    elif isinstance(seed, int):
        rs = np.random.RandomState(seed)
    elif isinstance(seed, np.random.RandomState):
        rs = seed
    else:
        raise RuntimeError("Unknown seed type: %s"%(str(type(seed))))

    ## Generate gaussians ##
    # Get mus
    mu = rs.uniform(low=0,high=1.,size=ngauss*ndim).reshape((ngauss, ndim))
    # Get gaussians
    gaussians = []
    for i in range(ngauss):
        gaussians.append(multivariate_normal(mean=mu[i], cov=0.1, seed=rs))

    ## Get samples ##
    # Identify gaussian choices for each sample
    choices = rs.choice(np.arange(ngauss), size=nsample)
    # initialize samples
    samples = np.empty((nsample, ndim),dtype=float)
    # Initialize sample count
    sample_count = 0
    # Loop the gaussians
    for i in range(ngauss):
        # find the number of samples for this Gaussian
        _nsample = np.sum(choices == i)
        # Get samples
        samples[sample_count:sample_count+_nsample] = gaussians[i].rvs(size=_nsample)
        sample_count += _nsample

    # Return samples
    return samples
    
