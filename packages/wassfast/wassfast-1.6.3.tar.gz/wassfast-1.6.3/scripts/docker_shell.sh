#!/bin/bash

MAPPINGPARAMS=()

DATA_DIR=$1
if [ -d "$DATA_DIR" ]; then
    echo Mapping $DATA_DIR to /DATA
    MAPPINGPARAMS+=( -v $DATA_DIR:/DATA)
fi

#DATA_IN_DIR=$2
#if [ -d "$DATA_IN_DIR" ]; then
#    echo Mapping $DATA_IN_DIR to /DATA_IN
#    MAPPINGPARAMS+=( -v $DATA_IN_DIR:/DATA_IN)
#fi
#
#DATA_OUT_DIR=$3
#if [ -d "$DATA_OUT_DIR" ]; then
#    echo Mapping $DATA_OUT_DIR to /DATA_OUT
#    MAPPINGPARAMS+=( -v $DATA_OUT_DIR:/DATA_OUT)
#fi

if [ -z "$MAPPINGPARAMS" ]; then
    echo "Note: you can run this script with $0 <DATA_DIR>"
fi

echo "Port 22 mapped to port 22189 (run scripts/start_sshd.sh if needed)"

#docker run --name wassfast_dev -p 22189:22 -e LOCAL_USER_ID=`id -u $USER` -u wass "${MAPPINGPARAMS[@]}" --rm -i -t --entrypoint "/workspaces/wassfast/entrypoint.sh"  wassfast:dev

if [[ ! -z $(docker image ls | grep wassfast | grep gpu) ]]; then
    echo "Running wassfast:gpu"
    docker run --runtime=nvidia --name wassfast -p 22189:22 -e LOCAL_USER_ID=`id -u $USER` -u wass "${MAPPINGPARAMS[@]}" --rm -i -t --entrypoint "/workspaces/wassfast/entrypoint.sh"  wassfast:gpu

fi


if [[ ! -z $(docker image ls | grep wassfast | grep cpu) ]]; then
    echo "Running wassfast:cpu"
    docker run --name wassfast -p 22189:22 -e LOCAL_USER_ID=`id -u $USER` -u wass "${MAPPINGPARAMS[@]}" --rm -i -t --entrypoint "/workspaces/wassfast/entrypoint.sh"  wassfast:cpu

fi
