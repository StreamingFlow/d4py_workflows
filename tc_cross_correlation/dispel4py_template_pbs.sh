#!/bin/bash --login
#PBS -l select=1:ncpus=36
#PBS -l walltime=00:02:00

#PBS -A ????

# Change to the directory that the job was submitted from
cd $PBS_O_WORKDIR

# Load any required modules
module load mpt
module load anaconda
module load intel-mpi-17

# Set the number of threads to 1
#   This prevents any threaded system libraries from automatically
#   using threading.
export OMP_NUM_THREADS=1

export PYTHONPATH=$PYTHONPATH:/lustre/home/z04/rosaf2/dispel4py_workflows/tc_cross_correlation

rm -rf  OUTPUT/DATA
rm -rf  OUTPUT/XCORR
mkdir   OUTPUT/DATA
mkdir  OUTPUT/XCORR

dispel4py multi realtime_prep.py -f realtime_xcorr_input.jsn -n 10
dispel4py multi realtime_xcorr.py -n 10

