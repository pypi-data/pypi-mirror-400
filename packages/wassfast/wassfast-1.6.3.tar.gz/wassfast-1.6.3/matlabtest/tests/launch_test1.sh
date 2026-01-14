#!/bin/bash
source `pipenv --venv`/bin/activate
                
                
DATAFILE="/media/fibe/DATA1/realtime/20180409T130727_east_break_polarim.raw"
CONFIGFILE="config.mat"
CALIBDIR="/media/fibe/DATA1/realtime/config/"
NFRAMES=1000

#for i in `seq 0 6`;
for i in `seq 1 1`;
do
    python3 wassfast.py $DATAFILE $CONFIGFILE $CALIBDIR ./matlabtest/tests/quality_fast$i.cfg -s -n $NFRAMES -o ./matlabtest/tests/out_fast$i.nc
done
