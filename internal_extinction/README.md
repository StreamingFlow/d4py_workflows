# Internal Extinction of Galaxies 

[This workflow](./int_ext_graph.py) has been developed to calculate the extinction within the galaxies, representing the dust extinction within the galaxies used in measuring the optical luminosity. The first PE, "ReadRaDec", read the coordinator data for 1051 galaxies in an input file. Then, these data are used in the second PE "GetVOTable" as arguments to make an HTTP request to the Virtual Observatory website  and get the VOTable as the response. Finally, these VOTable go into PE "FilterColumns"


## Requirements


Activate the conda python 3.10+ enviroment. If you had not created one, follow the [README instructions](https://github.com/StreamingFlow/d4py/tree/main).

```
conda activate py310
```

To run the this workflow, first you need to install:
```shell
$ pip install requests
$ pip install astropy
$ pip install jwt
$ pip install ujson
$ pip install coloredlogs
``` 

## Known Issues


1. Multiprocessing (multi) does not seem to work properly in MacOS (M1 chip).See bellow:


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
   In Linux enviroments to install mpi you can use:
```
pip install mpi4py
```

3. For the mpi mapping, we need to indicate **twice** the number of processes, using twice the -n flag -- one at te beginning and one at the end --:

```
mpiexec -n 10 dispel4py mpi dispel4py.examples.graph_testing.pipeline_test -i 20 -n 10
```

4. In some enviroments, you might need these flags for the mpi mapping:

```
--allow-run-as-root --oversubscribe

```
5. It seems that astropy 6.0.0 and python 3.10 has a problem with `astropy.io.votable import parse_single_table` and the `Logger`. See bellow: 

```
  File "<frozen importlib._bootstrap_external>", line 883, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/home/user/d4py_workflows/internal_extinction/int_ext_graph.py", line 38, in <module>
    from astropy.io.votable import parse_single_table
  File "/home/user/venv/lib/python3.10/site-packages/astropy/__init__.py", line 174, in <module>
    log = _init_log()
  File "/home/user/venv/lib/python3.10/site-packages/astropy/logger.py", line 113, in _init_log
    log._set_defaults()
AttributeError: 'Logger' object has no attribute '_set_defaults'
```

Fix:  Comment Line 113 of `XXXX/python3.10/site-packages/astropy/logger.py` --> `#log._set_defaults`. This should solve the issue

## Running with a Script

Check [run_int.sh](./run_int.sh); [run_init_moni.sh](./run_init_moni.sh); and [run_int_skew.sh](./run_int_skew.sh)

## Run the workflow with different mappings

### Simple mapping

```shell
python -m dispel4py.new.processor simple int_ext_graph.py -d '{"read" : [ {"input" : "coordinates.txt"} ]}'
```

OR

```shell
dispel4py simple int_ext_graph.py -d '{"read" : [ {"input" : "coordinates.txt"} ]}'
```
The ‘coordinates.txt’ file is the workflow's input data with the coordinates of the galaxies.


### Fixed MPI mapping
```shell
mpiexec -n 10 dispel4py mpi int_ext_graph.py -d '{"read" : [ {"input" : "coordinates.txt"} ]}' -n 10
```

```shell
mpiexec -n 10 python -m dispel4py.new.processor dispel4py.new.mpi_process int_ext_graph.py -d '{"read" : [ {"input" : "coordinates.txt"} ]}' -n 10
```

### Multi mappings

#### Fixed Multi mapping

```shell
python -m dispel4py.new.processor multi int_ext_graph.py -d '{"read" : [ {"input" : "coordinates.txt"} ]}' -n 10
```

OR

```shell
dispel4py multi int_ext_graph.py -d '{"read" : [ {"input" : "coordinates.txt"} ]}' -n 10
```

 Parameter '-n' specify the number of processes.

#### Dynamic Multi mapping 
```shell
python -m dispel4py.new.processor dyn_multi int_ext_graph.py -d '{"read" : [ {"input" : "coordinates.txt"} ]}' -n 10
```
OR
```shell
dispel4py dyn_multi int_ext_graph.py -d '{"read" : [ {"input" : "coordinates.txt"} ]}' -n 10


#### Dynamic Multi Autoscaling mapping 
```shell
python -m dispel4py.new.processor dyn_auto_multi int_ext_graph.py -d '{"read" : [ {"input" : "coordinates.txt"} ]}' -n 10 -thr 10
```
OR
```shell
dispel4py dyn_auto_multi int_ext_graph.py -d '{"read" : [ {"input" : "coordinates.txt"} ]}' -n 10 -thr 10
```

### Redis mappings

#### Dynamic Redis mapping

> Go to another terminal for following command line

```shell
redis-server
```

> Go back to previous terminal

```shell
python -m dispel4py.new.processor dyn_redis int_ext_graph.py -d '{"read" : [ {"input" : "coordinates.txt"} ]}' -n 10
```
OR
```shell
dispel4py dyn_redis int_ext_graph.py -d '{"read" : [ {"input" : "coordinates.txt"} ]}' -n 10
```

#### Dynamic Redis Autoscaling mapping 
```shell
python -m dispel4py.new.processor dyn_auto_redis int_ext_graph.py -d '{"read" : [ {"input" : "coordinates.txt"} ]}' -n 10 -thr 200
```

OR
```shell
dispel4py dyn_auto_redis int_ext_graph.py -d '{"read" : [ {"input" : "coordinates.txt"} ]}' -n 20 -thr 200
``` 


#### Hybrid Redis mapping 
```shell
python -m dispel4py.new.processor hybrid_redis int_ext_graph.py -d '{"read" : [ {"input" : "coordinates.txt"} ]}' -n 10
```
OR
```shell
dispel4py hybrid_redis int_ext_graph.py -d '{"read" : [ {"input" : "coordinates.txt"} ]}' -n 10
```
