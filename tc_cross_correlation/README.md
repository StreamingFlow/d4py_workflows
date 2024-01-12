# Seismic Noise Cross-Correlation codes

Earthquakes and volcanic eruptions are sometimes preceded or accompanied by changes in the geophysical properties of the Earth, such as wave velocities or event rates. The development of reliable risk assessment methods for these hazards requires real-time analysis of seismic data and truly prospective forecasting and testing to reduce bias. However, potential techniques, including seismic interferometry and earthquake "repeater" analysis, require a large number of waveform cross-correlations, which is computationally intensive, and is particularly challenging in real-time.

With dispel4py we have developed the Seismic Ambient Noise Cross-Correlation workflow (also called the xcorr workflow) as part of the VERCE project project, which preprocesses and cross-correlates traces from several stations in real-time. The xcorr workflow consists of two main phases:

1. Phase 1 -- Preprocess: Each continuous time series from a given seismic station (called a trace), is subject to a series of treatments. The processing of each trace is independent from other traces, making this phase "embarrassingly" parallel (complexity O(n), where n is the number of stations. **Note:** We have this workflow on its own [here](https://github.com/StreamingFlow/d4py_workflows/tree/main/seismic_preparation). 

2. Phase 2 -- Cross-Correlation Pairs all of the stations and calculates the cross-correlation for each pair (complexity O(n2)).

Since Phase 2 includes a statefull workflow, we are going to run this workflow with fixed mappings. 

**Note:** By the default, this workflow runs with a short list of stations (`Copy-Uniq-OpStationList-NetworkStation.txt`). If you want to run the workflow with a bigger list, change it the `realtime_xcorr_input.jsn` to use `Uniq-OpStationList-NetworkStation.txt` instead.

## Requirements

Activate the conda python 3.10+ enviroment. If you had not created one, follow the [README instructions](https://github.com/StreamingFlow/d4py/tree/main).

```
conda activate d4py_env
```

Furthermore, for this workflow you need to install:

```
pip install obspy
```

## Important

1. You need to edit the workflow (`realtime_prep.py` and `realtime_xcorr.py`) file to change the following path to yours. See bellow:

```
import sys, os
#### Important -- change with your path to this workflow
sys.path.append('/home/user/d4py_workflows/seismic_preparation')
####
```

2. You will need to open `realtime_xcorr_input.jsn` and change the path of the file Copy-Uniq-OpStationList-NetworkStation.txt

		xxx/tc_cross_correlation/Copy-Uniq-OpStationList-NetworkStation.txt  


3. You could also change the `realtime_xcorr_input.jsn` for using **Uniq-OpStationList-NetworkStation.txt** (it contains all the stations) instead of Copy-Uniq-OpStationList-NetworkStation.txt (it contains only a few of stations for testing the workflow). This data has been obtained from the [IRIS](http://ds.iris.edu/ds/nodes/dmc/earthscope/usarray/_US-TA-operational/) website. 

		{
    		"streamProducer" : [ { "input" : “/xxxxxxxxx/tc_cross_correlation/Uniq-OpStationList-NetworkStation.txt" } ]
		}
## Running the Seismic Correlation application

To run the Seismic Correlation application, which includes the preprocessing (`realtime_prep.py`) and cross-correlation (`realtime_xcorr.py`) workflows, follow these steps: First, execute the `realtime_prep.py` workflow, which stores its results in the OUTPUT/DATA directory. Then, run either `realtime_xcorr.py` for cross-correlation; their results will be saved in the OUTPUT/XCORR directory. 

We provide two scripts (run_tc.sh and dispel4py_template.pbs) to execute both workflows using multi-mapping. 


```	
### run_tc.sh 

rm -rf ./OUTPUT/DATA
rm -rf ./OUTPUT/XCORR
mkdir  ./OUTPUT/DATA
mkdir ./OUTPUT/XCORR

dispel4py multi realtime_prep.py -f realtime_xcorr_input.jsn -n 10
dispel4py multi realtime_xcorr.py -n 10
```	

- **Note**: It is important that you delete DATA and XCORR directories every time before starting to run your workflows. 
