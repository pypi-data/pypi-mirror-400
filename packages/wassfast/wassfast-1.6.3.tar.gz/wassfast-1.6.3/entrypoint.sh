#!/bin/bash

source `pipenv --venv`/bin/activate

curr=`pwd`
cd wassfast/PointsReducer
mkdir -p build
cd build
cmake ../
make install

cd $curr

Xvfb :1 -screen 0 1024x768x16 &

# exec "$@"

bash -c "pipenv shell"