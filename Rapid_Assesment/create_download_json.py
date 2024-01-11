from dispel4py.base import SimpleFunctionPE
from dispel4py.workflow_graph import WorkflowGraph
from dispel4py.base import create_iterative_chain, ConsumerPE, IterativePE, ProducerPE
from dispel4py.workflow_graph import write_image

import obspy
from obspy.core import read

import zipfile
import requests,json
import io
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO



import sys,os
import re
import numpy


def get_file_content(file_url=None,directory=None,
                     fname=None,archive=False):
    if archive:
        try:
            try:
                response = requests.get(file_url)
                zfiles=zipfile.ZipFile(io.BytesIO(response.content))
            except:
                zfiles=zipfile.ZipFile(file_url)
            listfile = zfiles.namelist()
        except:
             print('ERROR: Error reading zip file %s' % file_url)
             
        list_output = []
        if type(fname!=list):
            fname=list(fname)
        for name in fname:
            try:
                parfound=False
                for f in listfile:
                    if name in f:
                        ifile = zfiles.read(f)
                        ifile = ifile.decode('utf8')
                        if ('.json' in name) or ('.jsn' in name): 
                            ifile=json.loads(ifile)
                        list_output.append(ifile)
                        parfound=True
                        break
            except KeyError:
                parfound=False

        if not parfound:
            print('ERROR: Did not find %s in zip file' % fname)
            return None
    elif directory:
        if type(fname!=list):
            fname=list(fname)
        for name in fname:
            try:
                print(os.path.join(directory,name))
                f=open(os.path.join(directory,name),'r')
                ifile=f.read()
                ifile = ifile.decode('utf8')
                if ('.json' in name) or ('.jsn' in name):
                    ifile=json.loads(ifile)
                list_output.append(ifile)
            except:
                print('ERROR: Error reading %s file in %s' % (name,directory))
    elif ('.json' in fname) or ('.jsn' in fname):
        try:
            try:
                response = requests.get(file_url)
                ifile=response.json()
            except:
                f=open(file_url,'r')
                ifile=json.loads(f.read())
                f.close()
        except:
             print('ERROR: Error reading json file %s' % file_url)
        ifile = ifile.decode('utf8')
        if json_format: ifile=json.loads(ifile)
        list_output=[ifile]
    return list_output

def get_parameter(parameter=None,string=None,reg='\s+=([\s\d\.]+)'):
    if parameter is None:
        print('Parameter missed, ex: parameter="NPROC"')
        return None
    elif string is None:
        print('file string missing')
    txt=parameter+reg
    p=re.findall(txt, string,re.MULTILINE)
    if len(p) > 0:
        return p[0]
    else:
        return None

def create_event_time(cmtsolution):
    regex = r"PDE\s[\d\.\s]+"
    event_time=re.findall(regex, cmtsolution,re.MULTILINE)[0].split()[1:7]
    return '-'.join(x.zfill(2) for x in event_time[:3]) +\
            'T' +\
            ':'.join(x.zfill(2) for x in event_time[3:-1]) +':'+\
            '.'.join(x.zfill(2) for x in event_time[-1].split('.'))

def get_coordlimits(mesh):
    d = numpy.fromstring(mesh, sep=' ')
    data = d[1:].reshape(int(d[0]), 4)
    return data[:, 1].min(), data[:, 1].max(),\
        data[:, 2].min(), data[:, 2].max(),\
        data[:, 3].min(), data[:, 3].max()

def get_mesh_geolimits(lim,epsg):
    import pyproj
    wgs84=pyproj.Proj("+init=EPSG:4326") # LatLon with WGS84 datum used by GPS units and Google Earth
    meshcoordinate=pyproj.Proj("+init="+epsg)
    pyproj.transform(meshcoordinate, wgs84, lim[0], lim[2])
    longitude_min=max(pyproj.transform(meshcoordinate, wgs84, lim[0], lim[2])[0],
                  pyproj.transform(meshcoordinate, wgs84, lim[0], lim[3])[0])
    longitude_max=min(pyproj.transform(meshcoordinate, wgs84, lim[1], lim[2])[0],
                  pyproj.transform(meshcoordinate, wgs84, lim[1], lim[3])[0])
    latitude_min=max(pyproj.transform(meshcoordinate, wgs84, lim[0], lim[2])[1],
                  pyproj.transform(meshcoordinate, wgs84, lim[1], lim[2])[1])
    latitude_max=min(pyproj.transform(meshcoordinate, wgs84, lim[0], lim[3])[1],
                  pyproj.transform(meshcoordinate, wgs84, lim[1], lim[3])[1])
    return longitude_min,longitude_max,latitude_min,latitude_max



class WriteJSON(ProducerPE):
    def __init__(self):
        ProducerPE.__init__(self)

    def _process(self, data):
        print(data)
        data_url=data['specfem3d_data_url']
        #data_url='/Users/fmagnoni/dropbox/DOCUMENTS/Progetti/EPOS_IP/EINFRA21-DARE/WP6_workflows/cwl_workflow/WP6_EPOS/processing_elements/CWL_total_staged/TEST_ADD_CREATEJSON/data.zip'
        cmtsolution,parfile,infopar,meshfile=get_file_content(file_url=data_url,
                                                              fname=['CMTSOLUTION','Par_file','Info.json','nodes_coords_file'],
                                                              archive=True)
        #parfile=get_file_content(file_url=data_url,fname='Par_file',zip_format=True)
        #infopar=get_file_content(fname='Info.json')
        #meshfile=get_file_content(file_url=data_url,fname='nodes_coords_file',zip_format=True)

        NPROC=int(get_parameter('NPROC',parfile))
        print(NPROC)
        dt=float(get_parameter('DT',parfile))
        nstep=int(get_parameter('NSTEP',parfile))
        print(dt,nstep)
        try:
            RECORD_LENGTH_IN_MINUTES=float(get_parameter('RECORD_LENGTH_IN_MINUTES',parfile))
        except:
            RECORD_LENGTH_IN_MINUTES=dt*nstep/60.

        ETIME=create_event_time(cmtsolution)
        print(ETIME)
        lim=get_coordlimits(meshfile)
        print(RECORD_LENGTH_IN_MINUTES)
        print(lim)
        epsg=infopar['Coordinatesystem']['EPSG']
        longitude_min,longitude_max,latitude_min,latitude_max=get_mesh_geolimits(lim,epsg)
        xmin,xmax,ymin,ymax,zmin,zmax=lim


        d={
                "simulationRunId": None,
                "runId": None,
                "nproc": NPROC,
                "downloadPE": [
                    {
                    "input": {
                        "minimum_interstation_distance_in_m": 100,
                        "channel_priorities": ["BH[E,N,Z]","EH[E,N,Z]"],
                        "location_priorities": ["","00","10"],
                        "mseed_path": "./data",
                        "stationxml_path": "./stations",
                        "RECORD_LENGTH_IN_MINUTES": RECORD_LENGTH_IN_MINUTES,
                        "ORIGIN_TIME": ETIME,
                        "minlatitude": latitude_min,
                        "maxlatitude": latitude_max,
                        "minlongitude": longitude_min,
                        "maxlongitude": longitude_max
                        }
                    }
                ]
        }
        try:
            filename = data['output']
        except:
            filename='download_data.json'
        with open(filename, "w") as write_file:
            json.dump(d, write_file)

write_stream = WriteJSON()
write_stream.name="WJSON"

graph = WorkflowGraph()
graph.add(write_stream)
