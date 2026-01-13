#!/usr/bin/env python3
'''Active Galactic Nuclei Density

Authors
-------
    Vera Delfavero
    xevra86@gmail.com - vera.delfavero@ligo.org - vera.delfavero@nasa.gov

'''

######## Imports #########
#### Standard Library ####
import warnings
from os.path import join
from importlib import resources as impresources
#### Third Party ####
import numpy as np
from astropy import units as u
from scipy.interpolate import CubicSpline
#### Local ####
from basil_core.astro.relations.AGND import Lyon2024
#### Load data ####
Lyon_CG_AGN_PHI = np.loadtxt(impresources.files(Lyon2024) / 'Lyon2024AGNPhi.dat')

def Lyon2024_AGND(
                  redshift,
                  Lbin=10.75,
                 ):
    """The AGN density from Lyon et al. (2024)

    I copied the data and the license to this folder:
    https://gitlab.com/xevra/basil-core/src/basil_core/astro/relations/AGND/Lyon2024

    Citation
    --------
        https://arxiv.org/abs/2410.08541

    Parameters
    ----------
    redshift : array_like
        Redshift values to estimate AGN density at
    Lbin : float
        Luminosity bin from Lyon+2024

    Returns
    -------
    Phi : astropy.unit.Quantity
        AGN number density at each redshift
    """
    # Check Lbin
    assert Lbin in np.unique(Lyon_CG_AGN_PHI[:,0]), \
        f"Unknown luminosity bin {Lbin} in {np.unique(Lyon_CG_AGN_PHI[:,0])}"
    # Define luminosity mask
    luminosity_mask = Lyon_CG_AGN_PHI[:,0] == Lbin
    # Setup Cubic Spline
    cs = CubicSpline(
        Lyon_CG_AGN_PHI[luminosity_mask,1],
        Lyon_CG_AGN_PHI[luminosity_mask,2],
        extrapolate=False,
    )
    # Evaluate the cubic spline and return
    Phi = cs(redshift)
    # Set values outside of data close to zero
    Phi[~np.isfinite(Phi) & (redshift > 1.)] = 1e-10
    # Set values in the local universe to closest finite value
    Phi[~np.isfinite(Phi) & (redshift < 1.)] = Phi[np.isfinite(Phi)][-1]
    # Assign units to Phi
    Phi = Phi * u.Mpc**-3
    return Phi



def Ueda_AGND_gp(redshift, return_train=False):
    '''The AGN density from Ueda et al. (2014)

    Citation
    --------
        https://iopscience.iop.org/article/10.1088/0004-637X/786/2/104/pdf
        (follows the purple data)

    '''
    raise RuntimeError("Ueda method is depracated.")
    from gp_api.utils import fit_compact_nd
    redshift_train = np.asarray([0.1,0.3,0.5,0.7,0.9,1.1,1.3,1.5,1.8,2.2,2.7,3.3,3.9,4.6])
    sig_redshift_train = np.asarray([0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.2,0.2,0.3,0.3,0.4])
    phi_px = np.asarray([0,220,338,497,590,693,778,861,935,941,1031,826,945,734])
    upper_px = np.asarray([175,285,420,575,669,763,849,932,985,1016,1099,985,1072,953])
    sig_px = upper_px - phi_px
    px_min = 0
    px_max = 1234
    log_phi_min = -9
    log_phi_max = -6
    log_phi_px_scale = (log_phi_max - log_phi_min) / (px_max - px_min)
    log_phi_train = log_phi_min + log_phi_px_scale * phi_px 
    sig_log_phi_train = log_phi_px_scale * sig_px
    ## GP stuff
    x_train = redshift_train.reshape((redshift_train.size,1))
    y_train = phi_px
    y_train_err = sig_px
    gp = fit_compact_nd(x_train, y_train, train_err=y_train_err,order=0)
    phi_gp = gp.mean(redshift) * log_phi_px_scale + log_phi_min
    phi_gp = 10**phi_gp * (u.Mpc**-3)
    if return_train:
        return phi_gp, redshift_train, log_phi_train, sig_log_phi_train

def Ueda_AGND_dphi(
                  redshift,
                  logLx=46,
                  zc2=3.,
                  p2=-1.5,
                  p3=-6.2,
                  logLp=None,
                  alpha2=-0.1,
                  logLa2=44,
                  A=2.91,
                  logLbr=43.97,
                  gamma1=0.96,
                  gamma2=2.71,
                  p1s=4.78,
                  beta1=0.84,
                  zc1=1.86,
                  logLa1=44.61,
                  alpha1=0.29,
                  cosmology="Planck15",
                  ):
    '''The AGN density from Ueda et al. (2014)

    Citation
    --------
        https://iopscience.iop.org/article/10.1088/0004-637X/786/2/104/pdf
        (follows the purple data)

    '''
    raise RuntimeError("Ueda method is depracated.")
    from astropy import cosmology as allcosmo
    cosmo = allcosmo.__getattr__(cosmology)
    # Initialize redshift
    redshift = np.asarray(redshift, dtype=float)
    # Check Lx
    logLx = np.asarray(logLx, dtype=float)
    if logLx.size == 1:
        logLx = np.ones_like(redshift) * logLx
    # Fix logLp
    logLp = logLa2

    ## Luminosity dependence ##
    dphi0 = A * (10**((logLx - logLbr)*gamma1) + 10**((logLx - logLbr)*gamma2))**(-1)
    # luminosity dependence of redshift dependence
    p1 = p1s + (beta1 * (logLx - logLp))
    # Initialize cutoff luminosity arrays
    zc1_arr = np.zeros_like(redshift)
    zc2_arr = np.zeros_like(redshift)
    # Get luminosity masks
    maskL1 = logLx > logLa1
    maskL2 = logLx > logLa2
    # Assign zc1_arr
    zc1_arr[maskL1] = zc1
    zc1_arr[~maskL1] = zc1 * 10**(alpha1 * (logLx[~maskL1] - logLa1))
    # Assign zc2_arr
    zc2_arr[maskL2] = zc2
    zc2_arr[~maskL2] = zc2 * 10**(alpha2 * (logLx[~maskL2] - logLa2))

    
    ## Redshift dependence ##
    # Define redshift masks 0, 1, and 2
    maskz0 = redshift < zc1_arr
    maskz2 = redshift > zc2_arr
    maskz1 = (redshift >= zc1_arr) & (redshift <= zc2_arr)
    # Common sense checks for redshift maskz
    assert redshift.size == np.sum(maskz0) + np.sum(maskz1) + np.sum(maskz2)
    assert np.allclose(maskz1, (~maskz0) & (~maskz2))
    # initialize efunc
    e_zl = np.zeros_like(redshift)
    # Apply maskz 0
    e_zl[maskz0] = (1 + redshift[maskz0])**p1[maskz0]
    # Apply maskz 1
    e_zl[maskz1] = (1 + zc1_arr[maskz1])**p1[maskz1] * ((1 + redshift[maskz1])/(1 + zc1_arr[maskz1]))**p2
    # Apply maskz 2
    e_zl[maskz2] = (1 + zc1_arr[maskz2])**p1[maskz2] * ((1+zc2_arr[maskz2])/(1+zc1_arr[maskz2]))**p2 + ((1+redshift[maskz2])/(1+zc2_arr[maskz2]))**p3

    ## Put it all together ##
    dphi = dphi0 * e_zl
    # Apply units
    dphi = dphi * 10**-6 * (u.Mpc**-3)  #* h
    # Apply cosmology
    h70 = cosmo.H0 / (70 * (u.km/(u.s * u.Mpc)))
    dphi = dphi * h70**3
    return dphi
    
def Ueda_AGND(
              redshift,
              max_redshift=5.,
              logLx=46.,
              dlogLx=2.,
              **kwargs
             ):
    '''The AGN density from Ueda et al. (2014)

    Citation
    --------
        https://iopscience.iop.org/article/10.1088/0004-637X/786/2/104/pdf
        (follows the purple data)

    '''
    raise RuntimeError("Ueda method is depracated.")
    # Get mutable redshift array
    redshift = np.asarray(redshift).copy()
    redshift[redshift > max_redshift] = max_redshift
    # Get dphi
    dphi = Ueda_AGND_dphi(redshift, logLx=logLx, **kwargs)
    # Integrate over your bin
    phi = dphi * 10**dlogLx
    return phi
