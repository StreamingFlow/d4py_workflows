from dispel4py.provenance import *
from dispel4py.core import NAME, TYPE, GenericPE
import uuid
import traceback
from obspy.core import Trace,Stream
from dispel4py.base import SimpleFunctionPE
import traceback

try:
    from obspy.core.utcdatetime import UTCDateTime
except ImportError:
    pass

class SeismoPE(ProvenanceType):
    
 
    
    def __init__(self,*args,**kwargs):
        ProvenanceType.__init__(self,*args,**kwargs)
        self.addNamespacePrefix("seis","http://seis-prov.eu/ns/#")
        #self.outputconnections[OUTPUT_DATA][TYPE] = ['timestamp', 'location', 'streams']

        
    def extractItemMetadata(self,data,port):
         
        try:
            
            st=[]
             
            if type(data) == Trace:
                st.append(data)
                
            if type(data) == Stream:
                st=data
                
            elif type(data)==tuple or type(data)==list:
                for x in data:
                    if type(x)==Stream:
                        st=x
            
            else:
                st=data
            streammeta=list()
            for tr in st:
                
                metadic={}
                metadic.update({"prov:type":"waveform"});    
                metadic.update({"id":str(uuid.uuid1())});
                
                for attr, value in tr.stats.__dict__.items():
                    
                    if attr=="mseed":
                        mseed={}
                        for a,v in value.__dict__.items():
                            try:
                                if type(v)==UTCDateTime:
                                    mseed.update({a:str(v)});
                                else:
                                    mseed.update({a:float(v)});
                            except Exception:
                                mseed.update({a:str(v)});
                        metadic.update({"mseed":mseed});
                    else: 
                        try:
                            if type(value)==UTCDateTime:
                                metadic.update({attr:str(value)});
                            else:
                                metadic.update({attr:float(value)});
                        except Exception:
                            metadic.update({attr:str(value)});
                
                streammeta.append(metadic);
            
            return streammeta   
        except Exception:
            self.log("Applying default metadata extraction")
            #self.error=self.error+"Extract Metadata error: "+str(traceback.format_exc())
            return super(SeismoPE, self).extractItemMetadata(data,port)
        

class downloadSeismicData(ProvenanceType):
    
    def __init__(self,*args,**kwargs):
        ProvenanceType.__init__(self,*args,**kwargs)
        self.addNamespacePrefix("seis","http://seis-prov.eu/ns/#")
        #self.outputconnections[OUTPUT_DATA][TYPE] = ['timestamp', 'location', 'streams']

        
    def extractItemMetadata(self,data,port):
         
        try:
            
            #metadic
            streammeta=list()
            
            #metadic={"location":data};
            #streammeta.append(metadic)
            #self.log(str(os.path.realpath(data[1])))
            self.prov_location=[os.path.realpath(data[0]),os.path.realpath(data[1])]
            return streammeta 
        except Exception:
            self.log("Applying default metadata extraction")
            #self.error=self.error+"Extract Metadata error: "+str(traceback.format_exc())
            return super(downloadSeismicData, self).extractItemMetadata(data,port)
        
class PlotPE(ProvenanceType):
    
 
    
    def __init__(self,*args,**kwargs):
        ProvenanceType.__init__(self,*args,**kwargs)
        self.addNamespacePrefix("seis","http://seis-prov.eu/ns/#")
        #self.outputconnections[OUTPUT_DATA][TYPE] = ['timestamp', 'location', 'streams']

        
    def extractItemMetadata(self,data,port):
         
        try:
            
            #metadic
            streammeta=list()
            
            #metadic={"location":data};
            #streammeta.append(metadic)
            #self.log(str(os.path.realpath(data[1])))
            self.prov_location=os.path.realpath(data[1])
            return streammeta 
        except Exception:
            self.log("Applying default metadata extraction")
            #self.error=self.error+"Extract Metadata error: "+str(traceback.format_exc())
            return super(PlotPE, self).extractItemMetadata(data,port)
        
   
   
class SeismoSimpleFunctionPE(ProvenanceType):
    
 
    
    def __init__(self,*args,**kwargs):
        
        self.__class__ = type(str(self.__class__),(self.__class__,ProvenanceSimpleFunctionPE,SeismoPE,),{})
        ProvenanceSimpleFunctionPE.__init__(self,*args,**kwargs)
        #print(self.outputconnections)
        #self.outputconnections[OUTPUT_DATA][TYPE] = ['timestamp', 'location', 'streams']     
    
    
    
    
    
