import glob
import inspect
import json
import os

import numpy as np
import obspy
from obspy.core.event import read_events, ResourceIdentifier
from obspy.signal.invsim import cosine_sac_taper
from obspy.signal.util import _npts2nfft
import scipy.signal

from dispel4py.core import GenericPE
from dispel4py.base import IterativePE, ConsumerPE, create_iterative_chain
from dispel4py.workflow_graph import WorkflowGraph
from obspy.core.stream import Stream
from obspy.core.trace import Trace

def read_specfem_ascii_waveform_file(filename,station,network, channel):
    total=np.loadtxt(filename)
    time_array=total[:,0]
    data=total[:,1]
    dt = np.diff(time_array).mean()
    tr = obspy.Trace(data=data)
    tr.stats.delta = dt
    tr.stats.starttime += time_array[0]
    tr.stats.network = network
    tr.stats.station = station
    tr.stats.channel = channel
    return obspy.Stream(traces=[tr])


def complete_trace(filename,st):
     name=filename.split('/')[-1]
     st[0].stats.network=name.split(".")[0]
     st[0].stats.station=name.split(".")[1]
     st[0].stats.channel=name.split(".")[2]
     return st



def get_event_time(event, event_id):
    """
    Extract origin time from event XML file.
    """
    if not isinstance(event, obspy.core.event.Event):
        event = read_event(event, event_id)
    origin = event.preferred_origin() or event.origins[0]
    return origin.time

def get_synthetics(synts, event_time, station, network):
    print("Network is %s" %network)
    if isinstance(synts, list):
        file_names = synts
    else:
        file_names = glob.glob(synts)
    st = obspy.Stream()
    for name in file_names:
       try:
           #st += obspy.read(name)
            st_1 = obspy.read(name)
            if st_1[0].stats.channel=="":
                st += complete_trace(name,st_1)
            else:
                st+= st_1
       except:
          channel_1=name.split(network)[1]
          channel=channel_1.split(".")[2]
          print("channel is %s" % channel)
          st += read_specfem_ascii_waveform_file(name, station, network, channel) 
    # The start time of the synthetics might not be absolute. Grant a tolerance
    # of 10 seconds.
    if -10.0 <= st[0].stats.starttime.timestamp <= 0.0:
        for tr in st:
            offset = tr.stats.starttime - obspy.UTCDateTime(0)
            tr.stats.starttime = event_time + offset
    print("Stats of the first trace!!\n:")
    print(st[0].stats)
    return st


def read_event(event_file, event_id):
    events = read_events(event_file)
    event = None
    resource_id = ResourceIdentifier(event_id)
    for evt in events:
        if evt.resource_id == resource_id:
            event = evt
    if event is None:
        event = events[0]
    return event


def read_stream(data_files, sxml, event_file, event_id):
    print("!! DataFile is %s" % data_files)
    stream = obspy.read(data_files)
    stations = obspy.read_inventory(sxml, format="STATIONXML")
    stream.attach_response(stations)
    event = read_event(event_file, event_id)
    print(stream[0].stats.response)
    return stream, stations, event


def get_event_coordinates(event):
    if not isinstance(event, obspy.core.event.Event):
        event = obspy.read_events(event)[0]
    origin = event.preferred_origin() or event.origins[0]
    return origin.longitude, origin.latitude


def zerophase_chebychev_lowpass_filter(trace, freqmax):
    """
    Custom Chebychev type two zerophase lowpass filter useful for
    decimation filtering.

    This filter is stable up to a reduction in frequency with a factor of
    10. If more reduction is desired, simply decimate in steps.

    Partly based on a filter in ObsPy.

    :param trace: The trace to be filtered.
    :param freqmax: The desired lowpass frequency.

    Will be replaced once ObsPy has a proper decimation filter.
    """
    # rp - maximum ripple of passband, rs - attenuation of stopband
    rp, rs, order = 1, 96, 1e99
    ws = freqmax / (trace.stats.sampling_rate * 0.5)  # stop band frequency
    wp = ws  # pass band frequency

    while True:
        if order <= 12:
            break
        wp *= 0.99
        order, wn = scipy.signal.cheb2ord(wp, ws, rp, rs, analog=0)

    b, a = scipy.signal.cheby2(order, rs, wn, btype="low", analog=0,
                               output="ba")

    # Apply twice to get rid of the phase distortion.
    trace.data = scipy.signal.filtfilt(b, a, trace.data)


def aliasing_filter(tr, target_sampling_rate):
    while True:
        decimation_factor = int(1.0 / target_sampling_rate / tr.stats.delta)
        # Decimate in steps for large sample rate reductions.
        if decimation_factor > 8:
            decimation_factor = 8
        if decimation_factor > 1:
            new_nyquist = tr.stats.sampling_rate / 2.0 / float(
                decimation_factor)
            zerophase_chebychev_lowpass_filter(tr, new_nyquist)
            tr.decimate(factor=decimation_factor, no_filter=True)
        else:
            break


def sync_cut(data, synth, lenwin=None):
    """
    return cutted copy of data and synth

    :param data: Multicomponent stream of data.
    :param synth: Multicomponent stream of synthetics.
    :param sampling_rate: Desired sampling rate.
    """
    sampling_rate = min([tr.stats.sampling_rate for tr in (data + synth)])
    for tr in data:
        aliasing_filter(tr, sampling_rate)
    for tr in synth:
        aliasing_filter(tr, sampling_rate)

    starttime = max([tr.stats.starttime for tr in (data + synth)])
    endtime = min([tr.stats.endtime for tr in (data + synth)])

    if lenwin:
        if (endtime - starttime) < lenwin:
            raise ValueError("lenwin is larger than the data allows.")
        endtime = starttime + float(lenwin)

    npts = int((endtime - starttime) * sampling_rate)

    data.interpolate(sampling_rate=sampling_rate, method="cubic",
                     starttime=starttime, npts=npts)
    synth.interpolate(sampling_rate=sampling_rate, method="cubic",
                      starttime=starttime, npts=npts)

    return data, synth


def rotate_data(stream, stations, event):
    """
    Rotates the data to ZRT.
    """
    print("stream is %s"%stream)
    n = stream.select(component='N')
    e = stream.select(component='E')

    stations = stations.select(network=stream[0].stats.network,
                               station=stream[0].stats.station)
    if len(e) and len(n):
        lon_event, lat_event = get_event_coordinates(event)
        print( lon_event, lat_event)
        lon_station, lat_station = stations[0][0].longitude, stations[0][0].latitude
        dist, az, baz = obspy.geodetics.base.gps2dist_azimuth(
            float(lat_event), float(lon_event), float(lat_station),
            float(lon_station))
        stream.rotate('NE->RT', baz)
    else:
        raise ValueError("Could not rotate data")
    return stream


def remove_response(stream, pre_filt=(0.01, 0.02, 8.0, 10.0),
                    response_output="DISP"):
    """
    Removes the instrument response.

    Assumes stream.attach_response has been called before.
    """
    stream.remove_response(pre_filt=pre_filt,
                           output=response_output,
                           zero_mean=False, taper=False)
    return stream


def pre_filter(stream, pre_filt=(0.02, 0.05, 8.0, 10.0)):
    """
    Applies the same filter as remove_response without actually removing the
    response.
    """
    for tr in stream:
        data = tr.data.astype(np.float64)
        nfft = _npts2nfft(len(data))
        fy = 1.0 / (tr.stats.delta * 2.0)
        freqs = np.linspace(0, fy, nfft // 2 + 1)

        # Transform data to Frequency domain
        data = np.fft.rfft(data, n=nfft)
        data *= cosine_sac_taper(freqs, flimit=pre_filt)
        data[-1] = abs(data[-1]) + 0.0j
        # transform data back into the time domain
        data = np.fft.irfft(data)[0:len(data)]
        # assign processed data and store processing information
        tr.data = data
    return stream


def detrend(stream, method='linear'):
    stream.detrend(method)
    return stream


def taper(stream, max_percentage=0.05, taper_type="hann"):
    stream.taper(max_percentage=max_percentage, type=taper_type)
    return stream


def filter_lowpass(stream, frequency, corners, zerophase):
    stream.filter("lowpass", freq=frequency, corners=corners,
                  zerophase=zerophase)
    return stream


def filter_highpass(stream, frequency, corners, zerophase):
    stream.filter("highpass", freq=frequency, corners=corners,
                  zerophase=zerophase)
    return stream


def filter_bandpass(stream, min_frequency, max_frequency, corners, zerophase):
    stream.filter("bandpass", freqmin=min_frequency,
                  freqmax=max_frequency, corners=corners,
                  zerophase=zerophase)
    return stream

