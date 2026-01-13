#!/usr/bin/env python3
'''Nuclear Star Cluster fraction of Galactic Stellar Mass

Identify the probability of a galaxy having a nuclear star cluster
    as a function of galactic stellar mass

Authors
-------
    Vera Delfavero
    xevra86@gmail.com - vera.delfavero@ligo.org - vera.delfavero@nasa.gov

'''

######## Imports #########
import numpy as np
from scipy.interpolate import CubicSpline

######## Globals ########

NEUMAYER_NSC_EARLY_LOGM = np.asarray([5.85,6.55,7.25,7.95,8.65,9.35,10.05,10.75,11.45])
'''LOG(M/MSUN) for early-type galaxies with NSC, from Neumayer et al. (2020)'''
NEUMAYER_NSC_EARLY_FRAC = np.asarray([0.0625,0.16939891,0.40361446,0.6119403,0.80952381,0.725,0.59615385,0.33333333,0.11764706])
'''Fraction of early-type galaxies with NSC, from Neumayer et al. (2020)'''
NEUMAYER_NSC_EARLY_ERR  = np.asarray([0.02017179,0.02772848,0.03807964,0.05953418,0.04947262,
                                      0.07060011,0.06804332,0.07856742,0.07814249])
'''Error in fraction of early-type galaxies with NSC, from Neumayer et al. (2020)'''
NEUMAYER_NSC_LATE_LOGM = np.asarray([5.85,6.55,7.25,7.95,8.65,9.35,10.05,10.75])
'''LOG(M/MSUN) for late-type galaxies with NSC, from Neumayer et al. (2020)'''
NEUMAYER_NSC_LATE_FRAC = np.asarray([0.23076923,0.16666667,0.3,0.71428571,0.65151515,0.79365079,0.62857143,0.66666667])
'''Fraction of late-type galaxies with NSC, from Neumayer et al. (2020)'''
NEUMAYER_NSC_LATE_ERR  = np.asarray([0.11685454,0.10758287,0.10246951,0.07636035,0.05865192,0.0509854,0.08167346,0.19245009])
'''Error in fraction of late-type galaxies with NSC, from Neumayer et al. (2020)'''

# Generate cubic splines once on import
NEUMAYER_NSC_EARLY_CS = CubicSpline(NEUMAYER_NSC_EARLY_LOGM, NEUMAYER_NSC_EARLY_FRAC)
NEUMAYER_NSC_LATE_CS = CubicSpline(NEUMAYER_NSC_LATE_LOGM, NEUMAYER_NSC_LATE_FRAC)

def Neumayer_NSC_frac_of_GSM(mstar):
    '''Return fraction of galaxies with NSC for early and late-types

    Citation
    --------
    https://link.springer.com/article/10.1007/s00159-020-00125-0
    Figure 3

    Parameters
    ----------
    mstar: array_like
        Galaxy Stellar Mass
    
    Returns
    -------
    NSC_frac_early: array_like
        Fraction of early-type galaxies with NSC
    NSC_frac_late: array_like
        Fraction of late-type galaxies with NSC
    '''
    if hasattr(mstar,'unit'):
        mstar = mstar.to('solMass')
    else:
        warnings.warn("Neumayer_NSC_frac_of_GSM: assuming solar mass for unitless input")
    # Get logM
    logM = np.log10(mstar.value)
    # Interpolate
    NSC_frac_early = NEUMAYER_NSC_EARLY_CS(logM)
    NSC_frac_late = NEUMAYER_NSC_LATE_CS(logM)
    # Catch bounds
    NSC_frac_early[NSC_frac_early < 0.] = 0.
    NSC_frac_late[NSC_frac_late < 0.] = 0.
    NSC_frac_early[NSC_frac_early > 1.] = 1.
    NSC_frac_late[NSC_frac_late > 1.] = 1.
    # Return values
    return NSC_frac_early, NSC_frac_late
