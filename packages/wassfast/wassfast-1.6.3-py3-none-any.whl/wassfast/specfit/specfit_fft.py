from specfit.gausswin import gausswin_m

#import os
#os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

import numpy as np
from keras import backend as K
import tensorflow as tf
from scipy.optimize import minimize,fmin_l_bfgs_b
import scipy
import time
from scipy import signal





def build_loss_function_interp( winfun, Sp, data_weight = 1E4 ):

    W = tf.constant( winfun, dtype=np.float32 )

    #Spec_pred = tf.constant( Sp, dtype=np.complex64 )
    Spec_pred = tf.placeholder( shape=None,  dtype=np.complex64 )
    #node_loc = tf.constant( np.expand_dims( nodes_loc, axis=0) , dtype=np.float32 )
    node_loc = tf.placeholder( shape=None , dtype=np.float32 )
    #node_b = tf.constant( np.expand_dims( b, axis=0 ), dtype=np.float32 )
    node_b = tf.placeholder( shape=None, dtype=np.float32 )

    inS = tf.convert_to_tensor( K.variable( Sp, dtype=np.complex64  ) )

    spec_diff = inS-Spec_pred
    spec_loss = K.mean( tf.real( spec_diff * tf.conj(spec_diff) ) * W )

    elev_field = tf.real( tf.spectral.ifft2d( inS ) )

    node_data_interp = tf.contrib.resampler.resampler( tf.expand_dims( tf.expand_dims(elev_field,axis=0), axis=-1) , node_loc )

    data_loss = K.mean(  K.square( (node_data_interp - node_b) ) )

    loss = spec_loss + data_weight*data_loss

    grads = K.gradients( loss, inS )

    out = [spec_loss, data_loss, loss ]

    # Append gradient to out
    if isinstance(grads, (list, tuple)):
        out += grads
    else:
        out.append(grads)

    return K.function([inS, Spec_pred, node_loc, node_b], out)



class SpecfitFFT():

    def __init__( self, N, alpha=12 ):
        """
        N: spectrum size
        alpha: smoothness factor. low alpha -> smoother surface. (ie. spectrum is less forced to pass trough the points)
        """

        self.N = N
        self.set_alpha( alpha )
        self.l = None

    def __del__(self):
        K.clear_session()

    def set_alpha( self, alpha ):
        self.w = np.fft.ifftshift( gausswin_m( self.N, alpha ) )


    def setup( self, nodes, spec_sq, b, data_weight=1E4 ):

        assert( nodes.shape[1] == 2 )

        self.nodes_loc = (-nodes+0.5) * spec_sq.shape
        self.data_weight = data_weight

        self.b = b

        def convert_spectrum( spec ):
            spec_scale = spec.shape[0]*spec.shape[1]
            E = np.real( np.fft.fftshift( np.fft.ifft2( np.fft.ifftshift(spec*spec_scale) ) ) ).T
            return np.fft.fft2(E).astype(np.complex64)

        self.Sp = convert_spectrum( spec_sq )

        self.nodes_loc = np.expand_dims( self.nodes_loc, axis=0)
        self.b = np.expand_dims( self.b, axis=0 )

        if self.l  is None:
            self.l = build_loss_function_interp( self.w, self.Sp, self.data_weight )



    def optimize( self, verbose=False, mit=None, stol=None ):

        start_time = time.time()

        l = self.l
        Sp = self.Sp


        def real_to_complex(z):      # real vector of length 2n -> complex of length n
            return z[:len(z)//2] + 1j * z[len(z)//2:]

        def complex_to_real(z):      # complex vector of length n -> real of length 2n
            return np.concatenate((np.real(z), np.imag(z)))

        def eval_loss_and_grads(x):
            x = np.reshape( real_to_complex(x), Sp.shape )
            outs = l( [x,self.Sp,self.nodes_loc,self.b] )
            loss_value = outs[2]
            grad_values = np.array(outs[3]).flatten()
            return loss_value, grad_values


        # this Evaluator class makes it possible
        # to compute loss and gradients in one pass
        # while retrieving them via two separate functions,
        # "loss" and "grads". This is done because scipy.optimize
        # requires separate functions for loss and gradients,
        # but computing them separately would be inefficient.
        class Evaluator(object):

            def __init__(self):
                self.loss_value = None
                self.grads_values = None

            def loss(self, x):
                #assert self.loss_value is None
                loss_value, grad_values = eval_loss_and_grads(x)
                self.loss_value = loss_value
                self.grad_values = complex_to_real(grad_values).astype(np.float64)
                return self.loss_value

            def grads(self, x):
                assert self.loss_value is not None
                grad_values = np.copy(self.grad_values)
                self.loss_value = None
                self.grad_values = None
                return grad_values



        evaluator = Evaluator()
        x = complex_to_real( Sp.flatten() ).astype( np.float64 )

        
        if verbose:            
            initial_loss = evaluator.loss(x)
            print("Initial loss: ", initial_loss)


        x, min_val, info = fmin_l_bfgs_b(evaluator.loss, x.flatten(),
                                         fprime=evaluator.grads,
                                         maxfun=1000, factr=10, disp=-1, iprint=-1,
                                         pgtol = 1E-20,
                                         approx_grad=False )

        
        # Convert to NFFT format
        surfopt = np.fft.ifft2( np.reshape( real_to_complex(x), Sp.shape ) )
        spec_scale = surfopt.shape[0]*surfopt.shape[1]
        self.spout = np.fft.fftshift( np.fft.fft2( np.fft.ifftshift( np.real( surfopt.T ) ) ) ) / spec_scale

        end_time = time.time()
        
        if verbose:
            final_loss = evaluator.loss(x)
            print("Final loss: ", evaluator.loss(x))
            print(info)
            print('Optimized in %f (sec)' % ( end_time - start_time))

        return {"opt_time": ( end_time - start_time), "opt_nit": info["nit"]} #, "initial_loss":initial_loss, "final_loss":final_loss}



