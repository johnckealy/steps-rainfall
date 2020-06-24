#!/bin/env python

from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from pprint import pprint
from pysteps import io, motion, nowcasts, rcparams, verification
from pysteps.utils import conversion, transformation
from pysteps.visualization import plot_precip_field, quiver
from utils import get_latlon_grid



def extrapolate(datestr, n_leadtimes=12, provider="opera"):
    date = datetime.strptime(datestr, "%Y%m%d%H%M")
    data_source = rcparams.data_sources[provider]

    root_path = data_source["root_path"]
    path_fmt = data_source["path_fmt"]
    fn_pattern = data_source["fn_pattern"]
    fn_ext = data_source["fn_ext"]
    importer_name = data_source["importer"]
    importer_kwargs = data_source["importer_kwargs"]
    if provider == "meteireann":
        importer_kwargs['qty'] = "DBZH"
    timestep = data_source["timestep"]

    # Find the input files from the archive
    fns = io.archive.find_by_date(
        date, root_path, path_fmt, fn_pattern, fn_ext, timestep, num_prev_files=3
    )

    importer = io.get_method(importer_name, "importer")
    Z, _, metadata = io.read_timeseries(fns, importer, **importer_kwargs)

    R, metadata = conversion.to_rainrate(Z, metadata)
    R_o = R[-1, :, :].copy()
    R_ = R[-1, :, :].copy()
    R, metadata = transformation.dB_transform(R, metadata, threshold=0.1, zerovalue=-15.0)

    oflow_method = motion.get_method("LK")
    V = oflow_method(R[-3:, :, :])

    # Extrapolate the last radar observation
    extrapolate = nowcasts.get_method("extrapolation")
    R[~np.isfinite(R)] = metadata["zerovalue"]
    R_f = extrapolate(R[-1, :, :], V, n_leadtimes)

    # Back-transform to rain rate
    R_f = transformation.dB_transform(R_f, threshold=-10.0, inverse=True)[0]

    return R_o, R_f, metadata




def original_field(datestr, provider="opera"):
    date = datetime.strptime(datestr, "%Y%m%d%H%M")
    data_source = rcparams.data_sources[provider]

    root_path = data_source["root_path"]
    path_fmt = data_source["path_fmt"]
    fn_pattern = data_source["fn_pattern"]
    fn_ext = data_source["fn_ext"]
    importer_name = data_source["importer"]
    importer_kwargs = data_source["importer_kwargs"]
    if provider == "meteireann":
        importer_kwargs['qty'] = "DBZH"
    timestep = data_source["timestep"]

    # Find the input files from the archive
    fns = io.archive.find_by_date(
        date, root_path, path_fmt, fn_pattern, fn_ext, timestep, num_prev_files=3
    )

    importer = io.get_method(importer_name, "importer")
    Z, _, metadata = io.read_timeseries(fns, importer, **importer_kwargs)

    R, metadata = conversion.to_rainrate(Z, metadata)
    R_o = R[-1, :, :].copy()

    return R_o, metadata



if __name__=="__main__":
    original_field, extrapolated_fields, metadata = extrapolate("201808241945", n_leadtimes=12, provider="opera")

    pprint(metadata)

    plot_precip_field(original_field, geodata=metadata, map='cartopy')

    plt.figure()
    plot_precip_field(extrapolated_fields[-1], geodata=metadata, map='cartopy')

    plt.show()