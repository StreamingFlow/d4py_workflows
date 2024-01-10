import glob
import json
import numpy as np
from obspy import Stream, Trace, read
from obspy.core.trace import Stats


from dispel4py.core import GenericPE
from dispel4py.base import BasePE, IterativePE, ConsumerPE, create_iterative_chain
from dispel4py.workflow_graph import WorkflowGraph
from obspy.clients.fdsn import Client
from obspy.signal.util import next_pow_2
from whiten import spectralwhitening_smooth
from normalization import onebit_norm, mean_norm, gain_norm, env_norm
from scipy.fftpack import fft

# from obspy.core import read
from obspy import read_inventory
from obspy import UTCDateTime
# from obspy.core.stream import Stream
from numpy import linspace
import os
import traceback
# import matplotlib as mpl
# mpl.use('Agg')
# import matplotlib.pyplot as plt
# import glob
import re



# Convert Stream to dict
def stream_to_dict(stream):
    traces = []
    for tr in stream:
        trace_dict = {
            "stats": {
                "network": tr.stats.network,
                "station": tr.stats.station,
                "location": tr.stats.location,
                "channel": tr.stats.channel,
                "starttime": str(tr.stats.starttime),
                "sampling_rate": tr.stats.sampling_rate,
                "delta": tr.stats.delta,
                "npts": tr.stats.npts,
            },
            "data": tr.data.tolist()  # Convert numpy array to list
        }
        traces.append(trace_dict)
    return {"traces": traces}

# Convert dict back to Stream
def dict_to_stream(stream_dict):
    stream = Stream()
    for trace_dict in stream_dict["traces"]:
        stats = Stats()
        stats.network = trace_dict["stats"]["network"]
        stats.station = trace_dict["stats"]["station"]
        stats.location = trace_dict["stats"]["location"]
        stats.channel = trace_dict["stats"]["channel"]
        stats.starttime = trace_dict["stats"]["starttime"]
        stats.sampling_rate = trace_dict["stats"]["sampling_rate"]
        stats.delta = trace_dict["stats"]["delta"]
        stats.npts = trace_dict["stats"]["npts"]
        
        data_array = np.array(trace_dict["data"])  # Convert list back to numpy array
        
        tr = Trace(data=data_array, header=stats)
        stream.append(tr)
    return stream



# Convert complex number to dict
def complex_to_dict(c):
    return {"real": c.real, "imag": c.imag}

# Convert dict back to complex number
def dict_to_complex(d):
    return complex(d["real"], d["imag"])

# FFT data (complex numbers) to list
def fft_data_to_list(fft_data):
    complex_list = [complex_to_dict(c) for c in fft_data]
    return complex_list

# list back to FFT data (complex numbers)
def list_to_fft_data(complex_list):

    return np.array([dict_to_complex(d) for d in complex_list])



# # Read example stream
# network, station_name = "AK", "BMR"

# stream_file = glob.glob('INPUT/stream_%s_%s_*.mseed' % (network, station_name))

# print(stream_file)
# # Example Usage:
# st = read(stream_file[0])  # Load example stream

# data = stream_to_dict(st)

# st_from_data = dict_to_stream(data)

# print(st_from_data)
# print(type(st_from_data))

# st_from_data

# # Convert Stream to dict and then to JSON string
# stream_dict = stream_to_dict(st)
# json_string = json.dumps(stream_dict)

# # Convert the JSON string back to dict and then to Stream
# loaded_dict = json.loads(json_string)
# loaded_stream = dict_to_stream(loaded_dict)

# print(loaded_stream)  # Should print the same Stream details as the original




class StreamRead(IterativePE):
    
    def __init__(self):
        IterativePE.__init__(self)
        
    def _process(self, filename):
        
        # open the filename, and get each station and find its corresponding stream data file
        with open(filename, 'r') as f:

            for station in f.readlines():
                
                network, station_name = station.split()
                
                stream_file = glob.glob('INPUT/stream_%s_%s_*.mseed' % (network, station_name))
                
                if stream_file:

                    stream_data = read(stream_file[0])
                    counter = re.findall(r'stream_(.+)_(.+)_(.+).mseed', stream_file[0])[0][2]
                
                    # self.write('output', [stream_data, station_name, counter, network])
                    self.write('output', [stream_to_dict(stream_data), station_name, counter, network])

                else:
                	self.log('Failed to find %s %s' % (network, station_name))

class StreamToFile(ConsumerPE):
    
    def __init__(self):
        ConsumerPE.__init__(self)
        
    def _process(self, data):

        
        # str1 = data[0]
        str1 = list_to_fft_data(data[0])
        station= data[1]
        counter = data[2]

        dir = ROOT_DIR + 'DATA/'+ starttime
        if not os.path.exists(dir):
            os.makedirs(dir)
        directory = dir +'/'+ station
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        try:
            fout = directory+'/%s_%s_preprpcessed.SAC' % (station, counter)
        except TypeError:
            # maybe there's no "%s" in the string so we ignore count - bad idea?
            fout = file_dest
        
        np.save(fout, str1)



def factors(n):
    return [(i, n / i) for i in range(1, int(n**0.5)+1) if n % i == 0]


def factors(n):
    return [(i, n / i) for i in range(1, int(n**0.5)+1) if n % i == 0]


class Decimate(IterativePE):
    
    def __init__(self, sps):
        IterativePE.__init__(self)
        self.sps = sps
    
    def _process(self, data):
        # str1 = data[0]
        str1 = dict_to_stream(data[0])
        
        str1.decimate(int(str1[0].stats.sampling_rate/self.sps))
        
        j = int(str1[0].stats.sampling_rate/self.sps)
        
        if j > 16:
            facts=factors(j)[-1]
            str1[0].decimate(facts[0])
            str1[0].decimate(facts[1])
        else:
            str1[0].decimate(j)
        
        # data[0] = str1
        data[0] = stream_to_dict(str1)
        return data


class Detrend(IterativePE):
    
    def __init__(self):
        IterativePE.__init__(self)
    
    def _process(self, data):

        data[0] = dict_to_stream(data[0])
        
        data[0].detrend('simple')

        data[0] = stream_to_dict(data[0])
        return data

class Demean(IterativePE):
    
    def __init__(self):
        IterativePE.__init__(self)
        
    def _process(self, data):
        
        data[0] = dict_to_stream(data[0])

        data[0].detrend('demean')

        data[0] = stream_to_dict(data[0])
        return data


class RemoveResponse(IterativePE):
    
    def __init__(self, pre_filt, units):
        IterativePE.__init__(self)
        self.pre_filt = pre_filt
        self.units = units
    
    def _process(self, data):

        data[0] = dict_to_stream(data[0])

        # read the corresponding inventory file in order to get response later
        inv = read_inventory('INPUT/%s_inventory.xml' % data[-1])
        data[0].remove_response(inv, output=self.units, pre_filt=self.pre_filt)

        data[0] = stream_to_dict(data[0])
        
        return data


class Filter(IterativePE):
    
    def __init__(self, freqmin=0.01, freqmax=1., corners=4, zerophase=False):
        IterativePE.__init__(self)
        self.freqmin = freqmin
        self.freqmax = freqmax
        self.corners = corners
        self.zerophase= zerophase
    
    def _process(self, data):
        
        data[0] = dict_to_stream(data[0])

        data[0].filter('bandpass', freqmin=self.freqmin, freqmax=self.freqmax, \
                corners=self.corners, zerophase=self.zerophase)
        
        data[0] = stream_to_dict(data[0])
        return data


class CalculateNorm(IterativePE):
    
    def __init__(self, norm, N):
        IterativePE.__init__(self)
        self.norm = norm
        self.N = N
    
    def _process(self, data):

        data[0] = dict_to_stream(data[0])
        
        if self.norm is 'onebit':
            data[0] = onebit_norm(data[0])
        
        elif norm is 'mean':
            data[0] = mean_norm(data[0], self.N)
        
        elif norm is 'gain':
            data[0] = gain_norm(data[0], self.N)
        
        elif norm is 'env':
            data[0] = env_norm(data[0], self.N)

        data[0] = stream_to_dict(data[0])
        
        return data


class Whiten(IterativePE):
    
    def __init__(self, smooth):
        IterativePE.__init__(self)
        self.smooth = smooth
    
    def _process(self, data):
        
        data[0] = dict_to_stream(data[0])

        if self.smooth is not None:
            data[0] = spectralwhitening_smooth(data[0], smooth)

        data[0] = stream_to_dict(data[0])
        
        return data


class CalculateFft(IterativePE):
    
    def __init__(self, type, shift):
        IterativePE.__init__(self)
        self.type = type
        self.shift = shift
    
    def _process(self, data):

        data[0] = dict_to_stream(data[0])
        
        if self.type is not None:
            str_data = data[0][0].data
            N1 = len(str_data)
            str_data = str_data.astype(self.type)
            
            size = max(2 * self.shift + 1, (N1) + shift)
            nfft = next_pow_2(size)
            
            # print ("station %s and network %s - size in calc_fft %s " % \
            #    (data[0][0].stats['station'], data[0][0].stats['network'], size)) 
            
            IN1 = fft(str_data, nfft)

            # print("herererere")
            # print(IN1)
            # return [IN1, data[1], data[2]]

            return [fft_data_to_list(IN1), data[1], data[2]]
        else:
            # return [data[0][0].data, data[1], data[2]] 
            print("incorrect type")


ROOT_DIR = './OUTPUT/'
starttime='2020-06-01T06:00:00.000'
endtime='2020-06-01T07:00:00.000'


streamRead=StreamRead()
streamRead.name = 'streamRead'
streamToFile = StreamToFile()
streamToFile.name='StreamToFile'

decim = Decimate(4)
detrend = Detrend()
demean = Demean()

pre_filt = (0.005, 0.006, 30.0, 35.0)
units = 'VEL'
removeResponse = RemoveResponse(pre_filt, units)

filt = Filter()

norm = 'env'
N = 15
calNorm = CalculateNorm(norm, N)

whiten = Whiten(None)

type = 'float64'
shift = 5000
calcFft = CalculateFft(type, shift)

graph = WorkflowGraph()

graph.connect(streamRead, StreamRead.OUTPUT_NAME, decim, 'input')
graph.connect(decim, 'output', detrend, 'input')
graph.connect(detrend, 'output', demean, 'input')
graph.connect(demean, 'output', removeResponse, 'input')
graph.connect(removeResponse, 'output', filt, 'input')
graph.connect(filt, 'output', calNorm, 'input')
graph.connect(calNorm, 'output', whiten, 'input')
graph.connect(whiten, 'output', calcFft, 'input')
graph.connect(calcFft, 'output', streamToFile, StreamToFile.INPUT_NAME)

