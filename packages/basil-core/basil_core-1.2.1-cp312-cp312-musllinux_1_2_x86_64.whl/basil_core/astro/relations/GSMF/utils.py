#!/usr/bin/env python3
''' Confidence interval'''

######## Imports #########
import numpy as np
from os.path import join
from astropy import units as u
import warnings
######## Local ########
from basil_core.random.pcg64 import seed_parser

######## Functions ########

def GSMF_cdf(
             GSMF,
             redshift,
             gsm_min,
             gsm_max,
             mbins=100,
            ):
    '''Use the pdf to find the GSMF cdf
    
    Parameters
    ----------
    GSMF: function
        Galactic Stellar Mass Function which takes gsm, z, gsm_min, gsm_max as inputs
    redshift: float
        value of redshift
    gsm_min: float
        Smallest galaxy we care about
    gsm_max: float
        Biggest galaxy we care about
    mbins: int
        Bins for cdf interpolation

    Returns
    -------
    Mave: float
        Average Galaxy Stellar Mass at a given redshift
    '''
    # Generate the cdf
    gsm = np.exp(np.linspace(
                              np.log(gsm_min.to("solMass").value),
                              np.log(gsm_max.to("solMass").value),
                              mbins
                             )) * gsm_max.unit
    pdf = GSMF(gsm,redshift,gsm_min=gsm_min,gsm_max=gsm_max)
    # TODO fix this
    pdf[~np.isfinite(pdf)] = 0.
    cdf = np.cumsum(pdf)
    cdf /= np.max(cdf)
    return gsm.to('solMass'), cdf

def GSMF_mean(
              GSMF,
              redshift,
              gsm_min,
              gsm_max,
              mbins=100,
             ):
    ''' Use the GSMF cdf to find the GSMF mean
    
    Parameters
    ----------
    GSMF: function
        Galactic Stellar Mass Function which takes gsm, z, gsm_min, gsm_max as inputs
    redshift: float
        value of redshift
    gsm_min: float
        Smallest galaxy we care about
    gsm_max: float
        Biggest galaxy we care about
    mbins: int
        Bins for cdf interpolation

    Returns
    -------
    Mave: float
        Average Galaxy Stellar Mass at a given redshift
    '''
    # Generate the cdf
    gsm, cdf = GSMF_cdf(GSMF, redshift, gsm_min, gsm_max, mbins=mbins)
    
    # The sum of the booleans for which cdf < 0.5 is the index of gsm
    #   at its mean
    Mave = gsm[np.sum(cdf < 0.5)]
    return Mave

def GSMF_confidence(
                    GSMF,
                    redshift,
                    gsm_min,
                    gsm_max,
                    mbins=100,
                    confidence_value=0.68,
                   ):
    '''Use the GSMF cdf to find a left-handed confidence value
    
    Parameters
    ----------
    GSMF: function
        Galactic Stellar Mass Function which takes gsm, z, gsm_min, gsm_max as inputs
    redshift: float
        value of redshift
    gsm_min: float
        Smallest galaxy we care about
    gsm_max: float
        Biggest galaxy we care about
    mbins: int
        Bins for cdf interpolation
    confidence_value: float
        Fraction we are computing the confidence to

    Returns
    -------
    Mval: float
        Closest mass to fractional value
    '''
    # Check value is sensible
    assert confidence_value >= 0
    assert confidence_value <= 1
    # Generate the cdf
    gsm, cdf = GSMF_cdf(GSMF, redshift, gsm_min, gsm_max, mbins=mbins)
    
    # The sum of the booleans for which cdf < x is the index of gsm
    #   at fraction x of the pdf's integral
    Mval = gsm[np.sum(cdf < confidence_value)]
    return Mval

def GSMF_normalization(
                       GSMF,
                       redshift,
                       gsm_min_local,
                       gsm_max_local,
                       gsm_min_global,
                       gsm_max_global,
                       nbins = int(1e6),
                      ):
    '''Find the fraction of mass in a particular part of parameter space
    
    Parameters
    ----------
    GSMF: function
        Galactic Stellar Mass Function which takes gsm, z, gsm_min, gsm_max as inputs
    redshift: float
        value of redshift
    gsm_min_local: float
        Smallest galaxy we care about
    gsm_max_local: float
        Biggest galaxy we care about
    gsm_min_global: float
        Smallest galaxy in our universe
    gsm_max_global: float
        Biggest galaxy in our universe
    nbins: int
        Number of mass bins

    Returns
    -------
    local_fraction: float
        The fraction of the GSMF within specified limits
    '''
    # Get a space of galaxy masses from the global min and max
    gsm = np.linspace(gsm_min_global.to('solMass').value, gsm_max_global.to('solMass').value, nbins) * u.solMass
    # Make sure integration makes sense
    assert np.log10(gsm[1].to('solMass').value - gsm[0].to('solMass').value) < np.log10(gsm_min_global.to('solMass').value)
    # Make sure limits make sense
    assert (gsm_min_local.to('solMass').value >= gsm_min_global.to('solMass').value) or \
        np.isclose(gsm_min_local.to('solMass').value, gsm_min_global.to('solMass').value)
    assert (gsm_max_local.to('solMass').value <= gsm_max_global.to('solMass').value) or \
        np.isclose(gsm_max_local.to('solMass').value, gsm_max_global.to('solMass').value)
    # Get the pdf with global min and max
    pdf_global = GSMF(gsm, redshift, gsm_min=gsm_min_global, gsm_max=gsm_max_global)
    # Get the pdf for the selected min and max
    pdf_local = GSMF(gsm, redshift, gsm_min=gsm_min_local, gsm_max=gsm_max_local)
    # Find differences between global and local
    mask = (gsm >= gsm_min_local) & (gsm <= gsm_max_local)
    pdf_local[~mask] = 0.
    diff = pdf_local != pdf_global
    assert np.allclose(pdf_local[diff], 0.)
    # Find the normalization factor
    local_fraction = np.sum(pdf_local) / np.sum(pdf_global)
    return local_fraction

def GSMF_samples(
                 GSMF,
                 redshift,
                 gsm_min,
                 gsm_max,
                 nsample,
                 mbins=100,
                 seed=None,
                ):
    '''Generate some sample galaxies for a given redshift and average Z

    Parameters
    ----------
    nsample: int
        Number of galaxy samples to draw
    redshift: float
        Characteristic redshift value for galaxy samples
    gsm_min: float
        Minimum galaxy mass in span
    gsm_max: float
        Maximum galaxy mass in span
    mbins: int, optional
        Number of bins for CDF interpolation
    seed: int, optional
        Seed for random number generator

    Returns
    -------
    msample: np.ndarray
        Galaxy Stellar Mass samples
    '''
    from scipy.interpolate import CubicSpline
    # Get random seed
    rs = seed_parser(seed)
    ## Generate the galaxy mass samples ##
    # generate random samples
    rsample = rs.uniform(size=nsample)
    # Initialize array
    msample = np.empty(nsample)
    # Generate the cdf
    gsm, cdf = GSMF_cdf(GSMF, redshift, gsm_min, gsm_max, mbins=mbins)
    cdf, index = np.unique(cdf, return_index=True)
    gsm = gsm[index]
    gsm = gsm.value
    # Get cubic spline
    spline = CubicSpline(cdf, gsm)
    # Assign sample values
    #for i in range(nsample):
    #    msample[i] = gsm[np.sum(cdf < rsample[i])]
    msample = spline(rsample)
    # Assign units
    msample = msample * u.solMass
    return msample

