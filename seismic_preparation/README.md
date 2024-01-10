# Seismic Preparation - Phase 1 of the Seismic Cross Correlation 

This workflow just represent the phase 1 of the Seismic Cross-Correlation. Each continuous time series from a given seismic station (called a trace), is subject to a series of treatments. The processing of each trace is independent from other traces, making this phase "embarrassingly" parallel (complexity O(n), where n is the number of stations. 

The full workflow is XXX. 


## Requirements


Activate the conda python 3.10+ enviroment. If you had not created one, follow the [README instructions](https://github.com/StreamingFlow/d4py/tree/main).

```
conda activate d4py_env
```

## Preparation of data

```shell
cd seismic_preparation
mkdir INPUT
python download.py
```

## Known Issues

1. Using the Multiprocessing mapping in a MacOS you might have a problem the `simple_logger`. See bellow:

```
File "/Users/...../anaconda3/envs/py310/lib/python3.10/multiprocessing/spawn.py", line 126, in _main
    self = reduction.pickle.load(from_parent)
AttributeError: 'TestProducer' object has no attribute 'simple_logger'
```

In order to fix that, we recommend to use our [Docker image](https://github.com/StreamingFlow/d4py/tree/main) to create a container.

2. You might have to use the following command to install mpi in your MacOS laptop:
```
conda install -c conda-forge mpi4py mpich
```
3. In some enviroments, you might need these flags for the mpi mapping: --allow-run-as-root --oversubscribe

## Run the workflow with different mappings

### Dynamic Multi
```shell
python -m dispel4py.new.processor dyn_multi realtime_prep_dict.py -f xcorr_input.jsn -n 10
```
OR

```shell
dispel4py dyn_multi realtime_prep_dict.py -f xcorr_input.jsn -n 10 
```


### Dynamic autoscaling multi
```shell
python -m dispel4py.new.processor dyn_auto_multi realtime_prep_dict.py -f xcorr_input.jsn -n 10
```
OR

```shell
dispel4py dyn_auto_multi realtime_prep_dict.py -f xcorr_input.jsn -n 10 
```

### Hybrid Redis

You need REDIS server running in a tab:

```shell
redis-server
```


```shell
python -m dispel4py.new.processor hybrid_redis realtime_prep_dict.py -f xcorr_input.jsn -n 10
```

OR
```
dispel4py hybrid_redis realtime_prep_dict.py -f xcorr_input.jsn -n 10
```
## Running with a Script

Check [run_corr.sh](./run_corr.sh) and [run_corr_moni.sh](./run_corr_moni.sh).

