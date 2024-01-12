# Rapid Assessment

RA aims to model the strong ground motion after large earthquakes, in order to make rapid assessment of the earth- quakes impact, also in the context of emergency response. It has five main phases: (1) to select an earthquake gathering the real observed seismic wavefield, (2) to simulate synthetic seismic waveforms corresponding to the same earthquake using SPECFEM3D, a MPI-based parallel software; (3) to pre-process both synthetic and real data; (4) to calculate the ground motion parameters for synthetic and real data; (5) to compare them with each other by creating shake maps.

Since this use case has several statefull workflows, we are going to run it with **fixed mappings**. 

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


## Using Docker Container

Alternative you can follow [this instructions](https://github.com/StreamingFlow/d4py/tree/main#docker) to build a docker image and run dispel4py and this workflow within a docker container.

Once you are inside the docker container, you will have to clone this repository, and enter to the d4py_workflows directory. See bellow:
```
git clone https://github.com/StreamingFlow/d4py_workflows.git
cd d4py_workflows
```
Using our Docker  image, we can ensure that all the mappings described [bellow](https://github.com/StreamingFlow/d4py_workflows/tree/main/article_sentiment_analysis#run-the-workflow-with-different-mappings) work for this workflow.


## Running the Seismic Correlation application

To run the Seismic Correlation application, which includes the preprocessing (`realtime_prep.py`) and cross-correlation (`realtime_xcorr.py`) workflows, follow these steps: First, execute the `realtime_prep.py` workflow, which stores its results in the OUTPUT/DATA directory. Then, run either `realtime_xcorr.py` for cross-correlation; their results will be saved in the OUTPUT/XCORR directory. 

We provide two scripts (`run_tc_multi.sh` and `dispel4py_template.pbs`) to execute both workflows using multi mapping. Note that the `dispel4py_template.pbs` has been designed for running the workflows in a cluster with a queue system. 

We also provide an additional script (`run_tc_mpi.sh`) to execute both workflows using mpi mapping. 


```	
### run_tc_multi.sh 

rm -rf ./OUTPUT/DATA
rm -rf ./OUTPUT/XCORR
mkdir  ./OUTPUT/DATA
mkdir ./OUTPUT/XCORR

dispel4py multi realtime_prep.py -f realtime_xcorr_input.jsn -n 10
dispel4py multi realtime_xcorr.py -n 10
```	

- **Note**: It is important that you delete DATA and XCORR directories every time before starting to run your workflows. 
