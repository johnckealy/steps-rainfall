from io import BytesIO, open
from ftplib import FTP
import re
from datetime import datetime
from pyproj import Proj, transform
import h5py
import numpy as np
import time
from matplotlib import pyplot as plt
import os
from netCDF4 import Dataset as netcdf_dataset
from cartopy import config
from scipy import spatial

RADARPATH = "/home/jokea/steps-rainfall/radar"


def download_meteireann_radar(user='me3718', passwd='YTB@ZTg2', no_of_files=1):
    """ Download the latest frame of met eireann radar data from the ftp 
    server, starting with the latest and moving backwards by number_of_frames """

    validtimes = []
    filenames = []
    ftp = FTP('ftp.met.ie')
    ftp.login(user=user, passwd=passwd)
    ftp.cwd('/openradar')
    for filename in ftp.nlst():
        m = re.search('\d{14}', filename)
        validtimes.append(datetime.strptime(m.group(), "%Y%m%d%H%M%S"))
        filenames.append(filename)

    zipped = zip(validtimes, filenames) 
    zipped = list(zipped) 
    res = sorted(zipped, key=lambda x: x[0]) 

      

    for i in range(no_of_files):
        date = datetime.strftime(res[-1-i][0], "%Y%m%d")
        metdir = f"{RADARPATH}/meteireann/{date}"
        if not os.path.isdir(metdir):
            os.mkdir(metdir)  
        filename = res[-1-i][1]
        with open(f"{metdir}/{filename}", 'wb') as fp:
            print(f"Downloading {filename}")
            ftp.retrbinary(f"RETR {filename}", fp.write)

    ftp.quit()




def download_meteireann_radarfile(datetimestr, user='me3718', passwd='YTB@ZTg2'):
    """ Download a specific radar file from Met Eireann """

    ftp = FTP('ftp.met.ie')
    ftp.login(user=user, passwd=passwd)
    ftp.cwd('/openradar')

    metdir = f"{RADARPATH}/meteireann/{datetimestr[:8]}/"
    if not os.path.isdir(metdir):
        os.mkdir(metdir)        
    filename = f"T_PAAH72_C_EIDB_{datetimestr}00.hdf"

    with open(f"{metdir}/{filename}", 'wb') as fp:
        print(f"Downloading {filename}")
        ftp.retrbinary(f"RETR {filename}", fp.write)
    ftp.quit()



# for hr in range(11, 20):
#     for m in np.arange(0, 60, 5):
#         m = str(m).zfill(2)
#         download_meteireann_radarfile(f"20200623{hr}{m}", user='me3718', passwd='YTB@ZTg2')



def get_latlon_grid(h5filename, npfilename):
    """ Using the data in the met eireann h5 file, create
    a lat/lon grid array """
    start = datetime.now()
    with h5py.File(h5filename, 'r') as h5file:
        projection = h5file['where'].attrs['projdef'].decode('utf-8')
        xscale =  h5file['where'].attrs['xscale']
        yscale =  h5file['where'].attrs['yscale']
        xsize =  h5file['where'].attrs['xsize']
        ysize =  h5file['where'].attrs['ysize']
        LL_lat =  h5file['where'].attrs['LL_lat']
        LL_lon =  h5file['where'].attrs['LL_lon']

    #projection = '+proj=stere+ellps=WGS84+lat_0=56+lon_0=10.5666+lat_ts=56' 
    dmi_proj = Proj(projparams=projection)  # DMI input, custom stereographic projection
    wgs_proj = Proj(init='EPSG:4326')  # WGS84

    ###Get start projections as wgs projections instead of lat and lon (for the `calculation)`
    x0, y0 = transform(wgs_proj, dmi_proj, LL_lon, LL_lat)
    print(x0, y0)

    lons = np.zeros((xsize, ysize))
    lats = np.zeros((xsize, ysize))

    for j,lon in enumerate(lons):
        print(f"{j} of {len(lons)}")
        for k,_ in enumerate(lons[0]):
            # breakpoint()
            east = x0 + j*xscale
            north = y0 + k*yscale
            ### convert back to lat and lon
            lon, lat = transform(dmi_proj, wgs_proj, east, north)
            lons[j,k] = lon
            lats[j,k] = lat 

    np.savez(npfilename, lons=lons, lats=lats)   
    print(f"Lat/Lon data generated. Data is saved to {npfilename}. \n")         
    print(f"Time Taken: {datetime.now()-start}")         
    return lons, lats         




def plotter(lons, lats, data):
    fig = plt.figure()
    ax = plt.axes(projection=ccrs.PlateCarree())
    plt.contourf(lons, lats, data, np.linspace(0.1, 190, 200), 
                transform=ccrs.PlateCarree())
    plt.colorbar()                
    ax.coastlines()
    
    return fig


def find_gridpoint(lons, lats, lonpoint, latpoint):
    """ Find the closest grid index on the 2D latlon grid to
    the specified lat lon point.  """
    lonlats = np.array(list(zip(lons.flatten(), lats.flatten())))
    _, index = spatial.KDTree(lonlats).query([lonpoint, latpoint], k=100)
    for point in index:
        glat = lats[ lats==lonlats[point][1] ][0]
        glon = lons[ lons==lonlats[point][0] ][0]
        idx = np.where(np.logical_and(lons==glon, lats==glat))
        coords = idx[0][0], idx[1][0]
    print(f"Index ({coords}) found for latlon=[{lonpoint}, {latpoint}] => closest grided latlon is [{lons[coords]}, {lats[coords]}]")        
    return coords



def get_radar_data(h5filename):
    m = re.search('\d{14}', h5filename)
    dt = m.group()[:8]
  
    fmet = h5py.File(f"{RADARPATH}/meteireann/{dt}/{h5filename}")
    data = fmet['dataset1']['data1']['data'][:]
    data = np.flipud(data)
    data = np.swapaxes(data, 0, 1)
    data[data==255] = -10

    F = np.load('coords.npz')
    lons = F['lons']
    lats = F['lats']

    return lons, lats, data




# if __name__=="__main__":
#     download_meteireann_radar(no_of_files=3)

# import json
# with open('radar.json', 'w', encoding='utf-8') as f:
#     json.dump(data.tolist(), f, ensure_ascii=False, indent=4)


