import cv2 as cv
import numpy as np
import numpy.ma as ma


class SparseMatcher:
    def __init__(self, max_corners=80000, quality_level=0.005, min_distance=5, block_size=11):
        self.max_corners = int(max_corners)
        self.quality_level = float(quality_level)
        self.min_distance = int(min_distance)
        self.block_size = int(block_size)
        pass

    def extract_features(self, I0P, I1P, mask0, mask1, fb_threshold=0.8, winsize=(13,13), maxlevel=3, optflo_method= 'PyrLK' ):
        assert( len(I0P.shape) == 2 ) # must be a grayscale image
        self.features_0P = None
        self.features_1P = None


        # Extract features on image 0
        features_0 = np.squeeze( cv.goodFeaturesToTrack( I0P, self.max_corners, self.quality_level, self.min_distance, blockSize=self.block_size ) )

        if not isinstance(features_0, np.ndarray) or features_0.size < 5:
            return

        self.features_0P = np.floor( features_0 )
        self.features_0P_all = self.features_0P.copy()

        use_sparse_flow = False

        if optflo_method == 'PyrLK':
            # Sparse flow
            criteria=(cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 50, 0.001)

            p1, st, err = cv.calcOpticalFlowPyrLK( I0P, I1P, self.features_0P, None, winSize=winsize, maxLevel=maxlevel, criteria=criteria )
            p0r, st0, err = cv.calcOpticalFlowPyrLK( I1P, I0P, p1, None, winSize=winsize, maxLevel=maxlevel, criteria=criteria )

            # Set only good
            fb_good = (np.fabs(p0r-self.features_0P) < fb_threshold ).all(axis=1)
            fb_good = np.logical_and( np.logical_and( fb_good, st.flatten() ), st0.flatten() )

            self.features_0P = self.features_0P[ fb_good, :]
            self.features_1P = p1[ fb_good, :]
            self.features_1P[:,0] = np.clip( self.features_1P[:,0], 0, I0P.shape[0]-1 )
            self.features_1P[:,1] = np.clip( self.features_1P[:,1], 0, I0P.shape[1]-1 )

        elif optflo_method == "Fnbk":
            # Global farneback flow
            self.features_0P = self.features_0P.astype( np.uint32 )
            flow = None
            flow = cv.calcOpticalFlowFarneback(I0P,I1P,flow,pyr_scale=0.5,levels=maxlevel,winsize=winsize[0], iterations=10, poly_n=5, poly_sigma=1.1,flags = 0 )

            fu = np.squeeze( flow[:,:,0] )
            fv = np.squeeze( flow[:,:,1] )

            x_delta = fu[ self.features_0P[:,1], self.features_0P[:,0] ]
            y_delta = fv[ self.features_0P[:,1], self.features_0P[:,0] ]

            self.features_1P = self.features_0P.astype( np.float32 )
            self.features_1P[:,0] = np.clip( self.features_1P[:,0] + x_delta, 0, I0P.shape[0]-1 )
            self.features_1P[:,1] = np.clip( self.features_1P[:,1] + y_delta, 0, I0P.shape[1]-1 )

            features_1P_check = (self.features_1P+0.5).astype( np.uint32 )

            flow = None
            flow = cv.calcOpticalFlowFarneback(I1P,I0P,flow,pyr_scale=0.5,levels=maxlevel,winsize=winsize[0], iterations=10, poly_n=5, poly_sigma=1.1,flags = 0 )
            fu = np.squeeze( flow[:,:,0] )
            fv = np.squeeze( flow[:,:,1] )
            x_delta = fu[ features_1P_check[:,1], features_1P_check[:,0] ]
            y_delta = fv[ features_1P_check[:,1], features_1P_check[:,0] ]
            features_0Pcheck = features_1P_check.astype( np.float32 )
            features_0Pcheck[:,0] += x_delta
            features_0Pcheck[:,1] += y_delta

            diff = self.features_0P - features_0Pcheck
            good_pts = np.sqrt( diff[:,0]**2 + diff[:,1]**2 ) < fb_threshold

            self.features_1P = self.features_1P[  good_pts, :]
            self.features_0P = self.features_0P[  good_pts, :]

        f0aux = self.features_0P.astype(np.uint32)
        good0 = mask0[ f0aux[:,1], f0aux[:,0] ] > 0

        f1aux = self.features_1P.astype(np.uint32)
        good1 = mask1[ f1aux[:,1], f1aux[:,0] ] > 0

        goodaftermask = good0*good1
        self.features_1P = self.features_1P[  goodaftermask, :]
        self.features_0P = self.features_0P[  goodaftermask, :]


