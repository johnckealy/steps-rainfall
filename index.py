from io import BytesIO, open
from ftplib import FTP
import re
from datetime import datetime
import h5py


RADARPATH = "/home/jokea/weather/radar"


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

    # breakpoint()
    zipped = zip(validtimes, filenames) 
    zipped = list(zipped) 
    res = sorted(zipped, key=lambda x: x[0]) 

    for i in range(no_of_files):
        filename = res[-1-i][1]
        date = datetime.strftime(res[-1-i][0], "%Y%m%d")
        with open(f"{RADARPATH}/meteireann/{date}/{filename}", 'wb') as fp:
            print(f"Downloading {filename}")
            ftp.retrbinary(f"RETR {filename}", fp.write)

    ftp.quit()



# download_meteireann_radar(no_of_files=6)


fmet = h5py.File(f"{RADARPATH}/meteireann/20200622/T_PAAH72_C_EIDB_20200622200500.hdf")
fopera = h5py.File(f"{RADARPATH}/OPERA/20180824/T_PAAH21_C_EUOC_20180824204500.hdf")

breakpoint()