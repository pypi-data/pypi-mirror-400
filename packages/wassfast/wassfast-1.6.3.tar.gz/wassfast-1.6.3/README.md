# WASSfast

WASSfast is the next-generation stereo processing pipeline for sea waves 3D reconstruction. It exploits the linear dispertion relation and sparse feature triangulation to resolve sea-surface elevation in quasi real-time. At present state, WASSfast can work in two operating modes:

1) Predict-Update (PU) mode. See the [paper](https://www.sciencedirect.com/science/article/pii/S0098300420306385)

2) Convolutional Neural Network (CNN) mode (suggested). See the [paper](https://www.mdpi.com/2072-4292/13/18/3780/pdf)


For the standard pipeline see [http://www.dais.unive.it/wass](http://www.dais.unive.it/wass)

## How to use it

WASSfast is mostly written in Python and use [conda](https://www.anaconda.com/products/individual) to manage its dependencies.

Installation steps:

1. Install conda or [miniconda](https://docs.conda.io/en/latest/miniconda.html#latest-miniconda-installer-links) (the latter is suggested)

2. Clone WASSfast repository and cd into the project directory
```
$ git clone https://gitlab.com/fibe/wassfast.git
$ cd wassfast
```

3. Install the correct environment according to your OS:
```
$ conda env create -f <environment_name>
```
where ```<environment_name>``` is one of the following:

- ```environment.linux.pu.yml``` to run WASSfast in PU mode under Linux
- ```environment.linux.cnn.yml``` to run WASSfast in CNN mode under Linux
- ```environment.win10.pu.yml``` to run WASSfast in PU mode under Windows 10
- ```environment.win10.cnn.yml``` to run WASSfast in CNN mode under Windows 10
- ```environment.win10.cnn.gpu.yml``` to run WASSfast in CNN mode under Windows 10 with the GPU support (this is the reccomanded mode)

Note: if you have throubles installing the environment due to unsatisfied dependencies, try mamba instead:

```
$ conda install -n base conda-forge::mamba
$ mamba env create -f <environment_name>
```


4. ***For the PU mode only:*** Compile the PointsReducer C++ library:
```
$ cd wassfast/PointsReducer
$ mkdir build
$ cd build
$ cmake ../
$ make ; make install
```

5. Activate the environment and test if WASSfast works correctly:
```
$ conda activate wassfast_cnn
$ python -m wassfast
```

You should see something like:

```

       ╦ ╦╔═╗╔═╗╔═╗┌─┐┌─┐┌─┐┌┬┐
       ║║║╠═╣╚═╗╚═╗├┤ ├─┤└─┐ │
       ╚╩╝╩ ╩╚═╝╚═╝└  ┴ ┴└─┘ ┴
              _.~'~._.~'~._.~'~._.~'~._
         v. 1.4.2 - Copyright (C)
                    Filippo Bergamasco 2023

usage: __main__.py [-h] [--continuous_mode] [--kafka_mode] [--debug_mode] [--debug_stats] [--batchsize BATCHSIZE] [--start_from_plane] [--demosaic] [--save_polarization]
                   [--current_u CURRENT_U] [--current_v CURRENT_V] [--depth DEPTH] [-dd DEBUGDIR] [-s] [--nographics] [-n NFRAMES] [--first_frame FIRST_FRAME] [-r FRAMERATE]
                   [--nfft] [--fft] [--upload_url UPLOAD_URL] [--location LOCATION] [-o OUTPUT]
                   imgdata configfile calibdir settingsfile wavedirection processingmode
__main__.py: error: the following arguments are required: imgdata, configfile, calibdir, settingsfile, wavedirection, processingmode

```

You can run `python -m wassfast --help` for a brief description of the command-line options.


## Try it with test data

1. cd into WASSfast directory
2. Download the [test data](https://www.dais.unive.it/wass/wassfast_testdata_256.7z)
2. Extract the test data ```7z x wassfast_testdata_256.7z```. This will create a directory named `wassfast_testdata_256`
3. `$ cd wassfast_testdata_256`
4. run `$ conda activate wassfast_cnn` (or wassfast_pu)
5. run `$ ./run_wassfast_cnn.sh` or `$ ./run_wassfast_pu.sh`


After the processing, the NetCDF file `wassfast_output.nc` is produced. 

To render the resulting surfaces, clone [wassncplot](https://github.com/fbergama/wassncplot) into the same root directory containing also the WASSfast project and run:

```
$ cd wassfast_testdata_256/
$ ./run_wassncplot.sh
```

The resulting images will be placed in ```wassfast_testdata_256/frames```

## Acknowledgements

The study was partially supported by the project of Construction of Ocean Research Stations and their Application Studies funded by the Ministry of Oceans and Fisheries, Republic of Korea.


## License

```
Copyright (C) 2020-2021 Filippo Bergamasco 

WASSfast is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

WASSfast is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
```
