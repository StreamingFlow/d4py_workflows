# Sentiment Analyses for News Articles

[This workflow](./analysis_sentiment.py) uses two different approaches to analyse the sentiment of news articles (i.e. score the news article), and these sentiment scores are then grouped according to the location where they were published. Finally, the workflow will output the three happiest locations with their scores. 

The news articles used in this case are collected from a public Kaggle dataset [News Articles](https://www.kaggle.com/datasets/asad1m9a9h6mood/news-articles).This dataset contains news articles from 2015 related to business and sports with their heading, content, public location and date. As some of the data had missing fields and some of the articles contained a large number of nonsensical characters (e.g. <script>, `<br/>`), a Python script was developed for the project to pre-process the data. 

The first PE, "Read Articles", reads articles from an input file and then extracts the article content line by line. Every time a line is read and parsed, one data is generated and sent to two downstream PEs. PE "Sentiment AFINN" calculate the news article’s sentiment score by [AFINN lexicon](./AFINN-111.txt). PE "Tokenisation WD" and "Sentiment SWN3" tokenise the news article content and then calculate the sentiment score using the [SWN3](SentiWordNet_3.0.0_20130122.txt) lexicon. After that, data from both branches go to their respective "Find State" - "Happy State" - "Top 3 Happiest" PE chain. The three PEs find the location of each data, group the received data by location and finally display the three happiest (highest scoring) locations and their scores. The number of instances of the PE "Happy State" in the "SWN3" branch is set to 3 in order to reflect the stateful character.


## Requirements

Activate the conda python 3.10+ enviroment. If you had not created one, follow the [README instructions](https://github.com/StreamingFlow/d4py/tree/main).

```
conda activate py310
```
***Atention!!:** This workflow is a **statefull** workflow!! So only the **fixed workload mappings** and **hybrid** mapping could be used to run this workflow.

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

## Preparation of data

In order to run this workflow, you must first prepare the article data needed for the test. We collect some article data from http://aaa.com and saved as "Articles.csv" in this repository. Before running the test, you must first run "clean.py" in this directory to clean the data. 

```shell
$ pip install pandas
$ python clean.py Articles.csv
``` 

## Install NLTK packets

```shell
  $ pip install nltk numpy 
  $ python
  >>> import nltk
  >>> nltk.download('averaged_perceptron_tagger')

``` 

## Run the workflow with different mappings

### Simple mapping

```shell
python -m dispel4py.new.processor simple analysis_sentiment -d '{"read":[{"input":"Articles_cleaned.csv"}]}'
```

OR

```shell
dispel4py simple analysis_sentiment -d '{"read":[{"input":"Articles_cleaned.csv"}]}'

### Fixed MPI mapping
```shell
mpiexec -n 13 dispel4py mpi analysis_sentiment.py -d '{"read":[{"input":"Articles_cleaned.csv"}]}' -n 13
```

```shell
mpiexec -n 13 python -m dispel4py.new.processor dispel4py.new.mpi_process analysis_sentiment.py -d '{"read":[{"input":"Articles_cleaned.csv"}]}' -n 13 
```

### Multi mapping

```
python -m dispel4py.new.processor multi  analysis_sentiment -n 13 -d '{"read":[{"input":"Articles_cleaned.csv"}]}' 
``` 
OR 

``` 
dispel4py multi  analysis_sentiment -n 13  -d '{"read":[{"input":"Articles_cleaned.csv"}]}' 
``` 


### Hybrid Redis

You need REDIS server running in a tab: 

```shell
conda activate py37_d4p
redis server
```

In another tab you can do the following run: 

```
python -m dispel4py.new.processor hybrid_redis analysis_sentiment -n 13  -d '{"read":[{"input":"Articles_cleaned.csv"}]}' 
``` 
OR
``` 
dispel4py hybrid_redis analysis_sentiment -n 13  -d '{"read":[{"input":"Articles_cleaned.csv"}]}' 
``` 

