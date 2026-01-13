'''Python evaluation of c extensions for GW orbit calculations

'''

######## Imports ########
#### Standard Library ####
#### Third Party ####
import numpy as np
from astropy import units as u
#### Homemade ####
#### Local ####
## Extensions ##
from ._DWD_RLOF import _DWD_RLOF_a_of_m1_m2_r1_r2
from ._DWD_RLOF import _DWD_RLOF_P_of_m1_m2_r1_r2
from ._DWD_RLOF import _DWD_r_of_m
## Orbit ##

######## Declarations ########

__all__ = [
           "DWD_r_of_m",
           "DWD_RLOF_a_of_m1_m2_r1_r2",
           "DWD_RLOF_P_of_m1_m2_r1_r2",
          ]

######## Functions ########

def DWD_r_of_m(m):
    ''' Calculate the radius of a white dwarf (in solar radii)
    Taken from Eq. 91 in Hurley et al. (2000) from Eq. 17 in Tout et al. (1997)

    Would love to output in meters, but it's not my equation.

    Paramters
    ---------
    m: `~numpy.ndarray` (npts,)
        WD masses (Kg)

    Returns
    -------
    r: `~numpy.ndarray` (npts,)
        WD radii (RSUN)
    '''
    #### Check inputs ####
    ## Check m ##
    if not isinstance(m, np.ndarray):
        raise TypeError("m should be a numpy array, but is ", type(m))
    if len(m.shape) != 1:
        raise RuntimeError("m should be 1D array, but is ", m.shape)
    return _DWD_r_of_m(m)

def DWD_RLOF_a_of_m1_m2_r1_r2(m1, m2, r1, r2):
    ''' Calculate the separation of Roche Lobe overflow

    Paramters
    ---------
    m1: `~numpy.ndarray` (npts,)
        First set of masses (Kg)
    m2: `~numpy.ndarray` (npts,)
        Second set of masses (Kg)
    r1 : `~numpy.ndarray` (npts,)
        Radius of primary WD (meters)
    r2 : `~numpy.ndarray` (npts,)
        Radius of secondary WD (meters)

    Returns
    -------
    a : `~numpy.ndarray` (npts,)
        Separation of RLOF (m)
    '''
    #### Check inputs ####
    ## Check m1 ##
    if not isinstance(m1, np.ndarray):
        raise TypeError("m1 should be a numpy array, but is ", type(m1))
    if len(m1.shape) != 1:
        raise RuntimeError("m1 should be 1D array, but is ", m1.shape)
    ## Check m2 ##
    if not isinstance(m2, np.ndarray):
        raise TypeError("m2 should be a numpy array, but is ", type(m2))
    if len(m2.shape) != 1:
        raise RuntimeError("m2 should be 1D array, but is ", m2.shape)
    ## Check r1 ##
    if not isinstance(r1, np.ndarray):
        raise TypeError("r1 should be a numpy array, but is ", type(r1))
    if len(r1.shape) != 1:
        raise RuntimeError("r1 should be 1D array, but is ", r1.shape)
    ## Check r2 ##
    if not isinstance(r2, np.ndarray):
        raise TypeError("r2 should be a numpy array, but is ", type(r2))
    if len(r2.shape) != 1:
        raise RuntimeError("r2 should be 1D array, but is ", r2.shape)
    ## Check dimensions ##
    if not (m1.size == m2.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, m2.size = %d"%(
            m1.size, m2.size))
    if not (m1.size == r1.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, r1.size = %d"%(
            m1.size, r1.size))
    if not (m1.size == r2.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, r2.size = %d"%(
            m1.size, r2.size))
    return _DWD_RLOF_a_of_m1_m2_r1_r2(m1, m2, r1, r2)

def DWD_RLOF_P_of_m1_m2_r1_r2(m1, m2, r1, r2):
    ''' Calculate the orbital period of the separation at which
        Roche Lobe overflow begins

    Paramters
    ---------
    m1: `~numpy.ndarray` (npts,)
        First set of masses (Kg)
    m2: `~numpy.ndarray` (npts,)
        Second set of masses (Kg)
    r1 : `~numpy.ndarray` (npts,)
        Radius of primary WD (meters)
    r2 : `~numpy.ndarray` (npts,)
        Radius of secondary WD (meters)

    Returns
    -------
    P : `~numpy.ndarray` (npts,)
        Orbital period of RLOF (seconds)
    '''
    #### Check inputs ####
    ## Check m1 ##
    if not isinstance(m1, np.ndarray):
        raise TypeError("m1 should be a numpy array, but is ", type(m1))
    if len(m1.shape) != 1:
        raise RuntimeError("m1 should be 1D array, but is ", m1.shape)
    ## Check m2 ##
    if not isinstance(m2, np.ndarray):
        raise TypeError("m2 should be a numpy array, but is ", type(m2))
    if len(m2.shape) != 1:
        raise RuntimeError("m2 should be 1D array, but is ", m2.shape)
    ## Check r1 ##
    if not isinstance(r1, np.ndarray):
        raise TypeError("r1 should be a numpy array, but is ", type(r1))
    if len(r1.shape) != 1:
        raise RuntimeError("r1 should be 1D array, but is ", r1.shape)
    ## Check r2 ##
    if not isinstance(r2, np.ndarray):
        raise TypeError("r2 should be a numpy array, but is ", type(r2))
    if len(r2.shape) != 1:
        raise RuntimeError("r2 should be 1D array, but is ", r2.shape)
    ## Check dimensions ##
    if not (m1.size == m2.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, m2.size = %d"%(
            m1.size, m2.size))
    if not (m1.size == r1.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, r1.size = %d"%(
            m1.size, r1.size))
    if not (m1.size == r2.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, r2.size = %d"%(
            m1.size, r2.size))
    return _DWD_RLOF_P_of_m1_m2_r1_r2(m1, m2, r1, r2)
