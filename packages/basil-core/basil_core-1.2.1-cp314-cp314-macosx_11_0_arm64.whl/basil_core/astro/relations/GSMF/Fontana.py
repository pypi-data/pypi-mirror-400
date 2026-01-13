#!/usr/bin/env python3
''' Galactic Stellar Mass Function -- GSMF

Galaxy mass PDF as a function of other things

Authors
-------
    Vera Delfavero
    xevra86@gmail.com - vera.delfavero@ligo.org - vera.delfavero@nasa.gov

'''
# TODO: consider updating GSMF to reflect recent literature
# https://www.aanda.org/articles/aa/full_html/2023/09/aa45581-22/aa45581-22.html

######## Imports #########
import numpy as np
from astropy import units as u
from basil_core.stats import schechter

######## SETUP ########
#### Schechter function parameters ####
# Local universe schechter function
COLE_M0 = 11.16
COLE_alpha0 = -1.18
COLE_phi0 = 0.0035

# Fontana fit
FONTANA_M1 = 0.17
FONTANA_M2 = -0.07
FONTANA_alpha1 = -0.082
FONTANA_phi1 = -2.20

######## Functions ########
def Cole_GSMF(gsm,redshift,gsm_min=1e7 * u.solMass,gsm_max=1e12 *u.solMass):
    '''Galaxy Stellar Mass Function (GSMF)
    
    Citation
    --------

    Parameters
    ----------
    m: array_like
        Galaxy Stellar Mass
    redshift: float
        Redshift
    gsm_min: float
        Minimum galaxy mass in span
    gsm_max: float
        Maximum galaxy mass in span

    Returns
    -------
    GSMF: array_like
        Density function for Galaxy Stellar Mass Function at specified parameters
    '''
    gsm = gsm.to('solMass').value
    gsm_min = gsm_min.to('solMass').value
    gsm_max = gsm_max.to('solMass').value
    redshift = float(redshift)
    psi = schechter(
                    gsm,
                    redshift,
                    phi0=COLE_phi0,
                    alpha0=COLE_alpha0,
                    M0=COLE_M0,
                    gsm_min=gsm_min,
                    gsm_max=gsm_max,
                   )

    return psi

def Fontana_GSMF(gsm,redshift,gsm_min=1e7 * u.solMass,gsm_max=1e12 *u.solMass):
    '''Galaxy Stellar Mass Function (GSMF)
    
    Citation
    --------
        https://www.aanda.org/articles/aa/pdf/2006/45/aa5475-06.pdf
        see Eq. 1

    Parameters
    ----------
    m: array_like
        Galaxy Stellar Mass
    redshift: float
        Redshift
    gsm_min: float
        Minimum galaxy mass in span
    gsm_max: float
        Maximum galaxy mass in span

    Returns
    -------
    GSMF: array_like
        Density function for Galaxy Stellar Mass Function at specified parameters
    '''
    gsm = gsm.to('solMass').value
    gsm_min = gsm_min.to('solMass').value
    gsm_max = gsm_max.to('solMass').value
    if redshift > 4.:
        redshift = 4.
    redshift = float(redshift)
    psi = schechter(
                    gsm,
                    redshift,
                    phi0=COLE_phi0,
                    phi1=FONTANA_phi1,
                    alpha0=COLE_alpha0,
                    alpha1=FONTANA_alpha1,
                    M0=COLE_M0,
                    M1=FONTANA_M1,
                    M2=FONTANA_M2,
                    gsm_min=gsm_min,
                    gsm_max=gsm_max,
                   )
    return psi
