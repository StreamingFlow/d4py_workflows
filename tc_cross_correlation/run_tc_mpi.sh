#!/bin/bash


rm -rf ./OUTPUT/DATA
rm -rf ./OUTPUT/XCORR
mkdir  ./OUTPUT/DATA
mkdir ./OUTPUT/XCORR

mpiexec -n 10 --allow-run-as-root --oversubscribe  dispel4py mpi realtime_prep.py -f realtime_xcorr_input.jsn -n 10
mpiexec -n 10 --allow-run-as-root --oversubscribe  dispel4py mpi realtime_xcorr.py -n 10

