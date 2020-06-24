#!/bin/env python
"""
STEPS nowcast
=============

This tutorial shows how to compute and plot an ensemble nowcast using Swiss
radar data.

"""

from pylab import *
from datetime import datetime
from pprint import pprint
from pysteps import io, nowcasts, rcparams
from pysteps.motion.lucaskanade import dense_lucaskanade
from pysteps.postprocessing.ensemblestats import excprob
from pysteps.utils import conversion, dimension, transformation
from pysteps.visualization import plot_precip_field
import cartopy.crs as ccrs
from matplotlib.animation import FuncAnimation



def animate(i):
    # Set nowcast parameters
    # n_ens_members = 20
    n_leadtimes = 2
    # seed = 24

    ###############################################################################
    # Read precipitation field
    # ------------------------
    #
    # First thing, the sequence of Swiss radar composites is imported, converted and
    # transformed into units of dBR.

    date = datetime.strptime("202006222010", "%Y%m%d%H%M")
    data_source = "meireann"

    # Load data source config
    root_path = rcparams.data_sources[data_source]["root_path"]
    path_fmt = rcparams.data_sources[data_source]["path_fmt"]
    fn_pattern = rcparams.data_sources[data_source]["fn_pattern"]
    fn_ext = rcparams.data_sources[data_source]["fn_ext"]
    importer_name = rcparams.data_sources[data_source]["importer"]
    importer_kwargs = rcparams.data_sources[data_source]["importer_kwargs"]
    timestep = rcparams.data_sources[data_source]["timestep"]

    # Find the radar files in the archive
    fns = io.find_by_date(
        date, root_path, path_fmt, fn_pattern, fn_ext, timestep, num_prev_files=2
    )

    # Read the data from the archive
    importer = io.get_method(importer_name, "importer")
    R, _, metadata = io.read_timeseries(fns, importer, **importer_kwargs)
    R, metadata = conversion.to_rainrate(R, metadata)
    R, metadata = dimension.aggregate_fields_space(R, metadata, 2000)
    R, metadata = transformation.dB_transform(R, metadata, threshold=0.1, zerovalue=-15.0)

    # Set missing values with the fill value
    R[~np.isfinite(R)] = -15.0


    # Plot the rainfall field
    # plot_precip_field(R[-1, :, :], geodata=metadata)

    # Estimate the motion field
    V = dense_lucaskanade(R)

    # The S-PROG nowcast
    nowcast_method = nowcasts.get_method("sprog")
    R_f = nowcast_method(
        R[-3:, :, :],
        V,
        n_leadtimes,
        n_cascade_levels=8,
        R_thr=-10.0,
        decomp_method="fft",
        bandpass_filter_method="gaussian",
        probmatching_method="mean",
    )

    # Back-transform to rain rate
    # breakpoint()
    R_f = transformation.dB_transform(R_f, threshold=-10.0, inverse=True)[0]


    # R_f = np.flipud(R_f)
    # R_f = np.swapaxes(R_f, 0, 1)
    # fig = plt.figure(figsize=(8, 6))
    # ax = plt.axes(projection=ccrs.PlateCarree())
    plt.contourf(R_f[-1], np.linspace(0.1, 5, 200), )
                # transform=ccrs.PlateCarree()))
    plt.colorbar()                
    # ax.coastlines()
    plt.show()

    # # Plot the S-PROG forecast
    # cont = plot_precip_field(
    #     R_f[-1, :, :],
    #     geodata=metadata,
    #     title="S-PROG (+ %i min)" % (n_leadtimes * timestep),
    #     colorbar=False
    # )


    # return cont


animate(0)

# anim = FuncAnimation(fig, animate, frames=6,  interval=500)
# plt.show()
# anim.save('radar.gif', writer='imagemagick', fps=1)