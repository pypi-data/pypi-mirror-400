'''Schechter fits for Weibel et al. (2023)'''

######## Imports ########
import numpy as np
from astropy import units as u
from basil_core.astro.relations.GSMF.Fontana import COLE_M0, COLE_alpha0, COLE_phi0
from basil_core.stats import schechter
from scipy.optimize import curve_fit

######## Setup ########
#### Paper data ####
# Redshift
z_centers = np.asarray([4., 5., 6., 7., 8., 9.])

# alpha
alpha_weibel = np.asarray([-1.79, -1.86, -1.95, -1.93, -2.16, -2.])
sig_alpha_weibel = np.asarray([0.01, 0.03, 0.07, 0.04, 0.2])
# TODO reconsider uncertainties

# log_10(M*/M_odot)
M_weibel = np.asarray([11.01,10.26,10.01, 10.,10.,10.])
sig_M_weibel = np.asarray([0.14, 0.14, 0.36])

# Phi*
phi_weibel = np.asarray([-4.52, -4.07, -4.26, -4.36, -4.86, -4.93])
sig_phi_weibel = np.asarray([0.14, 0.14, 0.36, 0.06, 0.21, 0.08])

######## Functions ########
def phi_z(z, phi0=COLE_phi0, phi1=0.):
    '''phi(z) from Fontana et al. (2006)'''
    return phi0 * (1 + z)**(phi1)

def phi_z_cole(z, phi1):
    return phi_z(z, phi1=phi1)
 
def log10_phi_z_cole(z, phi1):
    return np.log10(phi_z_cole(z, phi1))

def fit_phi1(redshift, phi, sigma=None):
    '''Fit phi1 from the Fontana breakdown of the Schechter function

    phi(z) = phi_0 * (1 + z)^phi_1

    phi_0 is known in the local universe (z = 0.)

    phi is known at some redshift values
    sigma may be known
    '''
    popt, pcov = curve_fit(log10_phi_z_cole, redshift, phi, p0=0., sigma=sigma,)
    phi1 = float(popt)
    return phi1

def alpha_z(z, alpha0=COLE_alpha0, alpha1=0.):
    '''alpha(z) from Fontana et al. (2006)'''
    return alpha0 + alpha1*z

def alpha_z_cole(z, alpha1):
    '''alpha(z), but with alpha0 fixed'''
    return alpha_z(z, alpha1=alpha1)

def fit_alpha1(redshift, alpha, sigma=None):
    '''Fit alpha(z) from Fontana et al.'''
    popt, pcov = curve_fit(alpha_z_cole, redshift, alpha, p0=0., sigma=sigma)
    alpha1 = float(popt)
    return alpha1

def M_z(redshift, M0=COLE_M0, M1=0., M2=0.):
    '''M(z) from Fontana et al.'''
    return M0 + M1*redshift + M2*redshift**2

def M_z_cole(z, M1, M2):
    return M_z(z, M1=M1, M2=M2)

def fit_M1_M2(redshift, logM, sigma=None):
    '''Fit M1 and M2 from Fontana et al.'''
    popt, pcov = curve_fit(M_z_cole, redshift, logM, p0=np.asarray([0.,0.]), sigma=sigma)
    M1 = float(popt[0])
    M2 = float(popt[1])
    return M1, M2

######## On Import ########
#WEIBEL_phi1 = fit_phi1(z_centers, phi_weibel, sigma=sig_phi_weibel)
#WEIBEL_alpha1 = fit_alpha1(z_centers[:-1], alpha_weibel[:-1], sigma=sig_alpha_weibel)
#WEIBEL_M1, WEIBEL_M2 = fit_M1_M2(z_centers[:-3], M_weibel[:-3], sigma=sig_M_weibel)
WEIBEL_phi1 = fit_phi1(z_centers, phi_weibel)
WEIBEL_alpha1 = fit_alpha1(z_centers, alpha_weibel)
WEIBEL_M1, WEIBEL_M2 = fit_M1_M2(z_centers, M_weibel)

######## Algorithm ########
def Weibel_GSMF(gsm,redshift,gsm_min=1e7 * u.solMass,gsm_max=1e12 *u.solMass):
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
    if redshift > 6.:
        redshift = 6.
    redshift = float(redshift)
    psi = schechter(
                    gsm,
                    redshift,
                    phi0=COLE_phi0,
                    phi1=WEIBEL_phi1,
                    alpha0=COLE_alpha0,
                    alpha1=WEIBEL_alpha1,
                    M0=COLE_M0,
                    M1=WEIBEL_M1,
                    M2=WEIBEL_M2,
                    gsm_min=gsm_min,
                    gsm_max=gsm_max,
                   )
    return psi
