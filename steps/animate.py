
from extrapolation import extrapolate, original_field
from matplotlib.animation import FuncAnimation
from matplotlib import pyplot as plt
from utils import find_gridpoint, shell_command
from pysteps.visualization import plot_precip_field
import pprint
import numpy as np
import cartopy.crs as ccrs


fig = plt.figure()
fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)

oe_field, extrapolated_fields, metadata = extrapolate("202006241525", n_leadtimes=3, provider="meteireann")

# dates = ["201808242045", "201808242100", "201808242115", "201808242130", "201808242145", 
#          "201808242200", "201808242215", "201808242230", "201808242245", "201808242300", 
#          "201808242315", "201808242330"]
dates = ["202006241515", "202006241520", "202006241525"]


def point_value(field, lonpoint, latpoint):
    F = np.load('coords.npz')
    lons = F['lons']
    lats = F['lats']
    lons = np.flipud(lons)
    lats = np.flipud(lats)
    # import pdb; pdb.set_trace()
    coords = find_gridpoint(lons, lats, lonpoint, latpoint)
    return field[coords]

def animate_extrapolants(i):
    fig.clf()
    cont = plot_precip_field(extrapolated_fields[i-1], geodata=metadata, map='cartopy')
    return cont

def animate_originals(date):
    fig.clf()
    o_field, metadata = original_field(date, provider="meteireann")
    cont = plot_precip_field(o_field, geodata=metadata, map="cartopy", drawlonlatlines=True, cartopy_scale='10m')
    point_precip = point_value(oe_field, 53.784829, -7.694123)
    print(f"Point value at [53.784829, -7.694123] is {point_precip}mm/hr")
    plt.plot(-7.694123, 53.784829, color='r', marker='o', transform=ccrs.PlateCarree())
    plt.savefig(f"tmp/Ireland_{date}.png", dpi=300)




if __name__=="__main__":
    shell_command('mkdir tmp/')
    for i,date in enumerate(dates):
        animate_originals(date)
    shell_command('convert -delay 50 tmp/Ireland*.png -loop 0 Ireland.gif')
    shell_command('rm tmp/*')
    shell_command('rmdir tmp/')