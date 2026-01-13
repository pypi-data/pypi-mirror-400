'''Python evaluation of C extension for indexer'''

######## Imports ########
import numpy as np
import time
from basil_core.stats._schechter import _schechter_fixed_redshift64
from basil_core.stats._schechter import _schechter_varied_redshift64

######## Declarations ########

__all__ = [
           "schechter",
          ]

######## Globals ########
#### Schechter function parameters ####
# Local universe schechter function
COLE_M0 = 11.16
COLE_alpha0 = -1.18
COLE_phi0 = 0.0035

# Fontana fit
FONTANA_M1 = 0.17
FONTANA_M2 = -0.07
FONTANA_alpha1 = -0.082

######## Functions ########
def schechter(
              gsm,
              redshift,
              phi0=COLE_phi0,
              phi1=0.,
              alpha0=COLE_alpha0,
              alpha1=0.,
              M0=COLE_M0,
              M1=0.,
              M2=0.,
              gsm_min=1e7,
              gsm_max=1e13,
             ):
    '''
    '''
    #### Check inputs ####
    ## Check gsm ##
    if not isinstance(gsm, np.ndarray):
        raise TypeError("gsm should be a numpy array, but is ", type(gsm))
    # If gsm is a numpy array, it should be one dimensional
    if len(gsm.shape) != 1:
        raise RuntimeError("gsm should be a 1-D array, but has shape ", gsm.shape)
    # Get size
    npts_gsm = gsm.size

    ## Check redshift ##
    if isinstance(redshift, np.ndarray):
        # If redshift is a numpy array, it should be one dimensional
        if len(redshift.shape) != 1:
            raise RuntimeError("redshift should be a 1-D array, but has shape ", redshift.shape)
        # Get size
        npts_redshift = redshift.size
        assert all(redshift >= 0)
        assert npts_redshift == npts_gsm
    elif isinstance(redshift, float):
        npts_redshift = 1
        assert redshift >= 0.
    else:
        raise TypeError("redshift should be a numpy array, but is ", type(redshift))

    #### Check types ####
    assert isinstance(phi0, float)
    assert isinstance(phi1, float)
    assert isinstance(alpha0, float)
    assert isinstance(alpha1, float)
    assert isinstance(M0, float)
    assert isinstance(M1, float)
    assert isinstance(M2, float)
    assert isinstance(gsm_min, float)
    assert isinstance(gsm_max, float)

    #### Run C function ####
    if isinstance(redshift, float):
        return _schechter_fixed_redshift64(
                                                gsm,
                                                redshift,
                                                phi0, phi1,
                                                alpha0, alpha1,
                                                M0, M1, M2,
                                                gsm_min, gsm_max,
                                                npts_gsm,
                                               )

    else:
        return _schechter_varied_redshift64(
                                                 gsm,
                                                 redshift,
                                                 phi0, phi1,
                                                 alpha0, alpha1,
                                                 M0, M1, M2,
                                                 gsm_min, gsm_max,
                                                 npts_gsm,
                                                )


