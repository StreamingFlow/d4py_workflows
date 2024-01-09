#!/bin/bash

# Output log file
LOGFILE="output_int_100.log"

# Empty the log file first
> $LOGFILE

# Iterate over the number of processors for dyn_multi
for n in 4 8 12 16; do
# for n in 4; do
    echo "dyn_multi : running with $n processors" >> $LOGFILE
    python -m dispel4py.new.processor dyn_multi int_ext_graph.py -d '{"read" : [ {"input" : "cp_coordinates_100.txt"} ]}' -n $n >> $LOGFILE 2>&1
    echo "---------------------------------" >> $LOGFILE
done

# Iterate over the number of processors for dyn_auto_multi
for n in 4 8 12 16; do
# for n in 4; do
    echo "dyn_auto_multi : running with $n processors" >> $LOGFILE
    python -m dispel4py.new.processor dyn_auto_multi int_ext_graph.py -d '{"read" : [ {"input" : "cp_coordinates_100.txt"} ]}' -n $n >> $LOGFILE 2>&1
    echo "---------------------------------" >> $LOGFILE
done



# Iterate over the number of processors for dyn_multi
for n in 4 8 12 16; do
# for n in 4; do
    echo "dyn_redis : running with $n processors" >> $LOGFILE
    python -m dispel4py.new.processor dyn_redis int_ext_graph.py -d '{"read" : [ {"input" : "cp_coordinates_100.txt"} ]}' -n $n >> $LOGFILE 2>&1
    echo "---------------------------------" >> $LOGFILE
done


# Iterate over the number of processors for dyn_multi
for n in 4 8 12 16; do
# for n in 4; do
    echo "dyn_auto_redis : running with $n processors" >> $LOGFILE
    python -m dispel4py.new.processor dyn_auto_redis int_ext_graph.py -d '{"read" : [ {"input" : "cp_coordinates_100.txt"} ]}' -n $n >> $LOGFILE 2>&1
    echo "---------------------------------" >> $LOGFILE
done

echo "All experiments completed!" >> $LOGFILE