from tensorflow.keras import backend as K
import tensorflow as tf
from tensorflow.keras.layers import Layer, Lambda, Convolution2D, Concatenate, Add, Multiply, MaxPooling2D, ReLU, Activation
from tensorflow.keras.models import Model
from tensorflow.keras import Input
import numpy as np

def compute_phase_diff_matrix( KX_ab, KY_ab, xsign, ysign, dt, depth=np.inf, current_vector=[0.0, 0.0] ):
    'computes complex matrix for current scene'
    
    #xsign = -np.sign(np.cos(angle))
    #ysign = -np.sign(np.sin(angle))
    #xsign = -xsign
    #ysign = -ysign
    
    Kmag = np.sqrt( KX_ab*KX_ab + KY_ab*KY_ab )
    Ksign = np.sign( (xsign*KX_ab) + ( ysign*KY_ab) )

    omega_sq = 9.8 * Kmag * ( 1.0 if depth == np.inf else np.tanh( Kmag*depth )  )

    ph_diff = Ksign*( np.sqrt(omega_sq) + KX_ab*current_vector[0] + KY_ab*current_vector[1] )*dt
    ph_diff = np.triu(ph_diff) - np.tril(ph_diff )

    return np.exp(1j*np.fft.fftshift( ph_diff*( np.triu(-np.ones(KX_ab.shape)) + np.tril(+np.ones(KX_ab.shape)) ) ) )

##### SPARSECONV MODEL #####


###  A simple Bias-only layer implementation
###   we assume a channel-last layout
class Bias(Layer):

    def __init__(self, **kwargs):
        super(Bias, self).__init__(**kwargs)

    def build(self, input_shape):

        self.bias = self.add_weight(name='bias',
                            shape=(1,1,input_shape[3]),
                            initializer='zeros',
                            trainable=True)

        super(Bias, self).build(input_shape)  # Be sure to call this at the end

    def call(self, x):
        return x + self.bias

    def compute_output_shape(self, input_shape):
        return input_shape
        
    
###  Returns a sparse convolution block as
###  described in 
###  Jonas Uhrig et al. "Sparsity Invariant CNNs", Figure 2 (right)
def sparse_conv_block( I, M, ksize, depth ):

    IM = Multiply( )([I,M] )

    IMc = Convolution2D( depth, ksize, padding='same', use_bias=False, activation=None) ( IM )

    # A hack to convolve with a fixed "ones" kernel
    Mc = Convolution2D( 1, ksize, padding='same', use_bias=False, activation=None, 
                        kernel_initializer = 'ones',
                        trainable=False) ( M )


    Inorm = Lambda( lambda x: x[0]/(x[1]+1E-5) )( [IMc,Mc] )
    InormB = Bias( )(Inorm)

    #Mpooled = MaxPooling2D(pool_size=(2,2), strides=(1,1), padding='same')(M)
    Mpooled = MaxPooling2D(pool_size=ksize, strides=(1,1), padding='same')(M)

    return InormB, Mpooled

    
def create_sparseconv_256_model( input_layer=None ):
    
    if input_layer is None:
        input_data = Input( shape=(256,256,2) )
    else:
        input_data = input_layer
        
    I0 = Lambda( lambda x: K.expand_dims(x[:,:,:,0],axis=-1), name="I0" )( input_data )
    M0 = Lambda( lambda x: K.expand_dims(x[:,:,:,1],axis=-1), name="M0" )( input_data )
    
    I,M = sparse_conv_block( I0, M0, (11,11), 16)
    I = Activation('sigmoid')( I )
    I,M = sparse_conv_block( I, M, (7,7), 16)
    I = Activation('sigmoid')( I )
    I,M = sparse_conv_block( I, M, (5,5), 16)
    I = Activation('sigmoid')( I )
    I,M = sparse_conv_block( I, M, (3,3), 16)
    I = Activation('sigmoid')( I )
    I,M = sparse_conv_block( I, M, (3,3), 16)
    I = Activation('sigmoid')( I )

    I,M = sparse_conv_block( I, M, (1,1), 1)
    O = Activation('linear', name="sc_out")( I )
    
    model = Model(inputs=input_data, outputs=O )    
    return model



##### MODEL WITH PREDICTION (prev, curr, next)#####

def compute_data_mask( data ):
    
    sparse_data = tf.expand_dims(data, axis=-1)
    mask = tf.cast( tf.math.logical_not( tf.math.is_nan(sparse_data)), tf.float32)
    
    sparse_data = tf.math.multiply_no_nan(sparse_data, mask) # NaN * 0 = 0
    
    return tf.concat((sparse_data, mask), axis=3)


def spec_predict( l, phdiff ):
    
    l_spec = tf.signal.fft2d(tf.complex(l[:,:,:,0], 0.0))
    l_spec =  tf.multiply(l_spec, phdiff)
    
    l_out = tf.math.real(tf.signal.ifft2d(l_spec)) 
    l_out = tf.expand_dims(l_out, axis=-1)
    
    return l_out
    

"""
def create_model_with_prediction( sparsecnn_trainable=False ):
    
    model_sparsecnn = create_sparseconv_256_model()

    if not sparsecnn_trainable:
        for l in model_sparsecnn.layers:
            l.trainable = False
    
    input_data = Input( shape=(256,256,3) )
    input_ph_diff_matrix = Input( shape=(256,256,4) ) # prev_real, prev_imag, next_real, next_imag
    
    IpMp = Lambda( lambda x: compute_data_mask(x[:,:,:,0]), name="IpMp" )( input_data )
    IcMc = Lambda( lambda x: compute_data_mask(x[:,:,:,1]), name="IcMc" )( input_data )
    InMn = Lambda( lambda x: compute_data_mask(x[:,:,:,2]), name="InMn" )( input_data )
    
    Op = model_sparsecnn( IpMp )
    Oc = model_sparsecnn( IcMc )
    On = model_sparsecnn( InMn )
    
    ph_diff_prev = Lambda( lambda x: tf.complex(x[:,:,:,0], x[:,:,:,1])) (input_ph_diff_matrix)
    ph_diff_next = Lambda( lambda x: tf.complex(x[:,:,:,2], x[:,:,:,3])) (input_ph_diff_matrix)
    
    Oc = Lambda( lambda x: x, name="curr" )( Oc )
    
    Op_pred = Lambda( lambda x: spec_predict( x[0], x[1]), name="predict_prev" )( [Op, ph_diff_prev] )
    On_pred = Lambda( lambda x: spec_predict( x[0], x[1]), name="predict_next" )( [On, ph_diff_next] )
    
    Oc = Concatenate()([Op_pred, Oc, On_pred])
        
    Oc = Convolution2D( 16, (5,5), padding='same', use_bias=True, activation="sigmoid") ( Oc )
    Oc = Convolution2D( 16, (3,3), padding='same', use_bias=True, activation="sigmoid") ( Oc )
    Oc = Convolution2D( 8, (3,3), padding='same', use_bias=True, activation="sigmoid") ( Oc )
    Oc = Convolution2D( 1, (1,1), padding='same', use_bias=True, activation="linear") ( Oc )
        
    model = Model(inputs = [input_data,input_ph_diff_matrix], outputs=Oc )
    return model 
"""

def generate_IDW_kernel( ksize=31, exp=1 ):
    K = np.zeros( (ksize,ksize), dtype=np.float32 )
    XX,YY = np.meshgrid( np.arange(ksize), np.arange(ksize) )
    
    XX -= ksize//2
    YY -= ksize//2
    d = np.power( np.sqrt( XX**2 + YY**2 ), exp )
    d[ ksize//2, ksize//2 ] = 1
    K = 1.0/d
    return K.astype(np.float32)


def generate_kernels(n_kernels=10, sz_kernel=21, exp_vals=None):

    if not exp_vals:
        exp_vals = np.linspace(0.6, 4, n_kernels)

    K = np.empty((sz_kernel,sz_kernel,1,0), dtype=np.float32)

    for i in range(len(exp_vals)):

        k = generate_IDW_kernel( ksize=sz_kernel, exp=exp_vals[i])
        k = np.expand_dims( k, axis=(-1,-2))

        K = np.concatenate([K, k], axis=-1)
        
    return K


def create_model_with_prediction( sparsecnn_weights=None, sparsecnn_trainable=False, sparse_second_stage=True ):
    ''' creates a model with fft prediction using the model_sparsecnn as interpolator
        for sparse data'''
    
    model_sparsecnn = create_sparseconv_256_model()
    
    # if weights are provided
    if sparsecnn_weights is not None:
        model_sparsecnn.load_weights(sparsecnn_weights)
        
    if not sparsecnn_trainable:
        for l in model_sparsecnn.layers:
            l.trainable = False
    
    input_data = Input( shape=(256,256,3) )
    input_ph_diff_matrix = Input( shape=(256,256,4) ) # prev_real, prev_imag, next_real, next_imag
    
    
    IpMp = Lambda( lambda x: compute_data_mask(x), name="IpMp" )( input_data[:,:,:,0] )
    IcMc = Lambda( lambda x: compute_data_mask(x), name="IcMc" )( input_data[:,:,:,1] )
    InMn = Lambda( lambda x: compute_data_mask(x), name="InMn" )( input_data[:,:,:,2] )
    
    
    Op = model_sparsecnn( IpMp )
    On = model_sparsecnn( InMn )
    
    ph_diff_prev = tf.complex(input_ph_diff_matrix[:,:,:,0], input_ph_diff_matrix[:,:,:,1])
    ph_diff_next = tf.complex(input_ph_diff_matrix[:,:,:,2], input_ph_diff_matrix[:,:,:,3])
        
    Op_pred = Lambda( lambda x: spec_predict( x[0], x[1]), name="predict_prev" )( [Op, ph_diff_prev] )
    On_pred = Lambda( lambda x: spec_predict( x[0], x[1]), name="predict_next" )( [On, ph_diff_next] )
    
    
    if sparse_second_stage:
        Ic = tf.expand_dims( IcMc[...,0], axis=-1 )
        
        Mp = tf.expand_dims( IpMp[...,1], axis=-1 )
        Mc = tf.expand_dims( IcMc[...,1], axis=-1 )        
        Mn = tf.expand_dims( InMn[...,1], axis=-1 )
        
        W = Concatenate()([Mp,8*Mc,Mn])
        W = W / (tf.reduce_sum( W, axis=-1, keepdims=True) +1E-8 )
        
        V = Concatenate()([Op_pred, Ic, On_pred])
        M = tf.sign( Mp+Mc+Mn )
        V = tf.reduce_sum( V * W , axis=-1, keepdims=True ) * M
                
        k = generate_IDW_kernel( ksize=21, exp=2.8 )
        k = np.expand_dims( k, axis=(-1,-2))
        k = tf.constant(k)
                
        # convolve image and mask with fixed kernels
        I_IDW = tf.nn.conv2d( V, k, strides=1, padding="SAME")
        M_IDW = tf.nn.conv2d( M, k, strides=1, padding="SAME")
        I_IDW = Lambda( lambda x: x[0]/(x[1]+1E-9) )( [I_IDW, M_IDW] )
        
        V = (V - I_IDW)*M
        
        V,M = sparse_conv_block( V, M, (5,5), 32)
        V = Activation('relu')( V )
        
        V,M = sparse_conv_block( V, M, (3,3), 16)
        V = Activation('relu')( V )
        
        V,M = sparse_conv_block( V, M, (3,3), 8)
        V = Activation('relu')( V )
        
        V,M = sparse_conv_block( V, M, (1,1), 1)
        V = Activation('linear')( V )
        
        V += I_IDW
                
        model = Model(inputs = [input_data,input_ph_diff_matrix], outputs=V )
        
        
    else:
        Oc = model_sparsecnn( IcMc )
        Oc = Lambda( lambda x: x, name="curr" )( Oc )
        Oc = Concatenate()([Op_pred, Oc, On_pred])

        Oc = Convolution2D( 16, (5,5), padding='same', use_bias=True, activation="sigmoid") ( Oc )
        Oc = Convolution2D( 16, (3,3), padding='same', use_bias=True, activation="sigmoid") ( Oc )
        Oc = Convolution2D( 8, (3,3), padding='same', use_bias=True, activation="sigmoid") ( Oc )
        Oc = Convolution2D( 1, (1,1), padding='same', use_bias=True, activation="linear") ( Oc )

        model = Model(inputs = [input_data,input_ph_diff_matrix], outputs=Oc )
    return model
    
