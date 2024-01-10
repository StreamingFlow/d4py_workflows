#!/bin/bash

# Output log file
LOGFILE="output_corr.log"

# Empty the log file first
> $LOGFILE

# Iterate over the number of processors for multi
for n in 12 16; do
    echo "multi : running with $n processors" >> $LOGFILE
    python -m dispel4py.new.processor multi realtime_prep_dict.py -f xcorr_input.jsn -n $n >> $LOGFILE 2>&1
    echo "---------------------------------" >> $LOGFILE
done



# Iterate over the number of processors for dyn_multi
for n in 4 8 12 16; do
    echo "dyn_multi : running with $n processors" >> $LOGFILE
    python -m dispel4py.new.processor dyn_multi realtime_prep_dict.py -f xcorr_input.jsn -n $n >> $LOGFILE 2>&1
    echo "---------------------------------" >> $LOGFILE
done

# Iterate over the number of processors for dyn_auto_multi
for n in 4 8 12 16; do
    echo "dyn_auto_multi : running with $n processors" >> $LOGFILE
    python -m dispel4py.new.processor dyn_auto_multi realtime_prep_dict.py -f xcorr_input.jsn -n $n >> $LOGFILE 2>&1
    echo "---------------------------------" >> $LOGFILE
done


# Iterate over the number of processors for dyn_redis
for n in 4 8 12 16; do
# for n in 4; do
    echo "dyn_redis : running with $n processors" >> $LOGFILE
    python -m dispel4py.new.processor dyn_redis realtime_prep_dict.py -f xcorr_input.jsn -n $n >> $LOGFILE 2>&1
    echo "---------------------------------" >> $LOGFILE
done


# Iterate over the number of processors for dyn_auto_redis
for n in 4 8 12 16; do
# for n in 4; do
    echo "dyn_auto_redis : running with $n processors" >> $LOGFILE
    python -m dispel4py.new.processor dyn_auto_redis realtime_prep_dict.py -f xcorr_input.jsn -n $n -thr 4000 >> $LOGFILE 2>&1
    echo "---------------------------------" >> $LOGFILE
done


# Iterate over the number of processors for hybrid_redis
for n in 12 16; do
    echo "hybrid_redis : running with $n processors" >> $LOGFILE
    python -m dispel4py.new.processor hybrid_redis realtime_prep_dict.py -f xcorr_input.jsn -n $n >> $LOGFILE 2>&1
    echo "---------------------------------" >> $LOGFILE
done



echo "All experiments completed!" >> $LOGFILE
