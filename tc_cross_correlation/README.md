# Seismic Noise Cross-Correlation codes

Earthquakes and volcanic eruptions are sometimes preceded or accompanied by changes in the geophysical properties of the Earth, such as wave velocities or event rates. The development of reliable risk assessment methods for these hazards requires real-time analysis of seismic data and truly prospective forecasting and testing to reduce bias. However, potential techniques, including seismic interferometry and earthquake "repeater" analysis, require a large number of waveform cross-correlations, which is computationally intensive, and is particularly challenging in real-time.

With dispel4py we have developed the Seismic Ambient Noise Cross-Correlation workflow (also called the xcorr workflow) as part of the VERCE project project, which preprocesses and cross-correlates traces from several stations in real-time. The xcorr workflow consists of two main phases:

1. Phase 1 -- Preprocess: Each continuous time series from a given seismic station (called a trace), is subject to a series of treatments. The processing of each trace is independent from other traces, making this phase "embarrassingly" parallel (complexity O(n), where n is the number of stations. **Note:** We have this workflow on its own [here](https://github.com/StreamingFlow/d4py_workflows/tree/main/seismic_preparation). 

2. Phase 2 -- Cross-Correlation Pairs all of the stations and calculates the cross-correlation for each pair (complexity O(n2)).

Since Phase 2 includes a statefull workflow, we are going to run this workflow with fixed mappings. 

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

You need to edit the workflow (`realtime_prep.py` and `realtime_prep_dict.py`) file to change the following path to yours. See bellow:

```
import sys, os
#### Important -- change with your path to this workflow
sys.path.append('/home/user/d4py_workflows/seismic_preparation')
####
```

For running the preprocess (realtime_prep.py) and cross-correlation (realtime_xcorr.py or realtime_xcorr_storm.py) workflows, the next information is provided:

- The first workflow (realtime_prep.py) stores the results in a directory called OUTPUT/DATA. 
- The second one (realtime_xcorr.py or realtime_xcorr_storm.py) stores the results in OUTPUT/XCORR directory. 
- This is our script for executing both workflows with multi mapping: 

```	

    	export DISPEL4PY_XCORR_STARTTIME=2015-04-06T06:00:00.000
    	export DISPEL4PY_XCORR_ENDTIME=2015-04-06T07:00:00.000
    	rm -rf ./tc_cross_correlation/OUTPUT/DATA
    	rm -rf ./tc_cross_correlation/OUTPUT/XCORR
    	mkdir  ./tc_cross_correlation/OUTPUT/DATA
    	mkdir ./tc_cross_correlation/OUTPUT/XCORR

    	dispel4py multi tc_cross_correlation/realtime_prep.py -f tc_cross_correlation/realtime_xcorr_input.jsn -n 4
    	dispel4py multi tc_cross_correlation/realtime_xcorr.py -n 4

```	

- The last step is to open the file " tc_cross_correlation/realtime_xcorr_input.jsn” and change the path of the file Copy-Uniq-OpStationList-NetworkStation.txt

		xxx/tc_cross_correlation/Copy-Uniq-OpStationList-NetworkStation.txt  


- You could change the realtime_xcorr_input.jsn for using Uniq-OpStationList-NetworkStation.txt (it contains all the stations) instead of Copy-Uniq-OpStationList-NetworkStation.txt (it contains only a few of stations for testing the workflow). This data has been obtained from the [IRIS](http://ds.iris.edu/ds/nodes/dmc/earthscope/usarray/_US-TA-operational/) website. 

		{
    		"streamProducer" : [ { "input" : “/xxxxxxxxx/tc_cross_correlation/Uniq-OpStationList-NetworkStation.txt" } ]
		}


- It is important that you delete DATA and XCORR directories every time before starting to run your workflows. 
