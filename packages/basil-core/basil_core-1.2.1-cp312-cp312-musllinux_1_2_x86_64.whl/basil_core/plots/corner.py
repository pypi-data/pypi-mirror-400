'''Vera's corner plot utils

Stylistically, I just prefer to do things my own way rather than rely on 
    corner.py

'''
######## Imports ########
import numpy as np

from basil_core.plots.axis import ax_histogram1d, ax_histogram2d
from basil_core.plots.axis import ax_histogram_contour2d
from basil_core.plots.axis import ax_function1d, ax_function2d
from basil_core.plots.axis import ax_function_contour2d
from basil_core.plots.axis import ax_plot1d, ax_scatter2d_density, ax_scatter_contour2d, ax_scatter2d_error


######## Information ########

EXTENSIONS = ["png", "pdf"]

######## Corner object ########

class Corner(object):
    '''Object for corner plot configuration
    '''
    def __init__(
                 self,
                 ndim,
                 limits=None,
                 labels=None,
                 figsize=3.375,
                 fontscale=1.,
                 style='bmh',
                 log_scale=True,
                 density=True,
                 legend_loc=1,
                 title=None,
                 log_offset=0.,
                 diag_ticklabels=False,
                ):
        '''Initialize corner plot config

        Parameters
        ----------
        ndim: int
            Number of dimensions for corner plot
        limits: array like, dtype=float, shape=(ndim, 2)
            limit space plotted
        labels: list of strings
            List of axis labels
        figsize: float
            Size of figure (inches)
        fontscale: float
            Further adjust font sizes
        style: str
            Matplotlib style
        log_scale: bool
            Use log scale for histogram and marginals?
        log_offset: float
            Log offset for colors of imshow
        density: bool
            Normalize everything under integration?
        legend_loc: matplotlib legend loc
            Location for a legend, if present
        title: string
            Title for fgure
        diag_ticklabels: bool
            Show diagonal ticklabels?
 
        Returns
        -------
        self: Corner object
            The corner plot configuration object
        '''
        # Assign ndim
        assert isinstance(ndim, int)
        self.ndim = ndim

        # Assign limits
        if limits is None:
            self.limits = None
        else:
            # Check limits
            limits = np.asarray(limits)
            assert len(limits.shape) == 2
            assert limits.shape[0] == self.ndim
            assert limits.shape[1] == 2
            self.limits = limits

        # Check labels
        if labels is None:
            self.labels = None
        else:
            assert len(labels) == ndim
            self.labels = labels

        # Check size
        assert (isinstance(figsize, float)) or (isinstance(figsize, int))
        self.figsize = figsize

        # Assign fontscale
        assert (isinstance(fontscale, float)) or (isinstance(fontscale, int))
        self.fontscale = (self.figsize / 3.375) * fontscale

        # Assign log_scale
        self.log_scale = log_scale
        self.log_offset = log_offset

        # Assign density
        self.density = density

        # Assign style
        self.style = style

        # Assign title
        self.title = title

        # Assign diag ticklabels
        self.diag_ticklabels = diag_ticklabels

        # Initialize histogram layers
        self.histogram_layers = []
        # Initialize HOGPEN layers
        self.HOGPEN_layers = []
        # Initialize scatter2d layers
        self.scatter2d_layers = []

        # Initialize colorbar
        self._colorbar = None
        # Initialize legend toggle
        self._legend = False
        self.legend_loc = legend_loc

    #### User methods ####
    def add_histogram_layer(
                            self,
                            data,
                            bins=10,
                            label=None,
                            cmap="terrain_r",
                            imshow=False,
                            contour=False,
                            colorbar=False,
                            weights=None,
                            levels=[0.68,0.95],
                            linestyle="solid",
                            diag=True,
                           ):
        '''Add a histogram layer to the corner plot

        Parameters
        ----------
        data: array like, shape=(npts, ndim)
            Samples for histograming
        bins: int, string, or array like
            Bins for histogram
        label: str
            label for legend
        cmap: str
            cmap for matplotlib
        imshow: bool
            use imshow for 2D histogram?
        contour: bool
            Use contours for histogram?
        colorbar: bool
            Show colorbar for this density?
        weights: array like
            Do the samples have weights (like a prior)?
        levels: array like
            Levels for contour plot
        linestyle: matplotlib line style argument
            linestyle for matplotlib for contours
        '''
        # Check the data
        assert len(data.shape) == 2
        assert data.shape[1] == self.ndim
        npts = data.shape[0]
        # Check the bins
        if isinstance(bins, np.ndarray):
            assert len(bins) == self.ndim
        elif isinstance(bins, int):
            bins = np.ones(self.ndim, dtype=int) * bins
        elif isinstance(bins, str):
            # Check for bins automatically using a predefined method
            raise NotImplementedError
        # Define layer dictionary
        layer = {
                 "npts"     : npts,
                 "data"     : data,
                 "bins"     : bins,
                 "label"    : label,
                 "cmap"     : cmap,
                 "imshow"   : imshow,
                 "contour"  : contour,
                 "weights"  : weights,
                 "levels"   : levels,
                 "linestyle": linestyle,
                 "diag"     : diag,
                }
        # Append layer to histogram layers
        self.histogram_layers.append(layer)

    def add_scatter2d_layer(
                            self,
                            data,
                            sig,
                            label=None,
                            s=10.,
                            color='black',
                            marker='d',
                            ecolor='black',
                            elinewidth=0.5,
                            colorbar=False,
                           ):
        '''Add a scatter 2d layer to the corner plot

        Parameters
        ----------
        data: array like, shape=(npts, ndim)
            Samples for histograming
        label: str
            label for legend
        s: float
            Maker size
        color: str
            matplotlib color choices
        elinewidth: float
            error bar line width
        ecolor: str
            erorr bar color
        '''
        # Check the data
        assert len(data.shape) == 2
        assert data.shape[1] == self.ndim
        npts = data.shape[0]
        # Check sig
        if np.asarray(sig).size == self.ndim:
            sig = np.tile(sig, (npts,1))
        else:
            assert np.asarray(sig).shape[0] == npts
            assert np.asarray(sig).shape[1] == self.ndim
        # Check s
        s = s * self.fontscale
        # Define layer dictionary
        layer = {
                 "npts"         : npts,
                 "data"         : data,
                 "sig"          : sig,
                 "label"        : label,
                 's'            : s,
                 "color"        : color,
                 "marker"       : marker,
                 "colorbar"     : colorbar,
                 "ecolor"       : ecolor,
                 "elinewidth"   : elinewidth,
                }
        # Append layer to histogram layers
        self.scatter2d_layers.append(layer)

    def add_HOGPEN_layer(
                         self,
                         marginals,
                         res=100,
                         label=None,
                         cmap="terrain_r",
                         imshow=False,
                         contour=False,
                         hist_n=False,
                         hist_n1=False,
                         colorbar=False,
                         levels=[0.68,0.95],
                         linestyle="solid",
                        ):
        '''Add a histogram layer to the corner plot

        Parameters
        ----------
        marginals: dict
            Dictionary of HOGPEN marginals
        res: int or array like
            Resolution for evaluating gps
        label: str
            label for legend
        cmap: str
            cmap for matplotlib
        imshow: bool
            use imshow for density?
        contour: bool
            Use contours for density?
        hist_n: bool
            Show histogram data for n bins?
        hist_n1: bool
            Show histogram data for n + 1 bins?
        colorbar: bool
            Show colorbar for this density?
        levels: array like
            Levels for contour plot
        linestyle: matplotlib line style argument
            linestyle for matplotlib for contours
        '''
        # Check the res
        if isinstance(res, np.ndarray):
            assert len(res) == self.ndim
        elif isinstance(res, int):
            res = np.ones(self.ndim, dtype=int) * res
        else:
            raise RuntimeError("undefined resolution:", res)

        # Define layer dictionary
        layer = {
                 "res"      : res,
                 "label"    : label,
                 "cmap"     : cmap,
                 "imshow"   : imshow,
                 "contour"  : contour,
                 "hist_n"   : hist_n,
                 "hist_n1"  : hist_n1,
                 "colorbar" : colorbar,
                 "levels"   : levels,
                 "linestyle": linestyle,
                }
        # Append marginals
        layer.update(marginals)
        # Append layer to histogram layers
        self.HOGPEN_layers.append(layer)

    def show(self):
        '''Construct the plot and show the user

        Parameters
        ----------
        self: Corner object
            The corner plot configuration object
        '''
        # import pyplot
        from matplotlib import pyplot as plt
        # Activate the style
        plt.style.use(self.style)
        # Generate figure
        fig, axes = plt.subplots(
                                 self.ndim,
                                 self.ndim,
                                 figsize=(self.figsize, self.figsize),
                                 sharex='col',
                                )
        # Make the figure
        self._make(fig, axes)
        # Tight layout
        plt.tight_layout()
        # Show the plot
        plt.show()
        # Close the plot
        plt.close()

    def save(self, fname, extension="png", backend="Agg"):
        '''Save the plot to a file

        Parameters
        ----------
        self: Corner object
            The corner plot configuration object
        fname: string
            The path to where the plot should be saved
        extension: string
            The file extension
        backend: string
            The matplotlib backend
        '''
        # import matplotlib
        import matplotlib
        # Use the backend
        matplotlib.use(backend)
        # Import pyplot
        from matplotlib import pyplot as plt

        # Check extension
        assert extension in EXTENSIONS
        # Check for extensions in fname
        for _ext in EXTENSIONS:
            # Check if fname ends with given extension
            if fname.split('.')[-1] == _ext:
                # If it does, we need to set our extension to that extension
                extension = _ext
                # We also need to not duplicate it
                fname = ".".join(fname.split('.')[:-1])
                # Let's hope we only find one of these
                break
                

        # Activate the style
        plt.style.use(self.style)
        
        # Generate figure
        fig, axes = plt.subplots(
                                 self.ndim,
                                 self.ndim,
                                 figsize=(self.figsize, self.figsize),
                                 sharex='col',
                                )
        # Make the figure
        self._make(fig, axes)
        # Tight layout
        plt.tight_layout()
        # Save the plot
        plt.savefig("%s.%s"%(fname, extension))
        # Close the plot
        plt.close()


    #### Hidden methods ####

    def _remove_upper(self, axes):
        ''' Remove upper triangular plot elements

        Parameters
        ----------
        axes: matplotlib axis objects
            The axes for the plot
        '''
        # Loop i and j in ndim
        for i in range(self.ndim):
            for j in range(i):
                # Remove the unwanted plots
                axes[j,i].remove()

    def _fix_tick_params(self, axes):
        ''' Fix the tick params to match my ideas about corner plots

        Parameters
        ----------
        axes: matplotlib axis objects
            The axes for the plot
        '''
        # Loop the dimensions
        for i in range(self.ndim):
            # Update the tick params
            axes[i,i].tick_params(axis="both", which="both", labelsize=6*self.fontscale, labelleft=False)
            # Remove the y ticklabels
            if self.diag_ticklabels:
                pass
            else:
                axes[i,i].set_yticklabels([])
            # Update axis label ticks
            if not (self.labels is None):
                # Set the xlabels
                axes[-1,i].set_xlabel(self.labels[i], size=10*self.fontscale)
                # Set the y lables
                if not i==0:
                    axes[i,0].set_ylabel(self.labels[i], size=10*self.fontscale)

        # 2D plots
        for i in range(self.ndim):
            for j in range(i):
                # Handle ticks
                axes[i,j].tick_params(axis="both", which="both", labelsize=6*self.fontscale)
                # Remove y ticklabels
                if j != 0:
                    axes[i,j].set_yticklabels([])

    def _get_limits(self):
        ''' Get limits for the data in each dimension'''
        # Check if limits were specified already (by user or otherwise)
        if not (self.limits is None):
            return
        # Initialize limits
        limits = np.empty((self.ndim, 2))
        initialized = False
        # Check histogram layers
        if len(self.histogram_layers) > 0:
            for layer in self.histogram_layers:
                # Extract limits
                layer_limits = np.asarray([
                                           np.min(layer["data"], axis=0),
                                           np.max(layer["data"], axis=0),
                                          ]).T
                ## Update limits ##
                # If uninitialized, initialize
                if not initialized:
                    # Initialize those limits with layer limits
                    limits = layer_limits
                    # Update initialized
                    initialized = True
                    # Loop
                    continue

                # Find cases where layer limits are lower than limits
                update_min = layer_limits[:,0] < limits[:,0]
                # Update those lower limits
                limits[:,0][update_min] = layer_limits[:,0][update_min]
                # Find cases where layer limits are higher than limits
                update_max = layer_limits[:,1] > limits[:,1]
                # Update those upper limits
                limits[:,1][update_max] = layer_limits[:,1][update_max]
            # Update self.limits
            self.limits = limits
            # Return triumphantly
            return

        # Else
        raise RuntimeError("Failed to initialize limits")

    def _make_histogram_layer(self, axes, layer):
        ''' Make the histogram layer

        Parameters
        ----------
        axes: matplotlib axes
            The axes for the corner plot
        layer: dict
            dictionary created by "add_histogram_layer" method

        # Define layer dictionary
        layer = {
                 "npts"     : npts,
                 "data"     : data,
                 "bins"     : bins,
                 "label"    : label,
                 "cmap"     : cmap,
                 "imshow"   : imshow,
                 "contour"  : contour,
                 "colorbar" : colorbar,
                 "levels"   : levels,
                 "linestyle": linestyle,
                 "diag"     : diag,
                }
        '''
        ### 1D plots ###
        for i in range(self.ndim):
            # Check for diag
            if layer["diag"] == False:
                continue
            # Figure out label
            if layer["label"] is None:
                layer_label = None
            elif i != 0:
                layer_label = None
            else:
                layer_label = layer["label"]
                self._legend = True
            # Call the histogram thing
            ax_histogram1d(
                           axes[i,i],
                           layer["data"][:,i],
                           limits=self.limits[i],
                           set_limits=True,
                           log_scale=self.log_scale,
                           density=self.density,
                           bins=layer["bins"][i],
                           w=layer["weights"],
                           linestyle=layer["linestyle"],
                           label=layer_label,
                          )
        ### 2D plots ###
        for i in range(self.ndim):
            for j in range(i):
                # Call the histogram code
                if layer["imshow"]:
                    ax_histogram2d(
                                   axes[i,j],
                                   layer["data"][:,j],
                                   layer["data"][:,i],
                                   limits=np.asarray([self.limits[j], self.limits[i]]),
                                   set_limits=True,
                                   log_scale=self.log_scale,
                                   density=self.density,
                                   bins=np.asarray([layer["bins"][j], layer["bins"][i]]),
                                   cmap=layer["cmap"],
                                   w=layer["weights"],
                                  )
                elif layer["contour"]:
                    ax_histogram_contour2d(
                                           axes[i,j],
                                           layer["data"][:,j],
                                           layer["data"][:,i],
                                           limits=np.asarray([self.limits[j], self.limits[i]]),
                                           set_limits=True,
                                           bins=np.asarray([layer["bins"][j], layer["bins"][i]]),
                                           cmap=layer["cmap"],
                                           w=layer["weights"],
                                           linestyles=layer["linestyle"],
                                           levels=layer["levels"],
                                          )

    def _make_scatter2d_layer(self, axes, layer):
        ''' Make the Scatter2d layer
        
        Parameters
        ----------
        axes: matplotlib axes
            The axes for the corner plot
        layer: dict
            dictionary created by add_scatter2d_layer
        
        # Define layer dictionary
        layer = {
                 "npts"         : npts,
                 "data"         : data,
                 "sig"          : sig,
                 "label"        : label,
                 's'            : s,
                 "color"        : color,
                 "marker"       : marker,
                 "ecolor"       : ecolor,
                 "elinewidth"   : elinewidth,
                }
        '''
        ## No 1-D plots ##
        ### 2D plots ###
        for i in range(self.ndim):
            for j in range(i):
                # Set label
                if (i == 0) & (j == 0) & (not (layer["label"] is None)):
                    layer_label = layer["label"]
                    self._legend = True
                else:
                    layer_label = None

                # Make the scatter plot 
                ax_scatter2d_error(
                                   axes[i,j], 
                                   layer["data"][:,j],
                                   layer["data"][:,i],
                                   layer["sig"][:,j],
                                   layer["sig"][:,i],
                                   limits=np.asarray([self.limits[j], self.limits[i]]),
                                   set_limits=True,
                                   label=layer_label,
                                   s=layer["s"],
                                   color=layer["color"],
                                   marker=layer["marker"],
                                   ecolor=layer["ecolor"],
                                   elinewidth=layer["elinewidth"],
                                   zorder=2,
                                  )

    def _make_HOGPEN_layer(self, axes, layer):
        ''' Make the HOGPEN layer

        Parameters
        ----------
        axes: matplotlib axes
            The axes for the corner plot
        layer: dict
            dictionary created by "add_HOGPEN_layer" method

        # Define layer dictionary
        layer = {
                 "res"      : res,
                 "label"    : label,
                 "cmap"     : cmap,
                 "imshow"   : imshow,
                 "contour"  : contour,
                 "colorbar" : colorbar,
                 "levels"   : levels,
                 "linestyle": linestyle,
                }
        '''
        ### GP function ###
        def GPfunc(X):
            _x = X[:,1]
            _y = X[:,0]
            _X = np.stack([_x, _y]).T
            return layer["2d_%d_%d_gp_fit"%(i,j)](_X)

        #def GPfunc(X): return layer["2d_%d_%d_gp_fit"%(i,j)](X)

            
        ### 1D plots ###
        for i in range(self.ndim):
            # Figure out label
            if layer["label"] is None:
                layer_label = None
            elif i != 0:
                layer_label = None
            else:
                layer_label = layer["label"]
                self._legend = True

            # Scatter!
            if layer["hist_n"]:
                hist_bins = int(layer["1d_%d_bins"%i])
                ax_plot1d(
                          axes[i,i], 
                          layer["1d_%d_x_train"%i][:hist_bins],
                          layer["1d_%d_y_train"%i][:hist_bins],
                          limits=self.limits[i],
                          set_limits=True,
                          density=self.density,
                          linestyle=layer["linestyle"],
                          label=layer_label,
                          log_scale=self.log_scale,
                         )
            elif layer["hist_n1"]:
                hist_bins = int(layer["1d_%d_bins"%i])
                ax_plot1d(
                          axes[i,i], 
                          layer["1d_%d_x_train"%i][hist_bins:],
                          layer["1d_%d_y_train"%i][hist_bins:],
                          limits=self.limits[i],
                          set_limits=True,
                          density=self.density,
                          linestyle=layer["linestyle"],
                          label=layer_label,
                          log_scale=self.log_scale,
                         )
            else:
                ax_function1d(
                              axes[i,i],
                              layer["1d_%d_gp_fit"%i],
                              self.limits[i],
                              set_limits=True,
                              density=self.density,
                              res=layer["res"][i],
                              linestyle=layer["linestyle"],
                              label=layer_label,
                              log_scale=self.log_scale,
                             )
        ### 2D plots ###
        for i in range(self.ndim):
            for j in range(i):
                # Call the axis code
                if layer["imshow"]:
                    ax_function2d(
                                  axes[i,j],
                                  GPfunc,
                                  np.asarray([self.limits[j], self.limits[i]]),
                                  set_limits=True,
                                  log_scale=self.log_scale,
                                  log_offset=self.log_offset,
                                  density=self.density,
                                  res=np.asarray([layer["res"][j], layer["res"][i]]),
                                  cmap=layer["cmap"],
                                 )
                elif layer["hist_n"]:
                    hist_bins = np.prod(layer["2d_%d_%d_bins"%(i,j)])
                    if layer["contour"]:
                        ax_scatter_contour2d(
                                             axes[i,j],
                                             np.unique(layer["2d_%d_%d_x_train"%(i,j)][:hist_bins,1]),
                                             np.unique(layer["2d_%d_%d_x_train"%(i,j)][:hist_bins,0]),
                                             layer["2d_%d_%d_y_train"%(i,j)][:hist_bins].reshape(layer["2d_%d_%d_bins"%(i,j)]),
                                             cmap=layer["cmap"],
                                             limits=np.asarray([self.limits[j], self.limits[i]]),
                                             set_limits=True,
                                             levels=layer["levels"],
                                            )
                                             
                    else:
                        ax_scatter2d_density(
                                     axes[i,j], 
                                     layer["2d_%d_%d_x_train"%(i,j)][:hist_bins,1],
                                     layer["2d_%d_%d_x_train"%(i,j)][:hist_bins,0],
                                     layer["2d_%d_%d_y_train"%(i,j)][:hist_bins],
                                     cmap=layer["cmap"],
                                     limits=np.asarray([self.limits[j], self.limits[i]]),
                                     set_limits=True,
                                     density=self.density,
                                     label=layer_label,
                                     log_scale=self.log_scale,
                                     log_offset=self.log_offset,
                                    )
                elif layer["hist_n1"]:
                    hist_bins = np.prod(layer["2d_%d_%d_bins"%(i,j)])
                    if layer["contour"]:
                        ax_scatter_contour2d(
                                             axes[i,j],
                                             np.unique(layer["2d_%d_%d_x_train"%(i,j)][hist_bins:,1]),
                                             np.unique(layer["2d_%d_%d_x_train"%(i,j)][hist_bins:,0]),
                                             layer["2d_%d_%d_y_train"%(i,j)][hist_bins:].reshape(layer["2d_%d_%d_bins"%(i,j)]+1),
                                             cmap=layer["cmap"],
                                             limits=np.asarray([self.limits[j], self.limits[i]]),
                                             set_limits=True,
                                             levels=layer["levels"],
                                            )
                                             
                    else:
                        ax_scatter2d_density(
                                     axes[i,j], 
                                     layer["2d_%d_%d_x_train"%(i,j)][hist_bins:,1],
                                     layer["2d_%d_%d_x_train"%(i,j)][hist_bins:,0],
                                     layer["2d_%d_%d_y_train"%(i,j)][hist_bins:],
                                     cmap=layer["cmap"],
                                     limits=np.asarray([self.limits[j], self.limits[i]]),
                                     set_limits=True,
                                     density=self.density,
                                     log_scale=self.log_scale,
                                     log_offset=self.log_offset,
                                    )
                elif layer["contour"]:
                    ax_function_contour2d(
                                          axes[i,j],
                                          GPfunc,
                                          np.asarray([self.limits[j], self.limits[i]]),
                                          set_limits=True,
                                          res=np.asarray([layer["res"][j], layer["res"][i]]),
                                          cmap=layer["cmap"],
                                          linestyles=layer["linestyle"],
                                          levels=layer["levels"],
                                         )

    def _add_legend(self, fig):
        '''Provide the legend for the plot

        Parameters
        ----------
        self: Corner object
            The corner plot configuration object
        fig: matplotlib figure object
            The figure object for your corner plot
        '''
        # Check if we even want the legend
        if self._legend:
            # Make the legend
            fig.legend(loc=self.legend_loc, prop={"size":8*self.fontscale})

    def _add_title(self, fig):
        '''Add a title to the figure

        Parameters
        ----------
        self: Corner object
            The corner plot configuration object
        fig: matplotlib figure object
            The figure object for your corner plot
        '''
        # Check if we even want a title
        if not (self.title is None):
            # Assign the title
            fig.suptitle(self.title, fontsize= float(12*self.fontscale))

    def _make(self, fig, axes):
        '''Construct the plot

        Parameters
        ----------
        self: Corner object
            The corner plot configuration object
        fig: matplotlib figure object
            The figure object for your corner plot
        axes: matplotlib axes object
            The axes for your corner plot
        '''
        # Remove the upper plots
        self._remove_upper(axes)
        # Get limits
        self._get_limits()
        # Make the HOGPEN layers
        for layer in self.HOGPEN_layers:
            self._make_HOGPEN_layer(axes, layer)
        # Make the histogram layers
        for layer in self.histogram_layers:
            self._make_histogram_layer(axes, layer)
        # Make the scatter layers
        for layer in self.scatter2d_layers:
            self._make_scatter2d_layer(axes, layer)
        # Fix tick params
        self._fix_tick_params(axes)
        # Add legend
        self._add_legend(fig)
        # Add title
        self._add_title(fig)
        return fig, axes

