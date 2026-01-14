import numpy as np
import struct
import os
import glob
import cv2 as cv
import math


supported_extensions=["tif","jpg","png"]


class DirReader:

    def __init__( self, basedir ):

        self.basedir = basedir
        self.dir_cam0 = os.path.join( self.basedir, "cam0")
        self.dir_cam1 = os.path.join( self.basedir, "cam1")

        assert os.path.isdir(self.dir_cam0), "%s is not a valid directory"%self.dir_cam0
        assert os.path.isdir(self.dir_cam1), "%s is not a valid directory"%self.dir_cam0

        for ext in supported_extensions:
            cam1_filepattern = "%s/*."+ext
            cam2_filepattern = "%s/*."+ext

            self.cam0_images = [ f for f in glob.glob(cam1_filepattern%self.dir_cam0) ]
            self.cam1_images = [ f for f in glob.glob(cam2_filepattern%self.dir_cam1) ]

            self.cam0_images.sort()
            self.cam1_images.sort()
            if len(self.cam0_images)>0:
                break


        assert len(self.cam0_images) == len(self.cam1_images), "cam0 and cam1 directories contain a different set of images"
        assert len(self.cam0_images)>0 , "no image found"


        self.curr_frame = 0
        self.n_frames = len(self.cam0_images)

        I = cv.imread( self.cam0_images[0], cv.IMREAD_GRAYSCALE )
        if I is None:
            raise Exception("Unable to load "+self.cam0_images[0] )

        self.w = I.shape[1]
        self.h = I.shape[0]

        self.rel = False
        imgfile = self.cam0_images[0]
        imgfilename = os.path.split( imgfile )[1]
        self.first_timestamp = float(imgfilename.split("_")[1])/1000.0
        if self.first_timestamp == 0*13:
            self.rel = True
        else:
            self.first_timestamp = self.first_timestamp/1000


    def read_header( self ):
        pass


    def read_frame( self, n=-1 ):

        if n%2 == 0:
            imgfile = self.cam0_images[ math.floor( n/2 ) ]
        else:
            imgfile = self.cam1_images[ math.floor( n/2 ) ]

        imgfilename = os.path.split( imgfile )[1]

        if self.rel:
            timestamp = float(imgfilename.split("_")[1])/1000.0
        else:
            timestamp = float(imgfilename.split("_")[1])/1000.0
            timestamp = timestamp/1000
            timestamp = timestamp - self.first_timestamp

        img = cv.imread( imgfile, cv.IMREAD_GRAYSCALE )

        return (imgfile, timestamp, img)


