import numpy as np
import cv2 as cv
from ..specfit.tukeywin import tukeywin_m
from enum import Enum

class XDIR:
    RIGHT_TO_LEFT=-1.0
    LEFT_TO_RIGHT=1.0
    NONE=0.0

class YDIR:
    BOTTOM_TO_TOP=-1.0
    TOP_TO_BOTTOM=1.0
    NONE=0.0

def compute_mask(ZI, tukey_p=0.08, gauss_sigma=2.0 ):
    assert( ZI.shape[0] == ZI.shape[1] )
    N = ZI.shape[0]
    mask = np.logical_not( np.isnan( ZI ) ).astype( np.float32 )
    mask = cv.GaussianBlur( mask, (0,0), sigmaX=gauss_sigma, sigmaY=gauss_sigma )
    mask[ mask<0.99 ] = 0
    mask = cv.GaussianBlur( mask, (0,0), sigmaX=gauss_sigma, sigmaY=gauss_sigma )
    maskborder = tukeywin_m( N, tukey_p )
    mask = mask * maskborder
    return mask

    #plt.pcolor(XX, YY, mask )
    #plt.savefig('dbg/mask.png')
    #plt.close()


def elevation_to_spectrum( ZI ):
    spec_scale = 1.0 / (ZI.shape[0]*ZI.shape[1])
    spec = np.fft.fftshift( np.fft.fft2( np.fft.ifftshift(ZI) ) )
    return spec * spec_scale


def spectrum_to_elevation( spec ):
    spec_scale = spec.shape[0]*spec.shape[1]
    ele = np.real( np.fft.fftshift( np.fft.ifft2( np.fft.ifftshift(spec*spec_scale) ) ) )
    return ele 

def spectrum_expand( spec, newsize ):
    assert( newsize[0]%2==0 )
    assert( newsize[1]%2==0 )

    if newsize[0] == spec.shape[0] and newsize[1] == spec.shape[1]:
        return spec

    spec_c = np.zeros( newsize, dtype=spec.dtype )
    center = (np.array( spec_c.shape )/2 ).astype(np.int32) 

    p = center-(np.array(spec.shape)/2 )
    p2 = p+np.array(spec.shape)
    p = p.astype(np.int32) 
    p2 = p2.astype(np.int32) 

    spec_c[ p[0]:p2[0], p[1]:p2[1] ] = spec
    return spec_c


def compute_phase_diff( KX_ab, KY_ab, xsign, ysign, dt, depth=np.inf, current_vector=[0.0, 0.0] ):
    Kmag = np.sqrt( KX_ab*KX_ab + KY_ab*KY_ab )
    Ksign = np.sign( (xsign*KX_ab) + (ysign*KY_ab) )

    omega_sq = 9.8 * Kmag * ( 1.0 if depth == np.inf else np.tanh( Kmag*depth )  )

    ph_diff = Ksign*( np.sqrt(omega_sq) + KX_ab*current_vector[0] + KY_ab*current_vector[1] )*dt
    ph_diff = np.triu(ph_diff) - np.tril(ph_diff )
    ph_diff = ph_diff*( np.triu(-np.ones(KX_ab.shape)) + np.tril(+np.ones(KX_ab.shape)) )
    return ph_diff
