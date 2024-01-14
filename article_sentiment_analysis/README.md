# Sentiment Analyses for News Articles

[This workflow](./analysis_sentiment.py) uses two different approaches to analyse the sentiment of news articles (i.e. score the news article), and these sentiment scores are then grouped according to the location where they were published. Finally, the workflow will output the three happiest locations with their scores. 

The news articles used in this case are collected from a public Kaggle dataset [News Articles](https://www.kaggle.com/datasets/asad1m9a9h6mood/news-articles).This dataset contains news articles from 2015 related to business and sports with their heading, content, public location and date. As some of the data had missing fields and some of the articles contained a large number of nonsensical characters (e.g. <script>, `<br/>`), a Python script was developed for the project to pre-process the data. 

The first PE, "Read Articles", reads articles from an input file and then extracts the article content line by line. Every time a line is read and parsed, one data is generated and sent to two downstream PEs. PE "Sentiment AFINN" calculate the news article’s sentiment score by [AFINN lexicon](./AFINN-111.txt). PE "Tokenisation WD" and "Sentiment SWN3" tokenise the news article content and then calculate the sentiment score using the [SWN3](SentiWordNet_3.0.0_20130122.txt) lexicon. After that, data from both branches go to their respective "Find State" - "Happy State" - "Top 3 Happiest" PE chain. The three PEs find the location of each data, group the received data by location and finally display the three happiest (highest scoring) locations and their scores. The number of instances of the PE "Happy State" in the "SWN3" branch is set to 3 in order to reflect the stateful character.


## Requirements


Activate the conda python 3.10+ enviroment. If you had not created one, follow the [README instructions](https://github.com/StreamingFlow/d4py/tree/main).

```
conda activate d4py_env
```

Also, you will need to install the following packages: 


```shell
  pip install pandas
  $ pip install pandas
  $ pip install nltk  
  $ python
  >>> import nltk
  >>> nltk.download('averaged_perceptron_tagger')
  >>> nltk.download('punkt')
  >>> nltk.download('stopwords')
  >>> nltk.download('wordnet')
  >>> nltk.download('omw-1.4')

``` 

## Important

1. This workflow is a **statefull** workflow!! So only the **fixed workload mappings** and **hybrid** mapping could be used to run this workflow.

2. If you run the workflow from a different directory, you only need to specify the path as <DIR1>.<DIR2>.<NAME_WORKFLOW> without the .py extension. However, if you are in the article_sentiment_analysis directory, then use <NAME_WORKFLOW>.py. Bellow there are two examples for clarity:

Example 1 - within `article_sentiment_analysis` directory:

```shell
dispel4py simple analysis_sentiment.py -d '{"read":[{"input":"Articles_cleaned.csv"}]}'
```

Example 2 - other place (e.g. outside `d4py_workflows` directory):

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


## Preparation of data

In order to run this workflow, you must first prepare the article data needed for the test. We collect some article data from http://aaa.com and saved as "Articles.csv" in this repository. Before running the test, you must first run "clean.py" in this directory to clean the data. 

```shell
$ python clean.py Articles.csv
``` 


## Run the workflow with different mappings

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



