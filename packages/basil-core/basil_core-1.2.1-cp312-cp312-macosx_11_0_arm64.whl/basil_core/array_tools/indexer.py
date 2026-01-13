'''Python evaluation of C extension for indexer'''

######## Imports ########
import numpy as np
import time
from basil_core.array_tools._indexer import _unique_array_index64
from basil_core.array_tools._indexer import _unique_array_index32
from basil_core.array_tools._indexer import _unique_array_index16
from basil_core.array_tools._indexer import _unique_array_index64u
from basil_core.array_tools._indexer import _unique_array_index32u
from basil_core.array_tools._indexer import _unique_array_index16u

######## Declarations ########

__all__ = [
           "unique_array_index",
          ]

######## Functions ########

def unique_array_index(unique, sample):
    '''Find the indices of a unique array matching some sample

    Paramters
    ---------
    unique  : `~numpy.ndarray` (npts_unique,) dtype=int
        Unique array
    sample : `~numpy.ndarray` (npts,) dtype=int
        Sample array we would like to know the locations of

    Returns
    -------
    indices : `~numpy.ndarray` (npts) dtype=int
        Indices of sample in unique
    '''
    #### Check inputs ####
    ## Check unique ##
    if not isinstance(unique, np.ndarray):
        raise TypeError("unique should be a numpy array, but is ", type(unique))
    # If unique is a numpy array, it should be one dimensional
    if len(unique.shape) != 1:
        raise RuntimeError("unique should be a 1-D array, but has shape ", unique.shape)
    # Get size
    npts_unique = unique.size
    assert all(unique >= 0)

    ## Check sample ##
    if not isinstance(sample, np.ndarray):
        raise TypeError("sample should be a numpy array, but is ", type(sample))
    # If sample is a numpy array, it should be one dimensional
    if len(sample.shape) != 1:
        raise RuntimeError("sample should be a 1-D array, but has shape ", sample.shape)
    # Get size
    npts_sample = sample.size
    assert all(sample >= 0)

    #### Check types ####
    assert unique.dtype == sample.dtype
    # Initialize indices
    indices = None

    ## Attempt to find everything
    if unique.dtype == np.uint16:
        indices = _unique_array_index16u(unique, sample)
    elif unique.dtype == np.int16:
        indices = _unique_array_index16(unique, sample)
    elif unique.dtype == np.uint32:
        indices = _unique_array_index32u(unique, sample)
    elif unique.dtype == np.int32:
        indices = _unique_array_index32(unique, sample)
    elif unique.dtype == np.uint64:
        indices = _unique_array_index64u(unique, sample)
    elif unique.dtype == np.int64:
        indices = _unique_array_index64(unique, sample)
    else:
        raise RuntimeError("Something is wrong with unique_array_index inputs")

    if indices is None:
        raise RuntimeError("Failed to find indices")

    ## Estimate c function ##
    return indices


