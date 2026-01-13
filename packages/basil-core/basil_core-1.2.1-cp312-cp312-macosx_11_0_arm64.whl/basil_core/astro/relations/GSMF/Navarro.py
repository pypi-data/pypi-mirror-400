'''Schechter fits for Navarro-Carrera et al. (2023)'''

######## Imports ########
import numpy as np
from astropy import units as u
from basil_core.astro.relations.GSMF.Fontana import COLE_M0, COLE_alpha0, COLE_phi0
from basil_core.stats import schechter
from scipy.optimize import curve_fit

######## Setup ########
#### Paper data ####
# Redshift
z_edges = np.asarray([3.5, 4.5, 5.5, 6.5, 7.5, 8.5])
z_centers = 0.5*(z_edges[:-1] + z_edges[1:])
dz = z_edges[1] - z_edges[0]

# Number of galaxies
Ngal_navarro = np.asarray([615, 467, 539, 147, 36])
assert Ngal_navarro.size == z_centers.size

# alpha
alpha_navarro = np.asarray([-1.61, -1.69, -1.88, -1.98, -1.93])
sig_alpha_navarro = np.asarray([0.06, 0.07, 0.09, 0.14, 0.22])
assert alpha_navarro.size == Ngal_navarro.size
assert sig_alpha_navarro.size == Ngal_navarro.size

# log_10(M*/M_odot)
M_navarro = np.asarray([10.48,10.45,10.33,10.68,10.7])
sig_M_navarro = np.asarray([0.15, 0.27, 0.36, 0.79])
assert sig_M_navarro.size == Ngal_navarro.size - 1

# Phi*
phi_navarro = np.asarray([1.65e-4,9.6e-5,6.3e-5,1.3e-5,2.8e-6])
sig_phi_navarro = np.asarray([0.04e-4,0.9e-5,1e-5,1e-5,2.1e-6])

######## Functions ########
def phi_z(z, phi0=COLE_phi0, phi1=0.):
    '''phi(z) from Fontana et al. (2006)'''
    return phi0 * (1 + z)**(phi1)

def phi_z_cole(z, phi1):
    return phi_z(z, phi1=phi1)

def fit_phi1(redshift, phi, sigma=None):
    '''Fit phi1 from the Fontana breakdown of the Schechter function

    phi(z) = phi_0 * (1 + z)^phi_1

    phi_0 is known in the local universe (z = 0.)

    phi is known at some redshift values
    sigma may be known
    '''
    popt, pcov = curve_fit(phi_z_cole, redshift, phi, p0=0., sigma=sigma,)
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
NAVARRO_phi1 = fit_phi1(z_centers, phi_navarro, sigma=sig_phi_navarro)
NAVARRO_alpha1 = fit_alpha1(z_centers, alpha_navarro, sigma=sig_alpha_navarro)
NAVARRO_M1, NAVARRO_M2 = fit_M1_M2(z_centers[:-1], M_navarro[:-1], sigma=sig_M_navarro)
#NAVARRO_phi1 = fit_phi1(z_centers, phi_navarro)
#NAVARRO_alpha1 = fit_alpha1(z_centers, alpha_navarro)
#NAVARRO_M1, NAVARRO_M2 = fit_M1_M2(z_centers, M_navarro)

######## Algorithm ########
def Navarro_GSMF(gsm,redshift,gsm_min=1e7 * u.solMass,gsm_max=1e12 *u.solMass):
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
    if redshift > 9.:
        redshift = 9.
    redshift = float(redshift)
    psi = schechter(
                    gsm,
                    redshift,
                    phi0=COLE_phi0,
                    phi1=NAVARRO_phi1,
                    alpha0=COLE_alpha0,
                    alpha1=NAVARRO_alpha1,
                    M0=COLE_M0,
                    M1=NAVARRO_M1,
                    M2=NAVARRO_M2,
                    gsm_min=gsm_min,
                    gsm_max=gsm_max,
                   )
    return psi
