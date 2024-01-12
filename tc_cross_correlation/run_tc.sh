#!/bin/bash


rm -rf ./OUTPUT/DATA
rm -rf ./OUTPUT/XCORR
mkdir  ./OUTPUT/DATA
mkdir ./OUTPUT/XCORR

dispel4py multi realtime_prep.py -f realtime_xcorr_input.jsn -n 10
dispel4py multi realtime_xcorr.py -n 10

