# Covid and Skew Workflows

[covid_workflow](./covid_workflow.py) is focused on fetching, processing, and visualizing COVID-19 data, specifically for India. It begins with a DataProducer component that retrieves COVID-19 statistics from an online API, followed by a DataProcessor that parses this data to extract dates and daily new case figures. Lastly, the DataVisualizer component takes this processed data and creates a graphical representation of the COVID-19 daily new cases over time, plotting this data on a chart. The final output is a visual graph saved as an image file, providing a clear and informative depiction of the pandemic's trend in India. This workflow effectively combines data acquisition, manipulation, and visualization, making it a useful tool for analyzing and understanding the progression of COVID-19 cases. However, this is a **statefull workflow** - so only fixed mappings works with this workflow.  Note that this workflow generates a `covid_cases.png` file with the visualization of the results. 

[skew_workflow](./skew_workflow.py) is designed to generate random numbers, check if they are prime, and print the prime numbers. It consists of three processing elements (PEs): NumberProducer, IsPrime, and PrintPrime. The NumberProducer generates a random integer between 1 and 1000, after a brief, skewed sleep time (towards shorter durations). Each generated number is then passed to the IsPrime PE, which checks if the number is a prime. If a number is prime, it's passed to the PrintPrime PE. The PrintPrime PE simply prints out the prime numbers it receives. The workflow graph connects these PEs, ensuring the flow of data from the number generation to prime checking, and finally to printing the prime numbers. This workflow showcases basic data processing, conditional logic, and inter-PE communication in a dispel4py environmen

## Requirements


Activate the conda python 3.10+ enviroment. If you had not created one, follow the [README instructions](https://github.com/StreamingFlow/d4py/tree/main).

```
conda activate d4py_env
```

## Important

1. The `covid_workflow` is a **statefull** workflow!! So only the **fixed workload mappings**. Also, since it has a JSON file - it does not work with the hibryd_mapping. 

2. If you run those workflows from a different directory, you only need to specify the path as <DIR1>.<DIR2>.<NAME_WORKFLOW> without the .py extension. However, if you are in `others` directory, then use <NAME_WORKFLOW>.py. Below are examples for clarity:

Example 1 - within `others` directory:

```shell
dispel4py simple covid_workflow.py
```

Example 2 - other place (e.g. outside `d4py_workflows` directory):

```shell
dispel4py simple d4py_workflows.others.covid_workflow 
```

## Using Docker Container

Alternative you can follow [this instructions](https://github.com/StreamingFlow/d4py/tree/main#docker) to build a docker image and run dispel4py and this workflow within a docker container.

Once you are inside the docker container, you will have to clone this repository, and enter to the d4py_workflows directory. See bellow:
```
git clone https://github.com/StreamingFlow/d4py_workflows.git
cd d4py_workflows
```
Using our Docker  image, we can ensure that all the mappings described [bellow](https://github.com/StreamingFlow/d4py_workflows/tree/main/article_sentiment_analysis#run-the-workflow-with-different-mappings) work for this workflow.



## Run workflows with different mappings

### Simple mapping

##### Covid workflow

```shell
python -m dispel4py.new.processor simple covid_workflow.py 
```

OR

```shell
dispel4py simple covid_workflow.py 
```
##### Skew workflow

```shell
python -m dispel4py.new.processor simple skew_workflow.py -i 100 
```

OR

```shell
dispel4py simple skew_workflow.py -i 100
```

### (Fixed) MPI mapping

##### Covid workflow
```shell
mpiexec -n 10 dispel4py mpi covid_workflow.py 
```
OR 

```shell
mpiexec -n 10 --allow-run-as-root --oversubscribe dispel4py mpi covid_workflow.py 
```

OR

```shell
mpiexec -n 10 python -m dispel4py.new.processor dispel4py.new.mpi_process covid_workflow.py 
```

##### Skew workflow

```shell
mpiexec -n 10 dispel4py mpi skew_workflow.py -n 10 -i 100
```
OR 

```shell
mpiexec -n 10 --allow-run-as-root --oversubscribe dispel4py mpi skew_workflow.py -n 10 -i 100
```

OR

```shell
mpiexec -n 10 python -m dispel4py.new.processor dispel4py.new.mpi_process skew_workflow.py -n 10 -i 100 
```

### (Fixed) Multi mapping

##### Covid workflow

```
python -m dispel4py.new.processor multi  covid_workflow.py -n 10 
``` 
OR 

``` 
dispel4py multi  covid_workflow.py -n 10
``` 

##### Skew workflow

```
python -m dispel4py.new.processor multi  skew_workflow.py -n 10 -i 100
``` 
OR 

``` 
dispel4py multi  skew_workflow.py -n 10 -i 100
``` 
#### Dynamic Multi mapping - Skew workflow

```shell
python -m dispel4py.new.processor dyn_multi skew_workflow.py -n 10 -i 100 
```

OR 

```shell
dispel4py dyn_multi skew_workflow.py -n 10 -i 100
```
 
#### Dynamic Multi Autoscaling mapping

```shell
python -m dispel4py.new.processor dyn_auto_multi skew_workflow.py -n 10 -i 100 -thr 10
```

OR

```shell
dispel4py dyn_auto_multi skew_workflow.py -n 10 -i 100 -thr 10
```

### Redis Mappings - Skew workflow

#### Redis

Remember, you need to have installed both, redis server and redis client. 

> Go to another terminal for following command line

```shell
redis-server
```

> Go back to previous terminal

```
python -m dispel4py.new.processor redis skew_workflow.py -ri localhost -n 10 -i 100  
``` 
OR

``` 
dispel4py redis skew_workflow.py -ri localhost -n 10  -i 100
``` 
**Note**: You can use just one tab terminal, running redis-server in the background: `redis-server &`


#### Dynamic Redis

#### Hybrid Redis
Remember, you need to have installed both, redis server and redis client. 

```
python -m dispel4py.new.processor hybrid_redis skew_workflow.py -n 10 -i 100  
``` 
OR

``` 
dispel4py hybrid_redis skew_workflow.py -n 10  -i 100
``` 

#### Dynamic Redis mapping

> Go to another terminal for following command line

```shell
redis-server
```

> Go back to previous terminal

```shell
python -m dispel4py.new.processor dyn_redis skew_workflow.py -n 10 -i 10
```
OR
```shell
dispel4py dyn_redis dyn_redis skew_workflow.py -n 10 -i 10 
```

#### Dynamic Redis Autoscaling mapping
```shell
python -m dispel4py.new.processor dyn_auto_redis skew_workflow.py -n 10 -i 10 -thr 200
```

OR
```shell
dispel4py dyn_auto_redis skew_workflow.py -n 10 -i 10 -thr 200
```

