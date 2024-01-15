# dispel4py examples

This repository has a collection of different dispel4py workflows - tested with Python 3.10+

## Requirements

You need to have previously installed our latest [dispel4py](https://github.com/StreamingFlow/d4py/tree/main) (Python 3.10+).

Follow the instruction detailed [here](https://github.com/StreamingFlow/d4py/tree/main#installation) to install dispel4py with a Conda enviroment. Alternative you can follow [this instructions](https://github.com/StreamingFlow/d4py/tree/main#docker) to build a docker image and run dispel4py within a docker container.

## Known Issues

1. Multiprocessing mappings (multi, dyn_multi, dyn_auto_multi) do not seem to work properly in MacOS (M1 chip).See bellow:


```
File "/Users/...../anaconda3/envs/py310/lib/python3.10/multiprocessing/spawn.py", line 126, in _main
    self = reduction.pickle.load(from_parent)
AttributeError: 'TestProducer' object has no attribute 'simple_logger'
```

In order to fix that, we recommend to use our [Docker file](https://github.com/StreamingFlow/d4py#docker) to create an image and later a container.

2. You might have to use the following command to install mpi in your MacOS laptop:
```
conda install -c conda-forge mpi4py mpich
```
   In Linux enviroments to install mpi you can use:
```
pip install mpi4py
```

3. For the mpi mapping, we need to indicate **twice** the number of processes, using twice the -n flag (one at te beginning and one at the end ):

```
mpiexec -n 10 dispel4py mpi dispel4py.examples.graph_testing.pipeline_test -i 20 -n 10
```

4. In some enviroments, you might need these flags for the mpi mapping:

```
--allow-run-as-root --oversubscribe
```

5. When running workflows with **mpi mapping**  you may encounter messages like `Read -1, expected 56295, errno = 1`. There's no need for concern; these messages are typical and do not indicate a problem. Rest assured, your workflow is still running as expected.


## Worflow Collection


If you run a workflow from other directories you just need to indicate it `<DIR1>.<DIR2>.<NAME_WORKFLOW>` without `py`.  If you are in the directory of the workflow, then you will need to use `<NAME_WOWRKFLOW>.py` . You will find detailed explanations in each workflow's README. 


## Mappings

The mappings of dispel4py refer to the connections between the processing elements (PEs) in a dataflow graph. Dispel4py is a Python library used for specifying and executing data-intensive workflows. In a dataflow graph, each PE represents a processing step, and the mappings define how data flows between the PEs during execution. These mappings ensure that data is correctly routed and processed through the dataflow, enabling efficient and parallel execution of tasks. We currently support the following ones:

- **Sequential**
  - "simple": it executes dataflow graphs sequentially on a single process, suitable for small-scale data processing tasks. 
- **Parallel**:  
  -  **Fixed fixed workload distribution - support stateful and stateless PEs:**
        - "mpi": it distributes dataflow graph computations across multiple nodes (distributed memory) using the **Message Passing Interface (MPI)**. 
        - "multi": it runs multiple instances of a dataflow graph concurrently using **multiprocessing Python library**, offering parallel processing on a single machine. 
        - "zmq_multi": it runs multiple instances of a dataflow graph concurrently using **ZMQ library**, offering parallel processing on a single machine.
        - "redis" : it runs multiple instances of a dataflow graph concurrently using **Redis library**. 
  - **Dynamic workfload distribution -  support only stateless PEs** 
    - "dyn_multi": it runs multiple instances of a dataflow graph concurrently using **multiprocessing Python library**. Worload assigned dynamically (but no autoscaling). 
    - "dyn_auto_multi": same as above, but allows autoscaling. We can indicate the number of threads to use.
    - "dyn_redis": it runs multiple instances of a dataflow graph concurrently using **Redis library**. Workload assigned dynamically (but no autocasling). 
    - "dyn_auto_redis": same as above, but allows autoscaling. We can indicate the number of threads to use.
  - **Hybrid workload distribution - supports stateful and stateless PEs**
    - "hybrid_redis": it runs multiple instances of a dataflow graph concurrently using **Redis library**. Hybrid approach for workloads: Stafeless PEs assigned dynamically, while Stateful PEs are assigned from the begining.



