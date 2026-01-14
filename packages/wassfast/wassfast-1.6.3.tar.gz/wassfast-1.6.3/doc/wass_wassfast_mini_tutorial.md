---
title: |
        WASS / WASSfast mini tutorial
author: Filippo Bergamasco
date: 21/07/2023
...

[ compile it with pandoc -c pandoc.css -s wass_wassfast_mini_tutorial.md -o wass_wassfast_mini_tutorial.html ]::


## Dataset preparation

Start by creating a new dataset directory. In this tutorial let's create a
directory named `my_sequence/`. Inside `my_sequence/`, images and calibration
data must be arranged in the following way:

```
my_sequence
├── config
│   ├── distortion_00.xml
│   ├── distortion_01.xml
│   ├── intrinsics_00.xml
│   ├── intrinsics_01.xml
│   ├── matcher_config.txt
│   ├── stereo_config.txt
├── output
└── input
    ├── cam0
    │   ├── 000000_0000000000000_01.tif
    │   ├── 000001_0000000000199_01.tif
    │   ├── 000002_0000000000399_01.tif
    │   ├── 000003_0000000000599_01.tif
     ...
    ├── cam1
    │   ├── 000000_0000000000000_02.tif
    │   ├── 000001_0000000000199_02.tif
    │   ├── 000002_0000000000399_02.tif
    │   ├── 000003_0000000000599_02.tif
    ...
```

## Run WASS pipeline

**Note 1:** You can skip this step if WASS is executed via Matlab script.

**Note 2:** If needed, activate the "wass environment" with `$ conda activate wass`.

cd into the `my_sequence/` directory, and execute the WASS pipeline with the
`wasscli` tool:


```
$ wasscli


 WASS-cli v. 0.1.4
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
Copyright (C) Filippo Bergamasco 2022


Searching for WASS pipeline executables...OK
Current directory is: .../my_sequence 
? What do you want to do?  (Use arrow keys)
 ❯ Prepare
   Match
   Autocalibrate
   Stereo
   ---------------
   Set number of parallel workers
   Quit

```

Select `Prepare`, then `Match` and `Autocalibrate`. Then, select `Stereo` and
reconstruct just the first stereo pair for testing. Check the
`my_sequence/output/000000_wd` directory if the output looks good, then
select `Stereo` again to process the whole sequence.


## Configure for gridding

1. Create a directory named `gridding/` inside the `my_sequence/` directory:

```
$ mkdir gridding
```

2. Generate a default grid config file:

```
wassgridsurface --action generategridconfig . gridding
```

3. Open the newly generated file `my_sequence/gridding/gridconfig.txt`. It
   should contain something like:
   
```
[Area]
area_center_x=0.0
area_center_y=-35.0
area_size=50
N=1024
```

`area_center_x` and `area_center_y` controls the grid location (in meters).
`area_size` controls the area extent. `N` controls the grid resolution. For
example, `N=1024` means that a `1024x1024` grid will be created.

**Note:** You must set `N=256` if you plan to use WASSfast to reconstruct a sequence.

4. Setup the reconstruction grid by running the following command:

```
wassgridsurface --action setup ./output ./gridding --gridconfig ./gridding/gridconfig.txt --baseline [CAMERA_BASELINE]
```

Where `[CAMERA_BASELINE]` must be replaced with the camera baseline in meters. 

5. Open the file `my_sequence/gridding/area_grid.png` to check if the grid
   location and size is correct. If not, repeat steps 3, 4 and 5 until satisfied.


## Grid the point clouds 

Skip this step if you want to use WASSfast only. Otherwise, run

```
wassgridsurface --action grid --gridsetup ./gridding/config.mat ./output ./gridding
```

to grid the point clouds. The resulting NetCDF file is placed in
`my_sequence/gridding/gridded.nc`.


## Running WASSfast

1. Activate the `wassfast_cnn` environment:

```
conda activate wassfast_cnn
```

2. cd into the WASSfast root directory and run:

```
alias wassfast="python `pwd`/wassfast/wassfast.py"
```

3. In **the same shell**, cd into `my_sequence/gridding/` directory


4. Create a file named `settings.cfg` into `my_sequence/gridding` directory and
   paste the following:

```
[ImgProc]
use_clahe=yes
I0_cliplimit=1.0
I0_gridsize=8
I1_cliplimit=1.0
I1_gridsize=8

[SparseMatcher]
quality_level=0.001
max_corners=100000
min_distance=6
block_size=9

[Flow]
method=PyrLK
#method=Fnbk
winsize=15
fb_threshold=0.6
maxlevel=3

[SpecFit]
mit=1500
stol=1E-9
alpha=16.0
final_smooth_sigma=0.37

[PointsReducer]
max_pt_distance=0.0055
winsize=7

[Visual]
plot_surfaces=no
```

5. Run WASSfast by executing the following command:

```
wassfast ./input ./gridding/config.mat ./config ./gridding/settings.cfg AUTO CNN --batchsize 16 -r [FPS] -o ./gridding/wassfast_output.nc --debug_stats
```

where `[FPS]` must be replaced with camera framerate (in Hz). Output NetCDF
file will be saved in `my_sequence/gridding/wassfast_output.nc`


## Plot the reconstructed surface on top of the original images

1. Activate the `wass` environment:

```
conda activate wass
```

2. cd into `my_sequence/` and create a new directory where the rendered frames
   will be placed:

```
mkdir frames
```

3. Run wassncplot:

```
wassncplot ./gridding/wassfast_output.nc ./frames
```

Resulting images are saved in `my_sequence/frames`. To create an mp4 video
instead, add the following options:

```
wassncplot ./gridding/wassfast_output.nc ./frames --ffmpeg --ffmpeg-delete-frames
```

For a full list of wassncplot program options, run:

```
wassncplot --help
```

