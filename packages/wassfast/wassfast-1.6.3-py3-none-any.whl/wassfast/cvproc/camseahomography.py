import numpy as np
import cv2 as cv

class Cam2SeaH:
    def __init__( self, xmin, xmax, ymin, ymax, Rpl, Tpl, Pcam, scale, OUT_SIZE=1024 ):
        Rpl = np.matrix(Rpl)
        Tpl = np.matrix(Tpl)
        Pcam = np.matrix(Pcam)
        pts3d = np.matrix([ [xmin, ymin, 0.0 ],
                            [xmax, ymin, 0.0 ],
                            [xmax, ymax, 0.0 ],
                            [xmin, ymax, 0.0 ] ])
        pts3d = pts3d.T / scale

        Rp2c = Rpl.T
        Tp2c = -Rp2c*Tpl

        pts3d = Rp2c * pts3d + Tp2c
        pts2d_0 = Pcam * np.vstack( ( pts3d , np.matrix([1,1,1,1])))
        pts2d_0 = pts2d_0 / pts2d_0[2,:]

        src = np.copy( pts2d_0[0:2,:].T )
        dst = np.copy( np.matrix( [ [0,OUT_SIZE,OUT_SIZE,0],[0,0,OUT_SIZE,OUT_SIZE] ] ).T ) 
        self.H = cv.findHomography( src, dst )[0]
        self.IMG_SIZE = OUT_SIZE

    def warp( self, img ):
        Iw = cv.warpPerspective( img, self.H, dsize=(self.IMG_SIZE,self.IMG_SIZE), flags=(cv.INTER_LANCZOS4) )
        return Iw

    def transform( self, points, inverse=False ):
        assert( points.shape[0]==2 )
        Htr = self.H
        if inverse:
            Htr = np.linalg.inv(Htr)
        
        ptst = np.matmul( Htr , np.vstack( (points.astype(np.float64), np.ones( (1,points.shape[1]), dtype=np.float64 ) )  ) )
        ptst = ptst / ptst[2,:]
        return ptst[0:2,:]



