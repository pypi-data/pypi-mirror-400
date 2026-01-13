#!/usr/bin/env python3
'''Initial Mass Functions (IMF)

This file contains IMF functions motivated by literature.

Authors
-------
    Vera Delfavero
    xevra86@gmail.com - vera.delfavero@ligo.org - vera.delfavero@nasa.gov

'''
# TODO: consider updating GSMF to reflect recent literature
# https://www.aanda.org/articles/aa/full_html/2023/09/aa45581-22/aa45581-22.html
# TODO investigate alternate MZR/uncertainties

######## Imports #########
import numpy as np
from os.path import join
from scipy.interpolate import CubicSpline
from astropy import units as u
import warnings

def Salpeter_IMF(mass, IMF_alpha=2.35):
    ''' pdf of stellar mass

    Citation
    --------
        https://ui.adsabs.harvard.edu/abs/1955ApJ...121..161S

    Parameters
    ----------
    mass: array_like
        Mass is the dependent variable for evaluation of the density function
    IMF_alpha: float, optional
        A correction factor (see citation)

    Returns
    -------
    psi: np.ndarray
        The value of the density function at specified mass
    '''
    mass = np.asarray(mass)
    psi = np.zeros_like(mass)
    sample = (mass >= 0.08) & (mass <= 0.5)
    psi[sample] = mass[sample]**(-1.3)
    sample = (mass >= 0.5) & (mass <= 1.0)
    psi[sample] = mass[sample]**(-2.2)
    sample = (mass > 1.0) & (mass <= 150.)
    psi[sample] = mass[sample]**(-IMF_alpha)
    return psi

