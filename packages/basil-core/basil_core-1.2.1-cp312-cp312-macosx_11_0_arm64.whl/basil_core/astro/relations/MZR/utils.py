'''MZR utils; sampling from metallicity distributions'''

######## Global Imports ########
import numpy as np
from basil_core.astro.relations.MZR.MZR import Solar_MZR
from basil_core.random.pcg64 import seed_parser

######## Functions ########

def metallicity_samples(MZR, redshift, gsm, nsample, zsun=0.017, seed=None, noise=True):
    '''Generates metallicity samples for a given redshift

    Parameters
    ----------
    MZR: function
        Metallicity of redshift function
    redshift: float
        Redshift at which we need to know the metallicity
    gsm: float
        Galactic stellar mass
    nsample: int
        The number of samples we want to draw
    zsun: float
        The solar metallicity assumed for this relation in the StarTrack paper
        DO NOT CHANGE THIS unless you know why it was set to this value for
        this particular function in StarTrack
    seed: int, optional
        Seed for random number generator

    Returns
    -------
    Zsample: np.ndarray
        Galaxy star forming metallicity samples
    '''
    # Imports 
    from scipy.stats import norm
    # Get random seed
    rs = seed_parser(seed)
    # Generate random samples
    rsample = rs.uniform(size=nsample)
    # Get characteristic Metallicity
    Zave = MZR(redshift, gsm, zsun=zsun)
    if not noise:
        return Zave
    # Get CDF(0) -- negative metallicity is not physical
    CDF_zero = norm.cdf(0, loc=Zave, scale=np.exp(-0.5)*Zave)
    # Rescale random numbers
    rsample = rsample * (1 - CDF_zero) + CDF_zero
    # Get samples assuming 0.5 Dex error
    Zsample = norm.ppf(
                       rsample,
                       loc=Zave,
                       scale=np.exp(-0.5)*Zave,
                      )
    return Zsample
