
from netCDF4 import Dataset
import numpy as np
import scipy.io as sio
import cv2 as cv
from WaveFieldVisualize.waveview2_synth import WaveView
from tqdm import tqdm
import sys
import os
import argparse
import glob
import scipy.io
import h5py




if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("ncfile", help="Input NetCDF4 file")
    parser.add_argument("hdf5file", help="Input HDF5 file")
    parser.add_argument("out", help="Where to store the produced images")
    parser.add_argument("-f", "--first_index", default=0, type=int, help="First data index to process")
    parser.add_argument("-l", "--last_index", default=-1, type=int, help="Last data index to process (-1 to process all the frames)")
    parser.add_argument("-s", "--step_index", default=1, type=int, help="Sequence step")
    parser.add_argument("-sd", "--step_data_index", default=1, type=int, help="Sequence data step")
    parser.add_argument("--cam", default=0, type=int, help="Camera to use (0 or 1)")
    parser.add_argument("-b", "--baseline", type=float, help="Baseline of the stereo system (use this option to override the baseline value stored in the netcdf file)")
    parser.add_argument("--zmin", type=float, help="Minimum 3D point elevation (used for colorbar limits)")
    parser.add_argument("--zmax", type=float, help="Maximum 3D point elevation (used for colorbar limits)")
    parser.add_argument("--alpha", default=0.5, type=float, help="Surface transparency [0..1]")
    parser.add_argument("--pxscale", default=1.0, type=float, help="Desktop pixel scale (set to 0.5 if using OSX with retina display)")
    parser.add_argument("--wireframe", dest="wireframe", action="store_true", help="Render surface in wireframe")
    parser.add_argument("--no-wireframe", dest="wireframe", action="store_false", help="Render shaded surface")
    parser.set_defaults(wireframe=True)
    args = parser.parse_args()

    outdir = args.out

    if not os.path.isdir( outdir ):
        print("Output dir does not exist")
        sys.exit( -1 )
    else:
        print("Output renderings and data will be saved in: ", outdir)


    print("Opening netcdf file ", args.ncfile)
    rootgrp = Dataset( args.ncfile, mode="r")

    if args.baseline != None:
        stereo_baseline = args.baseline
    else:
        print("Loading baseline from netcdf")
        stereo_baseline = rootgrp["scale"][0]

    print("Stereo baseline: ",stereo_baseline, " (use -b option to change)")
    XX = np.array( rootgrp["X_grid"] )/1000.0
    YY = np.array( rootgrp["Y_grid"] )/1000.0
    ZZ = rootgrp["Z"]
    P0plane = np.array( rootgrp["meta"]["P0plane"] )
    P1plane = np.array( rootgrp["meta"]["P1plane"] )
    nframes = ZZ.shape[0]

    Iw, Ih = rootgrp["meta"].image_width, rootgrp["meta"].image_height

    if args.zmin is None:
        try:
            args.zmin = rootgrp["meta"].zmin
        except:
            print("zmin not specified from command line and not found in NC file, aborting.")
            sys.exit(-1)
    
    if args.last_index > 0:
        nframes = args.last_index

    waveview = None

    f = h5py.File(args.hdf5file, 'r')
    ZZ = f["/0000/data"]
    print("Synthetic dataset shape: ", ZZ.shape )

    print("Rendering synthetic data...")
    pbar = tqdm( range(args.first_index, nframes, args.step_index), file=sys.stdout, unit="frames" )

    data_idx = args.first_index
    I0 = cv.imdecode( rootgrp["cam0images"][0], cv.IMREAD_GRAYSCALE )*0

    for image_idx in pbar:


        if waveview is None:
            waveview = WaveView( title="Wave field",width=Iw,height=Ih, pixel_scale=args.pxscale )
            waveview.setup_field( XX, YY, P0plane.T if args.cam == 0 else P1plane.T )
            waveview.set_zrange( -1, 1, 1 )

        ZZ_data = ZZ[image_idx,:,:] #np.squeeze( np.array( ZZ[0,:,:] ) )/1000.0 - zmean

        img, img_xyz = waveview.render( I0, ZZ_data )

        img = (img*255).astype( np.uint8 )
        img = cv.cvtColor( img, cv.COLOR_RGB2GRAY )
        cv.imwrite('%s/%08d.tif'%(outdir,image_idx), img )

        data_idx += args.step_data_index

    print("Synthetic images saved to ", outdir )
