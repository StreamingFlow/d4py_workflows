import sys, os

#### Important -- change with your path to this workflow
sys.path.append('/home/user/d4py_workflows/seismic_preparation')
####

import copy
import glob
import os
import re
import traceback

import numpy as np
from numpy import (
    abs,
    absolute,
    amax,
    arange,
    conjugate,
    convolve,
    floor,
    linspace,
    logical_and,
    multiply,
    real,
    sign,
    sqrt,
    sum,
    true_divide,
    zeros,
)
from scipy.fftpack import fft, ifft
from scipy.signal.windows import triang

from obspy import UTCDateTime, read_inventory
from obspy.clients.fdsn import Client
from obspy.core import read
from obspy.core.stream import Stream
from obspy.signal import util
from obspy.signal.util import next_pow_2

from dispel4py.base import (
    BasePE,
    ConsumerPE,
    IterativePE,
    create_iterative_chain,
)
from dispel4py.core import GenericPE
from dispel4py.workflow_graph import WorkflowGraph

# -*- coding: utf-8 -*-
"""
Created on Mon Apr 07 09:23:16 2014

@author: abell5
"""


def nextpow2(N):
    """ Function for finding the next power of 2 """
    n = 1
    while n < N: n *= 2
    return n


def smooth(spec_ampl, N):
    # ....
    spec_ampl_2 = spec_ampl
    return spec_ampl_2


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

                    self.write('output', [stream_data, station_name, counter, network])

                else:
                    self.log('Failed to find %s %s' % (network, station_name))


class StreamToFile(ConsumerPE):

    def __init__(self):
        ConsumerPE.__init__(self)

    def _process(self, data):

        str1 = data[0]
        station = data[1]
        counter = data[2]

        dir = ROOT_DIR + 'DATA/' + starttime
        if not os.path.exists(dir):
            os.makedirs(dir)
        directory = dir + '/' + station
        if not os.path.exists(directory):
            os.makedirs(directory)

        try:
            fout = directory + '/%s_%s_preprpcessed.SAC' % (station, counter)
        except TypeError:
            fout = "tmp.SAC"

        np.save(fout, str1)


def factors(n):
    return [(i, n / i) for i in range(1, int(n ** 0.5) + 1) if n % i == 0]


def factors(n):
    return [(i, n / i) for i in range(1, int(n ** 0.5) + 1) if n % i == 0]


class Decimate(IterativePE):

    def __init__(self, sps):
        IterativePE.__init__(self)
        self.sps = sps

    def _process(self, data):
        str1 = data[0]

        str1.decimate(int(str1[0].stats.sampling_rate / self.sps))

        j = int(str1[0].stats.sampling_rate / self.sps)

        if j > 16:
            facts = factors(j)[-1]
            str1[0].decimate(facts[0])
            str1[0].decimate(facts[1])
        else:
            str1[0].decimate(j)

        data[0] = str1
        return data


class Detrend(IterativePE):

    def __init__(self):
        IterativePE.__init__(self)

    def _process(self, data):
        data[0].detrend('simple')
        return data


class Demean(IterativePE):

    def __init__(self):
        IterativePE.__init__(self)

    def _process(self, data):
        data[0].detrend('demean')
        return data


class RemoveResponse(IterativePE):

    def __init__(self, pre_filt, units):
        IterativePE.__init__(self)
        self.pre_filt = pre_filt
        self.units = units

    def _process(self, data):
        # read the corresponding inventory file in order to get response later
        inv = read_inventory('INPUT/%s_inventory.xml' % data[-1])
        data[0].remove_response(inv, output=self.units, pre_filt=self.pre_filt)

        return data


class Filter(IterativePE):

    def __init__(self, freqmin=0.01, freqmax=1., corners=4, zerophase=False):
        IterativePE.__init__(self)
        self.freqmin = freqmin
        self.freqmax = freqmax
        self.corners = corners
        self.zerophase = zerophase

    def _process(self, data):
        data[0].filter('bandpass', freqmin=self.freqmin, freqmax=self.freqmax, \
                       corners=self.corners, zerophase=self.zerophase)
        return data


class CalculateNorm(IterativePE):

    def onebit_norm(self, stream):
        stream2 = copy.deepcopy(stream)

        for trace in arange(len(stream2)):
            data = stream2[trace].data
            data = sign(data)
            stream2[trace].data = data

        return stream2

    def mean_norm(self, stream, N):
        stream2 = copy.deepcopy(stream)

        for trace in arange(len(stream2)):
            data = stream2[trace].data

            w = zeros(len(data))
            naux = zeros(len(data))

            for n in arange(len(data)):
                if n < N:
                    tw = absolute(data[0:n + N])
                elif logical_and(n >= N, n < (len(data) - N)):
                    tw = absolute(data[n - N:n + N])
                elif n >= (len(data) - N):
                    tw = absolute(data[n - N:len(data)])

                w[n] = true_divide(1, 2 * N + 1) * (sum(tw))

            naux = true_divide(data, w)
            stream2[trace].data = naux

        return stream2

    def gain_norm(self, stream, N):
        stream2 = copy.deepcopy(stream)

        for trace in arange(len(stream2)):
            data = stream2[trace].data

            dt = 1. / (stream2[trace].stats.sampling_rate)
            L = floor((N / dt + 1. / 2.))
            h = triang(2. * L + 1.)

            e = data ** 2.

            rms = (convolve(e, h, 'same') ** 0.5)
            epsilon = 1.e-12 * amax(rms)
            op = rms / (rms ** 2 + epsilon)
            dout = data * op

            stream2[trace].data = dout

        return stream2

    def env_norm(self, stream, N):
        stream2 = copy.deepcopy(stream)

        for trace in arange(len(stream2)):
            data = stream2[trace].data
            norm = util.smooth(absolute(data), N)
            # normdata = cpxtrace.normEnvelope(data, fs=stream2[trace].stats.sampling_rate, smoothie=N, fk=[1, 1, 1, 1, 1] )

            normdata = true_divide(data, norm)
            stream2[trace].data = normdata

        return stream2

    def __init__(self, norm, N):
        IterativePE.__init__(self)
        self.norm = norm
        self.N = N

    def _process(self, data):

        if self.norm is 'onebit':
            data[0] = self.onebit_norm(data[0])

        elif norm is 'mean':
            data[0] = self.mean_norm(data[0], self.N)

        elif norm is 'gain':
            data[0] = self.gain_norm(data[0], self.N)

        elif norm is 'env':
            data[0] = self.env_norm(data[0], self.N)

        return data


class Whiten(IterativePE):

    def spectralwhitening_smooth(self, stream, N):
        """
        Apply spectral whitening to data.
        Data is divided by its smoothed (Default: None) amplitude spectrum.
        """
        stream2 = copy.deepcopy(stream)

        for trace in arange(len(stream2)):
            data = stream2[trace].data

            n = len(data)
            nfft = nextpow2(n)

            spec = fft(data, nfft)
            spec_ampl = sqrt(abs(multiply(spec, conjugate(spec))))

            spec_ampl = smooth(spec_ampl, N)

            spec /= spec_ampl  # Do we need to do some smoothing here?
            ret = real(ifft(spec, nfft)[:n])

            stream2[trace].data = ret

        return stream2

    def __init__(self, smooth):
        IterativePE.__init__(self)
        self.smooth = smooth

    def _process(self, data):

        if self.smooth is not None:
            data[0] = self.spectralwhitening_smooth(data[0], smooth)

        return data


class CalculateFft(IterativePE):

    def __init__(self, type, shift):
        IterativePE.__init__(self)
        self.type = type
        self.shift = shift

    def _process(self, data):
        if self.type is not None:
            str_data = data[0][0].data
            N1 = len(str_data)
            str_data = str_data.astype(self.type)

            size = max(2 * self.shift + 1, (N1) + shift)
            nfft = next_pow_2(size)

            print("station %s and network %s - size in calc_fft %s " % \
                  (data[0][0].stats['station'], data[0][0].stats['network'], size))

            IN1 = fft(str_data, nfft)
            return [IN1, data[1], data[2]]
        else:
            return [data[0][0].data, data[1], data[2]]


ROOT_DIR = './OUTPUT/'
starttime = '2020-06-01T06:00:00.000'
endtime = '2020-06-01T07:00:00.000'

streamRead = StreamRead()
streamRead.name = 'streamRead'
streamToFile = StreamToFile()
streamToFile.name = 'StreamToFile'

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
