#!/usr/bin/env python3
'''Nuclear Star Cluster mass of Galactic Stellar Mass

Authors
-------
    Vera Delfavero
    xevra86@gmail.com - vera.delfavero@ligo.org - vera.delfavero@nasa.gov
'''
######## Imports ########
from astropy import units as u

def Neumayer_early_NSC_mass(mstar):
    '''Nuclear Star Cluster mass from Galaxy Stellar Mass

    Citation
    --------
        https://link.springer.com/article/10.1007/s00159-020-00125-0
        Eq 1.

    Notes
    -----
        log M_NSC = 0.48 log(M_* / 10**9 Msun) + 6.51

        or

        M_NSC = 10^(6.51) * (M_* * 10**-9 MSUN)^0.48
        10^6.51 = 3235936.569296281

        If for some reason you needed this to be faster,
            you could use a square root as an approximation.
        The literature supports this approximation.
    
    Parameters
    ----------
    mass: array_like
        Galaxy stellar mass
    
    Returns
    -------
    NSC_mass: array_like
        Nuclear Star Cluster mass for given specified
        Galactic Stellar Mass

    '''
    if hasattr(mstar, 'unit'):
        mstar = mstar.to('solMass').value
        return (3235936.569296281 * (mstar * 1e-9)**0.48) * u.solMass
    else:
        return 3235936.569296281 * (mstar * 1e-9)**0.48

def Neumayer_late_NSC_mass(mstar):
    '''late-type Nuclear Star Cluster mass from Galaxy Stellar Mass

    Citation
    --------
        https://link.springer.com/article/10.1007/s00159-020-00125-0
        Eq 2.

    Notes
    -----
        log M_NSC = 0.92 log(M_* / 10**9 Msun) + 6.13

        or

        M_NSC = 10^(6.13) * (M_* * 10**-9 MSUN)^0.92
        10^6.13 = 1348962.8825916534
    
    Parameters
    ----------
    mass: array_like
        Galaxy stellar mass
    
    Returns
    -------
    NSC_mass: array_like
        late-type Nuclear Star Cluster mass for given specified
        Galactic Stellar Mass
    '''
    if hasattr(mstar, 'unit'):
        mstar = mstar.to('solMass').value
        return (1348962.8825916534 * (mstar * 1e-9)**0.92) * u.solMass
    else:
        return 1348962.8825916534 * (mstar * 1e-9)**0.92

