''' random sphere generation utilities

These will work given a random number generator of either kind
    (np.random.RandomState or np.random.Generator);
    both have a uniform distribution with the same keyword arguments
'''

######## Imports ########
import numpy as np

######## Declarations ########

__all__ = [
           "random_unit_sphere",
           "random_spherical",
          ]

######## Functions ########

def random_unit_sphere(rs, npts):
    '''Generate randomly distributed points on a unit sphere

    Inspired by https://mathworld.wolfram.com/SpherePointPicking.html

    Parameters
    ----------
    rs: `~numpy.random.Generator` object
        random number generator
    npts: int
        number of points to generate
    Returns
    -------
    sample: `~numpy.ndarray`, shape = (npts, 3)
        randomly distributed points in three dimensions
    '''
    # Pick z = cos(phi) from random uniform
    z = rs.uniform(low=-1.,high=1.,size=npts)
    # Pick theta from random uniform
    theta = rs.uniform(low=0.,high=2*np.pi,size=npts)
    # Estimate sinphi so we don't have to do it twice
    sinphi = np.sqrt(1 - z**2)
    # Get x
    x = sinphi * np.cos(theta)
    # Get y
    y = sinphi * np.sin(theta)
    # Stack samples
    sample = np.stack((x, y, z), axis=-1)
    return sample

def random_spherical(rs, npts):
    '''Generate randomly distributed points inside of a sphere

    Inspired by https://math.stackexchange.com/questions/87230/picking-random-points-in-the-volume-of-sphere-with-uniform-probability

    Parameters
    ----------
    rs: `~numpy.random.Generator` object
        random number generator
    npts: int
        number of points to generate
    Returns
    -------
    sample: `~numpy.ndarray`, shape = (npts, 3)
        randomly distributed points in three dimensions
    '''
    # Generate a random unit sphere
    sample = random_unit_sphere(rs, npts)
    # Get random r from r = cube_root(uniform)
    r = np.cbrt(rs.uniform(low=0,high=1.,size=npts))
    # Multiply r through our sample
    sample = r[:,None] * sample
    return sample

