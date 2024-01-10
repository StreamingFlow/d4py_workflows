# Covid and Skew Workflows

[covid_workflow](./covid_workflow.py) 


## Requirements


Activate the conda python 3.10+ enviroment. If you had not created one, follow the [README instructions](https://github.com/StreamingFlow/d4py/tree/main).

```
conda activate d4py_env
```

## Important


If you run those workflows from a different directory, you only need to specify the path as <DIR1>.<DIR2>.<NAME_WORKFLOW> without the .py extension. However, if you are in `others` directory, then use <NAME_WORKFLOW>.py. Below are examples for clarity:

Example 1 - within article_sentiment directory:

```shell
dispel4py simple analysis_sentiment.py -d '{"read":[{"input":"Articles_cleaned.csv"}]}'
```

Example 2 - other place (e.g. outside d4py_workflows directory):

```shell
dispel4py simple d4py_workflows.article_sentiment_analysis.analysis_sentiment -d '{"read":[{"input":"Articles_cleaned.csv"}]}'
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

```shell
python -m dispel4py.new.processor simple analysis_sentiment.py -d '{"read":[{"input":"Articles_cleaned.csv"}]}'
```

OR

```shell
dispel4py simple analysis_sentiment.py -d '{"read":[{"input":"Articles_cleaned.csv"}]}'
```

### (Fixed) MPI mapping

```shell
mpiexec -n 13 dispel4py mpi analysis_sentiment.py -d '{"read":[{"input":"Articles_cleaned.csv"}]}' -n 13
```
OR 

```shell
mpiexec -n 13 --allow-run-as-root --oversubscribe dispel4py mpi analysis_sentiment.py -d '{"read":[{"input":"Articles_cleaned.csv"}]}' -n 13
```

OR

```shell
mpiexec -n 13 python -m dispel4py.new.processor dispel4py.new.mpi_process analysis_sentiment.py -d '{"read":[{"input":"Articles_cleaned.csv"}]}' -n 13 
```

### (Fixed) Multi mapping

```
python -m dispel4py.new.processor multi  analysis_sentiment.py -n 13 -d '{"read":[{"input":"Articles_cleaned.csv"}]}' 
``` 
OR 

``` 
dispel4py multi  analysis_sentiment.py -n 13  -d '{"read":[{"input":"Articles_cleaned.csv"}]}' 
``` 


### Hybrid Redis

Remember, you need to have installed both, redis server and redis client. 

> Go to another terminal for following command line

```shell
redis-server
```

> Go back to previous terminal

In another tab you can do the following run: 

```
python -m dispel4py.new.processor hybrid_redis analysis_sentiment.py -n 13  -d '{"read":[{"input":"Articles_cleaned.csv"}]}' 
``` 
OR

``` 
dispel4py hybrid_redis analysis_sentiment.py -n 13  -d '{"read":[{"input":"Articles_cleaned.csv"}]}' 
``` 
**Note**: You can use just one tab terminal, running redis-server in the background: `redis-server &`



