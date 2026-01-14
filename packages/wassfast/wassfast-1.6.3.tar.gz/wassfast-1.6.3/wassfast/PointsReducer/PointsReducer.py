import ctypes
import os
import numpy.ctypeslib as ctl
import numpy as np
import platform

class PointsReducer:
    """
    Usage:

    pr = PointsReducer()
    pr.reduce_points( points, Npts, max_dist, winsize, keep )

    where:

    - Npts is an integer
    - points is a np.float32 (Npts,2) matrix of points coordinates in range [-0.5 ... 0.5]
    - max_dist is a float value specifying the maximum distance of two points to be kept
    - winsize is an odd integer value affecting the resolution of the computed distances (11 is fine)
    - keep is a np.bool (Npts,1) column vector that will be filled with True or False if a point
      has to be kept or not


    See PointsReducerTest.ipynb for a usage demo

    """

    def __init__(self):

        #print( platform.system() )
        libname = None

        if platform.system() == "Darwin":
            libname = 'libPointsReducer.dylib';
        if platform.system() == "Linux":
            libname = 'libPointsReducer.so';
        if platform.system() == "Windows":
            libname = 'PointsReducer.dll';

        assert libname!=None, "Unable to identify library platform"

        libdir = os.path.dirname(__file__)+'/dist/lib/';
        print("Loading lib "+libdir+libname);
        self.lib = ctypes.CDLL( libdir + libname );

        self.reduce_points = self.lib.reduce_points;
        self.reduce_points.argtypes = [ctl.ndpointer(np.float32, flags='aligned, c_contiguous'), ctypes.c_uint32, ctypes.c_float,  ctypes.c_uint32, ctl.ndpointer(np.bool, flags='aligned, c_contiguous') ];





