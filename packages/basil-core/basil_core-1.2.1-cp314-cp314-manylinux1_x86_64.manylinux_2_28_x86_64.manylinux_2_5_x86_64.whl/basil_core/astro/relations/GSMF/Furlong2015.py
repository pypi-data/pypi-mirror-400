'''Schechter fits for Furlong et al. (2015)'''

######## Imports ########
import numpy as np
from astropy import units as u
from basil_core.astro.relations.GSMF.Fontana import COLE_M0, COLE_alpha0, COLE_phi0
from basil_core.stats import schechter
from scipy.optimize import curve_fit

######## Setup ########
#### Paper data ####
# Redshift
z_centers = np.asarray([0.1, 0.5, 1., 2., 3., 4.])

# alpha
alpha_furlong = np.asarray([-1.43, -1.45, -1.48, -1.57, -1.66, -1.74])
sig_alpha_furlong = np.asarray([0.01, 0.01, 0.01, 0.01, 0.01, 0.02])
# TODO reconsider uncertainties

# log_10(M*/M_odot)
M_furlong = np.asarray([11.14, 11.11, 11.06, 10.91, 10.78, 10.60])
sig_M_furlong = np.asarray([0.09, 0.08, 0.08, 0.08, 0.11, 0.15])

# Phi*
phi_furlong = np.asarray([0.84, 0.84, 0.74, 0.45, 0.22, 0.12]) * 1e-3
sig_phi_furlong = np.asarray([0.13, 0.12, 0.10, 0.07, 0.05, 0.04]) * 1e-3

######## Functions ########
def phi_z(z, phi0=COLE_phi0, phi1=0.):
    '''phi(z) from Fontana et al. (2006)'''
    return phi0 * (1 + z)**(phi1)

def fit_phi_z(redshift, phi, sigma=None):
    '''Fit phi1 from the Fontana breakdown of the Schechter function

    phi(z) = phi_0 * (1 + z)^phi_1

    phi_0 is known in the local universe (z = 0.)

    phi is known at some redshift values
    sigma may be known
    '''
    popt, pcov = curve_fit(phi_z, redshift, phi, p0=[COLE_phi0,0.], sigma=sigma,)
    phi0, phi1 = float(popt[0]), float(popt[1])
    return phi0, phi1

def alpha_z(z, alpha0=COLE_alpha0, alpha1=0.):
    '''alpha(z) from Fontana et al. (2006)'''
    return alpha0 + alpha1*z

def fit_alpha_z(redshift, alpha, sigma=None):
    '''Fit alpha(z) from Fontana et al.'''
    popt, pcov = curve_fit(alpha_z, redshift, alpha, p0=[COLE_alpha0,0.], sigma=sigma)
    alpha0, alpha1 = float(popt[0]), float(popt[1])
    return alpha0, alpha1

def M_z(redshift, M0=COLE_M0, M1=0., M2=0.):
    '''M(z) from Fontana et al.'''
    return M0 + M1*redshift + M2*redshift**2

def fit_M_z(redshift, logM, sigma=None):
    '''Fit M1 and M2 from Fontana et al.'''
    popt, pcov = curve_fit(M_z, redshift, logM, p0=np.asarray([COLE_M0,0.,0.]), sigma=sigma)
    M0 = float(popt[0])
    M1 = float(popt[1])
    M2 = float(popt[2])
    return M0, M1, M2

######## On Import ########
FURLONG_phi0, FURLONG_phi1 = fit_phi_z(z_centers, phi_furlong, sigma=sig_phi_furlong)
FURLONG_alpha0, FURLONG_alpha1 = fit_alpha_z(z_centers, alpha_furlong, sigma=sig_alpha_furlong)
FURLONG_M0, FURLONG_M1, FURLONG_M2 = fit_M_z(z_centers, M_furlong, sigma=sig_M_furlong)
#FURLONG_phi1 = fit_phi_z(z_centers, phi_furlong)
#FURLONG_alpha1 = fit_alpha_z(z_centers, alpha_furlong)
#FURLONG_M1, FURLONG_M2 = fit_M_z(z_centers, M_furlong)

######## Algorithm ########
def Furlong2015_GSMF(gsm,redshift,gsm_min=1e7 * u.solMass,gsm_max=1e12 *u.solMass):
    '''Galaxy Stellar Mass Function (GSMF)
    
    Citation
    --------
    https://arxiv.org/pdf/2403.08872

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
                    phi0=FURLONG_phi0,
                    phi1=FURLONG_phi1,
                    alpha0=FURLONG_alpha0,
                    alpha1=FURLONG_alpha1,
                    M0=FURLONG_M0,
                    M1=FURLONG_M1,
                    M2=FURLONG_M2,
                    gsm_min=gsm_min,
                    gsm_max=gsm_max,
                   )
    return psi
