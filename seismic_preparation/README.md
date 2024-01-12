# Seismic Preparation - Phase 1 of the Seismic Cross Correlation 

This workflow just represent the phase 1 of the Seismic Cross-Correlation application. Each continuous time series from a given seismic station (called a trace), is subject to a series of treatments. The processing of each trace is independent from other traces, making this phase "embarrassingly" parallel (complexity O(n), where n is the number of stations. 

The reason for using this workflow is that is stateless, which enables us to experiment with different dispel4py mappings. However, the phase 2 of the Seismic Cross Correlation is a statefull workflow, so only some dispel4py mappings (simple, fixed and hybrid mappings) are suitable for this workflow. 


The full application is [tc_cross_correlation ](https://github.com/StreamingFlow/d4py_workflows/tree/main/tc_cross_correlation) directory.


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

## Preparation of data

```shell
cd seismic_preparation
mkdir INPUT
python download.py
```

## Using Docker Container

Alternative you can follow [this instructions](https://github.com/StreamingFlow/d4py/tree/main#docker) to build a docker image and run dispel4py and this workflow within a docker container.

Once you are inside the docker container, you will have to clone this repository, and enter to the d4py_workflows directory. See bellow:
```
git clone https://github.com/StreamingFlow/d4py_workflows.git
cd d4py_workflows
```
Using our Docker  image, we can ensure that all the mappings described [bellow](https://github.com/StreamingFlow/d4py_workflows/tree/main/article_sentiment_analysis#run-the-workflow-with-different-mappings) work for this workflow.

## Run the workflow with different mappings

### Simple mapping

```shell
python -m dispel4py.new.processor simple realtime_prep_dict -f xcorr_input.jsn 
```
OR

```shell
dispel4py simple realtime_prep_dict -f xcorr_input.jsn 
```

### (Fixed) MPI mapping

```shell
mpiexec -n 10 dispel4py mpi realtime_prep_dict -f xcorr_input.jsn -n 10
```
OR

```shell
mpiexec -n 10 --allow-run-as-root --oversubscribe dispel4py mpi realtime_prep_dict -f xcorr_input.jsn -n 10
```

OR

```shell
mpiexec -n 10 python -m dispel4py.new.processor dispel4py.new.mpi_process realtime_prep_dict -f xcorr_input.jsn -n 10
```

### (Fixed) Multi

```shell
python -m dispel4py.new.processor multi realtime_prep_dict -f xcorr_input.jsn -n 10
```
OR

```shell
dispel4py multi realtime_prep_dict -f xcorr_input.jsn -n 10
```

### Dynamic Multi
```shell
python -m dispel4py.new.processor dyn_multi realtime_prep_dict -f xcorr_input.jsn -n 10
```
OR

```shell
dispel4py dyn_multi realtime_prep_dict -f xcorr_input.jsn -n 10 
```


### Dynamic autoscaling multi
```shell
python -m dispel4py.new.processor dyn_auto_multi realtime_prep_dict -f xcorr_input.jsn -n 10
```
OR

```shell
dispel4py dyn_auto_multi realtime_prep_dict -f xcorr_input.jsn -n 10 
```

### Hybrid Redis

You need REDIS server running in a tab:

```shell
redis-server
```


```shell
python -m dispel4py.new.processor hybrid_redis realtime_prep_dict -f xcorr_input.jsn -n 10
```

OR
```
dispel4py hybrid_redis realtime_prep_dict -f xcorr_input.jsn -n 10
```
## Running with a Script

Check [run_corr.sh](./run_corr.sh) and [run_corr_moni.sh](./run_corr_moni.sh).

