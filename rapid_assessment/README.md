# Rapid Assessment

RA aims to model the strong ground motion after large earthquakes, in order to make rapid assessment of the earth- quakes impact, also in the context of emergency response.

It has five main phases: (1) to select an earthquake gathering the real observed seismic wavefield, (2) to simulate synthetic seismic waveforms corresponding to the same earthquake using SPECFEM3D, a MPI-based parallel software; (3) to pre-process both synthetic and real data; (4) to calculate the ground motion parameters for synthetic and real data; (5) to compare them with each other by creating shake maps.

Since this use case has several statefull workflows, we are going to run it with **fixed mappings**. 

## Requirements

Activate the conda python 3.10+ enviroment. If you had not created one, follow the [README instructions](https://github.com/StreamingFlow/d4py/tree/main).

```
conda activate d4py_env
```

Furthermore, for this workflow you need to install:

```
pip install obspy
pip install pyproj
```

## Known Issues

The last workflow `dispel4py_RAmapping.py` can give some problems due to `Basemap` module. This workflow is currently commented in our `run_total_combined_<mapping>.sh` scripts.

## Using Docker Container

Alternative you can follow [this instructions](https://github.com/StreamingFlow/d4py/tree/main#docker) to build a docker image and run dispel4py and this workflow within a docker container.

Once you are inside the docker container, you will have to clone this repository, and enter to the d4py_workflows directory. See bellow:
```
git clone https://github.com/StreamingFlow/d4py_workflows.git
cd d4py_workflows
```
Using our Docker  image, we can ensure that all the mappings described [bellow](https://github.com/StreamingFlow/d4py_workflows/tree/main/article_sentiment_analysis#run-the-workflow-with-different-mappings) work for this workflow.


## Running the Rapid Assessment application

To run this application we provide several scripts, with different mappings:
 - `run_total_combined_simple.sh` : it uses simple mapping for all workflows
 - `run_total_combined_multi.sh` : it uses multi mapping for all workflows, except the first and the last one 

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
