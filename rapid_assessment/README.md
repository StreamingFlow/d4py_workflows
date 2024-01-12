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

We have several scripts to run the application with different **fixed mappings**:
 - `run_total_combined_simple`: uses simple mapping for all workflows.
 - `run_total_combined_mpi`: uses simple mapping for the first and last workflows, and mpi mapping for the rest.
 - `run_total_combined_multi`: uses simple mapping for the first and last workflows, and multi mapping for the rest.
 - `run_total_combined_times`: same as above, but with the `- monitoring` flag activated to monitor the execution times of each workflow. 



```	
### run_total_combined_multi.sh 

#!/bin/bash
set -x 

mkdir -p ./misfit_data
rm -r ./misfit_data/data
rm -r ./misfit_data/stations
rm -r ./misfit_data/output
rm -r ./misfit_data/output-images
mkdir ./misfit_data/output
mkdir ./misfit_data/data   #fm

rm -rf ./GM
mkdir -p ./GM

export PYTHONPATH=$PYTHONPATH:.
export MISFIT_PREP_CONFIG="processing.json" 
export STAGED_DATA="./misfit_data/"
export OUTPUT="./GM/"

######## 1. Run waveform simulation --- Specfem3D  -- it creates the sythetic waveforms (seeds)


######## 2. Create input for download -- This workflow read the input files of the specfem3d simulation and creates the correspond
ing input json file for the following download workflow
dispel4py simple create_download_json.py -d '{"WJSON" :
[{"specfem3d_data_url":"https://gitlab.com/project-dare/WP6_EPOS/raw/RA_total_script/processing_elements/Download_Specfem3d_Misfit
_RA/data.zip",
"output":"download_test.json"}]}'


######## 3. Get observed data -- This workflow download the obseved waveforms and stations xml
dispel4py multi download_FDSN.py -f download_test.json -n 6

# ####### 4. Get pre-processed synth and data --- Misfit Preprocess

dispel4py multi create_misfit_prep.py -n 17

# ####### 5. Get ground motion parameters and compare them

searchpath="./misfit_data/output/"
dispel4py multi dispel4py_RA.pgm_story.py -d '{"streamProducerReal": [ {"input":"'$searchpath'" } ], "streamProducerSynth": [ {"in
put": "'$searchpath'"} ]}' -n 7

# ####### 6. Plot the PGM map
#dispel4py simple dispel4py_RAmapping.py

```	

- **Note**: It is important that you delete `misfit_data` directory every time before starting to run your workflows. 
