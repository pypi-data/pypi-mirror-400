'''Python evaluation of c extensions for probabilistic distances

'''

######## Imports ########
import numpy as np
from ._distance import _bhattacharyya_distance
from ._distance import _hellinger_distance
from ._relative_entropy import _rel_entr
from ._relative_entropy import _log_rel_entr
from ._relative_entropy import _log_norm_rel_entr

######## Declarations ########

__all__ = [
           "bhattacharyya_distance",
           "hellinger_distance",
           "rel_entr",
          ]

######## Functions ########

def bhattacharyya_distance(P,Q):
    '''Calculate the bhattacharyya distance between P and Q for many Q

    Parameters
    ----------
    P : `~numpy.ndarray` (npts,)
        First distribution
    Q : `~numpy.ndarray` (nQ, npts)
        Second distribution (or arrangement of distributions)

    Returns
    -------
    B : `~numpy.ndarray`
        The value of the bhattacharyya distance for each Q
    '''
    #### Check inputs ####
    
    ## Check P ##
    # Check that P is a numpy array
    if not isinstance(P, np.ndarray):
        raise TypeError("P should be a numpy array, but is ", type(P))
    # P is a numpy array. It should be a one dimensional array
    if len(P.shape) != 1:
        raise RuntimeError("P should be a 1-D array, but has shape ", P.shape)
    # Okay. How many points are there?
    npts = P.size

    ## Check Q ##
    # Check that Q is a numpy array
    if not isinstance(Q, np.ndarray):
        # Don't panic. We will also accept a list of numpy arrays
        if hasattr(Q, "__iter__") and (len(Q) > 1):
            Q = np.asarray(Q)
        # Okay, you can crash now
        else:
            raise TypeError("Q should be a numpy array (or list of numpy arrays, but is ", type(Q))

    # Check that Q has the right shape
    if len(Q.shape) == 1:
        # This will fail anyway if there are the wrong number of points
        Q = Q.reshape((1,npts))
        nQ = 1
    elif len(Q.shape) == 2:
        if not (Q.shape[1] == npts):
            raise RuntimeError("Q should be a (nQ, npts) array, but is ", Q.shape)
        else:
            nQ = Q.shape[0]
    else:
        raise RuntimeError("Q has too many dimensions; Q.shape = ", Q.shape)

    return _bhattacharyya_distance(P, Q)

def hellinger_distance(P,Q):
    '''Calculate the Hellinger distance between P and Q for many Q

    Parameters
    ----------
    P : `~numpy.ndarray` (npts,)
        First distribution
    Q : `~numpy.ndarray` (nQ, npts)
        Second distribution (or arrangement of distributions)

    Returns
    -------
    B : `~numpy.ndarray`
        The value of the bhattacharyya distance for each Q
    '''
    #### Check inputs ####
    
    ## Check P ##
    # Check that P is a numpy array
    if not isinstance(P, np.ndarray):
        raise TypeError("P should be a numpy array, but is ", type(P))
    # P is a numpy array. It should be a one dimensional array
    if len(P.shape) != 1:
        raise RuntimeError("P should be a 1-D array, but has shape ", P.shape)
    # Okay. How many points are there?
    npts = P.size

    ## Check Q ##
    # Check that Q is a numpy array
    if not isinstance(Q, np.ndarray):
        # Don't panic. We will also accept a list of numpy arrays
        if hasattr(Q, "__iter__") and (len(Q) > 1):
            Q = np.asarray(Q)
        # Okay, you can crash now
        else:
            raise TypeError("Q should be a numpy array (or list of numpy arrays, but is ", type(Q))

    # Check that Q has the right shape
    if len(Q.shape) == 1:
        # This will fail anyway if there are the wrong number of points
        Q = Q.reshape((1,npts))
        nQ = 1
    elif len(Q.shape) == 2:
        if not (Q.shape[1] == npts):
            raise RuntimeError("Q should be a (nQ, npts) array, but is ", Q.shape)
        else:
            nQ = Q.shape[0]
    else:
        raise RuntimeError("Q has too many dimensions; Q.shape = ", Q.shape)

    return _hellinger_distance(P, Q)

def rel_entr(P, Q=None, lnP=None, lnQ=None, normQ=False):
    '''Calculate the Relative Entropy between P and Q for many Q

    Parameters
    ----------
    P : `~numpy.ndarray` (npts,)
        First distribution
    Q : `~numpy.ndarray` (nQ, npts)
        Second distribution (or arrangement of distributions)
    lnP : `~numpy.ndarray` (npts,)
        Log of the first distribution
    lnQ : `~numpy.ndarray` (nQ, npts)
        Log of the second distribution (or arrangement of distributions)
    normQ : bool
        Normalize Q?

    Returns
    -------
    B : `~numpy.ndarray`
        The value of the bhattacharyya distance for each Q
    '''
    #### Check inputs ####
    
    ## Check P ##
    # Check that P is a numpy array
    if not isinstance(P, np.ndarray):
        raise TypeError("P should be a numpy array, but is ", type(P))
    # P is a numpy array. It should be a one dimensional array
    if len(P.shape) != 1:
        raise RuntimeError("P should be a 1-D array, but has shape ", P.shape)
    # Okay. How many points are there?
    npts = P.size

    ## Check lnP ##
    if not (lnP is None):
        # Check that lnP is a numpy array
        if not isinstance(lnP, np.ndarray):
            raise TypeError("lnP should be a numpy array, but is ", type(lnP))
        # lnP is a numpy array. It should be a one dimensional array
        if len(lnP.shape) != 1:
            raise RuntimeError("lnP should be a 1-D array, but has shape ", lnP.shape)

    ## Check Q ##
    if ((Q is None) and (lnQ is None)):
        raise RuntimeError("Must specify Q or lnQ")
    if not (Q is None):     
        # Check that Q is a numpy array
        if not isinstance(Q, np.ndarray):
            # Don't panic. We will also accept a list of numpy arrays
            if hasattr(Q, "__iter__") and (len(Q) > 1):
                Q = np.asarray(Q)
            # Okay, you can crash now
            else:
                raise TypeError("Q should be a numpy array (or list of numpy arrays, but is ", type(Q))

        # Check that Q has the right shape
        if len(Q.shape) == 1:
            # This will fail anyway if there are the wrong number of points
            Q = Q.reshape((1,npts))
            nQ = 1
        elif len(Q.shape) == 2:
            if not (Q.shape[1] == npts):
                raise RuntimeError("Q should be a (nQ, npts) array, but is ", Q.shape)
            else:
                nQ = Q.shape[0]
        else:
            raise RuntimeError("Q has too many dimensions; Q.shape = ", Q.shape)

    if not (lnQ is None):     
        # Check that Q is a numpy array
        if not isinstance(lnQ, np.ndarray):
            # Don't panic. We will also accept a list of numpy arrays
            if hasattr(lnQ, "__iter__") and (len(lnQ) > 1):
                lnQ = np.asarray(lnQ)
            # Okay, you can crash now
            else:
                raise TypeError("Q should be a numpy array (or list of numpy arrays, but is ", type(lnQ))

        # Check that Q has the right shape
        if len(lnQ.shape) == 1:
            # This will fail anyway if there are the wrong number of points
            lnQ = lnQ.reshape((1,npts))
            nQ = 1
        elif len(lnQ.shape) == 2:
            if not (lnQ.shape[1] == npts):
                raise RuntimeError("lnQ should be a (nQ, npts) array, but is ", lnQ.shape)
            else:
                nQ = lnQ.shape[0]
        else:
            raise RuntimeError("lnQ has too many dimensions; lnQ.shape = ", lnQ.shape)
    
    #### Cases ####

    ## Case 0: P and Q given alone ##
    if (not (Q is None)) and (lnQ is None) and (lnP is None) and (not normQ):
        # Get numpy double max value
        max_value = np.finfo(np.double).max
        return _rel_entr(P, Q, max_value)
    #### Case 1: P and Q are given, normQ = True ####
    elif (not (Q is None)) and (lnQ is None) and (lnP is None) and normQ:
        if nQ == 1:
            Q /= np.sum(Q)
        else:
            Q /= np.sum(Q, axis=1).reshape((nQ,1))
        max_value = np.finfo(np.double).max
        return _rel_entr(P, Q, max_value)

    #### Case 2: lnP is given and lnQ is given, Q is not given, normQ = false ####
    elif (not normQ):
        # We don't care about Q
        if lnP is None:
            lnP = np.log(P)
        if lnQ is None:
            lnQ = np.log(Q)
        # We want to use the log information we already had to compute things faster
        return _log_rel_entr(P, lnP, lnQ)
    #### Case 3: Q does not come normalized out of the bag, and we want to use log info ####
    elif normQ:
        # Get log info if we don't already have it
        if lnP is None:
            lnP = np.log(P)
        if lnQ is None:
            lnQ = np.log(Q)
        # If Q is given, we actualy do want to take advantage of that
        if (not (Q is None)):
            if nQ == 1:
                Qsum = np.sum(Q)
            else:
                Qsum = np.sum(Q, axis=1)
            Qc = np.log(Qsum).reshape(nQ,1)
            lnQ -= Qc
            return _log_rel_entr(P, lnP, lnQ)
        # We only have P, lnP, lnQ, and we want to normalize
        else:
            return _log_norm_rel_entr(P, lnP, lnQ)
           
        
        

