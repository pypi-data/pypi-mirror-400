import numpy as np
import argparse
import os
import sys
import scipy.io
import glob
from tqdm import tqdm
import cv2 as cv

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cam0img", help="Directory containing cam0 images")
    parser.add_argument("configmat", help="The config.mat file produced by WASS gridding tool")
    parser.add_argument("out", help="Where to store the produced images")
    args = parser.parse_args()

    print("Cam0 image dir: ", args.cam0img )
    if not os.path.isdir( args.cam0img ):
        sys.exit(-1)

    print("Output dir: ", args.out )
    if not os.path.isdir( args.out ):
        sys.exit(-1)

    M = scipy.io.loadmat( args.configmat )
    #print("config.mat keys: ", M.keys() )

    BASELINE = M["CAM_BASELINE"].item(0)
    SCALEi = 1.0/BASELINE

    P0cam = M["P0cam"]
    Rpl = M["Rpl"] 
    Tpl = M["Tpl"] 

    P1cam = M["P1cam"]
    RTpl = np.eye( 4, dtype=np.float64 )
    RTpl[:3,:3] = Rpl.T
    RTpl[:3,3] = (-Rpl.T@Tpl).flatten()

    P1plane = P1cam@RTpl@np.diag((SCALEi, SCALEi, SCALEi, 1))
    P0plane = P0cam@RTpl@np.diag((SCALEi, SCALEi, SCALEi, 1))

    pts = np.array( [ [M["xmin"].item(0),M["ymin"].item(0),0,1],
                      [M["xmin"].item(0),M["ymax"].item(0),0,1],
                      [M["xmax"].item(0),M["ymax"].item(0),0,1],
                      [M["xmax"].item(0),M["ymin"].item(0),0,1]  ]).T * BASELINE

    pts_cam0 = P0plane @ pts
    pts_cam0 /= pts_cam0[2,:]

    pts_cam1 = P1plane @ pts
    pts_cam1 /= pts_cam1[2,:]

    H = cv.findHomography( pts_cam0[:2,:].T, pts_cam1[:2,:].T )[0]

    
    cam0_images = sorted( glob.glob( "%s/*_01.*"%args.cam0img ) )
    print( len(cam0_images) )

    for ii in tqdm( range(4000) ):
        cam0i = cam0_images[ii]
        I0 = cv.imread( cam0i, cv.IMREAD_GRAYSCALE )
        I1 = cv.warpPerspective( I0, H, I0.shape[::-1] )

        aux = os.path.basename( cam0i ).split("_")
        cam0filename = "%s_%s_01.png"%(aux[0],aux[1])
        cam1filename = "%s_%s_02.png"%(aux[0],aux[1])
        cv.imwrite("%s/cam0/%s"%(args.out,cam0filename), I0)
        cv.imwrite("%s/cam1/%s"%(args.out,cam1filename), I1)


if __name__ == "__main__":
    main()