# import libraries
from dispel4py.core import GenericPE
from dispel4py.base import BasePE, IterativePE, ConsumerPE, create_iterative_chain
from dispel4py.workflow_graph import WorkflowGraph

from obspy.clients.fdsn import Client
from obspy.signal.util import next_pow_2
from whiten import spectralwhitening_smooth
from normalization import onebit_norm, mean_norm, gain_norm, env_norm
from scipy.fftpack import fft
import numpy as np
from obspy.core import read
from obspy import UTCDateTime
from obspy.core.stream import Stream
from numpy import linspace
import os
import traceback
# import matplotlib as mpl
# mpl.use('Agg')
# import matplotlib.pyplot as plt



# to get the waveforms for each station in the stations_list
def get_waveforms(client, stations_list, stations_names):
    
    result = []
    
    try:

        st = client.get_waveforms_bulk(stations_list, attach_response=True) 
        counter = 0
        for tr in st:
            
            rl = []
            
            network_name = tr.stats['network']
            station_name = tr.stats['station']
            stations_names.remove((network_name, station_name))
            
            rl.append(network_name)
            rl.append(station_name)
            rl.append([Stream(traces=[tr]), station_name, counter])
            
            result.append(rl)

            counter += 1

        if stations_names:
            print('Failed to read stations %s' % stations_names)

    except:
        print('Failed to read stations XXXX %s' % stations_names)
        print(traceback.format_exc())
        pass
    
    return result



# parse the input file, 
# and write the response inventory file and the station stream data file
def parse_and_write_file(filename, starttime, endtime, channel, counter, bulksize):
    
    t_start = UTCDateTime(starttime)
    t_finish = UTCDateTime(endtime)
    
    client = Client()
    stations_list = []
    stations_names = set()
    result = []
    network_list = []
    
    # parse the file and get the waveforms for each station
    with open(filename, 'r') as f:
        i = 1
        for station in f.readlines():

            if i % bulksize != 0:
                network, station_name = station.split()

                if network not in network_list:
                    network_list.append(network)

                stations_names.add((network, station_name))
                # station_name = station.strip()
                stations_list.append((network, station_name, "", channel, t_start, t_finish))
                i += 1
            else:
                result.append(get_waveforms(client, stations_list, stations_names))
                stations_list = []
                stations_names = set()
                i = 1

    if stations_list:
        result.append(get_waveforms(client, stations_list, stations_names))
    
    
    # write the response inventory file
    for nt in network_list:
        inv = client.get_stations(network=nt, channel = channel, level="response")
        inv.write('INPUT/%s_inventory.xml' % nt, format='STATIONXML')

    
    # write the station stream data file
    for line in [x for sublist in result for x in sublist]:
        line[2][0].write('INPUT/stream_%s_%s_%s.mseed' % (line[0], line[1], line[2][2]))
    
    return



if __name__ == '__main__':
    
    filename = 'Copy-Uniq-OpStationList-NetworkStation.txt'
    starttime='2020-06-01T06:00:00.000'
    endtime='2020-06-01T07:00:00.000'
    channel='BHZ'
    counter = 0
    bulksize = 10
    
    parse_and_write_file(filename, starttime, endtime, channel, counter, bulksize)

