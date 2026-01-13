#!/usr/bin/env python3
''' Metallicity (z)redshift Relation -- MZR

Metallicity redshift relation examples

Authors
-------
    Vera Delfavero
    xevra86@gmail.com - vera.delfavero@ligo.org - vera.delfavero@nasa.gov

'''
######## Globals ########
DEFAULT_ZSUN=0.017
DEFAULT_logOH12sun=8.69

######## Imports #########
import warnings
import numpy as np
from astropy import units as u

def Madau_Fragos_MZR(z, gsm, zsun=DEFAULT_ZSUN):
    ''' Metllicity Redshift Relation (MZR)

    Citation
    --------
        https://arxiv.org/pdf/1606.07887.pdf
        see Eq. 6

    Parameters
    ----------
    z: array_like
        Redshift is the dependent variable for MZR
    gsm: array_like
        Galactic Solar Mass samples
    zsun: float, optional
        Solar metallicity, but don't change this unless you
        understand why it was 0.017 in the StarTrack papers

    Returns
    -------
    Metallicity: np.ndarray
        Average metallicity at given redshift
    '''
    #TODO log10?
    #TODO Check metallicity assumptions in paper
    return np.exp(np.log(zsun) + 0.153 - 0.074*z**(1.34))

def Ma2015_MZR(z, gsm, zsun=DEFAULT_ZSUN, logOH12sun=DEFAULT_logOH12sun):
    ''' Metallicity dependence on galactic stellar mass and redshift

    Citation
    --------
    https://academic.oup.com/mnras/article/456/2/2140/1061514

    Parameters
    ----------
    z: array_like
        Redshift is the dependent variable for MZR
    gsm: array_like
        Galactic Solar Mass samples
    zsun: float, optional
        Solar metallicity, but don't change this unless you
        understand why it was 0.017 in the StarTrack papers
    '''
    # TODO credit Floor as well
    if hasattr(gsm, 'unit'):
        gsm = gsm.to('solMass').value
    else:
        warnings.warn("Ma2015_MZR: assuming solar mass for unitless input")
    logM = np.log10(gsm)
    logZZsun = 0.35*(logM - 10) + 0.93*np.exp(-0.43*z) + 7.95 - logOH12sun
    return np.exp(logZZsun)*zsun

def Nakajima2023_MZR(z, gsm, zsun=DEFAULT_ZSUN, logOH12sun=DEFAULT_logOH12sun):
    ''' Metallicity dependence on galactic stellar mass and redshift

    Citation
    --------
    https://iopscience.iop.org/article/10.3847/1538-4365/acd556/pdf

    Parameters
    ----------
    z: array_like
        Redshift is the dependent variable for MZR
    gsm: array_like
        Galactic Solar Mass samples
    zsun: float, optional
        Solar metallicity, but don't change this unless you
        understand why it was 0.017 in the StarTrack papers

    #error in 0.25: \pm 0.03
    error in 8.24: \pm 0.05
    '''
    if hasattr(gsm, 'unit'):
        gsm = gsm.to('solMass').value
    else:
        warnings.warn("Nakajima2023_MZR: assuming solar mass for unitless input")
    logM = np.log10(gsm)
    logZZsun = 0.25*(logM - 10) + 8.24 - logOH12sun
    return np.exp(logZZsun)*zsun*np.ones(z.size)

def Solar_MZR(z, gsm, zsun=DEFAULT_ZSUN):
    """ Metallicity not dependent on anything

    Parameters
    ----------
    z: array_like
        Redshift is the dependent variable for MZR
    gsm: array_like
        Galactic Solar Mass samples
    zsun: float, optional
        Solar metallicity, but don't change this unless you
        understand why it was 0.017 in the StarTrack papers
    """
    return np.full(np.size(gsm),zsun)
