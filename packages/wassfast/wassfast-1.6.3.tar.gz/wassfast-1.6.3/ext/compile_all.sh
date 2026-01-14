#!/bin/bash


./bootstrap.sh
./configure --prefix `pwd`/dist --enable-openmp --disable-applications
make clean
make -j 4
make install


