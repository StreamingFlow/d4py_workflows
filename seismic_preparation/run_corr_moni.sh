#!/bin/bash

# Output log file
LOGFILE="output_corr_moni.log"

# Empty the log file first
> $LOGFILE




# Iterate over the number of processors for dyn_auto_multi
for n in 16; do
    echo "dyn_auto_multi : running with $n processors" >> $LOGFILE
    python -m dispel4py.new.processor dyn_auto_multi realtime_prep_dict.py -f xcorr_input.jsn -n $n >> $LOGFILE 2>&1
    echo "---------------------------------" >> $LOGFILE
done



# Iterate over the number of processors for dyn_auto_redis
for n in 16; do
# for n in 4; do
    echo "dyn_auto_redis : running with $n processors" >> $LOGFILE
    python -m dispel4py.new.processor dyn_auto_redis realtime_prep_dict.py -f xcorr_input.jsn -n $n -thr 2000 >> $LOGFILE 2>&1
    echo "---------------------------------" >> $LOGFILE
done




echo "All experiments completed!" >> $LOGFILE
