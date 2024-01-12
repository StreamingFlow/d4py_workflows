# Run:
# MISFIT_PREP_CONFIG="/Users/rosa/VERCE/dispy/dispel4py/test/seismo/misfit/processing.json" python -m dispel4py.new.processor simple dispel4py.test.seismo.misfit.create_misfit_prep -f /Users/rosa/VERCE/dispy/dispel4py/test/seismo/misfit/misfit_input.jsn
#
# Expects an environment variable MISFIT_PREP_CONFIG with the JSON file that specifies the preprocessing graph.

import json
import os
import sys
import networkx as nx
import glob,numpy

import preprocessing_functions as mf
from preprocessing_functions import get_event_time, get_synthetics, sync_cut, rotate_data
from dispel4py.core import GenericPE
from dispel4py.base import create_iterative_chain, ConsumerPE, IterativePE
from dispel4py.workflow_graph import WorkflowGraph
from dispel4py.workflow_graph import write_image
from obspy.core.event import read_events


def get_net_station(list_files):
    dlist=[]
    for d in list_files:
        net=d.split('/')[-1].split('.')[0]
        station=d.split('/')[-1].split('.')[1]
        dlist.append(net+'.'+station)
    dlist=numpy.unique(dlist)
    return dlist


class ReadDataPE(GenericPE):
    def __init__(self):
        GenericPE.__init__(self)
        self._add_input('input')
        self._add_output('output_real')
        self._add_output('output_synt')
        self.counter = 0

    def _process(self, inputs):

        if not inputs:
            STAGED_DATA=os.environ['STAGED_DATA']
            data_dir=os.path.join(STAGED_DATA,'data')
            synt_dir=os.path.join(STAGED_DATA,'synth')
            event_file=os.path.join(STAGED_DATA,'events_info.xml')
            e=read_events(event_file)
            event_id=e.events[0].resource_id #quakeml with single event
            event_id= "smi:webservices.ingv.it/fdsnws/event/1/query?eventId=1744261"
            stations_dir= os.path.join(STAGED_DATA,'stations')
            output_dir= os.path.join(STAGED_DATA,'output')

            data=glob.glob(os.path.join(data_dir,'*'))
            synt=glob.glob(os.path.join(synt_dir,'*'))
            dlist=get_net_station(data)
            slist=get_net_station(synt)

            networks=[]
            stations=[]
            for i,d in enumerate(dlist):
                if d in slist:
                    networks.append(d.split('.')[0])
                    stations.append(d.split('.')[1])

            misfit_json={
            "data": [
                {
                    "input": {
                        "data_dir": data_dir,
                        "synt_dir": synt_dir,
                         "events": event_file,
                        "event_id": event_id,
                        "stations_dir": stations_dir,
                        "output_dir" : output_dir,
                        "network": networks,
                        "station": stations
                        }
                    }
                ]
             }
            filename='misfit_input.jsn'
            with open(filename, "w") as write_file:
                json.dump(misfit_json, write_file)
        else:
             params = inputs['input']
             stations = params['station']
             networks = params['network']
             data_dir = params['data_dir']
             synt_dir = params['synt_dir']
             event_file = params['events']
             event_id = params['event_id']
             stations_dir = params['stations_dir']
             output_dir = params['output_dir']

        fe = 'v'
        if self.output_units == 'velocity':
            fe = 'v'
        elif self.output_units == 'displacement':
            fe = 'd'
        elif self.output_units == 'acceleration':
            fe = 'a'
        else:
            self.log('Did not recognise output units: %s' % output_units)
        quakeml = event_file
        for i in range(len(stations)):
            station = stations[i]
            network = networks[i]
            data_file = os.path.join(data_dir, network + "." + station + ".." + '?H?.mseed')
            #synt_file = os.path.join(synt_dir, network + "." + station + "." + '?X?.seed' + fe)
            ### in case we have the ascii synthetic traces, we have to comment the previous line, and uncomment the following one####### 
            #synt_file = os.path.join(synt_dir, network + "." + station + "." + '?X?.sem' + fe)
            synt_file = os.path.join(synt_dir, network + "." + station + "." + '?X?.sem' + fe +'*') #rf+fm read sac files
            sxml = os.path.join(stations_dir, network + "." + station + ".xml")
            real_stream, sta, event = mf.read_stream(data_file, sxml=sxml, event_file=quakeml,event_id=event_id)
            synt_stream = get_synthetics(synt_file, 
                                         get_event_time(quakeml, event_id), station, network)
            data, synt = sync_cut(real_stream, synt_stream)
            self.write(
                'output_real', [data, { 
                    'station' : sta, 
                    'event' : event, 
                    'stationxml' : sxml, 
                    'quakeml' : quakeml, 
                    'output_dir' : output_dir }
                ])

            self.write(
                'output_synt', [synt, {
                    'station' : sta, 
                    'event' : event, 
                    'stationxml' : sxml, 
                    'quakeml' : quakeml, 
                    'output_dir' : output_dir }
                ])


class RotationPE(IterativePE):
    def __init__(self, tag):
        IterativePE.__init__(self)
        self.tag = tag

    def _process(self, data):
        stream, metadata = data
        output_dir = metadata['output_dir']
        stations = metadata['station']
        event = metadata['event']
        stats = stream[0].stats
        filename = "%s.%s.%s.png" % (
            stats['network'], stats['station'], self.tag)
        #stream.plot(outfile=os.path.join(output_dir, filename))
        stream = rotate_data(stream, stations, event)
        filename = "rotate-%s.%s.%s.png" % (
            stats['network'], stats['station'], self.tag)
        #stream.plot(outfile=os.path.join(output_dir, filename))
        return (stream, metadata)


class StoreStream(ConsumerPE):
    def __init__(self, tag):
        ConsumerPE.__init__(self)
        self.tag = tag

    def _process(self, data):
        filelist = {}
        stream, metadata = data
        output_dir = metadata['output_dir']
        for i in range(len(stream)):
            stats = stream[i].stats
            filename = os.path.join(output_dir, "%s.%s.%s.%s" % (
                stats['network'], stats['station'], stats['channel'], self.tag))
            stream[i].write(filename, format='MSEED')
            filelist[stats['channel']] = filename


class MisfitPreprocessingFunctionPE(IterativePE):

    def __init__(self):
        IterativePE.__init__(self)

    def _process(self, data):
        stream, metadata = data
        result = self.compute_fn(stream, **self.params)
        return result, metadata


def create_processing_chain(proc):
    processes = []
    for p in proc:
        fn_name = p['type']
        params = p['parameters']
        fn = getattr(mf, fn_name)
        processes.append((fn, params))
    return create_iterative_chain(processes, FunctionPE_class=MisfitPreprocessingFunctionPE)

with open(os.environ['MISFIT_PREP_CONFIG']) as f:
    proc = json.load(f)

real_preprocess = create_processing_chain(proc['data_processing'])
synt_preprocess = create_processing_chain(proc['synthetics_processing'])
    
graph = WorkflowGraph()
read = ReadDataPE()
read.name = 'data'
read.output_units = proc['output_units']
rotate_real = RotationPE('data')
rotate_synt = RotationPE('synth')
store_real = StoreStream('data')
store_synt = StoreStream('synth')
graph.connect(read, 'output_real', real_preprocess, 'input')
graph.connect(read, 'output_synt', synt_preprocess, 'input')
if proc['rotate_to_ZRT']:
    graph.connect(real_preprocess, 'output', rotate_real, 'input')
    graph.connect(synt_preprocess, 'output', rotate_synt, 'input')
    graph.connect(rotate_real, 'output', store_real, 'input')
    graph.connect(rotate_synt, 'output', store_synt, 'input')
else:
    graph.connect(real_preprocess, 'output', store_real, 'input')
    graph.connect(synt_preprocess, 'output', store_synt, 'input')

write_image(graph, "misfit.png")

