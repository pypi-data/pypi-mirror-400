WASSfast is the next-generation stereo processing pipeline for sea waves 3D reconstruction. It exploits the linear dispertion relation and sparse feature triangulation to resolve sea-surface elevation in quasi real-time. At present state, WASSfast can work in two operating modes:

1) Predict-Update (PU) mode. See the [paper](https://www.sciencedirect.com/science/article/pii/S0098300420306385)

2) Convolutional Neural Network (CNN) mode (suggested). See the [paper](https://www.mdpi.com/2072-4292/13/18/3780/pdf)


For the standard pipeline see [http://www.dais.unive.it/wass](http://www.dais.unive.it/wass)

**Note** Due to TensorFlow version incompatibilities, WASSfast installed via Pypi supports CNN mode only.

## How to use it

Install via pip:

```
python -m pip install wassfast
```

and run `wassfast --help` for a brief description of the command-line options.


## Try it with test data

1. Download the [test data](https://www.dais.unive.it/wass/wassfast_testdata_256.7z)
2. Extract the test data ```7z x wassfast_testdata_256.7z```. This will create
   a directory named `wassfast_testdata_256`
3. Enter the newly extracted directory: `cd wassfast_testdata_256`
4. Execute WASSfast:

```
wassfast ./input ./config256.mat ./config ./settings.cfg RLTB CNN --batchsize 16 -n 49 -r 15.0 -o output.nc 
```

After the processing, the NetCDF file `output.nc` is produced. Use [Panoply](https://www.giss.nasa.gov/tools/panoply/) to inspect the reconstructed surface.


## Acknowledgements

The study was partially supported by the project of Construction of Ocean Research Stations and their Application Studies funded by the Ministry of Oceans and Fisheries, Republic of Korea.


## License

```
Copyright (C) 2020-2023 Filippo Bergamasco 

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
