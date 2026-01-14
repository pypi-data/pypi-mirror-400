import cv2 as cv
import numpy as np
import scipy.io as sio
import configparser
import argparse
import time
import os
import sys
import csv
import asyncio
import json

from tqdm import trange, tqdm

from types import SimpleNamespace
from .netcdfoutput import NetCDFOutput
from .cvproc.utils import load_ocv_matrix, debug_features, debug_featuresP, debug_area
from .cvproc.camseahomography import Cam2SeaH
from .cvproc.sparsematcher import SparseMatcher
from .cvproc.rawreader import RawReader
from .cvproc.dirreader import DirReader
from .cvproc.spectrum import compute_mask
from .cvproc.spectrum import elevation_to_spectrum
from .cvproc.spectrum import spectrum_to_elevation
from .cvproc.spectrum import spectrum_expand
from .cvproc.spectrum import compute_phase_diff
from .cvproc.spectrum import XDIR, YDIR
from .cvproc.Bicubicdemosaicer import BicubicDemosaicer
from .cvproc.HDF5Appender import HDF5Appender
from .specfit.gausswin import gausswin_m

from scipy.interpolate import griddata
from .analysis.analysis import NetCDFAnalysis

import tensorflow as tf
tf.get_logger().setLevel('ERROR')

from .cnn.wavenet_models import create_model_with_prediction
from .cnn.sparsecnn_with_prediction_model import compute_phase_diff_matrix

import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt



version = "1.6.3"




class SimpleLogger():
    def __init__(self, logfile = None):
        if logfile is None:
            logfiledir, _  = os.path.split(__file__)
            logfile = os.path.join(logfiledir, "../log.txt" )

        self.stdout = sys.stdout
        self.log = open(logfile, 'w')

    def write(self, text):
        self.stdout.write(text)
        self.log.write(text)
        self.log.flush()

    def close(self):
        self.stdout.close()
        self.log.close()

    def flush(self):
        self.log.flush()


status = {}


async def reset_status():
    global status
    status = { "code":0, "status":"Ready", "progress":0, "stats":{}, "datain":"", "dataout":"", "debugdir":"", "outdir":"" }


async def handle_status_request( reader, writer ):
    global status
    writer.write( json.dumps(status).encode("ascii") )
    await writer.drain()
    writer.close()

def initialize_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("imgdata", help="Stereo sequence directory (in WASS format) or data file in raw format")
    parser.add_argument("configfile", help="Stereo sequence configuration file")
    parser.add_argument("calibdir", help="Calibration dir for the given stereo image data")
    parser.add_argument("settingsfile", help="Settings file")
    parser.add_argument("wavedirection", help="Waves direction as appears on the images. Possible values: LRTB  RLTB  LRBT  RLBT  AUTO  NONE  (where L/R/T/B = Left/Right/Top/Bottom)")
    parser.add_argument("processingmode", help="Method to use. Select 'CNN' or 'PU'")
    parser.add_argument("--generate_settings", action="store_true", help="Generate a default settings file and exit" )
    parser.add_argument("--analyse", action="store_true", help="Analyse an existing NetCDF file and exit" )
    parser.add_argument("--continuous_mode", action="store_true", help="imgdata is considered as a directory containing raw files. WASSfast will continuously process files in that directory until stopped." )
    parser.add_argument("--kafka_mode", action="store_true", help="imgdata is introduced by an apache kafka stream. WASSfast will continuously process files in that directory until stopped." )
    parser.add_argument("--debug_mode", action="store_true", help="Save debug images at various steps of the algorithm (may slow down the process)" )
    parser.add_argument("--debug_stats", action="store_true", help="Save debug statistics during the processing" )
    parser.add_argument("--batchsize", type=int, default=32, help="CNN processing batch size" )
    parser.add_argument("--start_from_plane", action="store_true", help="Start processing assuming a planar surface" )
    parser.add_argument("--demosaic", action="store_true", help="Demosaic PFA camera data before processing" )
    parser.add_argument("--save_polarization", action="store_true", help="Save DOLP and AOLP in an HDF5 file for further processing (only if --demosaic is set)" )
    parser.add_argument("--current_u", type=float, default=0.0, help="Surface current horizontal compontent (m/s)" )
    parser.add_argument("--current_v", type=float, default=0.0, help="Surface current vertical compontent (m/s)" )
    parser.add_argument("--depth", type=str, default="inf", help="Sea depth (m)" )
    parser.add_argument("-dd", "--debugdir", type=str, help="Directory to store the debug images")
    parser.add_argument("-s", "--plot_surfaces", action="store_true", help="Plot resulting surfaces (may slow-down the processing)" )
    parser.add_argument("--nographics", action="store_true", help="Disable all renderings" )
    parser.add_argument("-n", "--nframes", default=-1, type=int, help="Number of stereo frames to process, -1 to process all frames")
    parser.add_argument("--first_frame", default=0, type=int, help="First frame to process")
    parser.add_argument("-r", "--framerate", type=float, help="Image frame rate override (in Hz)")
    parser.add_argument("--nfft", dest="nfft", action="store_true", help="Use NFFT for surface reconstruction")
    parser.add_argument("--fft", dest="nfft", action="store_false", help="Use FFT with bilinear interpolation for surface reconstruction")
    parser.add_argument("--upload_url", type=str, help="URL to upload the NetCDF report")
    parser.add_argument("--location", type=str, help="Acquired data location name")
    parser.add_argument("--savepts", dest="savepts", action="store_true", help="Save the sparse triangulated points for each frame. Be sure to also specify the --debugdir argument")
    parser.add_argument("--saveCNNinput", dest="saveCNNinput", action="store_true", help="Save the CNN (sparse) input data inside the NetCDF file.")
    parser.add_argument("-o", "--output", type=str, help="Output netCDF file")
    args = parser.parse_args()
    return args


def initialize_config(data, CALIBDIR):
    config = SimpleNamespace()
    config.limits = SimpleNamespace()
    config.cam = SimpleNamespace()
    config.limits.xmin = data["xmin"].item(0)
    config.limits.xmax = data["xmax"].item(0)
    config.limits.ymin = data["ymin"].item(0)
    config.limits.ymax = data["ymax"].item(0)
    config.limits.zmin = data["zmin"].item(0)
    config.limits.zmax = data["zmax"].item(0)
    config.KX_ab = data["KX_ab"]
    config.KY_ab = data["KY_ab"]
    config.baseline = data["CAM_BASELINE"].item(0)
    config.N = data["N"].item()
    print(" ==========  Reconstruction settings ==========")
    print("  Grid size: %dx%d"%(config.N,config.N) )
    print("    x range: %3.1f ... %3.1f"%(config.limits.xmin,config.limits.xmax) )
    print("    y range: %3.1f ... %3.1f"%(config.limits.ymin,config.limits.ymax) )
    print("    z range: %3.3f ... %3.1f"%(config.limits.zmin,config.limits.zmax) )
    print(" ==============================================")
    if np.abs(config.limits.zmax - config.limits.zmin)>1E-5:
        print( "WARNING: zmin-zmax range is not centered on 0." )
    print("Loading camera calibration from %s"%CALIBDIR)
    config.cam.dist_00 = load_ocv_matrix( "%s/distortion_00.xml"%(CALIBDIR) )
    config.cam.dist_01 = load_ocv_matrix( "%s/distortion_01.xml"%(CALIBDIR) )
    config.cam.intr_00 = load_ocv_matrix( "%s/intrinsics_00.xml"%(CALIBDIR) )
    config.cam.intr_01 = load_ocv_matrix( "%s/intrinsics_01.xml"%(CALIBDIR) )
    config.cam.P0cam = data["P0cam"]
    config.cam.P1cam = data["P1cam"]
    config.cam.Rpl = data["Rpl"]
    config.cam.Tpl = data["Tpl"]
    config.cam.P0plane = data["P0plane"]
    try:
        config.cam.P1plane = data["P1plane"]
    except KeyError as k:
        config.cam.P1plane = config.cam.P0plane * 0
        print("P1plane not found in config file, skipping")
    config.cam.c2sH_cam0 = Cam2SeaH( config.limits.xmin,
                                     config.limits.xmax,
                                     config.limits.ymin,
                                     config.limits.ymax,
                                     config.cam.Rpl,
                                     config.cam.Tpl,
                                     config.cam.P0cam,
                                     data["scale"],
                                     OUT_SIZE=1200 )
    config.cam.c2sH_cam1 = Cam2SeaH( config.limits.xmin,
                                     config.limits.xmax,
                                     config.limits.ymin,
                                     config.limits.ymax,
                                     config.cam.Rpl,
                                     config.cam.Tpl,
                                     config.cam.P1cam,
                                     data["scale"],
                                     OUT_SIZE=1200 )
    return config



def intialize_processors(nograph, args, config, settings):
    processors = SimpleNamespace()
    processors.waveview = None
    '''
    if not nograph:
        from waveview import WaveView
        processors.waveview = WaveView( title="WASSfast wave field")
    '''
    processors.sp = None
    processors.matcher = SparseMatcher( quality_level=settings.get("SparseMatcher","quality_level"),
                                        max_corners=settings.get("SparseMatcher","max_corners"),
                                        min_distance=settings.get("SparseMatcher","min_distance"),
                                        block_size=settings.get("SparseMatcher","block_size") )
    # Initialize image processing tools
    # moving to estimate_scattered_point_cloud to overcome pickling errors

    processors.clahe1 = None
    processors.clahe2 = None

    specfit_use_nfft = args.nfft

    if args.processingmode=="PU":
        if tf.__version__ > "1.14.0":
            print(" Error: PU mode not supported in this environment. Try CNN mode instead.")
            sys.exit(-1)

        if specfit_use_nfft:
            from .specfit.specfit_nfft import SpecfitNFFT
            processors.sp = SpecfitNFFT(config.N, alpha=settings.getfloat("SpecFit","alpha") )
        else:
            from .specfit.specfit_fft import SpecfitFFT
            processors.sp = SpecfitFFT(config.N, alpha=settings.getfloat("SpecFit","alpha") )

    return processors



def initialize_seqargs(args):
    sequence_args = SimpleNamespace()
    sequence_args.debug_mode = args.debug_mode
    sequence_args.savepts = args.savepts
    sequence_args.saveCNNinput = args.saveCNNinput
    sequence_args.nographics = args.nographics
    sequence_args.plot_surfaces = args.plot_surfaces
    sequence_args.start_from_plane = args.start_from_plane
    sequence_args.demosaic = args.demosaic
    sequence_args.save_polarization = args.save_polarization
    sequence_args.current_u = args.current_u
    sequence_args.current_v = args.current_v
    sequence_args.depth = float(args.depth) if args.depth!="inf" else np.inf
    sequence_args.processingmode = args.processingmode
    sequence_args.batchsize = args.batchsize
    return sequence_args


def create_mask( I0, I1, config ):
    cam0mask = config.cam.c2sH_cam0.warp(np.ones_like(I0))
    cam1mask = config.cam.c2sH_cam1.warp(np.ones_like(I1))
    # Set 1px border on image boundary
    cam0mask[0,:]=0 ; cam0mask[-1,:]=0 ; cam0mask[:,0]=0 ; cam0mask[:,-1]=0
    cam1mask[0,:]=0 ; cam1mask[-1,:]=0 ; cam1mask[:,0]=0 ; cam1mask[:,-1]=0

    cam0mask = cv.erode( cam0mask, np.ones((7,7)))
    cam1mask = cv.erode( cam1mask, np.ones((7,7)))
    return cam0mask, cam1mask



def create_csv_for_debug( statsfile ):
    fcsv = None
    wcsv = None
    if not statsfile is None:
        fcsv = open( statsfile, mode='w')
        fieldnames = ['frame', 'match_time', 'total_time', 'num_matches', 'num_filtered_matches', 'opt_time', 'opt_nit' ]
        wcsv = csv.DictWriter(fcsv, fieldnames=fieldnames)
        wcsv.writeheader()

    return fcsv, wcsv



def wavedir_string_to_shift( wp ):
    _xd = XDIR.NONE
    _yd = YDIR.NONE

    if wp == "LRTB":
        _xd = XDIR.LEFT_TO_RIGHT
        _yd = YDIR.TOP_TO_BOTTOM
    elif wp == "RLTB":
        _xd = XDIR.RIGHT_TO_LEFT
        _yd = YDIR.TOP_TO_BOTTOM
    elif wp == "LRBT":
        _xd = XDIR.LEFT_TO_RIGHT
        _yd = YDIR.BOTTOM_TO_TOP
    elif wp == "RLBT":
        _xd = XDIR.RIGHT_TO_LEFT
        _yd = YDIR.BOTTOM_TO_TOP
    elif wp == "AUTO" or wp == "NONE":
        _xd = XDIR.NONE
        _yd = YDIR.NONE
        pass
    else:
        return 0,0,False

    return _xd,_yd,True


def estimate_scattered_point_cloud( I0, I1, cam0mask, cam1mask, wp, _xd, _yd, I0p_first, config, processors, debug_mode, DEBUGDIR, settings, idx=0, savepts=False ):
    logstring = ""
    _xdydchanged = False
    I0 = cv.undistort(I0, config.cam.intr_00, config.cam.dist_00 )
    I1 = cv.undistort(I1, config.cam.intr_01, config.cam.dist_01 )

    if cam0mask is None:
        cam0mask, cam1mask = create_mask(I0,I1,config)

    I0p = config.cam.c2sH_cam0.warp( I0 )
    I1p = config.cam.c2sH_cam1.warp( I1 )

    if settings.getboolean("ImgProc","use_clahe"):
        processors.clahe1 = cv.createCLAHE(clipLimit=settings.getfloat("ImgProc","I0_cliplimit"),
                                           tileGridSize=(settings.getint("ImgProc","I0_gridsize"),
                                           settings.getint("ImgProc","I0_gridsize")) )
        processors.clahe2 = cv.createCLAHE(clipLimit=settings.getfloat("ImgProc","I1_cliplimit"),
                                           tileGridSize=(settings.getint("ImgProc","I1_gridsize"),
                                           settings.getint("ImgProc","I1_gridsize")))
        I0p = processors.clahe1.apply(I0p)
        I1p = processors.clahe2.apply(I1p)

    processors.clahe1 = None
    processors.clahe2 = None

    if debug_mode:
        cv.imwrite("%s/%06d_cam0P.jpg"%(DEBUGDIR,idx), I0p)
        cv.imwrite("%s/%06d_cam1P.jpg"%(DEBUGDIR,idx), I1p)
        cv.imwrite("%s/cam0mask.jpg"%DEBUGDIR, cam0mask*255)
        cv.imwrite("%s/cam1mask.jpg"%DEBUGDIR, cam1mask*255)


    processors.matcher.extract_features( I0p,
                                         I1p,
                                         cam0mask,
                                         cam1mask,
                                         fb_threshold = settings.getfloat("Flow","fb_threshold"),
                                         winsize=(settings.getint("Flow","winsize"),
                                         settings.getint("Flow","winsize") ),
                                         maxlevel=settings.getint("Flow","maxlevel"),
                                         optflo_method=settings.get("Flow","method") )

    if processors.matcher.features_0P is None  or processors.matcher.features_1P is None or processors.matcher.features_0P.size < 10 or processors.matcher.features_1P.size < 10:
        return np.zeros( (3,0) ), cam0mask, cam1mask, wp, _xd, _yd, I0p_first, _xdydchanged

    if debug_mode:
        debug_featuresP(processors.matcher,I0p,I1p,outdir=DEBUGDIR,image_idx=idx)

    features_0 = config.cam.c2sH_cam0.transform( processors.matcher.features_0P.T, inverse=True )
    features_1 = config.cam.c2sH_cam1.transform( processors.matcher.features_1P.T, inverse=True )


    if debug_mode:
        debug_area(I0,I1,I0p.shape,config.cam.c2sH_cam0,config.cam.c2sH_cam1,outdir=DEBUGDIR)
        debug_features(I0,I1,features_0,features_1,outdir=DEBUGDIR)

    # --- Automatic wave prediction direction estimation

    if wp=="AUTO" and _xd==XDIR.NONE and _yd==YDIR.NONE:
        # We need to set wave prediction direction

        if I0p_first is None:
            # Just save this image for further processing
            I0p_first = I0p
        else:
            # Try to match I0p with I0p_first
            processors.matcher.extract_features( I0p_first,
                                                    I0p,
                                                    cam0mask,
                                                    cam0mask,
                                                    fb_threshold = settings.getfloat("Flow","fb_threshold"),
                                                    winsize=(settings.getint("Flow","winsize"),
                                                    settings.getint("Flow","winsize") ),
                                                    maxlevel=settings.getint("Flow","maxlevel"),
                                                    optflo_method=settings.get("Flow","method") )

            avgdir = np.mean( processors.matcher.features_1P.T - processors.matcher.features_0P.T, axis=1 )
            _xd = np.sign( avgdir )[0]
            _yd = np.sign( avgdir )[1]
            _xdydchanged = True

            logstring += " Detected wave direction: \n"
            logstring += "   Left to right" if _xd == XDIR.LEFT_TO_RIGHT else "  Right to left" 
            logstring += "   Top to bottom" if _yd == YDIR.TOP_TO_BOTTOM else "  Bottom to top"
            logstring += "\n"

            if debug_mode:
                debug_featuresP(processors.matcher,I0p_first,I0p,outdir=DEBUGDIR,cam0name="direst_cam0_first", cam1name="direst_cam0_second")

            I0p_first = None

    # --- End of automatic wave prediction direction estimation

    p3d = cv.triangulatePoints( config.cam.P0cam, config.cam.P1cam, features_0, features_1 )
    p3d = p3d[0:3,:] / p3d[3,:]

    p3dN = np.matmul( config.cam.Rpl, p3d ) + config.cam.Tpl
    p3dN = p3dN * np.array( [ [config.baseline], [config.baseline], [-config.baseline]]  )

    logstring += "  Point cloud size:\n"
    logstring += "   - after sparse matching: %d\n"%(p3dN.shape[1])

    quantile_level = settings.getfloat("Filtering","outliers_quantile")

    if quantile_level>0.0 and quantile_level<=1.0:
        abselevations = np.abs(p3dN[2,:])
        zquant = np.quantile(abselevations, quantile_level )
        good_pts = abselevations < zquant
        p3dN = p3dN[:, good_pts]
        logstring += "   - after z filtering (outliers_quantile=%1.4f): %d\n"%(quantile_level,p3dN.shape[1])
    else:
        logstring += "   - No z filtering applied.\n"

    if debug_mode:
        plt.scatter( p3dN[0,:], p3dN[1,:], s=1, c=p3dN[2,:], vmin=config.limits.zmin, vmax=config.limits.zmax )
        plt.axis('equal')
        plt.grid()
        plt.savefig('%s/%06d_scatter.png'%(DEBUGDIR,idx) )
        plt.close()

    if savepts and os.path.isdir( DEBUGDIR):
        np.savetxt( '%s/%06d_point_cloud.txt'%(DEBUGDIR,idx), p3dN[:3,:].T )

    return p3dN, cam0mask, cam1mask, wp, _xd, _yd, I0p_first, _xdydchanged, logstring





###############################################################
# Sequence processing loops
###############################################################

async def process_sequence( dataReader, outdata, config, statsfile, first_frame_index, nframes, framerate, DEBUGDIR, args, settings, wavedirection, processors ):
    """ The main process sequence dispatcher
    """

    global plt

    # Create DEBUGDIR if needed
    if not os.path.exists( DEBUGDIR ):
        os.makedirs( DEBUGDIR )

    # Initialize matplotlib (if needed)
    if args.debug_mode or args.plot_surfaces:
        import matplotlib
        matplotlib.use('AGG')
        import matplotlib.pyplot as plt


    if args.processingmode == "PU":

        print("Using the prediction/update processing mode")
        from .PointsReducer import PointsReducer
        processors.points_reducer = PointsReducer.PointsReducer()
        return await process_sequence_predictupdate( dataReader, outdata, config, statsfile, first_frame_index, nframes, framerate, DEBUGDIR, args, settings, wavedirection, processors )

    elif args.processingmode == "CNN":

        print("Using the CNN processing mode")
        return await process_sequence_CNN( dataReader, outdata, config, statsfile, first_frame_index, nframes, framerate, DEBUGDIR, args, settings, wavedirection, processors )

    else:
        print("Invalid processing mode: "%args.processingmode )
        return False


def process_frame(q, timestamps, images, zz_mdct):

    pass_num, config, processors, args, hdf5_filename, cam0mask, cam1mask, loc_status, dataReader, DEBUGDIR, settings, wp = q.get()
    FRAME_IDX, FIRST_FRAME, LAST_FRAME, BATCH_SIZE, framerate, dt, in_batch_idx, I0p_first, scalefacx, scalefacy, _xd, _yd = pass_num

    start_time = time.time()
    stats = {"frame": FRAME_IDX}

    logstr = "\n"
    logstr += "----- Processing stereo frame %d\n"%FRAME_IDX
    (fn,timestamp,I0) = dataReader.read_frame( FRAME_IDX*2 )
    logstr += "  %s\n"%fn
    (fn,timestamp,I1) = dataReader.read_frame( FRAME_IDX*2+1 )
    logstr += "  %s\n"%fn

    demosaicer = None
    polarization_data = None

    if args.demosaic:
        demosaicer = BicubicDemosaicer()

        if args.save_polarization:
            hdf5_file = hdf5_filename
            polarization_data = HDF5Appender( hdf5_file )

    if not demosaicer is None:
        logstr += "Demosaicing PFA data...\n"
        S0_0, DOLP0, AOLP0 = demosaicer.demosaic( I0 )
        S0_1, DOLP1, AOLP1 = demosaicer.demosaic( I1 )
        I0 = np.clip(S0_0*128,0,255).astype(np.uint8)
        I1 = np.clip(S0_1*128,0,255).astype(np.uint8)

        if not polarization_data is None:
            if not polarization_data.has_dataset("DOLP_Cam0"):
                polarization_data.add_dataset("DOLP_Cam0", DOLP0.shape, dtype=np.float32, chunk_size=BATCH_SIZE )
                polarization_data.add_dataset("DOLP_Cam1", DOLP1.shape, dtype=np.float32, chunk_size=BATCH_SIZE )
            if not polarization_data.has_dataset("AOLP_Cam0"):
                polarization_data.add_dataset("AOLP_Cam0", AOLP0.shape, dtype=np.float32, chunk_size=BATCH_SIZE )
                polarization_data.add_dataset("AOLP_Cam1", AOLP1.shape, dtype=np.float32, chunk_size=BATCH_SIZE )
            if not polarization_data.has_dataset("S0_Cam0"):
                polarization_data.add_dataset("S0_Cam0", S0_0.shape, dtype=np.float32, chunk_size=BATCH_SIZE )
                polarization_data.add_dataset("S0_Cam1", S0_1.shape, dtype=np.float32, chunk_size=BATCH_SIZE )

            polarization_data.append("DOLP_Cam0", DOLP0)
            polarization_data.append("DOLP_Cam1", DOLP1)
            polarization_data.append("AOLP_Cam0", AOLP0)
            polarization_data.append("AOLP_Cam1", AOLP1)
            polarization_data.append("S0_Cam0", S0_0)
            polarization_data.append("S0_Cam1", S0_1)

    if not framerate is None:
        timestamp = float(FRAME_IDX-FIRST_FRAME)/float(framerate)

    timestamps[in_batch_idx] = timestamp

    if args.debug_mode:
        aux = np.concatenate( [I0,I1], axis=1 )
        aux = cv.pyrDown(aux)
        cv.imwrite('%s/sidebyside_%08d.png'%(DEBUGDIR,FRAME_IDX), aux )

    images[in_batch_idx] = I0

    logstr += "  time: %5.1f secs\n"%(timestamp)

    p3dN, cam0mask, cam1mask, wp, _xd, _yd, I0p_first, xdydchanged, locallogstring = estimate_scattered_point_cloud( I0, I1, cam0mask, cam1mask, wp, _xd, _yd, I0p_first, config, processors, args.debug_mode, DEBUGDIR, settings, idx=FRAME_IDX, savepts=args.savepts )

    logstr += locallogstring
    stats["match_time"]=(time.time()-start_time)
    stats["num_matches"]=p3dN.shape[1]

    # discretize p3dN into a regular grid
    p3dN = p3dN[:, np.random.permutation(p3dN.shape[1]) ]  # shuffle points to avoid aliasing when discretizing
    pts_x = np.floor( (p3dN[0,:]-config.limits.xmin)/scalefacx * (config.N-1) + 0.5 ).astype(np.uint32).flatten()
    pts_y = np.floor( (p3dN[1,:]-config.limits.ymin)/scalefacy * (config.N-1) + 0.5 ).astype(np.uint32).flatten()
    good_pts = np.logical_and( np.logical_and( pts_x >= 0 , pts_x < config.N ),
                                np.logical_and( pts_y >= 0 , pts_y < config.N ) )

    ZZ = np.ones( (config.N, config.N), dtype=np.float32 )*np.nan
    pts_x = pts_x[good_pts]
    pts_y = pts_y[good_pts]
    pts_z = p3dN[2,good_pts]

    ZZ[ pts_y, pts_x ] = pts_z

    num_samples = (ZZ.size - np.sum( np.isnan( ZZ ).astype(np.uint8) )).astype(float)
    logstr += "   %d / %d valid samples (density=%1.3f) "%(num_samples,ZZ.size,(num_samples/ZZ.size)) 

    progress = int( (FRAME_IDX-FIRST_FRAME)*100/(LAST_FRAME-FIRST_FRAME) )

    loc_status[progress] = {}
    tmp = loc_status[progress]
    tmp["frame"] = stats["frame"]
    tmp["match_time"] = stats["match_time"]
    tmp["num_matches"]= stats["num_matches"]
    loc_status[progress] = tmp

    zz_mdct[in_batch_idx] = ZZ
    tqdm.write(logstr)
    q.task_done()



async def process_sequence_CNN( dataReader, outdata, config, statsfile, first_frame_index, nframes, framerate, DEBUGDIR, args, settings, wavedirection, processors ):
    """ WASSfast processing loop based on CNN
    """

    if args.debug_mode:
        print("Debug mode: ",args.debug_mode)

    print("Tensorflow GPU devices: ")
    print(tf.config.list_physical_devices('GPU'))
    if len(tf.config.list_physical_devices('GPU'))==0:
        print("Performance Warning: Tensorflow is running on CPU!")

    wassfast_base_path, _ = os.path.split(__file__)

    BATCH_SIZE = args.batchsize
    mask = None
    cam0mask = None
    cam1mask = None
    I0p_first = None
    ph_diff_mat = None
    Zmean = 0.0
    Zmin = np.inf
    Zmax = -np.inf
    Zp2_mean = 0.0
    Zp98_mean = 0.0
    N_frames = 1

    #if config.N != 256:
    #    print("ERROR: CNN processing supports only 256x256 grids, aborting.")
    #    return False

    _zc = int(config.N/2)
    _zss = int(config.N/4)

    [XX,YY] = np.meshgrid( np.linspace(config.limits.xmin, config.limits.xmax, config.N ), np.linspace( config.limits.ymin, config.limits.ymax, config.N) )
    outdata.set_grids( XX*1000, YY*1000 )

    # Initialize wave prediction
    wp = wavedirection
    _xd, _yd, retval = wavedir_string_to_shift( wp )
    if not retval:
        print("Invalid wave direction: %s", wp )
        return False

    outdata.add_meta_attribute("wassfast_mode", "CNN" )
    outdata.add_meta_attribute("input_wave_direction_x", _xd )
    outdata.add_meta_attribute("input_wave_direction_y", _yd )

    # Select frame range
    FIRST_FRAME = first_frame_index
    LAST_FRAME = dataReader.n_frames - 1
    if nframes != None and nframes>0:
        LAST_FRAME = FIRST_FRAME + nframes

    # if there are more frames than the batch size
    if LAST_FRAME > BATCH_SIZE:
        # batchnum is the number of complete batches
        batchnum = LAST_FRAME//BATCH_SIZE
        # rem is the number of images in the last/partial batch, if any
        rem = LAST_FRAME%BATCH_SIZE
        # if there needs to be an extra partial batch
        if rem != 0:
            # add a partial batch
            batchnum += 1
    # if the batch size is greater than the number of frames
    elif LAST_FRAME < BATCH_SIZE:
        # only one batch, and it is partial
        batchnum = 1
        rem = LAST_FRAME
    else:
        batchnum = 1
        rem = 0

    print("         First frame: ", FIRST_FRAME)
    print("          Last frame: ", LAST_FRAME)
    print("          Batch size: ", BATCH_SIZE)
    print("   Number of batches: ", batchnum)
    print("Frames in last batch: ", rem)

    # Create csv file for debug statistics
    fcsv, wcsv = create_csv_for_debug( statsfile )

    status["code"] = 1
    status["status"] = "Processing"


    # Load CNN model and weights

    print("Loading CNN model")
    sparsecnn_weights_file = '%s/cnn/modeldata/2021-06-30_16-48-27.h5'%wassfast_base_path
    model = create_model_with_prediction( config.N, sparsecnn_weights=sparsecnn_weights_file )
    print(model.summary())

    # load weights
    print("Loading weights...")
    model.load_weights('%s/cnn/modeldata/2021-07-01_12-00-44_3.h5'%wassfast_base_path )


    # Initialize batch storage
    scatter_data_batch = np.zeros( (BATCH_SIZE, config.N, config.N, 3), dtype=np.float32 )
    timestamps = np.zeros( (BATCH_SIZE), dtype=np.float32 )
    images = np.zeros( (BATCH_SIZE+1), dtype=object )
    in_batch_idx=0
    prev_batch_last_sample = np.zeros( (config.N, config.N), dtype=np.float32 )  # This will hold the last sample of the previous batch, used to populate the
                                                                                 # previous channel of the first sample of the current batch

    scalefacx = (config.limits.xmax-config.limits.xmin)
    scalefacy = (config.limits.ymax-config.limits.ymin)

    demosaicer = None
    polarization_data = None
    hdf5_file = None
    last_timestamp = 0

    if args.demosaic:
        demosaicer = BicubicDemosaicer()

        if args.save_polarization:
            hdf5_file = outdata.get_filename()[:-3] + "_polardata.h5"
            polarization_data = HDF5Appender( hdf5_file )


    # Main loop
    global_start_time = time.time()
    zz_dct = {}

    # PROCESS FRAMES 0 AND 1 FIRST
    ######################################################################################
    print("--------")
    print("Reading frames 0 and 1 first.")
    for i in [0,1]:
        start_time = time.time()
        stats = {"frame": i}
        print("--------")
        print(" Processing stereo frame %d"%i)
        (fn,timestamp,I0) = dataReader.read_frame( i*2 )
        print("  %s"%fn)
        (fn,timestamp,I1) = dataReader.read_frame( i*2+1 )
        print("  %s"%fn)
        outdata.add_meta_attribute("image_width", I0.shape[1] )
        outdata.add_meta_attribute("image_height", I0.shape[0] )

        if not demosaicer is None:
            tqdm.write("Demosaicing PFA data...")
            S0_0, DOLP0, AOLP0 = demosaicer.demosaic( I0 )
            S0_1, DOLP1, AOLP1 = demosaicer.demosaic( I1 )
            I0 = np.clip(S0_0*128,0,255).astype(np.uint8)
            I1 = np.clip(S0_1*128,0,255).astype(np.uint8)

            if not polarization_data is None:
                if not polarization_data.has_dataset("DOLP_Cam0"):
                    polarization_data.add_dataset("DOLP_Cam0", DOLP0.shape, dtype=np.float32, chunk_size=BATCH_SIZE )
                    polarization_data.add_dataset("DOLP_Cam1", DOLP1.shape, dtype=np.float32, chunk_size=BATCH_SIZE )
                if not polarization_data.has_dataset("AOLP_Cam0"):
                    polarization_data.add_dataset("AOLP_Cam0", AOLP0.shape, dtype=np.float32, chunk_size=BATCH_SIZE )
                    polarization_data.add_dataset("AOLP_Cam1", AOLP1.shape, dtype=np.float32, chunk_size=BATCH_SIZE )
                if not polarization_data.has_dataset("S0_Cam0"):
                    polarization_data.add_dataset("S0_Cam0", S0_0.shape, dtype=np.float32, chunk_size=BATCH_SIZE )
                    polarization_data.add_dataset("S0_Cam1", S0_1.shape, dtype=np.float32, chunk_size=BATCH_SIZE )

                polarization_data.append("DOLP_Cam0", DOLP0)
                polarization_data.append("DOLP_Cam1", DOLP1)
                polarization_data.append("AOLP_Cam0", AOLP0)
                polarization_data.append("AOLP_Cam1", AOLP1)
                polarization_data.append("S0_Cam0", S0_0)
                polarization_data.append("S0_Cam1", S0_1)

        if not framerate is None:
            timestamp = float(i-FIRST_FRAME)/float(framerate)
        if i ==0:
            last_timestamp = timestamp
        dt = timestamp-last_timestamp
        if dt>0:
            outdata.add_meta_attribute("fps", (1.0/dt) )
        print("  Time: %5.1f secs, dt: %1.3f (%2.1f Hz)"%(timestamp,dt,1.0/dt if dt>0 else 0) )

        if args.debug_mode:
            aux = np.concatenate( [I0,I1], axis=1 )
            aux = cv.pyrDown(aux)
            cv.imwrite('%s/sidebyside_%08d.png'%(DEBUGDIR,i), aux )

        p3dN, cam0mask, cam1mask, wp, _xd, _yd, I0p_first, xdydchanged, locallogstring = estimate_scattered_point_cloud( I0, I1, cam0mask, cam1mask, wp, _xd, _yd, I0p_first, config, processors, args.debug_mode, DEBUGDIR, settings, idx=i, savepts=args.savepts )

        print(locallogstring)
        outdata.add_meta_attribute("detected_wave_direction_x", _xd )
        outdata.add_meta_attribute("detected_wave_direction_y", _yd )
        stats["match_time"]=(time.time()-start_time)
        stats["num_matches"]=p3dN.shape[1]
        if xdydchanged or (ph_diff_mat is None and dt>0):
            print("Creating phase diff matrix")
            phmatrix = np.expand_dims( compute_phase_diff_matrix( config.KX_ab, config.KY_ab, _xd, _yd, dt), axis=-1)
            phmatrix_conj = np.conj(phmatrix)
            phmatrix_concat = np.concatenate( (np.real(phmatrix), np.imag(phmatrix), np.real(phmatrix_conj), np.imag(phmatrix_conj)), axis=2 )
            ph_diff_mat = np.tile( phmatrix_concat, (BATCH_SIZE, 1, 1, 1) ).astype(np.float32)
            cam0maskbatch = cv.resize( cam0mask, (config.N,config.N), interpolation=cv.INTER_NEAREST ).astype(np.float32)
            cam0maskbatch[cam0maskbatch==0] = np.nan
            cam0maskbatch = np.expand_dims( np.tile( cam0maskbatch, (BATCH_SIZE,1,1) ), axis=-1 )
        p3dN = p3dN[:, np.random.permutation(p3dN.shape[1]) ]  # shuffle points to avoid aliasing when discretizing
        pts_x = np.floor( (p3dN[0,:]-config.limits.xmin)/scalefacx * (config.N-1) + 0.5 ).astype(np.uint32).flatten()
        pts_y = np.floor( (p3dN[1,:]-config.limits.ymin)/scalefacy * (config.N-1) + 0.5 ).astype(np.uint32).flatten()
        good_pts = np.logical_and( np.logical_and( pts_x >= 0 , pts_x < config.N ),
                                np.logical_and( pts_y >= 0 , pts_y < config.N ) )
        ZZ = np.ones( (config.N, config.N), dtype=np.float32 )*np.nan
        pts_x = pts_x[good_pts]
        pts_y = pts_y[good_pts]
        pts_z = p3dN[2,good_pts]
        ZZ[ pts_y, pts_x ] = pts_z
        num_samples = (ZZ.size - np.sum( np.isnan( ZZ ).astype(np.uint8) )).astype(float)
        print("   %d / %d valid samples (density=%1.3f) "%(num_samples,ZZ.size,(num_samples/ZZ.size)) )
        status["progress"] = int( (i-FIRST_FRAME)*100/(LAST_FRAME-FIRST_FRAME) )
        status["stats"] = stats
        in_batch_idx = i
        zz_dct[in_batch_idx] = ZZ
        timestamps[in_batch_idx] = timestamp
        images[in_batch_idx] = I0
        last_timestamp = timestamp

    for k in zz_dct.keys():
        if k>0:
            scatter_data_batch[ k-1, :, :, 2 ] = zz_dct[k]
        scatter_data_batch[ k, :, :, 1 ] = zz_dct[k]
        if k<BATCH_SIZE-1:
            scatter_data_batch[ k+1, :, :, 0 ] = zz_dct[k]

    ########################################################################################
    import multiprocessing as mp

    in_batch_idx = 2
    print("--------")
    print("Loading remaining frames into batches for processing.")

    #p = mp.Pool()
    p = mp.get_context("spawn").Pool()
    m = mp.Manager()
    zz_mdct = m.dict(zz_dct)

    stats_dct = {}
    for jj in ["Zmean", "Zmin", "Zmax", "Zp2_mean", "Zp98_mean"]:
        stats_dct[jj] = []

    for i in range(0, batchnum):
        if i ==0:
            id_start = 2
        else:
            id_start = 0

        if i < batchnum-1:
            btch = BATCH_SIZE
        else:
            btch = rem+1

        q = m.Queue()
        img_dct = {}
        for k in range(len(images)):
            img_dct[k] = images[k]
        loc_status = m.dict()
        timestamp_mlst = m.list(timestamps)
        images_mdct = m.dict(img_dct)

        for j in range(id_start, btch):
            if i == 0:
                FRAME_IDX = j
            else:
                FRAME_IDX = j + (i)*BATCH_SIZE
            in_batch_idx = j
            pass_num = [FRAME_IDX, FIRST_FRAME, LAST_FRAME, btch, framerate, dt, in_batch_idx, I0p_first, scalefacx, scalefacy, _xd, _yd]
            tst_arg = (pass_num, config, processors, args, hdf5_file, cam0mask, cam1mask, loc_status, dataReader, DEBUGDIR, settings, wp)
            q.put(tst_arg)

        if in_batch_idx >= btch-1:
            mod = q.qsize()
            p.starmap(process_frame, ((q, timestamp_mlst, images_mdct, zz_mdct,) for _ in range(mod)))
            #print(timestamp_mlst)
            for i in loc_status.keys():
                status["progress"] = i
                status["stats"] = loc_status[i]
            if i!=0:
                prev_batch_last_sample = scatter_data_batch[ -1,:,:,1]
                scatter_data_batch[ 0, :, :, 1 ] = ZZ
                scatter_data_batch[ 1, :, :, 0 ] = ZZ
                scatter_data_batch[ 0, :, :, 0 ] = prev_batch_last_sample
            for k in zz_mdct.keys():
                if k< btch:
                    scatter_data_batch[ k, :, :, 1 ] = zz_mdct[k]
                if k >0:
                    scatter_data_batch[ k-1, :, :, 2 ] = zz_mdct[k]
                if k<btch-1:
                    scatter_data_batch[ k+1, :, :, 0 ] = zz_mdct[k]
                if k == btch:
                    ZZ = zz_mdct[k]

            scatter_data_batch[scatter_data_batch==0] = np.nan

            print("\n--------------------------------------------------")
            print("  Running CNN-based interpolator")
            print("--------------------------------------------------")

            batch_mean = 0
            #batch_mean = np.nanmean( scatter_data_batch )
            batch_std = np.nanstd( scatter_data_batch )
            batch_min = batch_mean - 3*batch_std
            batch_max = batch_mean + 3*batch_std
            #batch_min = np.nanmin(scatter_data_batch)
            #batch_max = np.nanmax(scatter_data_batch)
            if float(batch_std) == 0.0:
                batch_min = -0.01
                batch_max = 0.01
            print("Batch mean (currently set to 0):", batch_mean )
            print("Batch min/max: %3.3f / %3.3f "%(batch_min, batch_max) )

            X = ( scatter_data_batch - batch_min) / (batch_max - batch_min)

            if args.debug_mode:
                # Batch debug
                for ii in range(btch):
                    pp = (X[ii,:,:,0] * 255 ).astype(np.uint8)
                    cc = (X[ii,:,:,1] * 255 ).astype(np.uint8)
                    nn = (X[ii,:,:,2] * 255 ).astype(np.uint8)
                    cv.imwrite( "%s/%03d_%03d_00prev.png"%(DEBUGDIR,FRAME_IDX,ii), pp )
                    cv.imwrite( "%s/%03d_%03d_01curr.png"%(DEBUGDIR,FRAME_IDX,ii), cc )
                    cv.imwrite( "%s/%03d_%03d_02next.png"%(DEBUGDIR,FRAME_IDX,ii), nn )

            Y = model.predict( [X,ph_diff_mat] )
            Y[Y==0] = np.nan
            Y = ( Y*(batch_max-batch_min) + batch_min ) * cam0maskbatch

            if args.debug_mode:
                np.savez( "%s/batch_%04d"%(DEBUGDIR, FRAME_IDX//BATCH_SIZE), X=X, PHdiff=ph_diff_mat, Y=Y )

            for ii in range(btch):
                #GLOBAL_FRAME_IDX = FRAME_IDX-BATCH_SIZE+ii
                GLOBAL_FRAME_IDX = ii
                ZIp = np.squeeze( Y[ii,:,:] )
                Zinput = None


                if args.saveCNNinput:
                    # Save CNN input in NetCDF file
                    Zinput = np.copy( np.squeeze( X[ii,:,:,1] ) )
                    Zinput = ( Zinput*(batch_max-batch_min) + batch_min ) 

                if args.debug_mode:
                    # CNN output debug
                    idbg = np.zeros_like(ZIp)
                    idbg = cv.normalize(ZIp, idbg, 0, 255, cv.NORM_MINMAX)
                    idbg = idbg.astype(np.uint8)
                    cv.imwrite( "%s/%06d_cnnpredicted.png"%(DEBUGDIR,GLOBAL_FRAME_IDX), idbg )

                ZIp_small = ZIp[ (_zc-_zss):(_zc+_zss), (_zc-_zss):(_zc+_zss) ]

                p2 = np.percentile( ZIp_small.flatten(), 2 )
                p98 = np.percentile( ZIp_small.flatten(), 98 )

                Zmean = Zmean + (np.nanmean(ZIp_small)-Zmean)/N_frames
                Zmin = min( Zmin, np.nanmin(ZIp_small) )
                Zmax = max( Zmax, np.nanmax(ZIp_small) )
                Zp2_mean = Zp2_mean + (p2 - Zp2_mean)/N_frames
                Zp98_mean = Zp98_mean + (p98 - Zp98_mean)/N_frames

                _, imgjpeg = cv.imencode(".jpg", cv.pyrDown( images_mdct[ii] ) )
                outdata.push_Z( ZIp*1000, timestamp_mlst[ii], GLOBAL_FRAME_IDX, imgjpeg, Zinput )

                stats_dct["Zmean"].append(Zmean)
                stats_dct["Zmin"].append(Zmin)
                stats_dct["Zmax"].append(Zmax)
                stats_dct["Zp2_mean"].append(Zp2_mean)
                stats_dct["Zp98_mean"].append(Zp98_mean)

            for k in zz_mdct.keys():
                zz_mdct[k].fill(0)
            in_batch_idx = 0
            timestamp_mlst[0] = timestamp

    Zmean = np.nanmean(stats_dct["Zmean"])
    Zmin = np.nanmean(stats_dct["Zmin"])
    Zmax = np.nanmean(stats_dct["Zmax"])
    Zp2_mean = np.nanmean(stats_dct["Zp2_mean"])
    Zp98_mean = np.nanmean(stats_dct["Zp98_mean"])

    outdata.add_meta_attribute("zmin", Zmin )
    outdata.add_meta_attribute("zmax", Zmax )
    outdata.add_meta_attribute("zmean", Zmean )
    outdata.add_meta_attribute("zp2mean", Zp2_mean )
    outdata.add_meta_attribute("zp98mean", Zp98_mean )
    outdata.close()

    print("\n\n")
    print("==============    Sea plane stats  ============")
    print("  Sea plane stats: ")
    print("     Z mean: %3.3f m"%Zmean )
    print("    Z range: %3.3f m"%(Zmax-Zmin) )
    print("  Z 98p-2p : %3.3f m"%(Zp98_mean-Zp2_mean) )
    print("===============================================")

    total_elapsed_time = (time.time()-global_start_time)
    avg_fps = float(LAST_FRAME-FIRST_FRAME)/float(total_elapsed_time)
    print("All done in %3.2f seconds.\nAverage processing speed %3.2f fps.\n"%(total_elapsed_time, avg_fps))

    return True





async def process_sequence_predictupdate( dataReader, outdata, config, statsfile, first_frame_index, nframes, framerate, DEBUGDIR, args, settings, wavedirection, processors ):
    """ Original WASSfast processing loop based on surface prediction / update
    """

    mask = None
    cam0mask = None
    cam1mask = None

    is_first_frame = True
    I0p_first = None

    Zmean = 0.0
    Zmin = np.inf
    Zmax = -np.inf
    N_frames = 1

    # Initialize wave prediction
    wp = wavedirection
    _xd, _yd, retval = wavedir_string_to_shift( wp )
    if not retval:
        print("Invalid wave direction: %s", wp )
        return False

    outdata.add_meta_attribute("wassfast_mode", "PU" )
    outdata.add_meta_attribute("input_wave_direction_x", _xd )
    outdata.add_meta_attribute("input_wave_direction_y", _yd )

    # Select frame range
    FIRST_FRAME = first_frame_index
    LAST_FRAME = dataReader.n_frames - 1
    if nframes != None and nframes>0:
        LAST_FRAME = FIRST_FRAME + nframes

    print("FIRST: ", FIRST_FRAME)
    print(" LAST: ", LAST_FRAME)

    # Create csv file for debug statistics
    fcsv, wcsv = create_csv_for_debug( statsfile )

    status["code"] = 1
    status["status"] = "Processing"

    # Main loop
    for FRAME_IDX in trange(FIRST_FRAME, LAST_FRAME, unit="frames" ):

        await asyncio.sleep( 0.01 ) # Needed to let other async functions continue their work
        start_time = time.time()
        stats = {"frame": FRAME_IDX}

        tqdm.write("--------")
        tqdm.write(" Processing stereo frame %d"%FRAME_IDX)
        (fn,timestamp,I0) = dataReader.read_frame( FRAME_IDX*2 )
        tqdm.write("  %s"%fn)
        (fn,timestamp,I1) = dataReader.read_frame( FRAME_IDX*2+1 )
        tqdm.write("  %s"%fn)


        if not framerate is None:
            timestamp = float(FRAME_IDX-FIRST_FRAME)/float(framerate)

        if is_first_frame:
            last_timestamp = timestamp
        dt = timestamp-last_timestamp

        if dt>0:
            outdata.add_meta_attribute("fps", (1.0/dt) )

        tqdm.write("  Time: %5.1f secs, dt: %1.3f"%(timestamp,dt) )

        p3dN, cam0mask, cam1mask, wp, _xd, _yd, I0p_first, xdydchanged, locallogstring = estimate_scattered_point_cloud( I0, I1, cam0mask, cam1mask, wp, _xd, _yd, I0p_first, config, processors, args.debug_mode, DEBUGDIR, settings, idx=FRAME_IDX, savepts=args.savepts )

        tqdm.write( locallogstring )

        stats["match_time"]=(time.time()-start_time)
        stats["num_matches"]=p3dN.shape[1]

        # Scattered point cloud is ready to be used for surface reconstruction

        scalefacx = config.limits.xmax-config.limits.xmin+1
        scalefacy = config.limits.ymax-config.limits.ymin+1
        p3dN_norm = np.copy(p3dN)
        p3dN_norm[0,:] = (p3dN_norm[0,:]-config.limits.xmin)/scalefacx - 0.5
        p3dN_norm[1,:] = (p3dN_norm[1,:]-config.limits.ymin)/scalefacy - 0.5

        pt2 = p3dN_norm[0:2,:].astype( np.float32 ).T
        npts = pt2.shape[0]
        keep = np.ones( (npts,1), dtype=np.bool )
        if not is_first_frame:
            processors.points_reducer.reduce_points( pt2,
                                                     npts,
                                                     settings.getfloat("PointsReducer","max_pt_distance"),
                                                     settings.getint("PointsReducer","winsize"),
                                                     keep )

        if args.debug_mode:
            plt.scatter( pt2[:,0], pt2[:,1], s=1, )
            plt.axis('equal')
            plt.grid()
            plt.savefig('%s/scatter_norm.png'%DEBUGDIR)
            plt.close()

        keep = np.squeeze(keep)
        p3dN = p3dN[:,np.squeeze(keep) ]
        pt2 = pt2[np.squeeze(keep),:].T
        stats["num_filtered_matches"]=p3dN.shape[1]
        tqdm.write("   - after close points reduction: %d"%(p3dN.shape[1]))

        if args.debug_mode:
            plt.scatter( p3dN[0,:], p3dN[1,:], s=1, c=p3dN[2,:], vmin=config.limits.zmin, vmax=config.limits.zmax )
            plt.axis('equal')
            plt.grid()
            plt.savefig('%s/scatter_pointreduced.png'%DEBUGDIR)
            plt.close()


        # Mask extraction
        if is_first_frame:

            outdata.add_meta_attribute("image_width", I0.shape[1] )
            outdata.add_meta_attribute("image_height", I0.shape[0] )

            # Interpolation
            [XX,YY] = np.meshgrid( np.linspace(config.limits.xmin, config.limits.xmax, config.N ), np.linspace( config.limits.ymin, config.limits.ymax, config.N) )
            outdata.set_grids( XX*1000, YY*1000 )
            ZI = griddata( p3dN[0:2,:].T, p3dN[2,:], (XX, YY), method='linear')

            if args.debug_mode:
                plt.pcolor(XX, YY, ZI, vmin=config.limits.zmin, vmax=config.limits.zmax )
                plt.savefig('%s/surf.png'%DEBUGDIR)
                plt.close()

            # Mask
            mask = compute_mask(ZI)
            if args.debug_mode:
                plt.pcolor(XX, YY, mask )
                plt.savefig('%s/mask.png'%DEBUGDIR)
                plt.close()
            outdata.set_mask(mask)

            # Apply mask
            ZI[ np.isnan(ZI) ] = 0
            ZI = ZI * mask
            if args.debug_mode:
                plt.pcolor(XX, YY, ZI, vmin=config.limits.zmin, vmax=config.limits.zmax )
                plt.savefig('%s/surf_masked.png'%DEBUGDIR)
                plt.close()

            # Setup waveview
            if not processors.waveview is None:
                processors.waveview.setup_field( XX, YY, config.cam.P0plane.T )
                processors.waveview.set_zrange( config.limits.zmin, config.limits.zmax, 0.5 )

            if args.start_from_plane:
                ZI *= 0

            # Other stuff
            last_timestamp = timestamp
            spec = elevation_to_spectrum( ZI )


        tqdm.write(" Predicting field spectrum. xy-direction: %d %d, current vector: (%2.3f , %2.3f) m/s, depth: %5.2f m"%(_xd,_yd,args.current_u,args.current_v,args.depth) )
        df = compute_phase_diff( config.KX_ab, config.KY_ab, _xd, _yd , dt, depth=args.depth, current_vector=[args.current_u,args.current_v] )
        spec_pred = spec * np.exp( df * 1j )
        ZIp = spectrum_to_elevation( spec_pred )
        ZIp = ZIp * mask
        spec_pred = elevation_to_spectrum( ZIp )

        if args.debug_mode and settings.getboolean("Visual","plot_surfaces"):
            plt.pcolor(XX, YY, ZIp, vmin=config.limits.zmin, vmax=config.limits.zmax )
            plt.savefig('%s/surf_pred%08d.png'%(DEBUGDIR,FRAME_IDX) )
            plt.close()

        nodes = p3dN_norm[ 0:2, keep].T
        nodes[:,0]*=-1
        nodes[:,1]*=-1

        if not is_first_frame:

            if settings.has_option("Extra","use_griddata") and settings.getboolean("Extra", "use_griddata"):
                tqdm.write(" Gridding...")
                ZIp = griddata( p3dN[0:2,:].T, p3dN[2,:], (XX, YY), method='linear')
                ZIp = ZIp * mask

            else:
                tqdm.write(" Optimizing field spectrum...")

                #np.save('%s/%08d_nodes'%(DEBUGDIR,FRAME_IDX), nodes)
                #np.save('%s/%08d_nodes_int'%(DEBUGDIR,FRAME_IDX), p3dN[0:2,:] )
                #np.save('%s/%08d_spec_pred.T'%(DEBUGDIR,FRAME_IDX), spec_pred.T)
                #np.save('%s/%08d_b'%(DEBUGDIR,FRAME_IDX), np.expand_dims( p3dN[2,:], axis=1 ) )

                processors.sp.setup( nodes, spec_pred.T, np.expand_dims( p3dN[2,:], axis=1 ) )
                optstats = processors.sp.optimize( mit=settings.getint("SpecFit","mit"), stol=settings.getfloat("SpecFit","stol") )
                stats.update( optstats )

                #np.save('%s/%08d_spec_out'%(DEBUGDIR,FRAME_IDX), sp.spout.T )

                ZIp = spectrum_to_elevation( processors.sp.spout.T )
                ZIp = cv.GaussianBlur(ZIp, None, settings.getfloat("SpecFit","final_smooth_sigma"))
                ZIp = ZIp * mask


        spec = elevation_to_spectrum( ZIp )

        Zmean = Zmean + (np.nanmean(ZIp)-Zmean)/N_frames
        Zmin = min( Zmin, np.nanmin(ZIp) )
        Zmax = max( Zmax, np.nanmax(ZIp) )

        ret, imgjpeg = cv.imencode(".jpg", cv.pyrDown(I0) )
        outdata.push_Z( ZIp*1000, timestamp, FRAME_IDX, imgjpeg )

        last_timestamp = timestamp

        if args.plot_surfaces:

            # Optimized surface
            plt.pcolor(XX, YY, ZIp, vmin=config.limits.zmin, vmax=config.limits.zmax )
            plt.colorbar()
            plt.savefig('%s/surf_opt%08d.png'%(DEBUGDIR,FRAME_IDX))
            plt.close()
            # Gridded surface
            # ZIaux = griddata( p3dN[0:2,:].T, p3dN[2,:], (XX, YY), method='linear') * mask
            # plt.pcolor(XX, YY, ZIaux, vmin=zmin, vmax=zmax )
            #plt.colorbar()
            # plt.savefig('%s/surf_opt%08d_.png'%(DEBUGDIR,FRAME_IDX))
            # plt.close()


        if not processors.waveview is None:
            img = processors.waveview.render( I0, ZIp )
            img = cv.cvtColor( img, cv.COLOR_RGB2BGR )
            cv.imwrite('%s/frm_%08d.png'%(DEBUGDIR,FRAME_IDX), img )

        # import matplotlib
        # matplotlib.use('AGG')
        # import matplotlib.pyplot as plt
        # ZIe = spectrum_to_elevation( spectrum_expand( spec, (Next,Next) ) )#*Upscale_Ws )
        # plt.pcolor(XXext, YYext, ZIe, vmin=zmin, vmax=zmax )
        # plt.colorbar()
        # plt.savefig('dbg/surf_%08d.png'%FRAME_IDX)
        # plt.close()

        is_first_frame = False
        stats["total_time"]=(time.time()-start_time)
        tqdm.write(" Done in %2.3f secs."%stats["total_time"] )

        if wcsv:
            wcsv.writerow( stats )
            fcsv.flush()

        status["progress"] = int( (FRAME_IDX-FIRST_FRAME)*100/(LAST_FRAME-FIRST_FRAME) )
        status["stats"] = stats

        N_frames += 1

        #await asyncio.sleep(0.01)

        # Prediction
        #for dt in range(1,2):
        #    print("Prediction %d"%dt)
        #    spec = elevation_to_spectrum( ZI )
        #    df = compute_phase_diff( data["KX_ab"], data["KY_ab"], -1, 1 , dt*0.1 )
        #    spec = spec * np.exp( df * 1j )
        #    ZIp = spectrum_to_elevation( spec )
        #    ZIp = ZIp * mask
        #    plt.pcolor(XX, YY, ZIp, vmin=zmin*0.5, vmax=zmax*0.5 )
        #    plt.savefig('dbg/surf_p%03d.png'%dt )
        #    plt.close()

    outdata.add_meta_attribute("zmin", Zmin )
    outdata.add_meta_attribute("zmax", Zmax )
    outdata.add_meta_attribute("zmean", Zmean )
    outdata.close()
    fcsv.close()
    return True


def initialize_netcdf( outfile, config, settings, imgdata, settingsfile ):

    outdata = NetCDFOutput( filename=outfile )
    outdata.scale[:] = config.baseline
    outdata.add_meta_attribute("info", "Generated with WASSFast v.%s"%version )
    outdata.add_meta_attribute("generator", "WASSFast" )
    import ntpath
    outdata.add_meta_attribute("settingsfile", ntpath.basename( settingsfile ) )
    outdata.add_meta_attribute("datafile", ntpath.basename( imgdata ) )
    outdata.add_meta_attribute("baseline", config.baseline )
    outdata.set_instrinsics( config.cam.intr_00, config.cam.intr_01, config.cam.dist_00, config.cam.dist_01, config.cam.P0plane, config.cam.P1plane )
    outdata.set_kxky( config.KX_ab, config.KY_ab )

    for each_section in settings.sections():
        for (each_key, each_val) in settings.items(each_section):
            outdata.add_meta_attribute("%s.%s"%(each_section,each_key), each_val )

    return outdata


def create_default_settings_file(  ):
    settings = """
# WASSfast Default settings
# lines starting with # are comments and will not be parsed
#

[ImgProc]
# Apply Contrast Limited Adaptive Histogram Equalization (CLAHE) o
# to the left and right images independently
use_clahe=no

# If use_clahe=yes, specify the cliplimit and gridsize.
# See: https://docs.opencv.org/4.x/d5/daf/tutorial_py_histogram_equalization.html
# and https://stackoverflow.com/questions/64576472/what-does-clip-limit-mean-exactly-in-opencv-clahe
# for info on the cliplimit parameter
#
I0_cliplimit=3
I0_gridsize=11
I1_cliplimit=3
I1_gridsize=11

[SparseMatcher]
# Increase the quality level to extract better features. To increase
# the amount of sparse matches try reducing the quality level
quality_level=0.01

# No need to modify the following options unless you know
# what you are doing
max_corners=100000
min_distance=6
block_size=11

[Flow]
# Optical flow method to use. PyrLK is suggested. Fnbk is slower
# but better in handling noisy scenarios
method=PyrLK
#method=Fnbk
winsize=15
fb_threshold=0.6
maxlevel=3


[Filtering]
# Filter points whose absolute elevation
# exceedds the nth quantile. Use 0 to disable
# quantile filtering
outliers_quantile=0.99

# Options valid for PU Mode ONLY
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
    """
    with open('default_settings.txt', 'w') as settingsfile:
      settingsfile.write( settings )
    print("default_settings.txt generated.")



async def main():

    print(" ")
    print("       ╦ ╦╔═╗╔═╗╔═╗┌─┐┌─┐┌─┐┌┬┐              ")
    print("       ║║║╠═╣╚═╗╚═╗├┤ ├─┤└─┐ │               ")
    print("       ╚╩╝╩ ╩╚═╝╚═╝└  ┴ ┴└─┘ ┴               ")
    print("              _.~'~._.~'~._.~'~._.~'~._      ")
    print("         v. %s - Copyright (C)            "%version)
    print("                    Filippo Bergamasco 2019-2025  ")
    print(" ")

    if len(sys.argv)>1:
        if sys.argv[1] == "--generate_settings":
            create_default_settings_file()
            sys.exit(0)

        if sys.argv[1] == "--analyse":
            if len(sys.argv) != 3:
                print("filename missing.")
                sys.exit(-1)

            ncfilename = sys.argv[2]
            print("Loading ", ncfilename )
            try:
                nca = NetCDFAnalysis( ncfilename )
                nca.analyse()
            except Exception as error:
                print(error)
                print("Error occurred during sea state analysis, aborting.")

            sys.exit(0)


    args = initialize_parser()


    ###############################################################
    # Global initialization
    ###############################################################

    sys.stdout = SimpleLogger()
    SETTINGSFILE = args.settingsfile
    
    if not os.path.exists( SETTINGSFILE ):
        print("%s not found."%SETTINGSFILE)
        sys.exit(-1)

    print("Loading settings %s"%SETTINGSFILE )
    settings = configparser.ConfigParser()
    settings.read( SETTINGSFILE )

    print("Loading data config file %s" % args.configfile )
    data = sio.loadmat( args.configfile )
    CALIBDIR = args.calibdir
    config = initialize_config(data, CALIBDIR)

    processors = intialize_processors(args.nographics, args, config, settings)
    sequence_args = initialize_seqargs(args)

    if args.debugdir:
        DEBUGDIR = args.debugdir+"/"
    else:
        DEBUGDIR = "dbg/"

    print("Using ", DEBUGDIR, " as debug dir")

    # Initialize status server
    await reset_status()
    server = await asyncio.start_server( handle_status_request, '127.0.0.1', 18098 )
    await server.start_serving()

    if args.continuous_mode:
        ###############################################################
        # Continuous processing
        ###############################################################

        datadir = args.imgdata
        status["datadir"]=datadir
        import glob

        while True:
            rawfiles = glob.glob( os.path.join(datadir, "[0-9]*.raw") ) # Any raw file starting with a number
            for rawfile in rawfiles:
                # Check if this RAW file was already processed
                basename = os.path.splitext(rawfile)[0]
                processed_raw_netcdf = basename + '.nc'
                unprocessed_raw_netcdf = basename + '_proc.nc'

                if not os.path.exists( processed_raw_netcdf ):
                    print( rawfile + " -> " + processed_raw_netcdf )

                    dataReader = RawReader( rawfile )
                    _, timestring = os.path.split( rawfile)
                    timestring = timestring[ 0:timestring.rfind('.') ]
                    print( "Raw file contains %d frames, size: %dx%d"%(dataReader.n_frames, dataReader.w, dataReader.h ) )
                    print(" Timestring: %s"%timestring )
                    status["datain"] = os.path.abspath( rawfile )

                    outdata = initialize_netcdf( outfile=unprocessed_raw_netcdf, config=config, settings=settings, imgdata=rawfile, settingsfile=SETTINGSFILE )
                    outdata.add_meta_attribute("timestring", timestring )
                    outdata.add_meta_attribute("location", args.location if args.location else "Unknown" )
                    status["dataout"] = os.path.abspath( unprocessed_raw_netcdf )

                    DEBUGDIR = basename + "_DBG"
                    status["debugdir"] = os.path.abspath(DEBUGDIR)

                    if await process_sequence(  dataReader=dataReader,
                                                outdata=outdata,
                                                config=config,
                                                statsfile=(os.path.join(DEBUGDIR,"stats.csv") if args.debug_stats else None ),
                                                first_frame_index=args.first_frame,
                                                nframes=args.nframes,
                                                framerate=args.framerate,
                                                DEBUGDIR=DEBUGDIR,
                                                args=sequence_args,
                                                settings=settings,
                                                wavedirection=args.wavedirection,
                                                processors=processors ):

                        print("Sequence completed.")
                        os.rename( unprocessed_raw_netcdf, processed_raw_netcdf )
                        try:
                            nca = NetCDFAnalysis( processed_raw_netcdf, upload_url=args.upload_url )
                            nca.analyse()
                        except Exception as error:
                            print(error)
                            print("Error occurred during sea state analysis, aborting.")
                        await reset_status()

            print("Waiting for some RAW file to process...")
            status["code"]=2
            status["status"]="Waiting RAW files"
            status["datadir"]=datadir
            await asyncio.sleep( 5.0 )

    else:

        ###############################################################
        # Sequence processing
        ###############################################################

        print("Loading %s"%args.imgdata)

        if not os.path.exists( args.imgdata ):
            print("%s does not exists."%args.imgdata)
            sys.exit(-1)

        status["datain"] = os.path.abspath( args.imgdata )

        import datetime
        if os.path.isdir( args.imgdata ):
            dataReader = DirReader(args.imgdata)
            fn1 = None
            for root, dirs, files in os.walk(args.imgdata+"/cam0"):
                for name in files:
                    if name[0:6] == '000000':
                        fn1 = name
            if fn1 is None:
                timestring = ""
                print("Invalid timestring in files.")
            else:
                timestring = fn1
                timestring = timestring.split("_")[1]
                timestamp= datetime.datetime.fromtimestamp(int(timestring)/1000)
                timestring = str(timestamp)

        else:
            dataReader = RawReader(args.imgdata)
            _, timestring = os.path.split( args.imgdata )
            timestring = timestring[ :timestring.rfind('.') ]
            print( "Raw file contains %d frames, size: %dx%d"%(dataReader.n_frames, dataReader.w, dataReader.h ) )
            print(" Timestring: %s"%timestring )


        # Initialize netCDF output (if needed)
        if args.output != None and len(args.output)>0:
            outdata = initialize_netcdf( outfile=args.output, config=config, settings=settings, imgdata=args.imgdata, settingsfile=SETTINGSFILE )
            outdata.add_meta_attribute("timestring", timestring )
            outdata.add_meta_attribute("location", args.location if args.location else "Unknown" )
            status["dataout"] = os.path.abspath( args.output )

        else:
            outdata = NetCDFOutput( filename=None )


        status["debugdir"] = os.path.abspath( DEBUGDIR )

        if await process_sequence( dataReader=dataReader,
                                   outdata=outdata,
                                   config=config,
                                   statsfile=(os.path.join(DEBUGDIR,"stats.csv") if args.debug_stats else None ),
                                   first_frame_index=args.first_frame,
                                   nframes=args.nframes,
                                   framerate=args.framerate,
                                   DEBUGDIR=DEBUGDIR,
                                   args=sequence_args,
                                   settings=settings,
                                   wavedirection=args.wavedirection,
                                   processors=processors ):

            print("Sequence completed.")
            try:
                nca = NetCDFAnalysis( args.output, upload_url=args.upload_url )
                nca.analyse()
            except Exception as error:
                print(error)
                print("Error occurred during sea state analysis, aborting.")

        await reset_status()

    ## All done


def wassfast_main():
    asyncio.run( main() )


if __name__=="__main__":
    wassfast_main()
