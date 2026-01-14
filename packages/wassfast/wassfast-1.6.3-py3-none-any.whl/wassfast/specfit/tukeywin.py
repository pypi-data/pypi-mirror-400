import numpy as np
from scipy import signal

def tukeywin_m( NN, Alpha ):
    """
    Implements and return a Matlab-stlye tukeywin
    """
    w = signal.tukey(NN,Alpha )
    w = w.reshape(NN,1)*w
    return w.astype( np.float64 )
