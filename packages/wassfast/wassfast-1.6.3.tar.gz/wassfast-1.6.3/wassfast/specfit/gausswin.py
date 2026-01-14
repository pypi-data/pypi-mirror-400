import numpy as np
from scipy import signal

def gausswin_m( NN, Alpha ):
    """
    Implements and return a Matlab-stlye gausswin
    """
    w = signal.gaussian(NN, std=(NN-1)/(2*Alpha) )
    w = w.reshape(NN,1)*w
    W = (1.0 - w)**2

    return W.astype( np.float64 )
