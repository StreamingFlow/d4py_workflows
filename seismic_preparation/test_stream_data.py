from obspy.core import read
import glob



filename = 'INPUT/stations.txt'
with open(filename, 'r') as f:

    for station in f.readlines():
        
        network, station_name = station.split()
        
        stream_file = glob.glob('INPUT/stream_%s_%s_*.mseed' % (network, station_name))