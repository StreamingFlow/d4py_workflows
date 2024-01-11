import json
import random
import os
import matplotlib.pyplot as plt 
try:
    from mpl_toolkits.basemap import Basemap
except:
    import os
    os.environ['PROJ_LIB']="/Users/fmagnoni/anaconda3/share/proj"
    from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1 import make_axes_locatable
from dispel4py.core import GenericPE
from dispel4py.base import ConsumerPE
from dispel4py.workflow_graph import WorkflowGraph
from dispel4py.workflow_graph import write_image


def plot_single(f,ax,variable='PGV',kind='data',source=None,bounds=None,xtitle=None,ytitle=None,vmin=None,vmax=None):
    lon= [x['properties']['geometry']['coordinates'][0]for x in source["features"]]
    lat= [x['properties']['geometry']['coordinates'][1]for x in source["features"]]
    values=[x['properties'][kind][variable] for x in source["features"]]
    a=plt.axes(ax)
    if not bounds:
        dlat=(max(lat)-min(lat))*.3
        dlon=(max(lon)-min(lon))*.3
        minlat=min(lat)-dlat
        maxlat=max(lat)+dlat
        minlon=min(lon)-dlon
        maxlon=max(lon)+dlon
    else:
        minlat=bound[2]
        maxlat=bound[3]
        minlon=bound[0]
        maxlon=bound[1]
    if vmin is None:
        vmin=min(values)
    if vmax is None:
        vmax=max(values)
    m = Basemap(projection='merc', resolution='l',
            llcrnrlat=minlat, urcrnrlat=maxlat,
            llcrnrlon=minlon, urcrnrlon=maxlon)
    x,y=m(lon,lat)
    if kind == 'difference' or kind == 'relative_difference':
        cmap='seismic'
    else:
        cmap='hot'
    scat=m.scatter(x,y, alpha=.5, edgecolors='k',cmap=cmap,c=values,vmin=vmin,vmax=vmax)
    #m.shadedrelief()
    m.drawcoastlines()
    if xtitle:
        plt.title(xtitle)
    if ytitle:
        plt.ylabel(ytitle)
    divider = make_axes_locatable(a)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    f.colorbar(scat, cax=cax, orientation='vertical')
    
def get_values_extremes(source=None,kind='data',variable='PGV'):
    values=[x['properties'][kind][variable] for x in source["features"]]
    return min(values),max(values)
    



class StreamProducer(GenericPE):
    """
    PE reading the JSON input file and generating one output per component of
    the input files. Will write to different output channels depending on the
    chosen misfit.
    """
    def __init__(self):
        GenericPE.__init__(self)
        self._add_output("output_max")
        self._add_output("output_mean")

    def process(self, inputs):
         data_max={}
         data_mean={}
         data_max["features"]=[]
         data_mean["features"]=[]
         for filename in os.listdir(gm_path):
             if filename.endswith("_max.json"):
                 with open(gm_path+"/"+filename, "r") as read_file:
                     data_station = json.load(read_file)
                     data_max["features"].append(data_station)
             else:
                 with open(gm_path+"/"+filename, "r") as read_file:
                     try:
                         data_station = json.load(read_file)
                         data_mean["features"].append(data_station)
                     except:
                         print('error loading ',gm_path+"/"+filename)
         self.write('output_mean', data_mean)
         self.write('output_max', data_max)


class PlotMap(ConsumerPE):
    def __init__(self, label):
        ConsumerPE.__init__(self)
        self.label = label

    def _process(self, data):
        data_source = data
        fig, axes = plt.subplots(6, 3, sharex='col', sharey='row')
        fig.set_size_inches([10,20])
        variables=['data', 'synt', 'difference']
        vmin_data,vmax_data=get_values_extremes(data_source,kind='data',variable='PGV')
        vmin_synt,vmax_synt=get_values_extremes(data_source,kind='synt',variable='PGV')
        PGV_min=min(vmin_data,vmin_synt)
        PGV_max=max(vmax_data,vmax_synt)
        vmin_data,vmax_data=get_values_extremes(data_source,kind='data',variable='PGA')
        vmin_synt,vmax_synt=get_values_extremes(data_source,kind='synt',variable='PGA')
        PGA_min=min(vmin_data,vmin_synt)
        PGA_max=max(vmax_data,vmax_synt)
        vmin_data,vmax_data=get_values_extremes(data_source,kind='data',variable='PGD')
        vmin_synt,vmax_synt=get_values_extremes(data_source,kind='synt',variable='PGD')
        PGD_min=min(vmin_data,vmin_synt)
        PGD_max=max(vmax_data,vmax_synt)
        vmin_data,vmax_data=get_values_extremes(data_source,kind='data',variable='PSA_0.3Hz')
        vmin_synt,vmax_synt=get_values_extremes(data_source,kind='synt',variable='PSA_0.3Hz')
        PSA_03Hz_min=min(vmin_data,vmin_synt)
        PSA_03Hz_max=max(vmax_data,vmax_synt)
        vmin_data,vmax_data=get_values_extremes(data_source,kind='data',variable='PSA_1.0Hz')
        vmin_synt,vmax_synt=get_values_extremes(data_source,kind='synt',variable='PSA_1.0Hz')
        PSA_1Hz_min=min(vmin_data,vmin_synt)
        PSA_1Hz_max=max(vmax_data,vmax_synt)
        vmin_data,vmax_data=get_values_extremes(data_source,kind='data',variable='PSA_3.0Hz')
        vmin_synt,vmax_synt=get_values_extremes(data_source,kind='synt',variable='PSA_3.0Hz')
        PSA_3Hz_min=min(vmin_data,vmin_synt)
        PSA_3Hz_max=max(vmax_data,vmax_synt)
        
        
        
        
        i =0
        for k in variables:
            ax=axes[:,i]
            print("k is %s" %k)
            plot_single(fig, ax[0] ,'PGA',k,source=data_source,xtitle=k,ytitle='PGA',vmin=PGA_min,vmax=PGA_max)
            plot_single(fig, ax[1] ,'PGV',k,source=data_source,xtitle=None,  ytitle='PGV',vmin=PGV_min,vmax=PGV_max)
            plot_single(fig, ax[2] ,'PGD',k,source=data_source,xtitle=None,  ytitle='PGD',vmin=PGD_min,vmax=PGD_max)
            plot_single(fig, ax[3] ,'PSA_0.3Hz',k,source=data_source,xtitle=None,  ytitle='PSA 0.3 Hz',vmin=PSA_03Hz_min,vmax=PSA_03Hz_max)
            plot_single(fig, ax[4] ,'PSA_1.0Hz'  ,k,source=data_source,xtitle=None,  ytitle='PSA 1 Hz',vmin=PSA_1Hz_min,vmax=PSA_1Hz_max)
            plot_single(fig, ax[5] ,'PSA_3.0Hz'  ,k,source=data_source,xtitle=None,  ytitle='PSA 3 Hz',vmin=PSA_3Hz_min,vmax=PSA_3Hz_max)
            i+=1
        fig.savefig(gm_path+"/RAMap_"+self.label+".png")


gm_path=os.environ['OUTPUT']
producer_PE=StreamProducer()
producer_PE.name="streamProducer"
plotMax=PlotMap("max")
plotMean=PlotMap("mean")

graph = WorkflowGraph()
graph.connect(producer_PE, "output_max", plotMax, "input")
graph.connect(producer_PE, "output_mean", plotMean, "input")
write_image(graph, "MapPlot.png")
