import numpy as np
import struct

class RawReader:

    def __init__( self, filename ):
        self.filename = filename
        self.curr_frame = 0
        self.n_frames = 0
        self.w = 0
        self.h = 0
        self.frame_size = 0
        self.frames_off = 12
        self.read_header()


    def read_header( self ):
        with open(self.filename, "rb") as fin:
            fin.seek( 0, 0)
            (self.n_frames, self.h, self.w) = struct.unpack( "III", fin.read( self.frames_off ) )
            self.n_frames = int( self.n_frames/2 )
            self.frame_size = self.w * self.h + 136


    def read_frame( self, n=-1 ):
        if n<0:
            n = self.curr_frame

        img = None
        filename = None
        timestamp = None

        with open(self.filename, "rb") as fin:
            fin.seek( self.frames_off + self.frame_size * n, 0 )
            filename = fin.read( 136 )
            filename = filename.decode("ascii").rstrip("\0")
            timestamp = float(filename.split("_")[1])/1000.0
            self.curr_frame = n+1
            
            img = np.reshape( np.frombuffer( fin.read(self.w * self.h), dtype=np.uint8 ), (self.h, self.w) )
        return (filename, timestamp, img)


