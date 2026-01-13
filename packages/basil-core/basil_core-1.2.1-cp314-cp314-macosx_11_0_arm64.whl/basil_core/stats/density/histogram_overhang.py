'''Utilities for density function methods

I have developed some rather baroque methods of constructing
    histogram-based density estimates, and they require utility functions
    provided here.
'''

######## Imports ########
import numpy as np
from fast_histogram import histogram1d, histogram2d, histogramdd
from basil_core.stats.density.density_utils import prune_samples
import sys

######## General histogram methods ########

def weighted_histogram_density_error(raw_hist_output, N, dx):
    '''Estimate error values for histogram bins

    Thanks Richard

    Parameters
    ----------
    raw_histogram_output: array like
        Counts for histogram bins
    nsample: int
        Number of samples used to construct the histogram

    Returns
    -------
    y_density: np.ndarray
        Scaled histogram output
    sig_density: np.ndarray
        Estimated counting error for histogram output
    '''
    # Calculate the sum of the histogram
    y_sum = np.sum(raw_hist_output)
    # Identify dimensionless p
    p = raw_hist_output / y_sum
    # Identify dimensionless q
    q = 1. - p

    # Rescale quantities
    y_density = raw_hist_output / (y_sum * dx)
    # sig_density
    sig_density = np.sqrt(p*q*y_sum)/(N*dx)
    return y_density, sig_density

def bin_combination_seeds(ndim, max_bins):
    '''Lists all possible starting bin configurations

    Parameters
    ----------
    ndim: int
        Dimensionality of data
    max_bins: int
        Maximum number of bins in one dimension

    Returns
    -------
    reduced_combinations: np.ndarray, dtype=int, shape=(X,ndim)
        Returns unique combinations of indices for which incrementing
        each dimension by one simultaneously will explore the entire subspace.

    ex:
        bin_combinations_seeds(2, 3)
        # ndim = 2
        # max_bins = 3
        
        Forget for a moment that you can't have zero bins.

        ALL combinations are: 
        [0,0], [0,1], [0,2], [0,3], [1,0], [1,1], [1,2], [1,3]
        [2,0], [2,1], [2,2], [2,3], [3,0], [3,1], [3,2], [3,3]
       
       However, [1,1] is explored when incrementing +1/+1 from [0,0],
            so it is not needed as a seed for the binning algorithm.
      
        Only the bin combinations:
        [0,0], [0,1], [0,2], [0,3], [1,0], [2,0], [3,0]
        are necessary to explore the space of integers for max_bins = 3
            when incrementing +1/+1 from the bin "seeds"
    '''
    # Initialize max_bins as an array
    max_bins = np.ones(ndim, dtype=int) * max_bins
    # Initialize grid slices
    slices = []
    # loop the dimensions
    for i in range(ndim):
        # Add slices
        slices.append(slice(max_bins[i]))
    # Generate the grid
    bin_combinations = np.mgrid[slices].reshape(ndim, np.prod(max_bins)).T
    # Find bin combinations that aren't equal to an incremented bin combination
    reduced = []
    # Loop the bin combinations
    for item in bin_combinations:
        # Initialize finder
        found = False
        # Check bins in reduced
        for jtem in reduced:
            # Loop indices up to max_bins
            for k in range(max(max_bins)):
                # Check for identical combinations displaced by k
                if all((item - k) == jtem):
                    # Indicate this combination has been found
                    found = True
        # Append unfound to reduced
        if not found:
            reduced.append(item)

    # Make reduced an array
    reduced_combinations = np.asarray(reduced)
    return reduced_combinations

######## histogram overhang utils ########

def histogram_overhang_bins_of_ndim(ndim):
    '''Verifies that more area is inside the box than outside

    When allowing half of a histogram bin to be empty by placing
        its center on a boundary, there will be some minimum number
        of bins for a k dimensional histogram to ensure that
        more volume is inside of the boundary than outside of the boundary.

    Finds the minimum n for which:

    .. math::
        (n+1)/n < 2^{1/k}

    Parameters
    ----------
    ndim: int
        The number of dimensions for the histogram
   
    Returns
    -------
    n: int
        The minimum number of bins for which more volume is enclosed by the
            boundary than is outside of the boundary.
    '''
    # Assert ndim is an integer
    assert isinstance(ndim, int)
    # Calculate the right hand side
    rhs = 2**(1./float(ndim))
    # Initialize the left hand side
    lhs = 2.
    # Initialize n
    n = 1
    while lhs > rhs:
        # Update n
        n += 1
        # Update the left hand side
        lhs = (n+1) / n

    return n

def histogram_overhang_edge_factor(bin_centers):
    ''' Account for the reduction in volume on account of bins overhanging
        a boundary

    When allowing half of a histogram bin to be empty by placing its center
        on a boundary in each dimension,
        it is useful to estimate how to correct the density function for
        each bin.

    Parameters
    ----------
    bin_centers: array-like, shape=(npts, ndim), dtype=float
        The coordinates for the center of each bin

    Returns
    -------
    edge_factor: array-like, shape=(npts,), dtype=int
        The density correction for each bin
    '''
    # Get information from the shape of bin_centers
    npts, ndim = bin_centers.shape
    # Initialize boolean array
    edge_factor = np.ones((npts,),dtype=int)
    # Loop each dimension
    for i in range(ndim):
        # Multiply the lower edge bin factors by 2
        # This works because all of the centers placed on a boundary will be 
        # roughly identical
        edge_factor[np.isclose(bin_centers[:,i], np.min(bin_centers[:,i]))] *= 2
        edge_factor[np.isclose(bin_centers[:,i], np.max(bin_centers[:,i]))] *= 2
    return edge_factor

######## Histogram Overhang Gaussian Process Estimate Nonparametric object ########

class HOGPEN(object):
    '''Represents a nonparametric density constructed from histograms in trunctaed spaces

    HOGPEN: Histogram Overhang Gaussian Process Estimate Nonparametric
    '''
    def __init__(
                 self,
                 x_sample,
                 limits,
                 weights=None,
                 verbose=False,
                ):
        '''Construct a HOGPEN object

        Parameters
        ----------
        x_sample: array like, shape = (samples, ndim)
            The samples we would like to marginalize
        limits: array like, shape = (ndim, 2)
            Limits for the histograms
        weights: array like, shape = (samples,), optional
            Weights for each x_sample

        Returns
        -------
        self: HOGPEN object
            The object with methods for fitting the samples
        '''
        # TODO: need to define ``n`` in docstring.

        # Extract information
        nsamples, ndim = x_sample.shape
        # Check limits
        assert limits.shape[0] == ndim
        # Check weights
        if not (weights is None):
            assert weights.size == nsamples

        # Prune samples not in limits
        keep = prune_samples(x_sample, limits)
        if np.sum(keep) == 0:
            raise RuntimeError("No samples found in ",limits)
        if np.sum(keep) != nsamples:
            print("Warning: pruning %f fraction of samples"%(
                (nsamples - np.sum(keep))/nsamples),
                file=sys.stderr)

        # Store useful information
        self.ndim = ndim
        self.nsamples = nsamples
        self.x_sample = x_sample[keep]
        self.limits = limits
        if weights is None:
            self.weights = None
        else:
            self.weights = weights[keep]
        self.verbose = verbose

    def fit_hist1d(self, bins, index, grab_edge=False):
        '''Fit a 1d histogram of the marginal

        Parameters
        ----------
        bins: int
            Number of bins to use
        index: int
            Axis along which to make the histogram
        grab_edge: bool, optional
            Special bins for edges.  If enabled, ensures the histogram has bins
            hanging halfway off the sample space.
            Since we pruned samples outside of our limits, this means our
            edge-bins are effectively half as large, but allows us to compute
            the histogram with uniform bin widths.

        Returns
        -------
        x_train: np.ndarray
            Histogram bin centers
        y_train: np.ndarray
            Histogram values (density weighting)
        sig_density: np.ndarray
            Histogram counting error (density weighting)
        '''
        # TODO: shorten explanation of ``grab_edge``, it's too technical

        # Extract limits
        limits = np.asarray(self.limits[index]).copy()
        # Assert our metric scale lengths
        dx = (limits[1] - limits[0])/bins

        ## Generate edges ##
        if grab_edge:
            # Create the edge hanging bins
            # Increase the number of bins to lean off the edge
            # Note: try very hard not to mutate bins
            bins = bins + 1
            # Extend limits
            limits[0] -= 0.5*dx
            limits[1] += 0.5*dx

        ## Build meshgrid ##
        # Initialize the eval string
        if grab_edge:
            x_train = np.linspace(
                                  self.limits[0][0],
                                  self.limits[0][1],
                                  bins,
                                 )[:,None]
        else:
            x_train = np.linspace(
                                  limits[0]+0.5*dx,
                                  limits[1]-0.5*dx,
                                  bins,
                                 )[:,None]

        # Generate histogram data
        y_train = histogram1d(
                              self.x_sample[:,index],
                              range=limits,
                              bins=bins,
                              weights=self.weights,
                             )

        # Identify the dA value
        if grab_edge:
            dx = dx / histogram_overhang_edge_factor(x_train)

        # Normalize normally
        y_density, sig_density = \
            weighted_histogram_density_error(
                                             y_train,
                                             self.x_sample.shape[0],
                                             dx,
                                            )

        return x_train, y_density, sig_density

    def fit_hist2d(self, bins, index, jndex, grab_edge=False):
        '''Fit a 1d histogram of the marginal

        Parameters
        ----------
        index: int
            Axis along which to make the histogram's first dimension
        jndex: int
            Axis along which to make the histogram's second dimension
        bins: int
            Number of bins to use
        grab_edge: bool, optional
            Special bins for edges.  If enabled, ensures the histogram has bins
            hanging halfway off the sample space.
            Since we pruned samples outside of our limits, this means our
            edge-bins are effectively half as large, but allows us to compute
            the histogram with uniform bin widths.

        Returns
        -------
        x_train: np.ndarray
            Histogram bin centers
        y_train: np.ndarray
            Histogram values (density weighting)
        sig_density: np.ndarray
            Histogram counting error (density weighting)
        '''
        # TODO: rename ``jndex``

        # Make bins an array
        bins = bins*np.ones(2,dtype=int)
        # Extract limits
        limits = np.asarray([self.limits[index],self.limits[jndex]])
        # Assert our metric scale lengths
        dx = (limits[:,1] - limits[:,0])/bins
        # Identify the dV value
        dA = np.prod(dx)

        ## Generate edges ##
        if grab_edge:
            # Create the edge hanging bins
            # Increase the number of bins to lean off the edge
            # Note: try very hard not to mutate bins
            bins = bins + 1
            # Extend limits
            limits[0,0] -= 0.5*dx[0]
            limits[0,1] += 0.5*dx[0]
            limits[1,0] -= 0.5*dx[1]
            limits[1,1] += 0.5*dx[1]

        ## Build meshgrid ##
        if grab_edge:
            slices = [
                      slice(self.limits[index][0], self.limits[index][1], bins[0]*1j),
                      slice(self.limits[jndex][0], self.limits[jndex][1], bins[1]*1j),
                     ]
        else:
            slices = [
                      slice(limits[0][0]+0.5*dx[0], limits[0][1]-0.5*dx[0], bins[0]*1j),
                      slice(limits[1][0]+0.5*dx[1], limits[1][1]-0.5*dx[1], bins[1]*1j),
                     ]
        # Generate sample space
        sample_space = np.mgrid[slices]

        # Reshape the sample space
        # This step prevents garbling of dimensions
        sample_space = sample_space.reshape(2, np.prod(bins))
        # Transpose this sample space for a list of points
        x_train = sample_space.T

        # Generate histogram data
        y_train = histogram2d(
                              self.x_sample[:,index],
                              self.x_sample[:,jndex],
                              range=[
                                     limits[0],
                                     limits[1]
                                    ],
                              bins=bins,
                              weights=self.weights,
                             ).flatten()

        # Identify the dA value
        if grab_edge:
            dA = dx[0]*dx[1] / histogram_overhang_edge_factor(x_train)

        # Normalize normally
        y_density, sig_density = \
            weighted_histogram_density_error(
                                             y_train,
                                             self.x_sample.shape[0],
                                             dA,
                                            )

        return x_train, y_density, sig_density

    def fit_histdd(self, indices, bins, grab_edge=False):
        '''Fit a high dimensinoal histogram of the distribution

        Parameters
        ----------
        indices: list of int
            Axes along which to make each of the histogram's dimensions
        bins: int
            Number of bins to use
        grab_edge: bool, optional
            Special bins for edges.  If enabled, ensures the histogram has bins
            hanging halfway off the sample space.
            Since we pruned samples outside of our limits, this means our
            edge-bins are effectively half as large, but allows us to compute
            the histogram with uniform bin widths.

        Returns
        -------
        x_train: np.ndarray
            Histogram bin centers
        y_train: np.ndarray
            Histogram values (density weighting)
        sig_density: np.ndarray
            Histogram counting error (density weighting)

        .. warning:: It's not advised to use more than three dimensions
        '''
        # Check indices
        indices = np.asarray(indices,dtype=int)
        assert len(indices.shape) == 1
        assert len(indices) <= self.ndim
        # How many dimensions are we fitting?
        fit_dim = len(indices)

        # Initialize bins
        if np.asarray(bins).size == 1:
            bins = bins*np.ones(fit_dim,dtype=int)
        else:
            bins = np.asarray(bins)
            assert bins.size == fit_dim

        # Forward declare things
        limits = self.limits[indices]

        # Assert our metric scale lengths
        dx = (limits[:,1] - limits[:,0])/bins
        # Identify the dV value
        dV = np.prod(dx)

        ## Generate edges ##
        if grab_edge:
            # Create the edge hanging bins
            # Increase the number of bins to lean off the edge
            # Note: try very hard not to mutate bins
            dx = (self.limits[indices,1] - self.limits[indices,0])/(bins - 1)
            # Identify the dV value
            dV = np.prod(dx)
            # Extend limits
            limits[:,0] = self.limits[indices,0] - 0.5*dx[:]
            limits[:,1] = self.limits[indices,1] + 0.5*dx[:]

        ## Build meshgrid ##
        slices = []
        # Generate slices
        for i in range(fit_dim):
            if grab_edge:
                slices.append(slice(
                                    self.limits[indices[i]][0],
                                    self.limits[indices[i]][1],
                                    bins[i]*1j,
                                   ))
            else:
                slices.append(slice(
                                    limits[i][0]+0.5*dx[i],
                                    limits[i][1]-0.5*dx[i],
                                    bins[i]*1j,
                                   ))
        # Generate sample space
        sample_space = np.mgrid[slices]
        # Reshape the sample space
        # This step prevents garbling of dimensions
        sample_space = sample_space.reshape(fit_dim, np.prod(bins))
        # Transpose this sample space for a list of points
        x_train = sample_space.T

        ## Generate the histogram ##
        y_train = histogramdd(
                              self.x_sample[:,indices],
                              range=limits,
                              bins=bins,
                              weights=self.weights,
                             ).flatten()

        # Identify the dV value
        if grab_edge:
            dV = dV / histogram_overhang_edge_factor(x_train)

        # Normalize normally
        y_density, sig_density = \
            weighted_histogram_density_error(
                                             y_train,
                                             self.x_sample.shape[0],
                                             dV,
                                            )

        return x_train, y_density, sig_density

    def fit_marginal(
                     self,
                     GP_function,
                     indices=None,
                     grab_edge=False,
                     min_bins=2,
                     max_bins=None,
                     criteria=None,
                    ):
        '''Fit a marginal for some combinations of the dimensions

        Parameters
        ----------
        GP_function: function(x_train, y_train, y_train_err)
            Function for constructing Gaussian process which returns a lambda
                evaluating the mean interpolation value
        indices: array like, dtype=int
            The identities of the indices of the dimensions to fit
        grab_edge: Boolean
            Use the histogram overhang method or not
        min_bins: array like (or int), dtype=int
            Minimum number of bins for each (or all) dimension(s)
        max_bins: array like (or int), dtype=int
            Maximum number of bins for each (or all) dimension(s)
        criteria: function(P, Q)
            Function for evaluating distance/divergence between P and Q
            default: rms error

        Returns
        -------
        err: float
            The error quantity we are minimizing
        bins: np.ndarray
            The bins for the best fit
        gp_fit: lambda
            the lambda for the GP evaluation of the best fit
        x_train: np.ndarray
            The training data for the GP
        y_train: np.ndarray
            The training evaluations for the GP
        y_error: np.ndarray
            The error in the training data evaluations
            (RMS of cross-evaluation and histogram counting error)
        '''
        # Initialize index
        if indices is None:
            indices = np.arange(self.ndim)
        # Assert things about the index
        indices = np.asarray(indices,dtype=int)
        assert len(indices.shape) == 1
        assert len(indices) <= self.ndim
        # How many dimensions are we fitting?
        fit_dim = len(indices)

        # Initialize min_bins
        min_bins = np.asarray(min_bins)*np.ones(fit_dim,dtype=int)
        # Check if there are enough bins, starting with the minimum value
        min_bin_diff = min(min_bins) - histogram_overhang_bins_of_ndim(fit_dim)
        if min_bin_diff < 0:
            min_bins -= min_bin_diff
        # Initialize current bins
        bins = np.copy(min_bins)

        # Initialize max_bins
        if max_bins is None:
            max_bins = min_bins + 1
        else:
            max_bins = np.asarray(max_bins)*np.ones(fit_dim,dtype=int)
        # Assert bins aren't greater than max_bins
        assert all(bins < max_bins)

        # Initialize loop variables
        initial_loop = True
        fit_bins = bins.copy()
        # Initialize err
        err = np.inf
        min_err = np.inf
        # Begin loop
        while (
               all(bins <= max_bins)
               # and (err > err_threshold)
              ):
            # If not first cycle, rename previous things
            if not initial_loop:
                x_train_p = x_train_n
                y_train_p = y_train_n
                y_error_p = y_error_n
                gp_fit_p = gp_fit_n

            # Fit a histogram for bins
            x_train_n, y_train_n, y_error_n = \
                self.fit_histdd(
                                indices,
                                bins,
                                grab_edge=grab_edge,
                               )

            # Fit a gaussian process
            gp_fit_n = GP_function(x_train_n, y_train_n, y_error_n)

            # Evaluate fit residuals
            if not initial_loop:
                # Cross-evaluate training data
                y_cross_n = gp_fit_p(x_train_n)
                y_cross_p = gp_fit_n(x_train_p)
                # Evaluate the residuals
                y_resid_n = np.abs(y_train_n - y_cross_n)
                y_resid_p = np.abs(y_train_p - y_cross_p)

            # Evaluate goodness of fit
            if not initial_loop:
                ## Cross-evaluate training data
                #  Get an evaluation set
                x_sample = np.empty((
                                     x_train_n.shape[0] + x_train_p.shape[0],
                                     x_train_n.shape[1]
                                    ),dtype=float)
                x_sample[:x_train_p.shape[0]] = x_train_p
                x_sample[x_train_p.shape[0]:] = x_train_n
                # Evaluate the evaluation set
                y_sample_n = gp_fit_p(x_sample)
                y_sample_p = gp_fit_n(x_sample)
                # Get probability distribution scaling
                P_p = y_sample_p / np.sum(y_sample_p)
                P_n = y_sample_n / np.sum(y_sample_n)
                # The err statistic is the maximum of those residuals
                if criteria is None:
                    err = np.sqrt(np.sum(np.power(P_p - P_n,2)))
                else:
                    err = criteria(P_p, P_n)

            # Update minimal err things
            if err < min_err:
                min_err = err
                fit_bins = bins - 1
                min_x_train_n = x_train_n
                min_y_train_n = y_train_n
                min_y_error_n = y_error_n
                min_y_resid_n = y_resid_n
                min_x_train_p = x_train_p
                min_y_train_p = y_train_p
                min_y_error_p = y_error_p
                min_y_resid_p = y_resid_p

            # Print things
            if self.verbose:
                print("marginal bins:", bins, ", %f err"%(err))
            # Increment bins
            initial_loop=False
            bins += 1

        # Use minimal err value
        #if not err < err_threshold:
        #    print("Warning: marginal err, err_threshold, max_bins: %f %f %d"%(
        #        min_err, err_threshold, max_bins),
        #        file=sys.stderr)
        #    print("bins: ",min_bins,file=sys.stderr)

        # Recover optimal quantities
        err = min_err
        bins = fit_bins
        x_train_n = min_x_train_n
        y_train_n = min_y_train_n
        y_error_n = min_y_error_n
        y_resid_n = min_y_resid_n
        x_train_p = min_x_train_p
        y_train_p = min_y_train_p
        y_error_p = min_y_error_p
        y_resid_p = min_y_resid_p
        # Create new set of training data
        # Create y data
        y_train = np.append(y_train_p, y_train_n).flatten()
        # Create x data
        x_train = np.empty((y_train.size, x_train_n.shape[1]))
        x_train[:y_train_p.size] = x_train_p
        x_train[y_train_p.size:] = x_train_n
        # Initialize error bounds for new training data
        y_error = np.empty_like(y_train)
        # Evaluate errors based on cross data
        y_error[:y_train_p.size] = np.sqrt(y_error_p**2 + y_resid_p**2)
        y_error[y_train_p.size:] = np.sqrt(y_error_n**2 + y_resid_n**2)

        # Fit a gaussian process
        gp_fit = GP_function(x_train, y_train, y_error)

        return err, bins, gp_fit, x_train, y_train, y_error

    def fit_marginal_methods(
                             self,
                             GP_function,
                             indices,
                             bins=None,
                             method="like",
                             min_bins=7,
                             max_bins=20,
                             **kwargs
                            ):
        '''Different search methods for marginal fits

        Parameters
        ----------
        indices: array like
            Dimensions we would like to fit
        bins: array like
            Initial configuration of bins
        method: string
            Way of searching for the right number of bins
            ["bins", "like", "search"]
        min_bins: int/array like
            Initial bin placements
        max_bins: int/array like
            Maximum number of bins
        
        Returns
        -------
        err: float
            The error quantity we are minimizing
        bins: np.ndarray
            The bins for the best fit
        gp_fit: lambda
            the lambda for the GP evaluation of the best fit
        x_train: np.ndarray
            The training data for the GP
        y_train: np.ndarray
            The training evaluations for the GP
        y_error: np.ndarray
            The error in the training data evaluations
            (RMS of cross-evaluation and histogram counting error)
        '''
        # First method is by given bins
        if method == "bins":
            assert not (bins is None)
            ks, bins, gp_fit, x_train, y_train, y_error = \
                self.fit_marginal(GP_function,indices,min_bins=bins,max_bins=bins+1,**kwargs)
            return ks, bins, gp_fit, x_train, y_train, y_error
        else:
            assert bins is None

        # Second method is the default behavior, assuming equal bins
        if method == "like":
            ks, bins, gp_fit, x_train, y_train, y_error = \
                self.fit_marginal(GP_function, indices,min_bins=min_bins,max_bins=max_bins,**kwargs)

        # Search method (the long one)
        elif method == "search":
            # First check the equal case
            ks, bins, gp_fit, x_train, y_train, y_error = \
                self.fit_marginal(
                                  GP_function,
                                  indices,
                                  min_bins=min_bins,
                                  max_bins=min_bins+1,
                                  **kwargs
                                 )
            # Initialize minimum ks value items
            min_ks = ks
            fit_bins = bins
            min_gp_fit = gp_fit
            min_x_train = x_train
            min_y_train = y_train
            min_y_error = y_error

            # Adjust bins
            fit_dim = len(indices)
            min_bins = np.asarray(min_bins)*np.ones(fit_dim,dtype=int)
            max_bins = np.asarray(max_bins)*np.ones(fit_dim,dtype=int)
            min_bin_diff = min(min_bins) - histogram_overhang_bins_of_ndim(fit_dim)
            if min_bin_diff < 0:
                min_bins -= min_bin_diff
            bin_diff = max_bins - min_bins

            # If there's no more places to search, we're done
            if any(bin_diff <= 0):
                return ks, bins, gp_fit, x_train, y_train, y_error
            # Find all the bin combinations
            bin_combs = bin_combination_seeds(
                    fit_dim,
                    bin_diff,
                   ) + min_bins

            # Loop through each bin combination
            for item in bin_combs:
                # Run a fit
                ks, bins, gp_fit, x_train, y_train, y_error = \
                    self.fit_marginal(
                                      GP_function,
                                      indices,
                                      min_bins=item,
                                      max_bins=max_bins,
                                      **kwargs
                                     )

                # update things if the fit is better
                if ks < min_ks:
                    min_ks = ks
                    fit_bins = bins
                    min_gp_fit = gp_fit
                    min_x_train = x_train
                    min_y_train = y_train
                    min_y_error = y_error

            ks = min_ks
            bins = fit_bins
            gp_fit = min_gp_fit
            x_train = min_x_train
            y_train = min_y_train
            y_error = min_y_error

        else:
            raise RuntimeError("Unknown method: %s"%method)

        return ks, bins, gp_fit, x_train, y_train, y_error


    def multifit_marginal1d(
                            self,
                            GP_function,
                            grab_edge=False,
                            max_bins=20,
                            **fit_kwargs
                           ):
        # Create a dictionary for the marginals
        marg_dict = {}

        for i in range(self.x_sample.shape[1]):
            # Fit the marginal
            ks, bins, gp_fit, x_train, y_train, y_error = \
                self.fit_marginal(
                                  GP_function,
                                  indices=[i],
                                  grab_edge=grab_edge,
                                  max_bins=max_bins,
                                  **fit_kwargs
                                 )

            # Store fit things
            marg_dict["1d_%d_ks"%i] = ks
            marg_dict["1d_%d_bins"%i] = bins
            marg_dict["1d_%d_gp_fit"%i] = gp_fit
            marg_dict["1d_%d_x_train"%i] = x_train
            marg_dict["1d_%d_y_train"%i] = y_train
            marg_dict["1d_%d_y_error"%i] = y_error

        return marg_dict

    def multifit_marginal2d(
                            self,
                            GP_function,
                            grab_edge=False,
                            max_bins=20,
                            **fit_kwargs
                           ):
        # Create a dictionary for the marginals
        marg_dict = {}

        for i in range(self.x_sample.shape[1]):
            for j in range(i):
                # Fit the marginal
                ks, bins, gp_fit, x_train, y_train, y_error = \
                    self.fit_marginal(
                                      GP_function,
                                      indices=[i,j],
                                      grab_edge=grab_edge,
                                      max_bins=max_bins,
                                      **fit_kwargs
                                     )

                # Store fit things
                marg_dict["2d_%d_%d_ks"%(i,j)] = ks
                marg_dict["2d_%d_%d_bins"%(i,j)] = bins
                marg_dict["2d_%d_%d_gp_fit"%(i,j)] = gp_fit
                marg_dict["2d_%d_%d_x_train"%(i,j)] = x_train
                marg_dict["2d_%d_%d_y_train"%(i,j)] = y_train
                marg_dict["2d_%d_%d_y_error"%(i,j)] = y_error

        return marg_dict

    def multifit_marginal1d2d(
                              self,
                              GP_function,
                              grab_edge=False,
                              max_bins=20,
                              **fit_kwargs
                             ):
        # Create a dictionary for the marginals
        marg_dict = {}
        # Update the dictionary with 1d fits
        marg_dict.update(self.multifit_marginal1d(
                                                  GP_function,
                                                  grab_edge=grab_edge,
                                                  max_bins=max_bins,
                                                  **fit_kwargs
                                                 ))
        # Get all the 1D bins
        bins1d = []
        for i in range(self.ndim):
            bins1d.append(marg_dict["1d_%d_bins"%i])
        # Make a bins array
        bins1d = np.asarray(bins1d).flatten()
        # Update the dictionary
        marg_dict["bins1d"] = bins1d

        for i in range(self.x_sample.shape[1]):
            for j in range(i):
                # Fit the marginal
                ks, bins, gp_fit, x_train, y_train, y_error = \
                    self.fit_marginal_methods(
                                              GP_function,
                                              [i,j],
                                              method="search",
                                              max_bins=np.asarray([bins1d[i],bins1d[j]]),
                                              grab_edge=grab_edge,
                                              **fit_kwargs
                                             )

                # Store fit things
                marg_dict["2d_%d_%d_ks"%(i,j)] = ks
                marg_dict["2d_%d_%d_bins"%(i,j)] = bins
                marg_dict["2d_%d_%d_gp_fit"%(i,j)] = gp_fit
                marg_dict["2d_%d_%d_x_train"%(i,j)] = x_train
                marg_dict["2d_%d_%d_y_train"%(i,j)] = y_train
                marg_dict["2d_%d_%d_y_error"%(i,j)] = y_error

        return marg_dict

    def multifit_corner(
                        self,
                        GP_function,
                        grab_edge=False,
                        max_bins=20,
                        savename=None,
                        figsize=7.0,
                        log_scale=False,
                        labels=None,
                        bin_info=False,
                        fontscale=1.,
                        **fit_kwargs
                       ):
        '''Fit a corner plot to the marginals'''
        # Imports 
        from basil_core.plots.corner import Corner
        # Run the 1d and 2d marginals
        marg_dict = self.multifit_marginal1d2d(
                                               GP_function,
                                               grab_edge=grab_edge,
                                               max_bins=max_bins,
                                               **fit_kwargs
                                              )
        # Create a corner plot
        mycorner = Corner(
                          self.ndim,
                          limits=self.limits,
                          figsize=figsize,
                          log_scale=log_scale,
                          density=False,
                          labels=labels,
                          fontscale=fontscale,
                         )
        # Add a HOGPEN layer
        mycorner.add_HOGPEN_layer(
                                  marg_dict,
                                  imshow=True,
                                  linestyle="solid",
                                  label="Gaussian Process"
                                 )
        if bin_info:
            # Add a histogram layer for n bins
            mycorner.add_HOGPEN_layer(
                                      marg_dict,
                                      contour=True,
                                      hist_n=True,
                                      linestyle="dotted",
                                      label="N bin histogram"
                                     )

            # Add a histogram layer for n + 1 bins
            mycorner.add_HOGPEN_layer(
                                      marg_dict,
                                      contour=True,
                                      hist_n1=True,
                                      linestyle="dashed",
                                      label="N + 1 bin histogram"
                                     )

        # Show it to me
        if (savename is None):
            mycorner.show()
        # Save it
        else:
            mycorner.save(savename)

        # You still want to return this
        return marg_dict

######## All Tests ########

