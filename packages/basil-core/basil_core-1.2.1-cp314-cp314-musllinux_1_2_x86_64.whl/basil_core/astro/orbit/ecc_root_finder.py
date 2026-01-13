"""Equations of motion for orbital decay"""
######## Imports ########
#### Standard Library ####
import time
import warnings
#### Third party ####
import numpy as np
from scipy.optimize import newton, fsolve, minimize
from scipy.integrate import solve_ivp
from astropy import units as u
from astropy import constants as const
import matplotlib.pyplot as plt

######## Functions ########

def f_enhancement(e):
    """Enhancement factor f(e)"""
    e2 = e**2
    return (1 + (73/24)*e2 + (37/96)*e2**2) / (1 - e2)**(7/2)

def c0_from_initial(a_0, e_0):
    """Calculate c_0 from initial conditions"""
    return a_0 * e_0**(-12/19) * (1 - e_0**2) * (1 + (121/304)*e_0**2)**(-870/2299)

def sep_of_ecc(e, c0):
    """Return the separation as a function of e and c0"""
    return c0*((e**(12/19))/(1 - e**2)) * (1 + (121/304)*e**2)**(870/2299)

def sep_check(a_0, e_0):
    """Test something"""
    c0 = c0_from_initial(a_0, e_0)
    sep = sep_of_ecc(e_0, c0)
    fail_mask = np.abs(sep - a_0)/a_0 > 1.e-8
    if any(fail_mask):
        print(f"sep_check failures:")
        print(f"  a_0: {a_0[fail_mask]}")
        print(f"  e_0: {e_0[fail_mask]}")
        print(f"  c0: {c0[fail_mask]}")
        print(f"  sep: {sep[fail_mask]}")
        print(f"  {np.sum(fail_mask)} of {np.size(fail_mask)} fail np.allclose")
        print(f"  |a_0 - sep|: {np.abs(a_0[fail_mask] - sep[fail_mask])}")
        raise RuntimeError("Vera's math was wrong")

def de_dt_peters(e, beta, c0):
    """Peters equation 5.50: de/dt"""
    numerator = e**(-67/19) * (1 - e**2)**(3/2)
    denominator = (1 + (121/304)*e**2)**(1181/2299)
    return (-19/12) * (beta / c0**4) * (numerator / denominator)

def time_to_merge(a_0, e_0, beta, c0=None):
    if e_0 == 0.0:
        return (a_0**4 / (4 * beta)).to('s')
    if c0 is None:
        c0 = c0_from_initial(a_0,e_0)
    return (a_0**4 / (4 * beta * f_enhancement(e_0))).to('s')

def objective_guess_circ(a_0, e_0, beta, delta_t, c0):
    """Equation to make a guess for minimize method"""
    # Estimate a0^4/f(e0)
    scaled_separation = a_0**4
    # Estimate beta part
    beta_part = 4 * beta * delta_t
    separation = np.abs(scaled_separation - beta_part)**(1/4)
    ecc = (separation / c0)**(19/12)
    return ecc

def objective_guess_second_order(a_0, e_0, beta, delta_t, c0):
    """Guess with terms of order e^2"""
    # Estimate a0^4/f(e0)
    scaled_separation = a_0**4 / f_enhancement(e_0)
    # Estimate beta part
    beta_part = 4 * beta * delta_t
    # Estimate the sane part
    sane_part = (scaled_separation /beta_part)/c0**4
    if not np.all(sane_part > 0):
        raise Exception
    #
    ecc = sane_part**(19/48)
    return ecc


def objective_guess_high_ecc(a_0, e_0, beta, delta_t, c0):
    """Equation to make a guess for minimize method"""
    # Estimate a0^4/f(e0)
    scaled_separation = a_0**4 / f_enhancement(e_0)
    # Estimate beta part
    beta_part = 4 * beta * delta_t
    rhs = (scaled_separation - beta_part)
    c1 = c0*(425/304)**(870/2299)

    ecc = (separation / c0)**(19/12)
    return ecc

def objective_function(e_f, a_0, e_0, beta, delta_t, c0):
    """
    Objective function to minimize for e_f using bounded optimization.
    We minimize the squared residual of the equation.
    """
    # Catch bounds
    if np.all(e_f < 0):
        return 1e10
    if np.all(e_f >= 1):
        return 1e10
    # Estimate this thing I'm going to call the determinant
    determinant = (a_0**4/f_enhancement(e_0) - 4 * beta * delta_t)
    # Avoid boundary issues
    if np.all(determinant < 0):
        return 1e10
    # Evaluate remaining samples
    return np.abs((determinant * f_enhancement(e_f))**(1/4) - sep_of_ecc(e_f,c0))/a_0

def objective_test(a_0, e_0, beta, delta_t):
    """Test the objective function"""
    # Get c0
    c0 = c0_from_initial(a_0, e_0)
    # Get value of objective function for no change
    obj_check = objective_function(e_0, a_0, e_0, beta, 0, c0)
    # Check for failures
    fail_mask = np.abs(obj_check) > 1e-5
    if any(fail_mask):
        print(f"objective test failure")
        print(f"  a_0: {a_0[fail_mask]}")
        print(f"  e_0: {e_0[fail_mask]}")
        print(f"  beta: {beta[fail_mask]}")
        print(f"  zero time error: {obj_check}")
        raise RuntimeError("Vera's math is wrong")

def eccentric_binary_evolution(e_0_arr, a_0_arr, beta_arr, delta_t_arr, rtol=1e-5):
    """
    Evolve eccentric binary systems using scipy.minimize
    
    Parameters:
    -----------
    e0_arr, a0_arr, beta_arr, delta_t_arr : arr-like
        Initial conditions and evolution parameters
    
    Returns:
    --------
    dict containing results from requested methods
    """
    # Convert to numpy arrs
    e_0_arr = np.asarray(e_0_arr)
    a_0_arr = np.asarray(a_0_arr)
    beta_arr = np.asarray(beta_arr)
    delta_t_arr = np.asarray(delta_t_arr)
    # Get c_0
    c0 = c0_from_initial(a_0_arr, e_0_arr)
    
    n_systems = len(e_0_arr)
    results = {}
    
    print("Running minimiz method...")
    start_time = time.time()
        
    # Estimate merge time to check inputs
    merge_time = time_to_merge(a_0_arr, e_0_arr, beta_arr, c0=c0)
    if np.any(merge_time < delta_t_arr):
        raise RuntimeError("You tried to evolve past merger")
    # initialize final eccentricity
    e_final_minimize = np.zeros(n_systems)
    # Initialize error
    error = np.zeros(n_systems)

    ## Guesswork
    # Initial guess for ef
    e_f_guess = objective_guess_circ(a_0_arr, e_0_arr, beta_arr, delta_t_arr, c0)
    # Print error of guess
    e_f_guess_fun = objective_function(e_f_guess, a_0_arr, e_0_arr, beta_arr, delta_t_arr, c0)

    # Get second order guess
    e_f_guess2 = objective_guess_second_order(a_0_arr, e_0_arr, beta_arr, delta_t_arr, c0)
    # Print error of guess
    e_f_guess_fun2 = objective_function(e_f_guess2, a_0_arr, e_0_arr, beta_arr, delta_t_arr, c0)
    # Check where the error is lower for guess 2
    mask_second_order = e_f_guess_fun2 < e_f_guess_fun
    print(f"Second order guess is better {np.sum(mask_second_order)/np.size(mask_second_order) * 100}% of the time!")
    e_f_guess[mask_second_order] = e_f_guess2[mask_second_order]
    e_f_guess_fun[mask_second_order] = e_f_guess_fun2[mask_second_order]

    # Get more guesses
    e_f_guess_new = 0.9*e_0_arr
    e_f_guess_new_err = objective_function(e_f_guess_new,a_0_arr,e_0_arr,beta_arr,delta_t_arr,c0)
    mask_guess = e_f_guess_new_err < e_f_guess_fun
    print(f"New guess helped {np.sum(mask_guess)/np.size(mask_guess) * 100}% of the time!")
    e_f_guess[mask_guess] = e_f_guess_new[mask_guess]
    e_f_guess_fun[mask_guess] = e_f_guess_new_err[mask_guess]

    # Get more guesses
    e_f_guess_new = 0.99*e_0_arr
    e_f_guess_new_err = objective_function(e_f_guess_new,a_0_arr,e_0_arr,beta_arr,delta_t_arr,c0)
    mask_guess = e_f_guess_new_err < e_f_guess_fun
    print(f"New guess helped {np.sum(mask_guess)/np.size(mask_guess) * 100}% of the time!")
    e_f_guess[mask_guess] = e_f_guess_new[mask_guess]
    e_f_guess_fun[mask_guess] = e_f_guess_new_err[mask_guess]

    # Get more guesses
    e_f_guess_new = 0.1*e_0_arr
    e_f_guess_new_err = objective_function(e_f_guess_new,a_0_arr,e_0_arr,beta_arr,delta_t_arr,c0)
    mask_guess = e_f_guess_new_err < e_f_guess_fun
    print(f"New guess helped {np.sum(mask_guess)/np.size(mask_guess) * 100}% of the time!")
    e_f_guess[mask_guess] = e_f_guess_new[mask_guess]
    e_f_guess_fun[mask_guess] = e_f_guess_new_err[mask_guess]

    # Get more guesses
    e_f_guess_new = 0.01*e_0_arr
    e_f_guess_new_err = objective_function(e_f_guess_new,a_0_arr,e_0_arr,beta_arr,delta_t_arr,c0)
    mask_guess = e_f_guess_new_err < e_f_guess_fun
    print(f"New guess helped {np.sum(mask_guess)/np.size(mask_guess) * 100}% of the time!")
    e_f_guess[mask_guess] = e_f_guess_new[mask_guess]
    e_f_guess_fun[mask_guess] = e_f_guess_new_err[mask_guess]


    # Enter loop
    for i in range(n_systems):
        # Use L-BFGS-B with bounds
        result = minimize(
            objective_function,
            x0=[e_f_guess[i]],
            args=(a_0_arr[i], e_0_arr[i], beta_arr[i], delta_t_arr[i], c0[i]),
            method='L-BFGS-B',
            bounds=[(0.,e_0_arr[i])],
            options={'ftol': 1e-12, 'gtol': 1e-8},
        )
        # Assign value
        e_final_minimize[i] = result.x[0]
        # Assign error
        error[i] = result.fun
    # Once we're done we check the errors
    bad = error > rtol
    if any(bad):
        warnings.warn(f"eccentricity of chirp time: " + \
            f"{np.sum(bad)} / {np.size(bad)} systems have error greater" + \
            f"than {rtol}")
    # Check for worse systems
    worse = (error > 0.1) & (e_0_arr < 0.9)
    if any(worse):
        raise RuntimeError(f"eccentricity of chirp time: " + \
            f"{np.sum(worse)} / {np.size(worse)} systems have error greater" +\
            f"than 10% and have eccentricity < 0.9")

    minimize_time = time.time() - start_time
    results['minimize'] = {
        'e_final': e_final_minimize,
        'computation_time': minimize_time,
        'time_per_system': minimize_time / n_systems
    }
    print(f"Minimize method completed in {minimize_time:.3f}s ({minimize_time/n_systems*1000:.3f}ms per system)")
    
    return results

def plot_error_analysis(e_0_arr, a_0_arr, beta_arr, delta_t_arr, results):
    """Create scatter plots of errors as a function of initial eccentricity"""
    
    # Calculate errors
    minimize_results = results['minimize']['e_final']
    
    # Remove NaN values for plotting
    minimize_mask = ~np.isnan(minimize_results)
    
    # Get c0
    c0 = c0_from_initial(a_0_arr, e_0_arr)
    # Get minimize errors
    minimize_errors = objective_function(
        results['minimize']['e_final'][minimize_mask],
        a_0_arr[minimize_mask],
        e_0_arr[minimize_mask],
        beta_arr[minimize_mask],
        delta_t_arr[minimize_mask],
        c0[minimize_mask],
    )
    # Create figure with subplots
    fig, ax = plt.subplots(1, 1, figsize=(6, 5))
    
    # Absolute error plot
    ax.scatter(e_0_arr[minimize_mask], np.abs(minimize_errors)/minimize_results, alpha=0.6, s=20, label='minimize')
    ax.set_xlabel('Initial Eccentricity $e_0$')
    ax.set_ylabel('Objective Function Error')
    ax.set_title('Objective Function Error vs Initial Eccentricity')
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig("orbital_shrinkage.png")
    
    # Print some statistics
    print(f"\nError Analysis:")
    print(f"Number of finite comparisons: {np.sum(np.isfinite(minimize_results))}")
    print(f"Median absolute error: {np.median(minimize_errors):.2e}")
    if np.sum(minimize_mask) > 20:
        print(f"95th percentile absolute error: {np.percentile(minimize_errors, 95):.2e}")

######### main ########
def main():
    # Test parameters
    n_test = 10000

    # Identify sensible betas
    const_G_c = (64/5) * (const.G.si**3) * const.c.si**-5
    beta_const = const_G_c * (1. * u.solMass)**2 * (2. * u.solMass)
    beta_const = beta_const.si
    
    # Generate test data with your specifications
    e_0_test = np.random.uniform(0.0, 1.0, n_test)  # Changed: 0 to 1
    a_0_test = np.random.uniform(1e-3, 1e-1, n_test) * u.au  # Convert AU to meters
    a_0_test = a_0_test.si.value
    beta_test = np.full(n_test, beta_const.value)  # Fixed value in SI units
    merge_time = time_to_merge(a_0_test, e_0_test, beta_test, c0=None)
    delta_t_test = np.random.uniform(size=n_test) * merge_time  # Convert years to seconds
    # Generate c0
    c0_test = c0_from_initial(a_0_test, e_0_test)

    # Test our separation
    sep_check(a_0_test, e_0_test)

    # Test the objective function
    objective_test(a_0_test, e_0_test, beta_test, delta_t_test)
    
    print(f"Test parameters:")
    print(f"Number of systems: {n_test}")
    print(f"e_0 range: [{np.min(e_0_test):.3f}, {np.max(e_0_test):.3f}]")
    print(f"a_0 range: [{np.min(a_0_test):.4f}, {np.max(a_0_test):.4f}] m")
    print(f"beta: {beta_test[0]:.1e} (SI units)")
    print(f"Δt range: [{np.min(delta_t_test):.1e}, {np.max(delta_t_test):.1e}] sec")
    print()
    
    # Run both methods
    results = eccentric_binary_evolution(
        e_0_test, a_0_test, beta_test, delta_t_test)
    
    # Print some results
    print(f"\nSample results (first 5 systems):")
    print("Initial e:", e_0_test[:5])
    print("Minimize e_f:", results['minimize']['e_final'][:5])
    
    # Create error analysis plots
    plot_error_analysis(e_0_test, a_0_test, beta_test, delta_t_test, results)

######### Execution ########
if __name__ == "__main__":
    main()
