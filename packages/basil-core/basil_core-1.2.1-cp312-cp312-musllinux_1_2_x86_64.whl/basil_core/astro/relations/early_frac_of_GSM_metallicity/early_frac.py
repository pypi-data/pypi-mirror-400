#!/usr/bin/env python3
'''Bayes factor for early/late type galaxy based on properties

Authors
-------
    Vera Delfavero
    xevra86@gmail.com - vera.delfavero@ligo.org - vera.delfavero@nasa.gov
'''
from importlib import resources as impresources
import numpy as np
from basil_core.astro.relations.early_frac_of_GSM_metallicity import Peng2015
#### Load data ####
import os
Peng2015_STAR_FORMING = np.loadtxt(impresources.files(Peng2015) / 'stellarMZR-SF.TXT')
'''Blue data points by eye for Fig 2a of https://doi.org/10.1038/nature14439'''
Peng2015_PASSIVE = np.loadtxt(impresources.files(Peng2015) / 'stellarMZR-passive.txt')
'''Red data points by eye for Fig 2a of https://doi.org/10.1038/nature14439'''

def Peng_early_frac_estimator(return_gp=False, whitenoise=0.0):
    '''Generate estimator for Bayes factor for early/late type galaxies

    Citation
    --------
        Fig 2a of https://doi.org/10.1038/nature14439

    Parameters
    ----------
    fname_blue: path_like
        location of "stellarMZR-SF.TXT"
    fname_red: path_like
        location of "stellarMZR-passive.txt"

    Returns
    -------
    early_frac_estimator: function
        Estimates Bayes factor for early/late type galaxies
    '''
    import numpy as np
    from astropy import units as u
    import warnings
    # Gaussian process regression
    try:
        from gp_api.utils import fit_compact_nd
    except:
        raise RuntimeError("Peng_early_frac_estimator will only work if gaussian_process_api is installed")
    from scipy.interpolate import CubicSpline
    ## Set up training data ##
    x_train_blue = np.atleast_2d(Peng2015_STAR_FORMING[:,0]).T
    x_train_red = np.atleast_2d(Peng2015_PASSIVE[:,0]).T
    ## Generate gp estimators ##
    GP_BLUE = fit_compact_nd(x_train_blue, Peng2015_STAR_FORMING[:,1], train_err=Peng2015_STAR_FORMING[:,2], whitenoise=whitenoise)
    #blue_data = GP_BLUE.rvs(100, x_train_blue, y_std=BLUE[:,2])
    GP_RED = fit_compact_nd(x_train_red, Peng2015_PASSIVE[:,1], train_err=Peng2015_PASSIVE[:,2], whitenoise=whitenoise)
    ## define Bayes estimator ##
    def bayes_early_frac(logMstar, logZrel):
        '''Bayes factor for early/late type galaxies (logMstar, logZrel)
   
        Parameters
        ----------
        logMstar: array_like
            log10(M/MSUN) for galaxy stellar mass
        logZrel: array_like
            log10(Z/ZSUN) for galaxy metallicity

        Returns
        -------
        early_frac: np.ndarray
            Bayes factor for early/late type galaxies
        '''
        # Get number of galaxies
        ngal = logMstar.size
        # Initialize output array
        early_frac = np.zeros(ngal)
        # Find out of bounds samples
        bounds_index = (logMstar > np.min(Peng2015_STAR_FORMING[:,0])) & \
                       (logMstar < np.max(Peng2015_PASSIVE[:,0]))
        # negative frac for out of bounds samples
        early_frac[~bounds_index] = -1.
        # Find categorically early (red) galaxies
        red_index = logMstar > np.max(Peng2015_STAR_FORMING[:,0])
        # Assign categorically red galaxies
        early_frac[red_index] = 1.
        # Find categorically late (blue) galaxies
        blue_index = (logMstar < np.min(Peng2015_PASSIVE[:,0])) | (logZrel < -1.0)
        #print("categorically blue: %d/%d"%(np.sum(blue_index), ngal))
        early_frac[blue_index] = 0.
     
        ## Estimate fraction for the rest of them ##
        # Find samples that matter
        pdf_index = (bounds_index) & (~red_index) & (~blue_index)
        if np.sum(pdf_index > 0):
            # Select index data
            logMstar_index = np.atleast_2d(logMstar[pdf_index]).T
            logZrel_index = logZrel[pdf_index]
            # Find how many standard deviations they are away from the curve
            #red_sigma = (CS_RED(logMstar_index) - logZrel_index) / LOGZREL_ERR
            red_mu = GP_RED.mean(logMstar_index)
            red_var = GP_RED.variance(logMstar_index)
            red_std = np.sqrt(np.diag(red_var))
            red_sigma = (red_mu - logZrel_index) / red_std
            assert all(np.isfinite(red_sigma))
            blue_mu = GP_BLUE.mean(logMstar_index)
            blue_var = GP_BLUE.variance(logMstar_index)
            blue_std = np.sqrt(np.diag(blue_var))
            blue_sigma = (blue_mu - logZrel_index) / blue_std
            assert all(np.isfinite(blue_sigma))
            # Find the pdf of each type
            red_pdf = np.exp(-0.5 * red_sigma**2)
            assert all(np.isfinite(red_pdf))
            blue_pdf = np.exp(-0.5 * blue_sigma**2)
            assert all(np.isfinite(blue_pdf))

            # Estimate the early fraction for these we got the pdf for
            early_frac_pdf = red_pdf/(red_pdf + blue_pdf)
            try:
                assert all(np.isfinite(early_frac_pdf))
            except:
                nfinite = ~np.isfinite(early_frac_pdf)
                print(logMstar_index[nfinite])
                print(logZrel_index[nfinite])
                print(red_sigma[nfinite])
                print(blue_sigma[nfinite])
                print(red_pdf[nfinite])
                print(blue_pdf[nfinite])
                print(early_frac_pdf[nfinite])
                raise Exception("Break!")

            # Estimate a Bayes factor
            early_frac[pdf_index] = early_frac_pdf
        return early_frac
    # Return the estimator
    if return_gp:
        return bayes_early_frac, GP_BLUE, GP_RED
    else:
        return bayes_early_frac

