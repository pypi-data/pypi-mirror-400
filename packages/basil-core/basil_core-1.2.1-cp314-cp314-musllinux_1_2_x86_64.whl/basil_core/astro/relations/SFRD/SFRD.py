#!/usr/bin/env python3
'''Star Formation Rate Density -- SFR(D) 

SFRD recipes 

Authors
-------
    Vera Delfavero
    xevra86@gmail.com - vera.delfavero@ligo.org - vera.delfavero@nasa.gov

TODO: Ask floor if she wants credit

'''

######## Imports #########
import numpy as np
from os.path import join
from scipy.interpolate import CubicSpline
from astropy import units as u
import warnings

def Madau_Fragos_SFR2(z, IMF_correction=0.66, cosmology="Planck15"):
    '''Star formation rate as function of redshift for minimum SFR at high z

    Citation
    --------
        https://arxiv.org/pdf/1606.07887.pdf
        see Eq. 1
    
    Parameters
    ----------
    z: array_like
        Redshift is the dependent variable for SFR
    IMF_correction: float, optional
        Correction factor for IMF (see citation)

    Returns
    -------
    sfr: :obj:Quantity
        SFR evaluated at given redshift
        (units of solar mass per year per Mpc^3).
        
    '''
    z = np.asarray(z)
    sfr = IMF_correction*0.015*(((1.0+z)**(2.6))/(1.0 + ((1.0 + z)/3.2)**(6.2)))
    sfr = sfr * u.solMass / ((u.Mpc ** 3) * u.yr)
    return sfr

def Madau_Fragos_SFR3(z, IMF_correction=0.66, cosmology="Planck15"):
    '''Star formation rate as function of redshift for maximum SFR at high z

    Citation
    --------
        https://arxiv.org/pdf/1606.07887.pdf
        see Eq. 1
    
    Parameters
    ----------
    z: array_like
        Redshift is the dependent variable for SFR
    IMF_correction: float, optional
        Correction factor for IMF (see citation)

    Returns
    -------
    sfr: :obj:Quantity
        SFR evaluated at given redshift
        (units of solar mass per year per Mpc^3).
        
    '''
    z = np.asarray(z)
    sfr = IMF_correction*0.015*(((1.0+z)**(2.7))/(1.0 + ((1.0 + z)/3.0)**(5.35)))
    sfr = sfr * u.solMass / ((u.Mpc ** 3) * u.yr)
    return sfr

def Madau_Fragos_SFRD(z,**kwargs):
    '''alias for Madau_Fragos_SFR2'''
    return Madau_Fragos_SFR2(z,**kwargs)

def Madau_Dickinson_SFRD(z, IMF_correction=0.66, cosmology="Planck15"):
    '''Star formation as a function of redshift

    Citation
    --------
        https://arxiv.org/pdf/1403.0007v3.pdf
        see Eq. 15 (Page 48)

    Parameters
    ----------
    z: array_like
        Redshift is the dependent variable for SFR

    Returns
    -------
    sfr: :obj:Quantity
        SFR evaluated at given redshift
        (units of solar mass per year per Mpc^3).
    '''
    z = np.asarray(z)
    sfr = 0.015 * (((1.0+z)**(2.7))/(1.0 + ((1.0 + z)/2.9)**(5.6)))
    sfr = sfr * u.solMass / ((u.Mpc ** 3) * u.yr)
    return sfr

def Strogler_SFRD(z, IMF_correction=0.66, cosmology="Planck15"):
    '''
    Citation
    --------
        https://arxiv.org/pdf/1308.1546.pdf
        Eq. 1

    Parameters
    ----------
    z: array_like
        Redshift is the dependent variable for SFR

    Returns
    -------
    sfr: :obj:Quantity
        SFR evaluated at given redshift
        (units of solar mass per year per Mpc^3).
    '''
    # Get cosmology
    from astropy import cosmology as allcosmo
    cosmo = allcosmo.__getattr__(cosmology)
    # Get hubble time from lookbacktime of redshift over 9000
    hubble_time = cosmo.lookback_time(9001)
    # Get lookback time
    t_lookback=cosmo.lookback_time(z)
    # should be Gyr
    t_age = hubble_time - t_lookback
    t_lookback = t_lookback.to('Gyr').value
    t_age = t_age.to('Gyr').value
    # Coeffs
    a,b,c,d =0.182, 1.26, 1.865, 0.071
    sfr = a * (t_age**b * np.exp(-t_age/c) + d*np.exp(d*(t_lookback)/c))
    if np.isnan(sfr.any()):
        raise ValueError("Nan in SFR calculation for Strogler_SFRD")
    # Apply units
    sfr = sfr * u.solMass / ((u.Mpc ** 3) * u.yr)
    return sfr

def Neijssel_SFRD(z, IMF_correction=0.66, cosmology="Planck15"):
    '''Star formation as a function of redshift

    Citation
    --------

    Parameters
    ----------
    z: array_like
        Redshift is the dependent variable for SFR

    Returns
    -------
    sfr: :obj:Quantity
        SFR evaluated at given redshift
        (units of solar mass per year per Mpc^3).
    '''
    #TODO get real citation
    z = np.asarray(z)
    sfr = 0.01 * ((1.+z)**2.77) / (1. + ((1.+z)/2.9)**4.7)
    sfr = sfr * u.solMass / ((u.Mpc ** 3) * u.yr)
    return sfr
