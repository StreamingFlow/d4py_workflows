#!/bin/bash

# Output log file
LOGFILE="output_sent.log"

# Empty the log file first
> $LOGFILE

# Iterate over the number of processors for hybrid_redis
for n in 8 10 12 14 16; do
    echo "hybrid_redis : running with $n processors" >> $LOGFILE
    python -m dispel4py.new.processor hybrid_redis analysis_sentiment.py -d '{"read":[{"input":"Articles_cleaned.csv"}]}' -n $n >> $LOGFILE 2>&1
    echo "---------------------------------" >> $LOGFILE
done

for n in 14 16; do
    echo "multi : running with $n processors" >> $LOGFILE
    python -m dispel4py.new.processor multi analysis_sentiment.py -d '{"read":[{"input":"Articles_cleaned.csv"}]}' -n $n >> $LOGFILE 2>&1
    echo "---------------------------------" >> $LOGFILE
done

echo "All experiments completed!" >> $LOGFILE
