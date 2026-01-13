"""Methods for orbital decay of binary sources

"""
######## Setup ########
__all__ = [
    "BETA_CONST",
    "beta_fn",
    "beta_fn_numpy",
    "peters_ecc_const",
    "peters_ecc_const_numpy",
    "peters_ecc_integrand",
    "peters_ecc_integrand_numpy",
    "orbital_period_of_m1_m2_a",
    "orbital_period_numpy",
    "merge_time_circ",
    "inv_merge_time_circ",
    "merge_time_circ_numpy",
    "merge_time_integral_sgl",
    "merge_time_integral_arr",
    "merge_time_integral",
    "a_of_m1_m2_forb",
    "forb_of_m1_m2_a",
    "ecc_of_a0_e0_a1",
    "a_of_ecc",
    "schwarzschild_separation",
    "merge_time_mandel",
    "merge_time_peters_low_e",
    "merge_time_peters_high_e",
    "merge_time_peters_enh",
    "merge_time",
    "circular_ODE_integration",
    "eccentric_ODE_integration",
    "decay_time",
    "orbital_separation_evolve_circ_numpy",
    "orbital_separation_evolve_circ",
    "orbital_separation_evolve",
    "MERGE_TIME_METHODS",
    "orbital_period_evolve",
]

######## Imports ########
#### Standard Library ####
import time
import warnings
#### Third Party ####
import numpy as np
from scipy.integrate import solve_ivp, quad
from scipy.optimize import minimize
from scipy.integrate._ivp.ivp import METHODS as IVP_METHODS
from astropy import units as u
from astropy import constants as const
#### Homemade ####
#### Local ####

######## Beta #########
BETA_CONST = (64/5) * (const.G**3) * const.c**-5

def beta_fn_numpy(m1, m2, unit=False):
    """Return Beta values for given parameters using only NumPy

    Parameters
    ----------
    m1 : array_like
        Primary mass (without astropy units, assumes kg)
    m2 : array_like
        Secondary mass (without astropy units, assumes kg)
    unit : bool
        Flag for returning units
    
    Returns
    _______
    beta : array_like
        beta constant from Peters' 1964

    Assume kg for legacy reasons
    """
    ## Check units
    if hasattr(m1, "unit"):
        # Check for kg
        if m1.unit == u.kg:
            m1 = m1.value
            unit = True
        elif m1.unit.is_equivalent(u.kg):
            m1 = m1.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m1 should have units kg, but has units {m1.unit}")
    ## Check units
    if hasattr(m2, "unit"):
        # Check for kg
        if m2.unit == u.kg:
            m2 = m2.value
            unit = True
        elif m2.unit.is_equivalent(u.kg):
            m2 = m2.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m2 should have units kg, but has units {m2.unit}")
    value = BETA_CONST.value * m1 * m2 * (m1 + m2)
    if unit:
        return value * BETA_CONST.unit * (u.kg)**3
    else:
        return value

def beta_fn(m1, m2, unit=False, fallback=True):
    '''Calculate the beta constant from page 8 of Peters (1964)

    Parameters
    ----------
    m1 : array_like
        Primary mass (without astropy units, assumes kg)
    m2 : array_like
        Secondary mass (without astropy units, assumes kg)
    unit : bool
        Flag for returning units
    fallback : bool
        Flag for allowing C extension to fail and defaulting to NumPy
    
    Returns
    _______
    beta : array_like
        beta constant from Peters' 1964
    '''

    #### Check inputs ####
    ## Check units
    if hasattr(m1, "unit"):
        # Check for kg
        if m1.unit == u.kg:
            m1 = m1.value
            unit = True
        elif m1.unit.is_equivalent(u.kg):
            m1 = m1.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m1 should have units kg, but has units {m1.unit}")
    if hasattr(m2, "unit"):
        # Check for kg
        if m2.unit == u.kg:
            m2 = m2.value
            unit = True
        elif m2.unit.is_equivalent(u.kg):
            m2 = m2.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m2 should have units kg, but has units {m2.unit}")
    # Check units
    if not unit:
        warnings.warn("beta: assuming beta function inputs are SI units")
    
    # Attempt to load C extensions
    try:
        from basil_core.astro.orbit._decay import _beta_arr, _beta_sgl
    except Exception as exc:
        warnings.warn("beta: C extensions not importing. Defaulting to NumPy")
        if fallback:
            return beta_fn_numpy(m1*u.kg,m2*u.kg)
        else:
            raise exc

    # Single value
    if (isinstance(m1, float) or isinstance(m1, np.float64)) and \
       (isinstance(m2, float) or isinstance(m2, np.float64)):
        if unit:
            return _beta_sgl(m1,m2) * (u.m**4 / u.s)
        else:
            return _beta_sgl(m1,m2)
    ## Check m1 ##
    if not isinstance(m1, np.ndarray):
        raise TypeError("m1 should be a numpy array, but is ", type(m1))
    if len(m1.shape) != 1:
        raise RuntimeError("m1 should be 1D array, but is ", m1.shape)
    ## Check m2 ##
    if not isinstance(m2, np.ndarray):
        raise TypeError("m2 should be a numpy array, but is ", type(m2))
    if len(m2.shape) != 1:
        raise RuntimeError("m2 should be 1D array, but is ", m2.shape)
    ## Check dimensions ##
    if not (m1.size == m2.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, m2.size = %d"%(
            m1.size, m2.size))
    if unit:
        return _beta_arr(m1, m2) * (u.m**4 / u.s)
    else:
        return _beta_arr(m1, m2)

######## Peters integration constant ########
def peters_ecc_const_numpy(ecc):
    """Calculate the eccentricity part of the constant of motion in Peters (1964)

    Parameters
    ----------
    ecc : np.ndarray
        Array of eccentricity values

    Returns
    -------
    const : np.ndarray
        Array of the eccentricity component of the constant of motion

    Using a numpy implementation
    """
    return (1 - ecc**2) / (ecc**(12/19) * (1 + (121/304)*ecc**2)**(870/2299))

def peters_ecc_const(ecc,fallback=True):
    '''Calculate the eccentricity part of the constant of motion in Peters (1964)

    Parameters
    ----------
    ecc : `~numpy.ndarray` (npts,)
        Eccentricity
    fallback : bool
        Flag for defaulting to NumPy if C extension fails

    Returns
    -------
    ecc_const : `~numpy.ndarray`
        The value of the eccentricity part of the constant of motion
    '''
    # Try to import the C extensions
    try:
        from basil_core.astro.orbit._decay import _peters_ecc_const_sgl
        from basil_core.astro.orbit._decay import _peters_ecc_const_arr
    except Exception as exc:
        # Fail and return the numpy expression
        warnings.warn("peters_ecc_const: C extensions not importing. Defaulting to NumPy")
        if fallback:
            return peters_ecc_const_numpy(ecc)
        else:
            raise exc
    #### Check inputs ####
    if (isinstance(ecc, float) or isinstance(ecc, np.float64)):
        return _peters_ecc_const_sgl(ecc)
    ## Check ecc ##
    if not isinstance(ecc, np.ndarray):
        raise TypeError("ecc should be a numpy array, but is ", type(ecc))
    if len(ecc.shape) != 1:
        raise RuntimeError("ecc should be 1D array, but is ", ecc.shape)
    ## Check dimensions ##
    return _peters_ecc_const_arr(ecc)

def peters_ecc_integrand_numpy(ecc):
    """Calculate the eccentricity orbital decay integrand

    Parameters
    ----------
    ecc : array_like
        Orbital eccentricities

    Returns
    -------
    integrand : array_like
        Integrand for eccentricity evolution of a binary
    """
    return (ecc**(29/19) * (1 + (121/304)*ecc**2)**(1181/2299)) * (1 - ecc**2)**(-3/2)

def peters_ecc_integrand(ecc, fallback=True):
    '''Calculate the eccentricity part of the constant of motion in Peters (1964)

    Parameters
    ----------
    ecc : `~numpy.ndarray` (npts,)
        Eccentricity
    fallback : bool
        Flag for defaulting to NumPy if C extension fails

    Returns
    -------
    ecc_integrand : `~numpy.ndarray`
        The value of the eccentricity part of the constant of motion
    '''
    # Try to import C extension
    try:
        from basil_core.astro.orbit._decay import _peters_ecc_integrand_sgl
        from basil_core.astro.orbit._decay import _peters_ecc_integrand_arr
    except Exception as exc:
        warnings.warn("peters_ecc_integrand: C extension not importing. Defaulting to NumPy")
        if fallback:
            return peters_ecc_integrand_numpy(ecc)
        else:
            raise exc
    #### Check inputs ####
    if (isinstance(ecc, float) or isinstance(ecc, np.float64)):
        return _peters_ecc_integrand_sgl(ecc)
    elif isinstance(ecc, int):
        return _peters_ecc_integrand_sgl(float(ecc))
    elif (np.size(ecc) >= 1) and isinstance(ecc, np.ndarray):
        if isinstance(ecc.dtype, np.float64):
            return _peters_ecc_integrand_arr(ecc)
        else:
            return _peters_ecc_integrand_arr(ecc.astype(float))
    else:
        raise TypeError("Unknown type for ecc: {ecc.type}")

######## Kepler's law! ########
def orbital_period_numpy(m1, m2, a):
    """Kepler's equation for orbital period

    Parameters
    ----------
    m1 : array_like
        Primary mass (without astropy units, assumes kg)
    m2 : array_like
        Secondary mass (without astropy units, assumes kg)
    a : array_like
        Semi-major axis (without astropy units, assumes meters)

    Returns
    -------
    orbital period : astropy quantity
        Orbital period
    """
    if hasattr(m1, "unit"):
        if not m1.unit.is_equivalent(u.kg):
            raise ValueError(
                f"m1 should have units kg, but has units {m1.unit}")
    else:
        m1 = m1 * u.kg
    if hasattr(m2, "unit"):
        if not m2.unit.is_equivalent(u.kg):
            raise ValueError(
                f"m2 should have units kg, but has units {m2.unit}")
    else:
        m2 = m2 * u.kg
    if hasattr(a, "unit"):
        if not a.unit.is_equivalent(u.m):
            raise ValueError(
                f"a should have units m, but has units {a.unit}")
    else:
        a = a * u.m
    return np.sqrt(4 * np.pi**2 * a**3 / (const.G * (m1 + m2)))

def orbital_period_of_m1_m2_a(m1, m2, a, unit=False, fallback=True):
    '''Calculate orbital period using Kepler's equations

    Paramters
    ---------
    m1 : `~numpy.ndarray` (npts,)
        First set of masses (Kg)
    m2 : `~numpy.ndarray` (npts,)
        Second set of masses (Kg)
    a : `~numpy.ndarray` (npts,)
        Orbital separation (meters)
    unit : bool
        Flag for returning units
    fallback : bool
        Flag for using NumPy if C extension fails

    Returns
    -------
    P : `~numpy.ndarray` (npts,)
        Orbital period (seconds)
    '''
    # Try to import C extensions
    try:
        from basil_core.astro.orbit._kepler import _orbital_period_of_m1_m2_a_sgl
        from basil_core.astro.orbit._kepler import _orbital_period_of_m1_m2_a_arr
    except Exception as exc:
        warnings.warn("orbital_period (Kepler): Failed to import C extension."
            "Defaulting to NumPy")
        if fallback:
            return orbital_period_numpy(m1, m2, a)
        else: 
            raise exc
    #### Check inputs ####
    ## Check units
    if hasattr(m1, "unit"):
        # Check for kg
        if m1.unit == u.kg:
            m1 = m1.value
            unit = True
        elif m1.unit.is_equivalent(u.kg):
            m1 = m1.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m1 should have units kg, but has units {m1.unit}")
    ## Check units
    if hasattr(m2, "unit"):
        # Check for kg
        if m2.unit == u.kg:
            m2 = m2.value
            unit = True
        elif m2.unit.is_equivalent(u.kg):
            m2 = m2.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m2 should have units kg, but has units {m2.unit}")
    ## Check units
    if hasattr(a, "unit"):
        # Check for m
        if a.unit == u.m:
            a = a.value
            unit = True
        elif a.unit.is_equivalent(u.m):
            a = a.to(u.m).value
            unit = True
        else:
            raise ValueError(
                f"a should have units m, but has units {a.unit}")
    # Check for single
    if (isinstance(m1, float) or isinstance(m1, np.float64)) and \
       (isinstance(m2, float) or isinstance(m2, np.float64)) and \
       (isinstance(a,  float) or isinstance(a,  np.float64)):
        if unit:
            return _orbital_period_of_m1_m2_a_sgl(m1,m2,a) * u.s
        else:
            return _orbital_period_of_m1_m2_a_sgl(m1,m2,a)
    ## Check m1 ##
    if not isinstance(m1, np.ndarray):
        raise TypeError("m1 should be a numpy array, but is ", type(m1))
    if len(m1.shape) != 1:
        raise RuntimeError("m1 should be 1D array, but is ", m1.shape)
    ## Check m2 ##
    if not isinstance(m2, np.ndarray):
        raise TypeError("m2 should be a numpy array, but is ", type(m2))
    if len(m2.shape) != 1:
        raise RuntimeError("m2 should be 1D array, but is ", m2.shape)
    ## Check a ##
    if not isinstance(a, np.ndarray):
        raise TypeError("a should be a numpy array, but is ", type(a))
    if len(a.shape) != 1:
        raise RuntimeError("a should be 1D array, but is ", a.shape)
    ## Check dimensions ##
    if not (m1.size == m2.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, m2.size = %d"%(
            m1.size, m2.size))
    if not (m1.size == a.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, a.size = %d"%(
            m1.size, a.size))
    # Check if to return units
    if unit:
        return _orbital_period_of_m1_m2_a_arr(m1, m2, a) * u.s
    else:
        return _orbital_period_of_m1_m2_a_arr(m1, m2, a)

######## BBH Contact ########
def schwarzschild_separation(m1,m2):
    """Return the sum of two Schwarzschild radii

    Parameters
    ----------
    m1 : `~numpy.ndarray` (npts,)
        First set of masses (Kg)
    m2 : `~numpy.ndarray` (npts,)
        Second set of masses (Kg)

    Returns
    -------
    sep : astropy.units.Quantity
        Schwarzschild distance
    """
    if hasattr(m1, "unit"):
        if not m1.unit.is_equivalent(u.kg):
            raise ValueError(
                f"m1 should have units kg, but has units {m1.unit}")
    else:
        m1 = m1 * u.kg
    if hasattr(m2, "unit"):
        if not m2.unit.is_equivalent(u.kg):
            raise ValueError(
                f"m2 should have units kg, but has units {m2.unit}")
    else:
        m2 = m2 * u.kg
    return (2*const.G/(const.c**2)) * (m1 + m2)

######## merge_time_circ ########
def merge_time_circ_numpy(m1, m2, a, unit=False):
    """Time to merger for a circular binary at a given initial separation
    
    Parameters
    ----------
    m1 : array_like
        Primary mass (without astropy units, assumes kg)
    m2 : array_like
        Secondary mass (without astropy units, assumes kg)
    a : array_like
        Semi-major axis (without astropy units, assumes meters)
    unit : bool
        Flag for returning quantity with units

    Returns
    -------
    t : array_like
        Time to merger
    """
    ## Check units
    if hasattr(m1, "unit"):
        # Check for kg
        if m1.unit == u.kg:
            m1 = m1.value
            unit = True
        elif m1.unit.is_equivalent(u.kg):
            m1 = m1.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m1 should have units kg, but has units {m1.unit}")
    ## Check units
    if hasattr(m2, "unit"):
        # Check for kg
        if m2.unit == u.kg:
            m2 = m2.value
            unit = True
        elif m2.unit.is_equivalent(u.kg):
            m2 = m2.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m2 should have units kg, but has units {m2.unit}")
    ## Check units
    if hasattr(a, "unit"):
        # Check for m
        if a.unit == u.m:
            a = a.value
            unit = True
        elif a.unit.is_equivalent(u.m):
            a = a.to(u.m).value
            unit = True
        else:
            raise ValueError(
                f"a should have units m, but has units {a.unit}")
    # Get value
    value = a**4 / (4 * beta_fn_numpy(m1,m2))
    # Check unit
    if unit:
        return value * u.s
    else:
        return value

def inv_merge_time_circ(m1, m2, T):
    """Inverse merger time for circular binary (calculates initial sep)

    Parameters
    ----------
    m1 : array_like
        Primary mass (without astropy units, assumes kg)
    m2 : array_like
        Secondary mass (without astropy units, assumes kg)
    t : array_like
        Time to merger

    Returns
    -------
    a : array_like
        Semi-major axis (without astropy units, assumes meters)
    """
    if hasattr(m1, "unit"):
        if not m1.unit.is_equivalent(u.kg):
            raise ValueError(
                f"m1 should have units kg, but has units {m1.unit}")
    else:
        m1 = m1 * u.kg
    if hasattr(m2, "unit"):
        if not m2.unit.is_equivalent(u.kg):
            raise ValueError(
                f"m2 should have units kg, but has units {m2.unit}")
    else:
        m2 = m2 * u.kg
    if hasattr(T, "unit"):
        if not T.unit.is_equivalent(u.s):
            raise ValueError(
                f"a should have units s, but has units {T.unit}")
    else:
        T = T * u.s
    return np.power(4 * T * beta_fn(m1,m2),1/4)

def merge_time_circ(m1, m2, a, unit=False, fallback=True):
    """Calculate the time for a binary to merge in a circular orbit due to GW

    Parameters
    ----------
    m1 : array_like
        Primary mass (without astropy units, assumes kg)
    m2 : array_like
        Secondary mass (without astropy units, assumes kg)
    a : array_like
        Semi-major axis (without astropy units, assumes meters)
    unit : bool
        Flag for returning quantity with units
    fallback : bool
        Flag for defaulting to NumPy if C extension fails

    Returns
    -------
    t : array_like
        Time to merger
    """
    # Try to import C extension
    try:
        from basil_core.astro.orbit._decay import _merge_time_circ_sgl
        from basil_core.astro.orbit._decay import _merge_time_circ_arr
    except Exception as exc :
        warnings.warn("merge_time_circ: Failed to import C extension."
            "Defaulting to NumPy")
        if fallback:
            return merge_time_circ_numpy(m1,m2,a)
        else:
            raise exc
    ## Check units
    if hasattr(m1, "unit"):
        # Check for kg
        if m1.unit == u.kg:
            m1 = m1.value
            unit = True
        elif m1.unit.is_equivalent(u.kg):
            m1 = m1.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m1 should have units kg, but has units {m1.unit}")
    ## Check units
    if hasattr(m2, "unit"):
        # Check for kg
        if m2.unit == u.kg:
            m2 = m2.value
            unit = True
        elif m2.unit.is_equivalent(u.kg):
            m2 = m2.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m2 should have units kg, but has units {m2.unit}")
    ## Check units
    if hasattr(a, "unit"):
        # Check for m
        if a.unit == u.m:
            a = a.value
            unit = True
        elif a.unit.is_equivalent(u.m):
            a = a.to(u.m).value
            unit = True
        else:
            raise ValueError(
                f"a should have units m, but has units {a.unit}")

    # Check for single
    if (np.size(m1) == 1) and (np.size(m2) == 1) and (np.size(a) == 1):
        if unit:
            return _merge_time_circ_sgl(m1,m2,a) * u.s
        else:
            return _merge_time_circ_sgl(m1,m2,a)
    ## Check m1 ##
    if not isinstance(m1, np.ndarray):
        raise TypeError("m1 should be a numpy array, but is ", type(m1))
    if len(m1.shape) != 1:
        raise RuntimeError("m1 should be 1D array, but is ", m1.shape)
    ## Check m2 ##
    if not isinstance(m2, np.ndarray):
        raise TypeError("m2 should be a numpy array, but is ", type(m2))
    if len(m2.shape) != 1:
        raise RuntimeError("m2 should be 1D array, but is ", m2.shape)
    ## Check a ##
    if not isinstance(a, np.ndarray):
        raise TypeError("a should be a numpy array, but is ", type(a))
    if len(a.shape) != 1:
        raise RuntimeError("a should be 1D array, but is ", a.shape)
    ## Check dimensions ##
    if not (m1.size == m2.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, m2.size = %d"%(
            m1.size, m2.size))
    if not (m1.size == a.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, a.size = %d"%(
            m1.size, a.size))
    # Check if to return units
    if unit:
        return _merge_time_circ_arr(m1, m2, a) * u.s
    else:
        return _merge_time_circ_arr(m1, m2, a)

######## Semi-major axis and frequency ########
def forb_of_m1_m2_a(m1,m2,a):
    """Calculate orbital frequency

    Parameters
    ----------
    m1 : array_like
        Primary mass (without astropy units, assumes kg)
    m2 : array_like
        Secondary mass (without astropy units, assumes kg)
    a : array_like
        Semi-major axis (without astropy units, assumes meters)

    Returns
    -------
    forb : array_like
        Orbital frequency
    """
    return 1./orbital_period_of_m1_m2_a(m1,m2,a)

def a_of_m1_m2_forb(m1,m2,forb):
    """Calculate semi-major axis given orbital frequency

    Parameters
    ----------
    m1 : array_like
        Primary mass (without astropy units, assumes kg)
    m2 : array_like
        Secondary mass (without astropy units, assumes kg)
    forb : array_like
        Orbital frequency

    Returns
    -------
    a : array_like
        Semi-major axis (without astropy units, assumes meters)
    """
    if hasattr(m1, "unit"):
        if not m1.unit.is_equivalent(u.kg):
            raise ValueError(
                f"m1 should have units kg, but has units {m1.unit}")
    else:
        m1 = m1 * u.kg
    if hasattr(m2, "unit"):
        if not m2.unit.is_equivalent(u.kg):
            raise ValueError(
                f"m2 should have units kg, but has units {m2.unit}")
    else:
        m2 = m2 * u.kg
    if hasattr(forb, "unit"):
        if not forb.unit.is_equivalent(u.Hz):
            raise ValueError(
                f"forb should have units Hz, but has units {a.unit}")
    else:
        forb = forb * u.Hz
    a = np.power((np.sqrt(const.G * (m1+m2))/(2*np.pi)) / forb, 2/3)
    return a

######## Other external merge times ########
def merge_time_mandel(m1, m2, a, ecc, unit=False):
    """Correction factor (Eq. 5 of 
        https://iopscience.iop.org/article/10.3847/2515-5172/ac2d35/ampdf

    Parameters
    ----------
    m1 : array_like
        Primary mass (without astropy units, assumes kg)
    m2 : array_like
        Secondary mass (without astropy units, assumes kg)
    a : array_like
        Semi-major axis (without astropy units, assumes meters)
    ecc : array_like
        Orbital eccentricity
    unit : bool
        Flag for returning quantity with units

    Returns
    -------
    t : array_like
        Time to merger
    """
    ## Check units
    if hasattr(m1, "unit"):
        # Check for kg
        if m1.unit == u.kg:
            m1 = m1.value
            unit = True
        elif m1.unit.is_equivalent(u.kg):
            m1 = m1.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m1 should have units kg, but has units {m1.unit}")
    ## Check units
    if hasattr(m2, "unit"):
        # Check for kg
        if m2.unit == u.kg:
            m2 = m2.value
            unit = True
        elif m2.unit.is_equivalent(u.kg):
            m2 = m2.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m2 should have units kg, but has units {m2.unit}")
    ## Check units
    if hasattr(a, "unit"):
        # Check for m
        if a.unit == u.m:
            a = a.value
            unit = True
        elif a.unit.is_equivalent(u.m):
            a = a.to(u.m).value
            unit = True
        else:
            raise ValueError(
                f"a should have units m, but has units {a.unit}")
    value = merge_time_circ(m1,m2,a) * \
        (1 + 0.27*ecc**10 + 0.33*ecc**20 + 0.2*ecc**1000)*(1 - ecc**2)**(7/2)
    # Check if to return units
    if unit:
        return value * u.s
    else:
        return value

def merge_time_peters_low_e(m1, m2, a, ecc, unit=False):
    """Peters+1964 low eccentricity approximation

    Parameters
    ----------
    m1 : array_like
        Primary mass (without astropy units, assumes kg)
    m2 : array_like
        Secondary mass (without astropy units, assumes kg)
    a : array_like
        Semi-major axis (without astropy units, assumes meters)
    ecc : array_like
        Orbital eccentricity
    unit : bool
        Flag for returning quantity with units

    Returns
    -------
    t : array_like
        Time to merger
    """
    ## Check units
    if hasattr(m1, "unit"):
        # Check for kg
        if m1.unit == u.kg:
            m1 = m1.value
            unit = True
        elif m1.unit.is_equivalent(u.kg):
            m1 = m1.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m1 should have units kg, but has units {m1.unit}")
    ## Check units
    if hasattr(m2, "unit"):
        # Check for kg
        if m2.unit == u.kg:
            m2 = m2.value
            unit = True
        elif m2.unit.is_equivalent(u.kg):
            m2 = m2.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m2 should have units kg, but has units {m2.unit}")
    ## Check units
    if hasattr(a, "unit"):
        # Check for m
        if a.unit == u.m:
            a = a.value
            unit = True
        elif a.unit.is_equivalent(u.m):
            a = a.to(u.m).value
            unit = True
        else:
            raise ValueError(
                f"a should have units m, but has units {a.unit}")
    value = merge_time_circ(m1,m2,a) * \
        np.power(peters_ecc_const(ecc) * ecc**(12/19),4)
    # Check if to return units
    if unit:
        return value * u.s
    else:
        return value

def merge_time_peters_high_e(m1, m2, a, ecc, unit=False):
    """Peters 1964 high eccentricity approximation

    Parameters
    ----------
    m1 : array_like
        Primary mass (without astropy units, assumes kg)
    m2 : array_like
        Secondary mass (without astropy units, assumes kg)
    a : array_like
        Semi-major axis (without astropy units, assumes meters)
    ecc : array_like
        Orbital eccentricity
    unit : bool
        Flag for returning quantity with units

    Returns
    -------
    t : array_like
        Time to merger
    """
    ## Check units
    if hasattr(m1, "unit"):
        # Check for kg
        if m1.unit == u.kg:
            m1 = m1.value
            unit = True
        elif m1.unit.is_equivalent(u.kg):
            m1 = m1.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m1 should have units kg, but has units {m1.unit}")
    ## Check units
    if hasattr(m2, "unit"):
        # Check for kg
        if m2.unit == u.kg:
            m2 = m2.value
            unit = True
        elif m2.unit.is_equivalent(u.kg):
            m2 = m2.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m2 should have units kg, but has units {m2.unit}")
    ## Check units
    if hasattr(a, "unit"):
        # Check for m
        if a.unit == u.m:
            a = a.value
            unit = True
        elif a.unit.is_equivalent(u.m):
            a = a.to(u.m).value
            unit = True
        else:
            raise ValueError(
                f"a should have units m, but has units {a.unit}")
    value = merge_time_circ(m1,m2,a) * (1-ecc**2)**(7/2)
    # Check if to return units
    if unit:
        return value * u.s
    else:
        return value

def merge_time_peters_enh(m1, m2, a, ecc, unit=False):
    """Peters 1964 enhancement factor estimation of merger time

    Parameters
    ----------
    m1 : array_like
        Primary mass (without astropy units, assumes kg)
    m2 : array_like
        Secondary mass (without astropy units, assumes kg)
    a : array_like
        Semi-major axis (without astropy units, assumes meters)
    ecc : array_like
        Orbital eccentricity
    unit : bool
        Flag for returning quantity with units

    Returns
    -------
    t : array_like
        Time to merger
    """
    ## Check units
    if hasattr(m1, "unit"):
        # Check for kg
        if m1.unit == u.kg:
            m1 = m1.value
            unit = True
        elif m1.unit.is_equivalent(u.kg):
            m1 = m1.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m1 should have units kg, but has units {m1.unit}")
    ## Check units
    if hasattr(m2, "unit"):
        # Check for kg
        if m2.unit == u.kg:
            m2 = m2.value
            unit = True
        elif m2.unit.is_equivalent(u.kg):
            m2 = m2.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m2 should have units kg, but has units {m2.unit}")
    ## Check units
    if hasattr(a, "unit"):
        # Check for m
        if a.unit == u.m:
            a = a.value
            unit = True
        elif a.unit.is_equivalent(u.m):
            a = a.to(u.m).value
            unit = True
        else:
            raise ValueError(
                f"a should have units m, but has units {a.unit}")
    f_enh = (1 + (73 * ecc**2 /24) + (37 /96)*ecc**4) / (1 - ecc**2)**(7/2)
    value = merge_time_circ(m1,m2,a) / f_enh
    # Check if to return units
    if unit:
        return value * u.s
    else:
        return value
    

######## Merge_time_integral ########
def merge_time_integral_sgl(m1, m2, a0, e0, unit=False):
    """Integrate the orbital decay time of a binary
    Parameters
    ----------
    m1 : array_like
        Primary mass (without astropy units, assumes kg)
    m2 : array_like
        Secondary mass (without astropy units, assumes kg)
    a0 : array_like
        Initial semi-major axis (without astropy units, assumes meters)
    e0 : array_like
        Initial orbital eccentricity
    unit : bool
        Flag for returning quantity with units

    Returns
    -------
    t : array_like
        Time to merger
    """
    if np.size(m1) > 1:
        raise ValueError(f"m1 was passed {m1} to unvectorized function")
    # Calculate circular time
    Tc = merge_time_circ(m1,m2,a0)
    # Integrate correction
    cor = quad(peters_ecc_integrand, 0, e0)[0] * \
        (48/19) * np.power(peters_ecc_const(e0),4)
    return Tc * cor

def merge_time_integral_arr(m1, m2, a0, e0):
    """Integrate the orbital decay time of several binaries

    Parameters
    ----------
    m1 : array_like
        Primary mass (without astropy units, assumes kg)
    m2 : array_like
        Secondary mass (without astropy units, assumes kg)
    a0 : array_like
        Initial semi-major axis (without astropy units, assumes meters)
    e0 : array_like
        Initial orbital eccentricity
    unit : bool
        Flag for returning quantity with units

    Returns
    -------
    t : array_like
        Time to merger
    """
    if np.size(m1) < 2:
        raise ValueError(f"m1 was passed {m1} to vectorized function")
    # Calculate circular time
    Tc = merge_time_circ(m1,m2,a0)
    # Integrate correction
    cor = np.zeros(Tc.size)
    for i in range(Tc.size):
        cor[i] = quad(peters_ecc_integrand, 0., e0[i])[0] 
    # Multiprocessing made it slower for some reason
    #
    #elif isinstance(threads, int):
    #    #cor[i] = quad(peters_ecc_integrand, 0., e0[i])[0] 
    #    # Define function for multiprocessing
    #    with tqdm(total=Tc.size,desc="Integrating eccentric orbits...") as pbar:
    #      with concurrent.futures.ProcessPoolExecutor(max_workers=threads) as executor:
    #        future_to_correction = {executor.submit(concurrent_merge_time_integral,e0[i]): i for i in range(Tc.size)}
    #        for future in concurrent.futures.as_completed(future_to_correction):
    #            cor[future_to_correction[future]] = future.result()
    #            #try:
    #            #    cor[future_to_correction[future]] = future.result()
    #            #except Exception as exc:
    #            #    exc_id = future_to_correction[future]
    #            #    print('%r generated an exception: %s'%(future,exc))
    #            #    raise exc
    #            # Update tqdm
    #            pbar.update(1)
    cor *= (48/19) * np.power(peters_ecc_const(e0),4)
    return Tc * cor

def merge_time_integral(m1, m2, a0, e0):
    """Integrate the orbital decay time of 1 or more binaries

    Parameters
    ----------
    m1 : array_like
        Primary mass (without astropy units, assumes kg)
    m2 : array_like
        Secondary mass (without astropy units, assumes kg)
    a0 : array_like
        Initial semi-major axis (without astropy units, assumes meters)
    e0 : array_like
        Initial orbital eccentricity

    Returns
    -------
    t : array_like
        Time to merger
    """
    if np.size(m1) > 1:
        return merge_time_integral_arr(m1,m2,a0,e0)
    else:
        return merge_time_integral_sgl(m1,m2,a0,e0)

MERGE_TIME_METHODS = {
    "circ_numpy"    : merge_time_circ_numpy,
    "circ"          : merge_time_circ,
    "circle"        : merge_time_circ,
    "circular"      : merge_time_circ,
    "Ilya"          : merge_time_mandel,
    "ilya"          : merge_time_mandel,
    "Mandel"        : merge_time_mandel,
    "mandel"        : merge_time_mandel,
    "Mandel+2021"   : merge_time_mandel,
    "mandel+2021"   : merge_time_mandel,
    "integrate"     : merge_time_integral,
    "Integrate"     : merge_time_integral,
    "int"           : merge_time_integral,
    "Int"           : merge_time_integral,
    "peters_low"    : merge_time_peters_low_e,
    "Peters_low"    : merge_time_peters_low_e,
    "Peters+1964L"  : merge_time_peters_low_e,
    "peters_high"   : merge_time_peters_high_e,
    "Peters_high"   : merge_time_peters_high_e,
    "Peters+1964H"  : merge_time_peters_high_e,
    "peters_enh"    : merge_time_peters_enh,
    "Peters_enh"    : merge_time_peters_enh,
    "Peters+1964E"  : merge_time_peters_enh,
    "enhancement"   : merge_time_peters_enh,
    "enh"           : merge_time_peters_enh,
    "f(e)"          : merge_time_peters_enh,
}
"""A dict of the estimators for merger time"""

def merge_time(
        m1,m2,a0,e0,
        ecc_bound=1e-6,
        method="integrate",
        unit=False,
    ):
    """Evaluate the time to merger of a binary using a particular method

    Parameters
    ----------
    m1 : array_like
        Primary mass (without astropy units, assumes kg)
    m2 : array_like
        Secondary mass (without astropy units, assumes kg)
    a0 : array_like
        Initial semi-major axis (without astropy units, assumes meters)
    e0 : array_like
        Initial orbital eccentricity
    ecc_bound : float
        The minimum eccentricity for a binary before we call it circular
    method : str
        Indicates which method to use for estimation
        The method should belong to the MERGE_TIME_METHODS dictionary
    unit : bool
        Flag for returning quantity with units

    Returns
    -------
    t : array_like
        Time to merger
    """
    ## Check units
    if hasattr(m1, "unit"):
        # Check for kg
        if m1.unit == u.kg:
            m1 = m1.value
            unit = True
        elif m1.unit.is_equivalent(u.kg):
            m1 = m1.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m1 should have units kg, but has units {m1.unit}")
    ## Check units
    if hasattr(m2, "unit"):
        # Check for kg
        if m2.unit == u.kg:
            m2 = m2.value
            unit = True
        elif m2.unit.is_equivalent(u.kg):
            m2 = m2.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m2 should have units kg, but has units {m2.unit}")
    ## Check units
    if hasattr(a0, "unit"):
        # Check for m
        if a0.unit == u.m:
            a0 = a0.value
            unit = True
        elif a0.unit.is_equivalent(u.m):
            a0 = a0.to(u.m).value
            unit = True
        else:
            raise ValueError(
                f"a0 should have units m, but has units {a0.unit}")
    # Identify circular binaries
    circ_mask = e0 < ecc_bound
    # Identify single or array
    if np.size(circ_mask) < 2:
        # Case 1: circular binary
        if bool(circ_mask) or method in ["circ", "circular"]:
            value = merge_time_circ(m1,m2,a0)
        elif method in ["circ_numpy"]:
            value = merge_time_circ_numpy(m1,m2,a0)
        # Case 2: Ilya's method
        elif method in ["Ilya", "ilya", "Mandel", "mandel", "Mandel+2021", "mandel+2021"]:
            value = merge_time_mandel(m1,m2,a0,e0)
        # Case 3: Numerical integration
        elif method in ["integrate", "Integrate", "int", "Int"]:
            value = merge_time_integral_sgl(m1,m2,a0,e0)
        # Case 4: peters_low
        elif method in ["peters_low", "Peters_low", "Peters+1964L"]:
            value = merge_time_peters_low_e(m1,m2,a0,e0)
        # Case 5: peters_high
        elif method in ["peters_high", "Peters_high", "Peters+1964H"]:
            value = merge_time_peters_high_e(m1,m2,a0,e0)
        # Case 6: peters_low
        elif method in ["peters_enh", "Peters_enh", "Peters+1964E", "enhancement", "enh", "f(e)"]:
            value = merge_time_peters_enh(m1,m2,a0,e0)
        else:
            raise ValueError(f"Unknown estimator method: {method}")
        # Check unit
        if unit:
            return value * u.s
        else:
            return value
    # Whole second set of cases for array
    else:
        # Construct output array
        merge_time_arr = np.zeros(np.size(circ_mask))
        # Apply circ mask
        if np.any(circ_mask):
            merge_time_arr[circ_mask] = \
                merge_time_circ(m1[circ_mask],m2[circ_mask],a0[circ_mask],unit=True).to('s').value
        # Check if all binaries are circular
        if np.sum(circ_mask) == np.size(circ_mask):
            if unit:
                return merge_time_arr * u.s
            else:
                return merge_time_arr
        # Otherwise downselect
        m1 = m1[~circ_mask]
        m2 = m2[~circ_mask]
        a0 = a0[~circ_mask]
        e0 = e0[~circ_mask]
        # Case 1: circular binary
        if method in ["circ", "circular"]:
            _arr = merge_time_circ(m1,m2,a0)
            if hasattr(_arr,'unit'):
                merge_time_arr[~circ_mask] = _arr.to('s').value
            else:
                merge_time_arr[~circ_mask] = _arr
        elif method in ["circ_numpy"]:
            _arr = merge_time_circ_numpy(m1,m2,a0)
            if hasattr(_arr,'unit'):
                merge_time_arr[~circ_mask] = _arr.to('s').value
            else:
                merge_time_arr[~circ_mask] = _arr
        # Case 2: Ilya's method
        elif method in ["Ilya", "ilya", "Mandel", "mandel", "Mandel+2021", "mandel+2021"]:
            _arr = merge_time_mandel(m1,m2,a0,e0)
            if hasattr(_arr,'unit'):
                merge_time_arr[~circ_mask] = _arr.to('s').value
            else:
                merge_time_arr[~circ_mask] = _arr
        # Case 3: Numerical integration
        elif method in ["integrate", "Integrate", "int", "Int"]:
            _arr = merge_time_integral(m1,m2,a0,e0)
            if hasattr(_arr,'unit'):
                merge_time_arr[~circ_mask] = _arr.to('s').value
            else:
                merge_time_arr[~circ_mask] = _arr
        # Case 4: peters_low
        elif method in ["peters_low", "Peters_low", "Peters+1964L"]:
            _arr = merge_time_peters_low_e(m1,m2,a0,e0)
            if hasattr(_arr,'unit'):
                merge_time_arr[~circ_mask] = _arr.to('s').value
            else:
                merge_time_arr[~circ_mask] = _arr
        # Case 5: peters_high
        elif method in ["peters_high", "Peters_high", "Peters+1964H"]:
            _arr = merge_time_peters_high_e(m1,m2,a0,e0)
            if hasattr(_arr,'unit'):
                merge_time_arr[~circ_mask] = _arr.to('s').value
            else:
                merge_time_arr[~circ_mask] = _arr
        # Case 6: peters_low
        elif method in ["peters_enh", "Peters_enh", "Peters+1964E", "enhancement", "enh", "f(e)"]:
            _arr = merge_time_peters_enh(m1,m2,a0,e0)
            if hasattr(_arr,'unit'):
                merge_time_arr[~circ_mask] = _arr.to('s').value
            else:
                merge_time_arr[~circ_mask] = _arr
        else:
            raise ValueError(f"Unknown estimator method: {method}")
        # Check units
        if unit:
            return merge_time_arr * u.s
        else:
            return merge_time_arr

######## Eccentricity and Constants of Motion ########

def a_of_ecc(ecc,c0=None,a0=None,e0=None):
    """Solve for a, given reference point and eccentricity

    Parameters
    ----------
    ecc : array_like
        Eccentricities of interest
    c0 : array_like
        Constant of motion
    a0 : array_like
        Initial semi-major axis (without astropy units, assumes meters)
    e0 : array_like
        Initial orbital eccentricity
    
    Returns
    -------
    a : array_like
        Orbital semi-major axis
    """
    # If necessary estimate c0
    if c0 is None:
        # Check for completeness of inputs
        if (e0 is None) or (a0 is None):
            raise RuntimeError("To estiate separation given eccentricity, you"
                "must provide a reference point")
        # Check for units
        if hasattr(a0, "unit"):
            if not a0.unit.is_equivalent(u.m):
                raise ValueError(
                    f"a0 should have units m, but has units {a0.unit}")
        else:
            a0 = a0 * u.m
        # Calculate c0
        c0 = a0.to('m') * peters_ecc_const(e0)
    # Return a
    return c0 / peters_ecc_const(ecc)

def ecc_of_a0_e0_a1(a0,e0,a1,elow=1e-6, decay=False):
    """Solve for the inverse of c0 = a0 * stuff(e)

    Parameters
    ----------
    a0 : array_like
        Initial semi-major axis (without astropy units, assumes meters)
    e0 : array_like
        Initial orbital eccentricity
    a1 : array_like
        Semi-major axis at some later time
    decay : bool
        Flag indicating if separations provided are always decreasing

    Returns
    -------
    ecc : array_like
        Eccentricities of interest
    """
    # Check for units
    if hasattr(a0, "unit"):
        if not a0.unit.is_equivalent(u.m):
            raise ValueError(
                f"a0 should have units m, but has units {a0.unit}")
    else:
        a0 = a0 * u.m
    # Calculate c0
    c0 = a0.to('m') * peters_ecc_const(e0)
    # Get a1 in meters
    if hasattr(a1, "unit"):
        if not a1.unit.is_equivalent(u.m):
            raise ValueError(
                f"a1 should have units m, but has units {a1.unit}")
    else:
        a1 = a1 * u.m
    # Get remove units
    a1 = a1.value
    c0 = c0.value
    # Check ehigh
    if decay:
        ehigh = e0
    else:
        if np.size(a1) < 2:
            ehigh = 1.-elow
        else:
            ehigh = np.ones(a1.size) - elow
    # Check size of arguments
    if np.size(a1) < 2:
        # Define objective function
        def objective(ecc):
            return np.abs(a1 - (c0 / peters_ecc_const(ecc)))
        # Use minimize with bounds
        result = minimize(
            objective,
            x0=[e0],
            method='L-BFGS-B',
            bounds=[(elow,ehigh)],
            options={'ftol': 1e-12, 'gtol': 1e-8},
        )
        # Assign value
        e_final_minimize = result.x[0]
        # Assign error
        error = result.fun * u.m
        #print(f"e_final_minimize: {e_final_minimize}")
        #print(f"error: {error.to('au')}")
    else:
        # Initialize value
        e_final_minimize = np.zeros(np.size(a1))
        # Loop
        for i in range(np.size(a1)):
            # Define objective function
            a1i = a1[i]
            c0i = c0[i]
            def objective(ecc):
                return np.abs(a1i - (c0i / peters_ecc_const(ecc)))
            # Use minimize with bounds
            result = minimize(
                objective,
                x0=[e0[i]],
                method='L-BFGS-B',
                bounds=[(elow,ehigh[i])],
                options={'ftol': 1e-12, 'gtol': 1e-8},
            )
            # Assign value
            e_final_minimize[i] = result.x[0]
    return e_final_minimize
            

######## ODE stuff ########
def da_dt_circ_integrand(m1,m2,a0):
    """Return the integrand for semi-major axis as a function of time

    Parameters
    ----------
    m1 : float
        Primary mass (without astropy units, assumes kg)
    m2 : float
        Secondary mass (without astropy units, assumes kg)
    a0 : float
        Initial semi-major axis (without astropy units, assumes meters)

    Returns
    -------
    integrand : function
        The defined integrand function for our ODE solver
    """
    mass_const = m1.to('kg') * m2.to('kg') * (m1+m2).to('kg')
    mass_const = mass_const * (-64/5) * const.G.si**3 * (const.c**-5)
    mass_const = mass_const.value

    def integrand(t, a):
        return mass_const / a**3
    return integrand

def circular_ODE_integration(
        m1,m2,a0,
        Teval=None,
        forb_tol=2.e-3*u.s**-1,
        method="DOP853",
        verbose=False,
        **solve_ivp_kwargs
    ):
    """Estimate the change in orbital semi-major axis from initial to origin

    Parameters
    ----------
    m1 : float
        Primary mass (without astropy units, assumes kg)
    m2 : float
        Secondary mass (without astropy units, assumes kg)
    a0 : float
        Initial semi-major axis (without astropy units, assumes meters)
    Teval : float
        How long to evolve the binary for
    forb_tol : float
        Orbital frequency tolerance (currently unused)
    method : str
        ODE solver method (see scipy.integrate._ivp.ivp.METHODS)
    verbose : bool
        Verbosity flag
    solve_ivp_kwargs : dict
        Keyword arguments for ODE solver

    Returns
    -------
    ivp_outputs : dict
        Outputs from the ODE solver
    err : astropy quantity
        Error in orbital decay time incurred by ODE solution
    """
    tic = time.perf_counter()
    # Set vectorized
    solve_ivp_kwargs["vectorized"] = True
    # Set method
    solve_ivp_kwargs["method"] = method
    # Calculate circular time
    Tc = merge_time_circ(m1,m2,a0)
    Tc = Tc.to('s')
    # Calculate orbital period for highest frequency we care about
    Porb = 1/forb_tol
    # Calculate Schwarzschild time
    #Tschwarzschild = merge_time_circ(m1,m2,schwarzschild_separation(m1,m2))
    Tstop = Porb.to('s')
    # Calculate evaluation time
    if (Teval is None):
        Teval = Tc-Tstop
    elif Teval > Tc-Tstop:
        raise ValueError(f"Evaluation time {Teval} is post-merger!")
    elif not hasattr(Teval,'unit'):
        Teval = Teval * u.s
    elif not Teval.unit.is_equivalent('s'):
        raise ValueError(f"Evaluation time {Teval} has units {Teval.unit}!")
    # Set up ODE solver
    ivp_outputs = solve_ivp(
        da_dt_circ_integrand(m1,m2,a0),
        [0.,Teval.value],
        [a0.to('m').value],
        **solve_ivp_kwargs
    )
    # Identify end state
    t1 = (ivp_outputs.t[-1] * u.s).to('yr')
    if solve_ivp_kwargs['vectorized']:
        a1 = (ivp_outputs.y[-1,-1] * u.m).to('au')
    else:
        a1 = (ivp_outputs.y[-1] * u.m).to('au')
    # Estimate merge time from end product
    Tc1 = merge_time_circ(m1,m2,a1).to("yr")
    tf = t1 + Tc1
    err = (tf - Tc).to('yr')
    toc = time.perf_counter()
    if verbose:
        print(f"Circular time: {Tc.to('yr'):.3e}")
        #print(f"Schwarzschild time: {Tschwarzschild.to('yr'):.3e}")
        print(f"Stop time: {Tstop.to('yr'):.3e}")
        print(f"Integral time: {t1.to('yr')}, a:{a1.to('au')}")
        print(f"Circular time post-integration: {Tc1.to('yr')}")
        print(f"total merge time estimate: {tf.to('yr')}")
        print(f"Error: {err}")
        print(f"ODE time: {toc-tic:.6f}")
    #if np.abs(err) > (1/forb_tol).to('yr'):
    #    warnings.warn(f"ODE integration error ({err:.3e}) "
    #        f"exceeds one orbital period for f_orb: {forb_tol.to('Hz')} "
    #        f"(Porb = {(1/forb_tol).to('yr'):.3e})")

    return ivp_outputs, err

def eccentric_ODE_integrand(
    m1,m2,c0,
    vectorized=True,
    ):
    """Return the integrand for semi-major axis as a function of time

    Parameters
    ----------
    m1 : float
        Primary mass (without astropy units, assumes kg)
    m2 : float
        Secondary mass (without astropy units, assumes kg)
    c0 : float
        Peter's constant of motion
    vectorized : bool
        Flag for using a vectorized ODE solver integrand

    Returns
    -------
    integrand : function
        The defined integrand function for our ODE solver
    """
    from basil_core.astro.orbit._decay import _orb_sep_evol_ecc_integrand_sgl
    from basil_core.astro.orbit._decay import _orb_sep_evol_ecc_integrand_arr
    # Check inputs
    if hasattr(m1,'unit'):
        m1 = m1.to('kg').value
    if hasattr(m2,'unit'):
        m2 = m2.to('kg').value
    # Estimate de_dt_const
    de_dt_const = (-304/15) * (const.G.value**3 / const.c.value**5) * m1 * m2 * (m1+m2)
    # Evaluate C extension
    if vectorized:
        # Define integrand
        def integrand(t, Y):
            return _orb_sep_evol_ecc_integrand_arr(de_dt_const, c0, Y[0])
    else:
        # Define integrand
        def integrand(t, Y):
            return _orb_sep_evol_ecc_integrand_sgl(de_dt_const, c0, Y[0])
    return integrand

def eccentric_ODE_integration(
        m1,m2,a0,e0,
        Teval=None,
        forb_tol=2.e-3*u.s**-1,
        e_tol=1e-3,
        method="DOP853",
        verbose=False,
        vectorized=True,
        **solve_ivp_kwargs
    ):
    """Estimate the change in orbital eccentricity from initial to origin

    Parameters
    ----------
    m1 : float
        Primary mass (without astropy units, assumes kg)
    m2 : float
        Secondary mass (without astropy units, assumes kg)
    a0 : float
        Initial orbital separation (without astropy units, assumes meters)
    e0 : float
        Initial orbital eccentricity
    forb_tol : float
        Orbital frequency tolerance (currently unused)
    e_tol : float
        Orbital eccentricity tolerance (currently unused)
    method : str
        ODE solver method (see scipy.integrate._ivp.ivp.METHODS)
        If you are integrating to merger time, DOP853 is reccomended
    verbose : bool
        Verbosity flag
    vectorized : bool
        Flag for using a vectorized ODE solver integrand
    solve_ivp_kwargs : dict
        Keyword arguments for ODE solver

    Returns
    -------
    ivp_outputs : dict
        Outputs from the ODE solver
    err : astropy quantity
        Error in orbital decay time incurred by ODE solution
    """
    #tic = time.perf_counter()
    # Check inputs
    if hasattr(m1,'unit'):
        m1 = m1.to('kg').value
    if hasattr(m2,'unit'):
        m2 = m2.to('kg').value
    if hasattr(a0,'unit'):
        a0 = a0.to('m').value
    if hasattr(Teval,'unit'):
        Teval = Teval.to('s').value

    # Set vectorized
    solve_ivp_kwargs["vectorized"] = vectorized
    # Set method
    solve_ivp_kwargs["method"] = method
    # Calculate circular time
    Tc = merge_time_circ(m1,m2,a0)
    # Calculate orbital period for highest frequency we care about
    # Estimate tolerance in semi-major axis
    a_tol = a_of_m1_m2_forb(m1,m2,forb_tol.value)
    # Calculate c_0 once
    c0 = a0 * peters_ecc_const(e0)
    # Calculate etol
    #e_tol_from_forb = ecc_of_a0_e0_a1(a0,e0,a_tol)
    #if e_tol_from_forb < e_tol:
    #    e_tol = e_tol_from_forb
    ## Check against e0
    #if e_tol > e0:
    #    e_tol = e0 * 1e-2
    #if verbose:
    #    print(f"forb_tol: {forb_tol}; a_tol: {(a_tol).to('au')}; e_tol: {e_tol}")
    # Calculate the time to merger once
    Tmerge = merge_time(m1,m2,a0,e0)
    # Calculate orbital period for highest frequency we care about
    Porb = 1/forb_tol
    Tstop = Porb.to('s').value
    # Calculate evaluation time
    if (Teval is None):
        Teval = Tmerge-Tstop
    elif hasattr(Teval,'unit'):
        Teval = Teval.to('s').value
    elif Teval > Tmerge-Tstop:
        raise ValueError(f"Evaluation time {Teval} is post-merger!")
    # Define integrand 
    integrand = eccentric_ODE_integrand(
        m1,m2,c0,
        vectorized=solve_ivp_kwargs["vectorized"],
    )
    #toc = time.perf_counter()
    #print(f"setup time: {toc-tic:.6f}"); tic=toc
    # Set up ODE solver
    ivp_outputs = solve_ivp(
        integrand,
        [0.,Teval],
        [e0],
        **solve_ivp_kwargs
    )
    # Identify end state
    #toc = time.perf_counter()
    #print(f"solve_ivp time: {toc-tic:.6f}"); tic=toc
    t1 = (ivp_outputs.t[-1] * u.s).to('yr')
    e1 = ivp_outputs.y[-1]
    if np.size(e1) > 1:
        e1 = e1[-1]
    a1 = c0 * u.m / peters_ecc_const(e1)
    # Estimate merge time from end product
    Tc1 = merge_time_circ(m1,m2,a1,unit=True).to("yr")
    Te1 = merge_time(m1,m2,a1,e1,unit=True)
    err_c = (t1 + Tc1 - (Tmerge*u.s))
    err_e = (t1 + Te1 - (Tmerge*u.s))
    #toc = time.perf_counter()
    #print(f"post time: {toc-tic:.6f}"); tic=toc
    if verbose:
        print(f"Circular time: {(Tc * u.s).to('yr'):.3e}")
        print(f"Quadrature time: {(Tmerge * u.s).to('yr'):.3e}")
        print(f"Stop time: {(Tstop * u.s).to('yr'):.3e}")
        print(f"Integral time: {t1.to('yr'):.3e}, a:{a1.to('au'):.3e}; e:{e1:.3e}")
        print(f"Circular time post-integration: {Tc1.to('yr'):.3e}")
        print(f"Quadrature time post-integration: {Te1.to('yr'):.3e}")
        print(f"total merge time estimate: {(t1+Te1).to('yr'):.3e}")
        print(f"Error (circular end): {err_c:.3e}")
        print(f"Error (eccentric end): {err_e:.3e}")
        #print(f"ODE time: {toc-tic:.6f}")
    #if np.abs(err) > (1/forb_tol).to('yr'):
    #    warnings.warn(f"ODE integration error ({err:.3e}) "
    #        f"exceeds one orbital period for f_orb: {forb_tol.to('Hz')} "
    return ivp_outputs, err_e

######## Time between states ########
def decay_time(
        m1,
        m2,
        a0,
        af=None,
        e0=None,
        ef=None,
        forb_f=None,
        **kwargs,
    ):
    """Calculate the time it takes to go between two orbits
        (from an initial separation/eccentricity to a 
            final separation/eccentricity)

    Parameters
    ----------
    m1 : array_like
        Primary mass (without astropy units, assumes kg)
    m2 : array_like
        Secondary mass (without astropy units, assumes kg)
    a0 : array_like
        Initial semi-major axis (without astropy units, assumes meters)
    af : array_like
        Final semi-major axis (without astropy units, assumes meters)
    e0 : array_like
        Initial orbital eccentricity
    ef : array_like
        Final orbital eccentricity
    forb_f : array_like
        Final orbital period

    Returns
    -------
    t : array_like
        Time difference between two states
    """
    ## Simple cases
    # Case 1: Only m1, m2, a0 given
    # Merge time circular
    if (af is None) and (e0 is None) and (ef is None) and (forb_f is None):
        return merge_time_circ(m1,m2,a0)
    # Case 2: Only m1, m2, a0, e0 given
    elif (af is None) and (ef is None) and (forb_f is None):
        return merge_time(m1,m2,a0,e0,**kwargs)
    ## Circular cases
    # Case 3: Only m1, m2, a0, af given
    elif (e0 is None) and (ef is None) and (forb_f is None):
        return merge_time_circ(m1,m2,a0) - merge_time_circ(m1,m2,af)
    # Case 4: Only m1, m2, a0, forb_f given
    elif (af is None) and (e0 is None) and (ef is None):
        # Calculate af
        af = a_of_m1_m2_forb(m1,m2,forb_f)
        return merge_time_circ(m1,m2,a0) - merge_time_circ(m1,m2,af)
    ## Eccentric cases
    # Case 5: Only m1, m2, a0, e0, af given
    elif (ef is None) and (forb_f is None):
        # Calculate ef
        ef = ecc_of_a0_e0_a1(a0,e0,af)
        return merge_time(m1,m2,a0,e0,**kwargs) - merge_time(m1,m2,af,ef,**kwargs)
    # Case 6: Only m1, m2, a0, e0, ef given
    elif (af is None) and (forb_f is None):
        # Estimate constant of motion
        if hasattr(a0,'unit'):
            _a0 = a0.to('m').value
        else:
            _a0 = a0
        c0 = _a0 * peters_ecc_const(e0)
        # Calculate af
        af = c0 / peters_ecc_const(ef)
        if hasattr(a0,'unit'):
            return merge_time(m1,m2,_a0*u.m,e0,**kwargs) - \
                merge_time(m1,m2,af*u.m,ef,**kwargs)
        else:
            return merge_time(m1,m2,_a0,e0,**kwargs) - merge_time(m1,m2,af,ef,**kwargs)
    # Case 7: Only m1, m2, a0, e0, forb_f given
    elif (af is None) and (ef is None):
        # Calculate af
        af = a_of_m1_m2_forb(m1,m2,forb_f)
        # Calculate ef
        ef = ecc_of_a0_e0_a1(a0,e0,af)
        return merge_time(m1,m2,a0,e0,**kwargs) - merge_time(m1,m2,af,ef,**kwargs)
    ## Silly cases
    # So, I wanted to allow these, but it's prone to high errors
    ## Case 8: Only m1, m2, a0, ef, af given
    #elif (e0 is None) and (forb_f is None):
    #    # Calculate ef
    #    e0 = ecc_of_a0_e0_a1(af,ef,a0)
    #    return merge_time(m1,m2,a0,e0,**kwargs) - merge_time(m1,m2,af,ef,**kwargs)
    ## Case 9: Only m1, m2, a0, ef, forb_f given
    #elif (af is None) and (e0 is None):
    #    # Calculate af
    #    af = a_of_m1_m2_forb(m1,m2,forb_f)
    #    # Calculate ef
    #    e0 = ecc_of_a0_e0_a1(af,ef,a0)
    #    return merge_time(m1,m2,a0,e0,**kwargs) - merge_time(m1,m2,af,ef,**kwargs)
    ## Otherwise, this is overspecified
    else:
        raise RuntimeError("Inputs to decay time are overspecified!")

######## Evolve Orbit ########

def orbital_separation_evolve_circ_numpy(m1,m2,a0,evolve_time):
    """Evolve circular binar(y/ies) using the analytic expression in Numpy

    Parameters
    ----------
    m1 : array_like
        Primary mass (without astropy units, assumes kg)
    m2 : array_like
        Secondary mass (without astropy units, assumes kg)
    a0 : array_like
        Initial semi-major axis (without astropy units, assumes meters)
    evolve_time : array_like
        Time to evolve binary for

    Returns
    -------
    sep : array_like
        Final orbital separation
    """
    if hasattr(m1, "unit"):
        if not m1.unit.is_equivalent(u.kg):
            raise ValueError(
                f"m1 should have units kg, but has units {m1.unit}")
    else:
        m1 = m1 * u.kg
    if hasattr(m2, "unit"):
        if not m2.unit.is_equivalent(u.kg):
            raise ValueError(
                f"m2 should have units kg, but has units {m2.unit}")
    else:
        m2 = m2 * u.kg
    if hasattr(a0, "unit"):
        if not a0.unit.is_equivalent(u.m):
            raise ValueError(
                f"a0 should have units m, but has units {a0.unit}")
    else:
        a0 = a0 * u.m
    if hasattr(evolve_time, "unit"):
        if not evolve_time.unit.is_equivalent(u.s):
            raise ValueError(
                f"evolve_time should have units m, but has units {evolve_time.unit}")
    else:
        evolve_time = evolve_time * u.s
    return np.power(np.power(a0,4) - (4 * beta_fn(m1,m2) * evolve_time),1/4)

def orbital_separation_evolve_circ(m1,m2,a0,evolve_time,fallback=True,unit=False):
    """Evolve circular binar(y/ies) using the analytic expression in C

    Parameters
    ----------
    m1 : array_like
        Primary mass (without astropy units, assumes kg)
    m2 : array_like
        Secondary mass (without astropy units, assumes kg)
    a0 : array_like
        Initial semi-major axis (without astropy units, assumes meters)
    evolve_time : array_like
        Time to evolve binary for
    fallback : bool
        Flag to use NumPy if C extension fails
    unit : bool
        Flag to return quantity with units

    Returns
    -------
    sep : array_like
        Final orbital separation
    """
    # Try to import C extensions
    try:
        from basil_core.astro.orbit._decay import _orb_sep_evol_circ_sgl
        from basil_core.astro.orbit._decay import _orb_sep_evol_circ_arr
    except Exception as exc:
        warnings.warn("orbital_separation_evolve_sgl: Failed to import C extension."
            "Defaulting to NumPy")
        if fallback:
            return orbital_separation_evolve_circ_numpy(m1,m2,a0,evolve_time)
        else: 
            raise exc
    #### Check inputs ####
    ## Check units
    if hasattr(m1, "unit"):
        # Check for kg
        if m1.unit == u.kg:
            m1 = m1.value
            unit = True
        elif m1.unit.is_equivalent(u.kg):
            m1 = m1.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m1 should have units kg, but has units {m1.unit}")
    ## Check units
    if hasattr(m2, "unit"):
        # Check for kg
        if m2.unit == u.kg:
            m2 = m2.value
            unit = True
        elif m2.unit.is_equivalent(u.kg):
            m2 = m2.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m2 should have units kg, but has units {m2.unit}")
    ## Check units
    if hasattr(a0, "unit"):
        # Check for m
        if a0.unit == u.m:
            a0 = a0.value
            unit = True
        elif a0.unit.is_equivalent(u.m):
            a0 = a0.to(u.m).value
            unit = True
        else:
            raise ValueError(
                f"a0 should have units m, but has units {a0.unit}")
    ## Check units
    if hasattr(evolve_time, "unit"):
        # Check for m
        if evolve_time.unit == u.s:
            evolve_time = evolve_time.value
            unit = True
        elif evolve_time.unit.is_equivalent(u.s):
            evolve_time = evolve_time.to(u.s).value
            unit = True
        else:
            raise ValueError(
                f"evolve_time should have units s, but has units {evolve_time.unit}")
    # Check for single
    if (isinstance(m1, float) or isinstance(m1, np.float64)) and \
       (isinstance(m2, float) or isinstance(m2, np.float64)) and \
       (isinstance(a0, float) or isinstance(a0, np.float64)) and \
       (isinstance(evolve_time,  float) or isinstance(evolve_time,  np.float64)):
        if unit:
            return _orb_sep_evol_circ_sgl(m1,m2,a0,evolve_time) * u.m
        else:
            return _orb_sep_evol_circ_sgl(m1,m2,a0,evolve_time)
    ## Check m1 ##
    if not isinstance(m1, np.ndarray):
        raise TypeError("m1 should be a numpy array, but is ", type(m1))
    if len(m1.shape) != 1:
        raise RuntimeError("m1 should be 1D array, but is ", m1.shape)
    ## Check m2 ##
    if not isinstance(m2, np.ndarray):
        raise TypeError("m2 should be a numpy array, but is ", type(m2))
    if len(m2.shape) != 1:
        raise RuntimeError("m2 should be 1D array, but is ", m2.shape)
    ## Check a0 ##
    if not isinstance(a0, np.ndarray):
        raise TypeError("a0 should be a numpy array, but is ", type(a0))
    if len(a0.shape) != 1:
        raise RuntimeError("a0 should be 1D array, but is ", a0.shape)
    ## Check evolve_time ##
    if not isinstance(evolve_time, np.ndarray):
        raise TypeError("evolve_time should be t numpy array, but is ", type(evolve_time))
    if len(evolve_time.shape) != 1:
        raise RuntimeError("evolve_time should be 1D array, but is ", evolve_time.shape)
    ## Check dimensions ##
    if not (m1.size == m2.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, m2.size = %d"%(
            m1.size, m2.size))
    if not (m1.size == a0.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, a0.size = %d"%(
            m1.size, a0.size))
    if not (m1.size == evolve_time.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, evolve_time.size = %d"%(
            m1.size, evolve_time.size))
    # Check if to return units
    if unit:
        return _orb_sep_evol_circ_arr(m1,m2,a0,evolve_time) * u.m
    else:
        return _orb_sep_evol_circ_arr(m1,m2,a0,evolve_time)

def orb_sep_evol_sgl_opt(
        m1,m2,a0,evolve_time,e0,
        method="integral",
        guess=None,
    ):
    """Evolve an eccentric binary by using a root finder in separation

    Parameters
    ----------
    m1 : float
        Primary mass (without astropy units, assumes kg)
    m2 : float
        Secondary mass (without astropy units, assumes kg)
    a0 : float
        Initial semi-major axis (without astropy units, assumes meters)
    evolve_time : float
        Time to evolve binary for
    e0 : float
        Initial eccentricities
    method : str
        Method for evaluating merge times
    guess : float
        Value to start optimizer at

    Returns
    -------
    sep : float
        Final orbital separation
    """
    # Set guesses
    if guess is None:
        guess = orbital_separation_evolve_circ(
            m1,m2,a0,evolve_time,unit=False
        )
    elif method=="integral":
        guess = orb_sep_evol_sgl_opt(
            m1,m2,a0,evolve_time,unit=False,method="Mandel",
        )
    # Define objective function
    def objective(_sep):
        # Estimate time to given separation
        _decay_time = decay_time(m1,m2,a0,af=_sep,e0=e0,method=method)
        return np.abs(evolve_time - _decay_time)

    # Use walkers
    result = minimize(
            objective,
            x0=[guess],
            method='L-BFGS-B',
            bounds=[(0.,a0)],
            #options={'ftol': 1e-12, 'gtol': 1e-8},
        )
    return result.x[0]
    
def orb_ecc_evol_sgl_opt(
        m1,m2,a0,evolve_time,e0,
        method="integral",
        guess=None,
    ):
    """Evolve an eccentric binary by using a root finder in eccentricity

    Parameters
    ----------
    m1 : float
        Primary mass (without astropy units, assumes kg)
    m2 : float
        Secondary mass (without astropy units, assumes kg)
    a0 : float
        Initial semi-major axis (without astropy units, assumes meters)
    evolve_time : float
        Time to evolve binary for
    e0 : float
        Initial eccentricities
    method : str
        Method for evaluating merge times
    guess : float
        Value to start optimizer at

    Returns
    -------
    sep : float
        Final orbital separation
    """
    # Set guesses
    if guess is None:
        guess = orbital_separation_evolve_circ(
            m1,m2,a0,evolve_time,unit=False
        )
    elif method=="integral":
        guess = orb_ecc_evol_sgl_opt(
            m1,m2,a0,evolve_time,unit=False,method="Mandel",
        )
    # Calculate merge time
    Tmerge = merge_time(m1,m2,a0,e0=e0,method=method)
    # Calculate constant of motion
    c0 = a0 * peters_ecc_const(e0)
    # Define objective function
    def objective(_ecc):
        # Calculate af
        af = c0 / peters_ecc_const(_ecc)
        # Estimate time to given separation
        _decay_time = Tmerge - merge_time(m1,m2,af,_ecc,method=method)
        return np.abs(evolve_time - _decay_time)

    # Use walkers
    result = minimize(
            objective,
            x0=[guess],
            method='L-BFGS-B',
            bounds=[(1.e-6,e0)],
            #options={'ftol': 1e-12, 'gtol': 1e-8},
        )
    return result.x[0]

def orbital_separation_evolve_sgl(
        m1, m2, a0, evolve_time,
        e0=None,
        unit=False,
        method="DOP853",
        return_ecc=False,
        **kwargs
    ):
    """Evolve an eccentric binary by using a specified method

    Parameters
    ----------
    m1 : float
        Primary mass (without astropy units, assumes kg)
    m2 : float
        Secondary mass (without astropy units, assumes kg)
    a0 : float
        Initial semi-major axis (without astropy units, assumes meters)
    evolve_time : float
        Time to evolve binary for
    e0 : float
        Initial eccentricities
    unit : flag
        Return quantity with units
    method : str
        Method for evaluating merge times
        DOP853 is the fastest one in my tests (not going all the way to merger)
    return_ecc : bool
        Flag for returning eccentricity as well as orbital separation

    Returns
    -------
    sep : float
        Final orbital separation
    ecc : float
        Final orbital eccentricity
    """
    # Case 0: No eccentricity was given in the first place
    if (e0 is None) or (method in ["circ", "circle", "circular"]):
        if return_ecc:
            return orbital_separation_evolve_circ(m1,m2,a0,evolve_time), 0.
        else:
            return orbital_separation_evolve_circ(m1,m2,a0,evolve_time)
    #### If not Case 0, we need to check inputs ####
    # Initialize af
    af = None
    ef = None
    ## Check units
    if hasattr(m1, "unit"):
        # Check for kg
        if m1.unit == u.kg:
            m1 = m1.value
            unit = True
        elif m1.unit.is_equivalent(u.kg):
            m1 = m1.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m1 should have units kg, but has units {m1.unit}")
    ## Check units
    if hasattr(m2, "unit"):
        # Check for kg
        if m2.unit == u.kg:
            m2 = m2.value
            unit = True
        elif m2.unit.is_equivalent(u.kg):
            m2 = m2.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m2 should have units kg, but has units {m2.unit}")
    ## Check units
    if hasattr(a0, "unit"):
        # Check for m
        if a0.unit == u.m:
            a0 = a0.value
            unit = True
        elif a0.unit.is_equivalent(u.m):
            a0 = a0.to(u.m).value
            unit = True
        else:
            raise ValueError(
                f"a0 should have units m, but has units {a0.unit}")
    ## Check units
    if hasattr(evolve_time, "unit"):
        # Check for m
        if evolve_time.unit == u.s:
            evolve_time = evolve_time.value
            unit = True
        elif evolve_time.unit.is_equivalent(u.s):
            evolve_time = evolve_time.to(u.s).value
            unit = True
        else:
            raise ValueError(
                f"evolve_time should have units s, but has units {evolve_time.unit}")

    # Estimate constant of motion
    c0 = a0 * peters_ecc_const(e0)
    # Okay, now 
    # Case 1: It's an ODE method
    if method in IVP_METHODS:
        # Solve ODE way
        ivp_out, err = eccentric_ODE_integration(
            m1,m2,a0,e0,
            Teval=evolve_time,
            method=method,
        )
        ef = ivp_out.y[-1]
        if np.size(ef) > 1:
            ef = ef[-1]
    elif method in MERGE_TIME_METHODS:
        if ("circ" in method) or ("Circ" in method):
            # Solve merge time way
            af = orb_sep_evol_sgl_opt(
                m1,m2,a0,evolve_time,e0,
                method=method,
            )
            # Solve for e
            if return_ecc:
                # Calculate ef
                ef = ecc_of_a0_e0_a1(a0,e0,af)
        else:
            # Solve merge time way for ecc
            ef = orb_ecc_evol_sgl_opt(
                m1,m2,a0,evolve_time,e0,
                method=method,
            )
    else:
        raise ValueError(f"Unknown method {method}")
    # Calculate af
    if unit and (af is None):
        af = c0 * u.m / peters_ecc_const(ef)
    elif (af is None):
        af = c0 / peters_ecc_const(ef)
    elif unit:
        af = af * u.m
    else:
        assert af.unit.is_equivalent(u.m)
    # Return value
    if return_ecc:
        return af, ef
    else:
        return af

def orbital_separation_evolve_arr(
        m1, m2, a0, evolve_time,
        e0=None,
        unit=False,
        method="DOP853",
        return_ecc=False,
        **kwargs
    ):
    """Evolve several eccentric binaries by using a specified method

    Parameters
    ----------
    m1 : float
        Primary mass (without astropy units, assumes kg)
    m2 : float
        Secondary mass (without astropy units, assumes kg)
    a0 : float
        Initial semi-major axis (without astropy units, assumes meters)
    evolve_time : float
        Time to evolve binary for
    e0 : float
        Initial eccentricities
    unit : flag
        Return quantity with units
    method : str
        Method for evaluating merge times
        DOP853 is the fastest one in my tests (not going all the way to merger)
    return_ecc : bool
        Flag for returning eccentricity as well as orbital separation

    Returns
    -------
    sep : float
        Final orbital separation
    ecc : float
        Final orbital eccentricity
    """
    # Case 0: No eccentricity was given in the first place
    if (e0 is None) or (method in ["circ", "circle", "circular"]):
        if return_ecc:
            return orbital_separation_evolve_circ(m1,m2,a0,evolve_time), 0.
        else:
            return orbital_separation_evolve_circ(m1,m2,a0,evolve_time)
    #### If not Case 0, we need to check inputs ####
    # Initialize af
    af = None
    ef = None
    ## Check units
    if hasattr(m1, "unit"):
        # Check for kg
        if m1.unit == u.kg:
            m1 = m1.value
            unit = True
        elif m1.unit.is_equivalent(u.kg):
            m1 = m1.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m1 should have units kg, but has units {m1.unit}")
    ## Check units
    if hasattr(m2, "unit"):
        # Check for kg
        if m2.unit == u.kg:
            m2 = m2.value
            unit = True
        elif m2.unit.is_equivalent(u.kg):
            m2 = m2.to(u.kg).value
            unit = True
        else:
            raise ValueError(
                f"m2 should have units kg, but has units {m2.unit}")
    ## Check units
    if hasattr(a0, "unit"):
        # Check for m
        if a0.unit == u.m:
            a0 = a0.value
            unit = True
        elif a0.unit.is_equivalent(u.m):
            a0 = a0.to(u.m).value
            unit = True
        else:
            raise ValueError(
                f"a0 should have units m, but has units {a0.unit}")
    ## Check units
    if hasattr(evolve_time, "unit"):
        # Check for m
        if evolve_time.unit == u.s:
            evolve_time = evolve_time.value
            unit = True
        elif evolve_time.unit.is_equivalent(u.s):
            evolve_time = evolve_time.to(u.s).value
            unit = True
        else:
            raise ValueError(
                f"evolve_time should have units s, but has units {evolve_time.unit}")
    # Check for single
    if (isinstance(m1, float) or isinstance(m1, np.float64)) and \
       (isinstance(m2, float) or isinstance(m2, np.float64)) and \
       (isinstance(a0, float) or isinstance(a0, np.float64)) and \
       (isinstance(evolve_time,  float) or isinstance(evolve_time,  np.float64)):
        return orbital_separation_evolve_sgl(
            m1,m2,a0,evolve_time,
            e0=e0,
            unit=unit,
            method=method,
            return_ecc=return_ecc,
            **kwargs
        )
    ## Check m1 ##
    if not isinstance(m1, np.ndarray):
        raise TypeError("m1 should be a numpy array, but is ", type(m1))
    if len(m1.shape) != 1:
        raise RuntimeError("m1 should be 1D array, but is ", m1.shape)
    ## Check m2 ##
    if not isinstance(m2, np.ndarray):
        raise TypeError("m2 should be a numpy array, but is ", type(m2))
    if len(m2.shape) != 1:
        raise RuntimeError("m2 should be 1D array, but is ", m2.shape)
    ## Check a0 ##
    if not isinstance(a0, np.ndarray):
        raise TypeError("a0 should be a numpy array, but is ", type(a0))
    if len(a0.shape) != 1:
        raise RuntimeError("a0 should be 1D array, but is ", a0.shape)
    ## Check e0 ##
    if not isinstance(e0, np.ndarray):
        raise TypeError("e0 should be a numpy array, but is ", type(e0))
    if len(e0.shape) != 1:
        raise RuntimeError("e0 should be 1D array, but is ", e0.shape)
    ## Check dimensions ##
    if not (m1.size == m2.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, m2.size = %d"%(
            m1.size, m2.size))
    if not (m1.size == a0.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, a0.size = %d"%(
            m1.size, a0.size))
    if not (m1.size == e0.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, e0.size = %d"%(
            m1.size, e0.size))

    ## Check for methods compatible with vectorization
    if method in ["circ_numpy"]:
        return orbital_separation_evolve_circ_numpy(m1,m2,a0,evolve_time)
    ## Default to loop over single-valued function
    else:
        # Initialize value
        ef = np.zeros(m1.size)
        af = np.zeros(m1.size)
        # Check return_ecc
        if return_ecc:
            for i in range(m1.size):
                # Check evolve time
                if np.size(evolve_time) == 1:
                    _evolve_time = evolve_time
                else:
                    _evolve_time = evolve_time[i]
                # Get value
                af[i], ef[i] = orbital_separation_evolve_sgl(
                    m1[i],m2[i],a0[i],_evolve_time,
                    e0=e0[i],
                    method=method,
                    return_ecc=True,
                    **kwargs
                   )
        # No eccentricity values here!
        else:
            for i in range(m1.size):
                # Check evolve time
                if np.size(evolve_time) == 1:
                    _evolve_time = evolve_time
                else:
                    _evolve_time = evolve_time[i]
                # Get value
                af[i] = orbital_separation_evolve_sgl(
                    m1[i],m2[i],a0[i],_evolve_time,
                    e0=e0[i],
                    method=method,
                    **kwargs
                   )
        # Check units
        if unit:
            af = af * u.m
        # Return things
        if return_ecc:
            return af, ef
        else:
            return af

def orbital_separation_evolve(m1, m2, a0, *args, **kwargs):
    """Evolve one or more binaries by using a specified method

    Parameters
    ----------
    m1 : float
        Primary mass (without astropy units, assumes kg)
    m2 : float
        Secondary mass (without astropy units, assumes kg)
    a0 : float
        Initial semi-major axis (without astropy units, assumes meters)

    Returns
    -------
    sep : float
        Final orbital separation
    ecc : float
        Final orbital eccentricity
    """
    if np.size(a0) == 1:
        return orbital_separation_evolve_sgl(m1,m2,a0,*args,**kwargs)
    else:
        # Check on possible strange combinations of inputs
        if (np.size(m1) == 1) and (np.size(m2) == 1):
            m1 = m1 * np.ones(a0.size)
            m2 = m2 * np.ones(a0.size)
        if ("e0" in kwargs) and (np.size(kwargs["e0"]) == 1):
            kwargs["e0"] = kwargs["e0"] * np.ones(a0.size)
        # Return array version
        return orbital_separation_evolve_arr(m1,m2,a0,*args,**kwargs)

def orbital_period_evolve(m1, m2, a0, *args, **kwargs):
    """Evolve one or more binaries by using a specified method

    Parameters
    ----------
    m1 : float
        Primary mass (without astropy units, assumes kg)
    m2 : float
        Secondary mass (without astropy units, assumes kg)
    a0 : float
        Initial semi-major axis (without astropy units, assumes meters)

    Returns
    -------
    period : float
        Orbital period of an evolved set of binaries
    """
    # Check if third positional argument has units of seconds
    if hasattr(a0,'unit') and a0.unit.is_equivalent(u.s):
        # Get initial separation
        a0 = a_of_m1_m2_forb(m1,m2,1/a0)
    # Evolve separation
    if np.size(a0) == 1:
        sep = orbital_separation_evolve_sgl(m1,m2,a0,*args,**kwargs)
    else:
        # Check on possible strange combinations of inputs
        if (np.size(m1) == 1) and (np.size(m2) == 1):
            m1 = m1 * np.ones(a0.size)
            m2 = m2 * np.ones(a0.size)
        if ("e0" in kwargs) and (np.size(kwargs["e0"]) == 1):
            kwargs["e0"] = kwargs["e0"] * np.ones(a0.size)
        # Return array version
        sep = orbital_separation_evolve_arr(m1,m2,a0,*args,**kwargs)
    # Get orbital period
    return orbital_period_of_m1_m2_a(m1, m2, sep)

######## Main -- for testing ########
def main():
    m1 = 1. * u.solMass
    m2 = 1. * u.solMass
    e0 = 0.5
    a0 = 1.e-3 * u.AU
    circular_ODE_integration(m1,m2,a0)
    eccentric_ODE_integration(m1,m2,a0,e0)
    #ecc_integration_time(m1,m2,a0,e0)

    print("Success!")
    return

######## Execution -- for testing ########
if __name__ == "__main__":
    main()
