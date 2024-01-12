'''
Execution:
Real --> dispel4py simple dispel4py_RA.pgm_story.py -d '{"streamProducer": [ {"input": "IV.MA9..HHR.START.OTLOC.SAC.20.50.real"} ] }'
Synth --> dispel4py simple dispel4py_RA.pgm_story.py -d '{"streamProducer": [ {"input": "IV.MA9.HXR.semv.sac.20.50.synt"} ] }'


Comparison:
dispel4py simple dispel4py_RA.pgm_story.py -d '{"streamProducerReal": [ {"input": "IV.MA9..HHR.START.OTLOC.SAC.20.50.real"} ], "streamProducerSynth": [ {"input": "IV.MA9.HXR.semv.sac.20.50.synt"} ]   }'

Output:
WriteStream3: output_data is {'GroundMotion': {'stream': 'IV.MA9..HHR.START.OTLOC.SAC.20.50.real', 'ty': 'velocity', 'p_norm': 'max', 'pgd': '0.0006945877', 'pgv': '0.0002320527', 'pga': '0.00013708159', 'dmp_spec_acc': '0.00032428280150622804'}}

'''

from dispel4py.core import GenericPE
from dispel4py.base import BasePE, IterativePE, ConsumerPE, create_iterative_chain
from dispel4py.workflow_graph import WorkflowGraph
from dispel4py.workflow_graph import write_image


from obspy.core.stream import read
from obspy.signal.invsim import corn_freq_2_paz, simulate_seismometer
from obspy.signal import differentiate_and_integrate as di
from obspy import read_inventory
import obspy
import math
import numpy as np
import os
import re
import json, glob
from collections import defaultdict

def select_horizontal_channels(stream):
    channels = stream.select(channel='??[R,T]')
    print(channels)
    print(stream)
    if len(channels)==0:
        channels = stream.select(channel='??[N,E]')
        if len(channels)==0:
            return None
    return channels




def calculate_norm(stream,ty,delta):
    station = stream[0].stats.station
    print(station)
    print(len(stream))
    print(stream)
    channels=select_horizontal_channels(stream)

    data_v_square = 0.
    data_a_square = 0.
    data_d_square = 0.
    data_v_max = 0.
    data_a_max = 0.
    data_d_max = 0.


    for channel in channels:
        if ty == 'velocity':
            data_v = channel
            data_a = di.integrate_cumtrapz(channel, delta)
            data_d = np.gradient(channel, delta)
        elif ty == 'displacement':
            data_v = channel
            data_a = np.gradient(channel, delta)
            data_d = np.gradient(data_v, delta)
        elif ty == 'acceleration':
            data_v= channel
            data_a= di.integrate_cumtrapz(channel, delta)
            data_d= di.integrate_cumtrapz(data_v, delta)
        data_v_square=data_v_square+np.square(data_v)
        data_a_square=data_a_square+np.square(data_a)
        data_d_square=data_d_square+np.square(data_d)
        data_v_max=np.maximum(data_v_max,np.abs(data_v))
        data_a_max=np.maximum(data_a_max,np.abs(data_a))
        data_d_max=np.maximum(data_d_max,np.abs(data_d))

    data_v_mean=np.sqrt(data_v_square)
    data_a_mean=np.sqrt(data_a_square)
    data_d_mean=np.sqrt(data_d_square)

    return data_d_mean, data_v_mean, data_a_mean, data_d_max, data_v_max, data_a_max


def calculate_damped_spectral_acc(data,delta,freq,damp,ty):

    samp_rate = 1.0 / delta
    t = freq * 1.0
    d = damp
    omega = (2 * math.pi * t) ** 2

    paz_sa = corn_freq_2_paz(t, damp=d)
    paz_sa['sensitivity'] = omega
    paz_sa['zeros'] = []

    if ty == 'displacement':
        data = np.gradient(data, delta)
        data = np.gradient(data, delta)
    elif ty == 'velocity':
        data = np.gradient(data, delta)

    data = simulate_seismometer(data, samp_rate, paz_remove=None,
                            paz_simulate=paz_sa, taper=True,
                            simulate_sensitivity=True, taper_fraction=0.05)

    return data


class StreamProducer(IterativePE):

    def __init__(self, label):
        IterativePE.__init__(self)
        self.label = label
        self.ext = 'data' if label == 'real' else label
        self.pattern = re.compile('(\w*\.\w*)\.(\w*)\.{}'.format(self.ext))

    def _process(self, input):
        stations = defaultdict(lambda:[])
        # first group all files by station
        for filename in os.listdir(input):
             m = self.pattern.match(filename)
             if m:
                 stations[m.group(1)].append(m.group(2))

        # now read and create an obspy stream from each group
        for s, fs in stations.items():
            streaming=obspy.Stream()
            for f in fs:
                filename = os.path.join(input, '{}.{}.{}'.format(s, f, self.ext))
                streaming=streaming+read(filename)
            self.write('output', [streaming, self.label])

class PeakGroundMotion(IterativePE):
    def __init__(self,ty,freq=(0.3, 1.0, 3.0),damp=0.1):
        IterativePE.__init__(self)
        self.ty=ty
        self.frequencies = freq
        self.damp = damp

    def _process(self, s_data):
        print('data: ',s_data)
        stream, filename, (data_d, data_v, data_a), p_norm = s_data
        delta = stream[0].stats.delta
        pgd, pgv, pga = max(data_d), max(data_v), max(data_a)

        channels=select_horizontal_channels(stream)
        dmp_spec_acc = {}
        for freq in self.frequencies:
            data_dump = 0.
            for channel in channels:
                data = calculate_damped_spectral_acc(channel,delta,freq,self.damp,self.ty)
                if p_norm == 'mean':
                    data_dump=data_dump+np.square(data)
                elif p_norm == 'max':
                    data_dump=np.maximum(data_dump,np.abs(data))
            if p_norm == 'mean': data_dump=np.sqrt(data_dump)
            dmp_spec_acc['PSA_{}Hz'.format(freq)] = max(data_dump).item()

        results = {
            'PGD': pgd.item(),
            'PGV': pgv.item(),
            'PGA': pga.item(),
            'p_norm': p_norm
        }
        results.update(dmp_spec_acc)
        return [
            stream[0].stats.station,
            filename, stream, self.ty, results]




class NormPE(GenericPE):
    def __init__(self,ty):
        GenericPE.__init__(self)
        self._add_input("input")
        self._add_output("output_mean")
        self._add_output("output_max")
        self.ty=ty

    def _process(self, data):
        print('data: ',data)
        stream, filename = data['input']
        delta = stream[0].stats.delta
        data_d_mean, data_v_mean, data_a_mean, data_d_max, data_v_max, data_a_max = calculate_norm(stream,self.ty,delta)
        self.write('output_mean', [stream, filename, (data_d_mean, data_v_mean, data_a_mean), 'mean'])
        self.write('output_max', [stream, filename, (data_d_max, data_v_max, data_a_max), 'max'])



class Match(GenericPE):
    def __init__(self):
        GenericPE.__init__(self)
        self._add_input('input', grouping=[0])
        self._add_output('output')
        self.store = defaultdict(lambda: {})

    def _process(self, data):
        station, label,stream, ty, pgm = data['input']
        p_norm = pgm['p_norm']
        self.store[(station, p_norm)][label] = stream, ty, pgm
        if len(self.store[(station, p_norm)]) >= 2:
            self.write('output', [station, p_norm, self.store[(station, p_norm)]])
            del self.store[station, p_norm]


def comp(real_param, synt_param):
    result_diff = real_param - synt_param
    result_rel_diff = (real_param - synt_param)/real_param
    return result_diff, result_rel_diff


class WriteGeoJSON(ConsumerPE):
    def __init__(self):
        ConsumerPE.__init__(self)
        self._add_output('output')  #prov

    def _process(self, data):
        station, p_norm, matching_data = data

        difference = { }
        relative_difference = {}
        stream_r, ty_r, pgm_r = matching_data['real']
        stream_s, ty_s, pgm_s = matching_data['synth']
        try:
            station = stream_r[0].stats.station
            network = stream_r[0].stats.network
            inventory_path=misfit_path+"/stations/"+network+"."+station+".xml"
            inv = read_inventory(inventory_path , format="STATIONXML")
            net = inv[0]
            sta = net[0]
            coordinates = [sta.latitude, sta.longitude]
        except:
            coordinates = []
        for param in pgm_r:
            if param == 'p_norm':
                continue
            diff, rel_diff = comp(pgm_r[param], pgm_s[param])
            difference[param] = diff
            relative_difference[param] = rel_diff

        output_dir = os.environ['OUTPUT']
        output_data={
            "type": "Feature",
            "properties": {
                "station": station,
                "data": pgm_r,
                "synt": pgm_s,
                "difference": difference,
                "relative_difference": relative_difference,
                "geometry": {
                  "type": "Point",
                  "coordinates": coordinates
                }
            }
        }
        # self.log("output_data is %s" % json.dumps(output_data))
        filename = "/{}_{}.json".format(station, p_norm)
        with open(output_dir+filename, 'w') as outfile:
            json.dump(output_data, outfile)

misfit_path=os.environ['STAGED_DATA']

streamProducerReal=StreamProducer('real')
streamProducerReal.name="streamProducerReal"
streamProducerSynth=StreamProducer('synth')
streamProducerSynth.name='streamProducerSynth'
seismogram_type='velocity'
norm=NormPE(seismogram_type)
pgm_mean=PeakGroundMotion(seismogram_type)
pgm_max=PeakGroundMotion(seismogram_type)
match = Match()
write_stream = WriteGeoJSON()


graph = WorkflowGraph()
graph.connect(streamProducerReal, 'output', norm,'input')
graph.connect(streamProducerSynth, 'output', norm,'input')
graph.connect(norm, 'output_mean', pgm_mean,'input')
graph.connect(norm, 'output_max', pgm_max,'input')
graph.connect(pgm_max, 'output', match, 'input')
graph.connect(pgm_mean, 'output', match, 'input')
graph.connect(match,'output',write_stream,'input')
#write_image(graph, "PGM.png")

