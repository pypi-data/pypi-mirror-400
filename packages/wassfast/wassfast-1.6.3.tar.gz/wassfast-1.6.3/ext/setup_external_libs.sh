#!/bin/bash

source `pipenv --venv`/bin/activate

if [ $# -gt 0 ]; then
    cd $1
fi

git clone https://github.com/NFFT/nfft.git --depth 1
ls -alh
cp compile_all.sh nfft/
cd nfft
./compile_all.sh
cd ..

git clone https://github.com/ghisvail/pyNFFT.git --depth 1
cd pyNFFT

python setup.py build_ext -I `pwd`/../nfft/dist/include -L `pwd`/../nfft/dist/lib -R `pwd`/../nfft/dist/lib
python setup.py install
