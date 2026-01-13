from __future__ import division
import numbers
import numpy as np
from ._coordinates import _mc_of_m1_m2, _eta_of_m1_m2
from ._coordinates import _M_of_mc_eta
from ._coordinates import _m1_of_M_eta, _m2_of_M_eta
from ._coordinates import _detector_of_source, _source_of_detector
from ._spin import _chieff_of_m1_m2_chi1z_chi2z
from ._spin import _chiMinus_of_m1_m2_chi1z_chi2z
from ._spin import _chi1z_of_m1_m2_chieff_chiMinus
from ._spin import _chi2z_of_m1_m2_chieff_chiMinus
from ._tides import _lambda_tilde_of_eta_lambda1_lambda2
from ._tides import _delta_lambda_of_eta_lambda1_lambda2
from ._tides import _lambda1_of_eta_lambda_tilde_delta_lambda
from ._tides import _lambda2_of_eta_lambda_tilde_delta_lambda

__all__ = [
           "mc_of_m1_m2",
           "eta_of_m1_m2",
           "mc_eta_of_m1_m2",
           "M_of_mc_eta",
           "m1_of_M_eta",
           "m2_of_M_eta",
           "m1_m2_of_M_eta",
           "m1_of_mc_eta",
           "m2_of_mc_eta",
           "m1_m2_of_mc_eta",
           "q_of_mc_eta",
           "detector_of_source",
           "source_of_detector",
           "chieff_of_m1_m2_chi1z_chi2z",
           "chiMinus_of_m1_m2_chi1z_chi2z",
           "chieff_chiMinus_of_m1_m2_chi1z_chi2z",
           "chi1z_of_m1_m2_chieff_chiMinus",
           "chi2z_of_m1_m2_chieff_chiMinus",
           "chi1z_chi2z_of_m1_m2_chieff_chiMinus",
           "lambda_tilde_of_eta_lambda1_lambda2",
           "delta_lambda_of_eta_lambda1_lambda2",
           "lambda_tilde_delta_lambda_of_eta_lambda1_lambda2",
           "lambda1_of_eta_lambda_tilde_delta_lambda",
           "lambda2_of_eta_lambda_tilde_delta_lambda",
           "lambda1_lambda2_of_eta_lambda_tilde_delta_lambda",
          ]

def mc_of_m1_m2(m1, m2):
    """Compute the chirp mass given m1 and m2

    Parameters
    ----------
    m1 : `~numpy.ndarray`
        The first component mass
    m2 : `~numpy.ndarray`
        The second component mass

    Returns
    -------
    mc : `~numpy.ndarray`
        The chirp mass values
    """
    return _mc_of_m1_m2(m1, m2)

def eta_of_m1_m2(m1, m2):
    """Compute the symmetric mass ratio given m1 and m2

    Parameters
    ----------
    m1 : `~numpy.ndarray`
        The first component mass
    m2 : `~numpy.ndarray`
        The second component mass

    Returns
    -------
    eta : `~numpy.ndarray`
        The symmetric mass ratio values
    """
    return _eta_of_m1_m2(m1, m2)

def mc_eta_of_m1_m2(m1, m2):
    """Compute both the chirp mass and symmetric mass ratio of m1 and m2

    Parameters
    ----------
    m1 : `~numpy.ndarray`
        The first component mass
    m2 : `~numpy.ndarray`
        The second component mass

    Returns
    -------
    mc : `~numpy.ndarray`
        The chirp mass values
    eta : `~numpy.ndarray`
        The symmetric mass ratio values
    """
    return _mc_of_m1_m2(m1, m2), _eta_of_m1_m2(m1, m2)

def M_of_mc_eta(mc, eta):
    """ Compute total mass of mc and eta

    Parameters
    ----------
    mc : `~numpy.ndarray`
        The chirp mass values
    eta : `~numpy.ndarray`
        The symmetric mass ratio values

    Returns
    -------
    M : `~numpy.ndarray`
        The total mass
    """
    return _M_of_mc_eta(mc, eta)

def m1_of_M_eta(M, eta):
    """Compute m1 of total mass and eta

    Parameters
    ----------
    M : `~numpy.ndarray`
        The total mass
    eta : `~numpy.ndarray`
        The symmetric mass ratio values

    Returns
    -------
    m1 : `~numpy.ndarray`
        The first component mass
    """
    return _m1_of_M_eta(M, eta)

def m2_of_M_eta(M, eta):
    """Compute m2 of total mass and eta

    Parameters
    ----------
    M : `~numpy.ndarray`
        The total mass
    eta : `~numpy.ndarray`
        The symmetric mass ratio values

    Returns
    -------
    m2 : `~numpy.ndarray`
        The second component mass
    """
    return _m2_of_M_eta(M, eta)

def m1_m2_of_M_eta(M, eta):
    """Compute both m1 and m2 from total mass and eta

    Parameters
    ----------
    M : `~numpy.ndarray`
        The total mass
    eta : `~numpy.ndarray`
        The symmetric mass ratio values

    Returns
    -------
    m1 : `~numpy.ndarray`
        The first component mass
    m2 : `~numpy.ndarray`
        The second component mass
    """
    return _m1_of_M_eta(M, eta), _m2_of_M_eta(M, eta)

def m1_of_mc_eta(mc, eta):
    """Compute m1 from mc and eta

    Parameters
    ----------
    mc : `~numpy.ndarray`
        The chirp mass values
    eta : `~numpy.ndarray`
        The symmetric mass ratio values

    Returns
    -------
    m1 : `~numpy.ndarray`
        The first component mass
    """
    M = M_of_mc_eta(mc ,eta)
    return _m1_of_M_eta(M, eta)

def m2_of_mc_eta(mc, eta):
    """Compute m2 from mc and eta

    Parameters
    ----------
    mc : `~numpy.ndarray`
        The chirp mass values
    eta : `~numpy.ndarray`
        The symmetric mass ratio values

    Returns
    -------
    m2 : `~numpy.ndarray`
        The second component mass
    """
    M = M_of_mc_eta(mc ,eta)
    return _m2_of_M_eta(M, eta)

def m1_m2_of_mc_eta(mc, eta):
    """Compute m1 and m2 from mc and eta

    Parameters
    ----------
    mc : `~numpy.ndarray`
        The chirp mass values
    eta : `~numpy.ndarray`
        The symmetric mass ratio values

    Returns
    -------
    m1 : `~numpy.ndarray`
        The first component mass
    m2 : `~numpy.ndarray`
        The second component mass
    """
    M = M_of_mc_eta(mc ,eta)
    return _m1_of_M_eta(M, eta), _m2_of_M_eta(M, eta)

def q_of_mc_eta(mc, eta):
    """Compute the mass ratio from mc and eta

    Parameters
    ----------
    mc : `~numpy.ndarray`
        The chirp mass values
    eta : `~numpy.ndarray`
        The symmetric mass ratio values

    Returns
    -------
    q : `~numpy.ndarray`
        The mass ratio
    """
    M = M_of_mc_eta(mc ,eta)
    return _m2_of_M_eta(M, eta)/ _m1_of_M_eta(M, eta)

def detector_of_source(msrc, z):
    """Compute the detector frame mass from source and redshift

    Parameters
    ----------
    msrc    : `~numpy.ndarray`
        The source mass
    z       : `~numpy.ndarray`
        The redshift

    Returns
    -------
    mdet    : `~numpy.ndarray`
        The detector frame mass
    """
    if (type(z) == np.ndarray) and (z.size != 1):
        return _detector_of_source(msrc, z)
    else:
        return msrc * (1. + z)

def source_of_detector(mdet, z):
    """Compute the source frame mass from detector and redshift

    Parameters
    ----------
    mdet    : `~numpy.ndarray`
        The detector frame mass
    z       : `~numpy.ndarray`
        The redshift

    Returns
    -------
    msrc    : `~numpy.ndarray`
        The source frame mass
    """
    if (type(z) == np.ndarray) and (z.size != 1):
        return _source_of_detector(mdet, z)
    else:
        return mdet / (1. + z)

def chieff_of_m1_m2_chi1z_chi2z(m1, m2, chi1z, chi2z):
    """Compute chi effective given m1, m2, chi1z, chi2z

    Parameters
    ----------
    m1      : `~numpy.ndarray`
        The first component mass
    m2      : `~numpy.ndarray`
        The second component mass
    chi1z   : `~numpy.ndarray`
        The aligned spin of the primary
    chi2z   : `~numpy.ndarray`
        The aligned spin of the secondary

    Returns
    -------
    chieff : `~numpy.ndarray`
        The effective spin aligned with the plane of the orbit
    """
    return _chieff_of_m1_m2_chi1z_chi2z(m1, m2, chi1z, chi2z)

def chiMinus_of_m1_m2_chi1z_chi2z(m1, m2, chi1z, chi2z):
    """Compute chiMinus given m1, m2, chi1z, chi2z

    Parameters
    ----------
    m1      : `~numpy.ndarray`
        The first component mass
    m2      : `~numpy.ndarray`
        The second component mass
    chi1z   : `~numpy.ndarray`
        The aligned spin of the primary
    chi2z   : `~numpy.ndarray`
        The aligned spin of the secondary

    Returns
    -------
    chiMinus : `~numpy.ndarray`
        The chiMinus component of spin
    """
    return _chiMinus_of_m1_m2_chi1z_chi2z(m1, m2, chi1z, chi2z)

def chieff_chiMinus_of_m1_m2_chi1z_chi2z(m1, m2, chi1z, chi2z):
    """Compute chi effective and chiMinus given m1, m2, chi1z, chi2z

    Parameters
    ----------
    m1      : `~numpy.ndarray`
        The first component mass
    m2      : `~numpy.ndarray`
        The second component mass
    chi1z   : `~numpy.ndarray`
        The aligned spin of the primary
    chi2z   : `~numpy.ndarray`
        The aligned spin of the secondary

    Returns
    -------
    chieff : `~numpy.ndarray`
        The effective spin aligned with the plane of the orbit
    chiMinus : `~numpy.ndarray`
        The chiMinus component of spin
    """
    return _chieff_of_m1_m2_chi1z_chi2z(m1, m2, chi1z, chi2z), _chiMinus_of_m1_m2_chi1z_chi2z(m1, m2, chi1z, chi2z)

def chi1z_of_m1_m2_chieff_chiMinus(m1, m2, chieff, chiMinus):
    """Compute chi1z given m1, m2, chieff, chiMinus

    Parameters
    ----------
    m1      : `~numpy.ndarray`
        The first component mass
    m2      : `~numpy.ndarray`
        The second component mass
    chieff : `~numpy.ndarray`
        The effective spin aligned with the plane of the orbit
    chiMinus : `~numpy.ndarray`
        The chiMinus component of spin

    Returns
    -------
    chi1z   : `~numpy.ndarray`
        The aligned spin of the primary
    """
    return _chi1z_of_m1_m2_chieff_chiMinus(m1,m2,chieff,chiMinus)

def chi2z_of_m1_m2_chieff_chiMinus(m1, m2, chieff, chiMinus):
    """Compute chi2z given m1, m2, chieff, chiMinus

    Parameters
    ----------
    m1      : `~numpy.ndarray`
        The first component mass
    m2      : `~numpy.ndarray`
        The second component mass
    chieff : `~numpy.ndarray`
        The effective spin aligned with the plane of the orbit
    chiMinus : `~numpy.ndarray`
        The chiMinus component of spin

    Returns
    -------
    chi2z   : `~numpy.ndarray`
        The aligned spin of the secondary
    """
    return _chi2z_of_m1_m2_chieff_chiMinus(m1,m2,chieff,chiMinus)

def chi1z_chi2z_of_m1_m2_chieff_chiMinus(m1, m2, chieff, chiMinus):
    """Compute chi1z and chi2z given m1, m2, chieff, chiMinus

    Parameters
    ----------
    m1      : `~numpy.ndarray`
        The first component mass
    m2      : `~numpy.ndarray`
        The second component mass
    chieff : `~numpy.ndarray`
        The effective spin aligned with the plane of the orbit
    chiMinus : `~numpy.ndarray`
        The chiMinus component of spin

    Returns
    -------
    chi1z   : `~numpy.ndarray`
        The aligned spin of the primary
    chi2z   : `~numpy.ndarray`
        The aligned spin of the secondary
    """
    return _chi1z_of_m1_m2_chieff_chiMinus(m1,m2,chieff,chiMinus), _chi2z_of_m1_m2_chieff_chiMinus(m1,m2,chieff,chiMinus)

def lambda_tilde_of_eta_lambda1_lambda2(eta, lambda1, lambda2):
    """ Get lambda tilde from eta, lambda1, lambda2
    follows Les Wade's paper
    Lambda1 is assumed to be the more massive star

    Parameters
    ----------
    eta     : `~numpy.ndarray`
        The symmetric mass ratio
    lambda1 : `~numpy.ndarray`
        The tidal deformability of the primary star
    lambda2 : `~numpy.ndarray`
        The tidal deformability of the secondary star
   
    Returns
    -------
    lambda_tilde    : `~numpy.ndarray`
        The lambda tilde quantity of tidal deformability
    """
    return _lambda_tilde_of_eta_lambda1_lambda2(eta, lambda1, lambda2)

def delta_lambda_of_eta_lambda1_lambda2(eta, lambda1, lambda2):
    """ Get delta lambda tilde from eta, lambda1, lambda2
    follows Les Wade's paper
    Lambda1 is assumed to be the more massive star

    Parameters
    ----------
    eta     : `~numpy.ndarray`
        The symmetric mass ratio
    lambda1 : `~numpy.ndarray`
        The tidal deformability of the primary star
    lambda2 : `~numpy.ndarray`
        The tidal deformability of the secondary star
   
    Returns
    -------
    delta_lambda    : `~numpy.ndarray`
        The delta lambda tilde quantity of tidal deformability
    """
    return _delta_lambda_of_eta_lambda1_lambda2(eta, lambda1, lambda2)

def lambda_tilde_delta_lambda_of_eta_lambda1_lambda2(eta, lambda1, lambda2):
    """ Get lambda tilde and delta lambda tilde from eta, lambda1, lambda2
    follows Les Wade's paper
    Lambda1 is assumed to be the more massive star

    Parameters
    ----------
    eta     : `~numpy.ndarray`
        The symmetric mass ratio
    lambda1 : `~numpy.ndarray`
        The tidal deformability of the primary star
    lambda2 : `~numpy.ndarray`
        The tidal deformability of the secondary star
   
    Returns
    -------
    lambda_tilde    : `~numpy.ndarray`
        The lambda tilde quantity of tidal deformability
    delta_lambda    : `~numpy.ndarray`
        The delta lambda tilde quantity of tidal deformability
    """
    return _lambda_tilde_of_eta_lambda1_lambda2(eta, lambda1, lambda2), _delta_lambda_of_eta_lambda1_lambda2(eta, lambda1, lambda2)

def lambda1_of_eta_lambda_tilde_delta_lambda(eta, lambda_tilde, delta_lambda):
    """ Get lambda1 from eta, lambda tilde, and delta lambda tilde
    follows Les Wade's paper
    Lambda1 is assumed to be the more massive star

    Parameters
    ----------
    eta     : `~numpy.ndarray`
        The symmetric mass ratio
    lambda_tilde    : `~numpy.ndarray`
        The lambda tilde quantity of tidal deformability
    delta_lambda    : `~numpy.ndarray`
        The delta lambda tilde quantity of tidal deformability
   
    Returns
    -------
    lambda1 : `~numpy.ndarray`
        The tidal deformability of the primary star
    """
    return _lambda1_of_eta_lambda_tilde_delta_lambda(eta, lambda_tilde, delta_lambda)

def lambda2_of_eta_lambda_tilde_delta_lambda(eta, lambda_tilde, delta_lambda):
    """ Get lambda 2 from eta, lambda tilde, and delta lambda tilde
    follows Les Wade's paper
    Lambda1 is assumed to be the more massive star

    Parameters
    ----------
    eta     : `~numpy.ndarray`
        The symmetric mass ratio
    lambda_tilde    : `~numpy.ndarray`
        The lambda tilde quantity of tidal deformability
    delta_lambda    : `~numpy.ndarray`
        The delta lambda tilde quantity of tidal deformability
   
    Returns
    -------
    lambda1 : `~numpy.ndarray`
        The tidal deformability of the primary star
    lambda2 : `~numpy.ndarray`
        The tidal deformability of the secondary star
    """
    return _lambda2_of_eta_lambda_tilde_delta_lambda(eta, lambda_tilde, delta_lambda)

def lambda1_lambda2_of_eta_lambda_tilde_delta_lambda(eta, lambda_tilde, delta_lambda):
    """ Get lambda1 and lambda 2 from eta, lambda tilde, and delta lambda tilde
    follows Les Wade's paper
    Lambda1 is assumed to be the more massive star

    Parameters
    ----------
    eta     : `~numpy.ndarray`
        The symmetric mass ratio
    lambda_tilde    : `~numpy.ndarray`
        The lambda tilde quantity of tidal deformability
    delta_lambda    : `~numpy.ndarray`
        The delta lambda tilde quantity of tidal deformability
   
    Returns
    -------
    lambda1 : `~numpy.ndarray`
        The tidal deformability of the primary star
    lambda2 : `~numpy.ndarray`
        The tidal deformability of the secondary star
    """
    return _lambda1_of_eta_lambda_tilde_delta_lambda(eta, lambda_tilde, delta_lambda), _lambda2_of_eta_lambda_tilde_delta_lambda(eta, lambda_tilde, delta_lambda)
