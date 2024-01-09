# dispel4py examples

This repository has a collection of different dispel4py workflows - tested with Python 3.10+

## Requirements

You need to have previously installed our latest [dispel4py](https://github.com/StreamingFlow/d4py/tree/main) (Python 3.10+).

Follow the instruction detailed [here](https://github.com/StreamingFlow/d4py/tree/main) to install dispel4py - either with a Conda enviroment or with Docker container .

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

## Worflow Collection

### Astrophysics: Internal Extinction of Galaxies*


[This workflow](./internal_extinction) has been developed to calculate the extinction within the galaxies, representing the dust extinction within the galaxies used in measuring the optical luminosity. The first PE, "ReadRaDec", read the coordinator data for 1051 galaxies in an input file. Then, these data are used in the second PE "GetVOTable" as arguments to make an HTTP request to the Virtual Observatory website  and get the VOTable as the response. Finally, these VOTable go into PE "FilterColumns" to filter specified columns used in the internal extinction computation. And this computation happened in the last PE, "InternalExtinction".

More info about how to run this workflow is available [here](./internal_extinction/README.md). 

Note: This is a **stateless** workflow. 

### Seismo

Note: This is a **statefull** workflow. 

### Articles Sentiment Analysis 

[This workflow](./article_sentiment_analysis) uses two different approaches to analyse the sentiment of news articles (i.e. score the news article), and these sentiment scores are then grouped according to the location where they were published. Finally, the workflow will output the three happiest locations with their scores.


More info about how to run this workflow is available [here](./article_sentiment_analysis/README.md)

Note: This is a **statefull** workflow. 


### Others

- [Skew workflow](others/skew_workflow.py)
- [Covid workflow](others/covid_workflow.py)

## Mappings

The mappings of dispel4py refer to the connections between the processing elements (PEs) in a dataflow graph. Dispel4py is a Python library used for specifying and executing data-intensive workflows. In a dataflow graph, each PE represents a processing step, and the mappings define how data flows between the PEs during execution. These mappings ensure that data is correctly routed and processed through the dataflow, enabling efficient and parallel execution of tasks. We currently support the following ones:

- **Sequential**
  - "simple": it executes dataflow graphs sequentially on a single process, suitable for small-scale data processing tasks.
- **Parallel**:
  -  **Fixed fixed workload distribution - support stateful and stateless PEs:**
    - "mpi": it distributes dataflow graph computations across multiple nodes (distributed memory) using the Message Passing Interface (MPI).
    - "mpi" it runs multiple instansces of dataflow graph concurrently using MPI, offering parallel processing in a distributed shared memory enviroment, such as a HPC cluster.
    - "multi": it runs multiple instances of a dataflow graph concurrently using **multiprocessing Python library**, offering parallel processing on a single machine.
  - **Dynamic workfload distribution -  support only stateless PEs**
    - "dyn_multi": it runs multiple instances of a dataflow graph concurrently using **multiprocessing Python library**. Worload assigned dynamically (but no autoscaling). 
    - "dyn_auto_multi": same as above, but allows autoscaling. 
    - "dyn_redis": it runs multiple instances of a dataflow graph concurrently using **Redis library**. Worload assigned dynamically (but no autocasling).
    - "dyn_auto_redis": same as above, but allows autoscaling. 
  - **Hybrid workload distribution - supports stateful and stateless PEs**
    - "hybrid_redis": it runs multiple instances of a dataflow graph concurrently using **Redis library**. Hybrid approach for workloads: Stafeless PEs assigned dynamically, while Stateful PEs are assigned from the begining



