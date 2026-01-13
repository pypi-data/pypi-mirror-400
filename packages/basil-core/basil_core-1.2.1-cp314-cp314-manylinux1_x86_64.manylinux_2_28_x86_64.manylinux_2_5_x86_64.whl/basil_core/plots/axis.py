'''Axis utilities for corner plots
'''

from basil_core.plots.utils import bin_centers
from basil_core.plots.utils import percentile_levels

######## Axis Plot Methods ########
#### Histogram Plots ####
def ax_histogram1d(
                 ax,
                 x,
                 w=None,
                 limits=None,
                 set_limits=False,
                 log_scale=False,
                 density=False,
                 log_offset=0.,
                 bins=100,
                 **kwargs
                ):
    '''\
    Quickly make a histogram of some samples
    '''
    import numpy as np
    from fast_histogram import histogram1d
    
    # Update limits
    if limits is None:
        limits = np.asarray([np.min(x), np.max(x)])

    # Make histogram
    rho = histogram1d(x, bins, limits, weights=w)

    # Get the bin centers
    centers = bin_centers(limits[0], limits[1], bins)
    
    # Make sure this thing integrates to one
    if density:
        dx = centers[1] - centers[0]
        rho = rho / np.sum(rho*dx)

    # log scale
    if log_scale:
        # Implement log scale
        ax.set_yscale('log')
        #rho = np.log(rho + log_offset)

    # Show data
    ax.plot(centers, rho, **kwargs)
    # Set limits
    if set_limits:
        ax.set_xlim(limits)

    # We may need to return this
    return ax

def ax_histogram2d(
                 ax,
                 x,
                 y,
                 w=None,
                 limits=None,
                 set_limits=False,
                 log_scale=False,
                 density=False,
                 log_offset=0.,
                 cmap = 'terrain_r',
                 bins=100,
                 **kwargs
                ):
    '''\
    Quickly make a histogram of some samples
    '''
    import numpy as np
    from fast_histogram import histogram2d
    
    # Update limits
    if limits is None:
        limits = np.asarray([[np.min(x), np.max(x)],[np.min(y), np.max(y)]])

    # Update bins
    if np.asarray([bins]).size == 1:
        bins = np.asarray([bins, bins])

    # Make histogram
    rho = histogram2d(x, y, bins, limits, weights=w)
    # Get x and y  centers
    xcenters = bin_centers(limits[0,0], limits[0,1], bins[0])
    ycenters = bin_centers(limits[1,0], limits[1,1], bins[1])

    # Check density
    if density:
        dA = (xcenters[1] - xcenters[0]) * (ycenters[1] - ycenters[0])
        rho = rho / np.sum(rho*dA)

    # log scale
    if log_scale:
        # Implement log scale
        rho = np.log(rho + log_offset)

    # Show data
    im = ax.imshow(
                   rho.T,
                   extent = [limits[0,0], limits[0,1], limits[1,0], limits[1,1]],
                   origin='lower',
                   aspect = 'auto',
                   cmap = cmap,
                   zorder=0,
                  )

    if set_limits:
        ax.set_xlim(limits[0])
        ax.set_ylim(limits[1])
    return im

def ax_histogram_contour2d(
                           ax,
                           x,
                           y,
                           levels=[0.68, 0.95],
                           w=None,
                           limits=None,
                           set_limits=False,
                           cmap="terrain_r",
                           bins=100,
                           **kwargs
                          ):
    '''Quickly make some contours using histograms'''
    import numpy as np
    from fast_histogram import histogram2d

    # Update bins
    if np.asarray([bins]).size == 1:
        bins = np.asarray([bins, bins])

    # Make histogram
    rho = histogram2d(x, y, bins, limits, weights=w)
    rho[~np.isfinite(rho)] = 0.0
    rho = rho/np.sum(rho)
    # Get x and y  centers
    xcenters = bin_centers(limits[0,0], limits[0,1], bins[0])
    ycenters = bin_centers(limits[1,0], limits[1,1], bins[1])
    xgrid, ygrid = np.meshgrid(xcenters, ycenters)
    # Get percentile levels
    percentiles = percentile_levels(xgrid, ygrid, rho, levels)

    # Show data
    ct = ax.contour(
                    xgrid,
                    ygrid,
                    rho.T,
                    levels=percentiles,
                    extent = [limits[0,0], limits[0,1], limits[1,0], limits[1,1]],
                    origin='lower',
                    aspect = 'auto',
                    vmin=0.,
                    vmax=np.max(rho),
                    cmap = cmap,
                    **kwargs
                    )

    # Set limits
    if set_limits:
        ax.set_xlim(limits[0])
        ax.set_ylim(limits[1])
    return ct

#### Function evaluation plots ####
def ax_function1d(
                  ax,
                  func,
                  limits,
                  set_limits=False,
                  log_scale=False,
                  density=False,
                  res=100,
                  **kwargs
                 ):
    '''\
    Quickly make a plot of some function
    '''
    import numpy as np
    
    # Get xspace
    xspace = np.linspace(limits[0], limits[1], res).reshape((res,1))
    # Get yspace 
    yspace = func(xspace)
    # Interpolators can be weird sometimes. Best to avoid negative densities
    yspace[yspace < 0.0] = 0.0


    # Make sure this thing integrates to one
    if density:
        dx = xspace[1] - xspace[0]
        yspace = yspace / np.sum(yspace*dx)

    # log scale
    if log_scale:
        # Implement log scale
        ax.set_yscale('log')
        #rho = np.log(rho + log_offset)

    # Show data
    ax.plot(xspace, yspace, **kwargs)
    # Set limits
    if set_limits:
        ax.set_xlim(limits)

    # We may need to return this
    return ax

def ax_function_contour2d(
                          ax,
                          func,
                          limits,
                          levels=[0.68, 0.95],
                          set_limits=False,
                          cmap="terrain_r",
                          res=100,
                          **kwargs
                         ):
    '''Quickly make some contours using histograms'''
    import numpy as np

    # Update bins
    if np.asarray([res]).size == 1:
        res = np.asarray([res, res])

    # Get xspace
    xspace = np.linspace(limits[0,0], limits[0,1], res[0])
    # Get yspace
    yspace = np.linspace(limits[1,0], limits[1,1], res[1])
    # Get meshgrid
    xgrid, ygrid = np.meshgrid(xspace, yspace)
    # Get evaluation set
    x_eval = np.asarray([xgrid.flatten(), ygrid.flatten()]).T
    # Get density
    rho = func(x_eval).reshape(res)
    # set nans to zero
    rho[~np.isfinite(rho)] = 0.0
    rho[rho < 0.0] = 0.0
    # make density
    rho = rho/np.sum(rho)
    # Get percentile levels
    percentiles = percentile_levels(xgrid, ygrid, rho, levels)

    # Show data
    ct = ax.contour(
                    xgrid,
                    ygrid,
                    rho,
                    levels=percentiles,
                    extent = [limits[0,0], limits[0,1], limits[1,0], limits[1,1]],
                    aspect = 'auto',
                    origin='lower',
                    cmap = cmap,
                    vmin=0.,
                    vmax=np.max(rho),
                    zorder=0,
                    **kwargs
                    )

    # Set limits
    if set_limits:
        ax.set_xlim(limits[0])
        ax.set_ylim(limits[1])
    return ct

def ax_function2d(
                  ax,
                  func,
                  limits,
                  set_limits=False,
                  cmap="terrain_r",
                  res=100,
                  density=False,
                  log_scale=False,
                  log_offset=0.,
                  **kwargs
                 ):
    '''Quickly make some contours using histograms'''
    import numpy as np

    # Update bins
    if np.asarray([res]).size == 1:
        res = np.asarray([res, res])

    # Get xspace
    xspace = np.linspace(limits[0,0], limits[0,1], res[0])
    # Get yspace
    yspace = np.linspace(limits[1,0], limits[1,1], res[1])
    # Get meshgrid
    xgrid, ygrid = np.meshgrid(xspace, yspace)
    xgrid = xgrid.flatten()
    ygrid = ygrid.flatten()
    # Get evaluation set
    x_eval = np.asarray([xgrid, ygrid]).T
    # Get density
    rho = func(x_eval).reshape(res)
    # log scale
    #if log_scale:
    #    # Implement log scale
    #    rho = np.log(rho + log_offset)

    # set nans to zero
    rho[~np.isfinite(rho)] = 0.0
    # Interpolators can be weird sometimes. Best to avoid negative densities
    rho[rho < 0.0] = 0.0
    if density:
        # make density
        dA = (xspace[1] - xspace[0]) * (yspace[1] - yspace[0])
        rho = rho / np.sum(rho*dA)
    # Log scale colors
    if log_scale:
        colornorm="log"
        vmin = np.min(rho) + log_offset
    else:
        colornorm="linear"
        vmin = 0.
    # Show data
    im = ax.imshow(
                   rho,
                   extent = [limits[0,0], limits[0,1], limits[1,0], limits[1,1]],
                   origin='lower',
                   aspect = 'auto',
                   cmap = cmap,
                   norm=colornorm,
                   vmin = vmin,
                   vmax = np.max(rho),
                   zorder=0,
                   **kwargs
                  )

    # Set limits
    if set_limits:
        ax.set_xlim(limits[0])
        ax.set_ylim(limits[1])
    return im

#### Scatter methods ####
def ax_plot1d(
              ax,
              x, y,
              limits=None,
              set_limits=False,
              log_scale=False,
              density=False,
              **kwargs
             ):
    '''\
    Quickly make a plot of some function
    '''
    import numpy as np
    
    # Update limits
    if limits is None:
        limits = np.asarray([np.min(x), np.max(x)])

    # Make sure this thing integrates to one
    if density:
        _ux = np.sort(np.unique(x))
        dx = _ux[1] - _ux[0]
        y = y / np.sum(y*dx)

    # log scale
    if log_scale:
        # Implement log scale
        ax.set_yscale('log')
        #rho = np.log(rho + log_offset)

    # Show data
    ax.plot(x, y, **kwargs)
    # Set limits
    if set_limits:
        ax.set_xlim(limits)

    # We may need to return this
    return ax

def ax_scatter_contour2d(
                         ax,
                         x, y, z,
                         limits=None,
                         levels=[0.68, 0.95],
                         set_limits=False,
                         cmap="terrain_r",
                         **kwargs
                        ):
    '''Quickly make some contours using histograms'''
    import numpy as np

    # Update limits
    if limits is None:
        limits = np.asarray([[np.min(x), np.max(x)],[np.min(y), np.max(y)]])

    # set nans to zero
    z[~np.isfinite(z)] = 0.0
    # Interpolators really be like that
    z[z < 0.0] = 0.0
    # make density
    z = z/np.sum(z)
    # Get percentile levels
    percentiles = percentile_levels(x, y, z, levels)

    # Show data
    ct = ax.contour(
                    x,
                    y,
                    z,
                    levels=percentiles,
                    extent = [limits[0,0], limits[0,1], limits[1,0], limits[1,1]],
                    aspect = 'auto',
                    origin='lower',
                    cmap = cmap,
                    vmin=0.,
                    vmax=np.max(z),
                    zorder=0,
                    **kwargs
                    )

    # Set limits
    if set_limits:
        ax.set_xlim(limits[0])
        ax.set_ylim(limits[1])
    return ct

def ax_scatter2d_density(
                         ax,
                         x, y, z,
                         limits=None,
                         set_limits=False,
                         cmap="terrain_r",
                         density=False,
                         log_scale=False,
                         log_offset=0.,
                         **kwargs
                        ):
    '''Quickly make some contours using histograms'''
    import numpy as np
    # Update limits
    if limits is None:
        limits = np.asarray([[np.min(x), np.max(x)],[np.min(y), np.max(y)]])

    # log scale
    if log_scale:
        # Implement log scale
        z = np.log(z + log_offset)

    # set nans to zero
    z[~np.isfinite(z)] = 0.0
    # Interpolators can be weird sometimes. Best to avoid negative densities
    z[z < 0.0] = 0.0

    # Make sure this thing integrates to one
    if density:
        _ux, _uy = np.sort(np.unique(x)), np.sort(np.unique(y))
        dx = _ux[1] - _ux[0]
        dy = _uy[1] - _uy[0]
        z = z / np.sum(z*dx*dy)

    # Show data
    im = ax.scatter(
                    x,y,c=z,
                    cmap = cmap,
                    vmin=0.,
                    vmax=np.max(z),
                    **kwargs
                   )

    # Set limits
    if set_limits:
        ax.set_xlim(limits[0])
        ax.set_ylim(limits[1])
    return im

def ax_scatter2d_error(
                       ax,
                       x, y,
                       dx,dy,
                       limits=None,
                       set_limits=False,
                       ecolor=None,
                       elinewidth=None,
                       **kwargs
                      ):
    '''Quickly make some contours using histograms'''
    import numpy as np
    # Update limits
    if limits is None:
        limits = np.asarray([[np.min(x), np.max(x)],[np.min(y), np.max(y)]])

    # Show data
    ax.scatter(
               x,y,
               **kwargs
              )
    if (not ecolor is None) and (not elinewidth is None):
        # Show error bars
        ax.errorbar(
                    x,y,
                    dy,dx,
                    fmt='none',
                    ecolor=ecolor,
                    elinewidth=elinewidth,
                   )

    # Set limits
    if set_limits:
        ax.set_xlim(limits[0])
        ax.set_ylim(limits[1])

