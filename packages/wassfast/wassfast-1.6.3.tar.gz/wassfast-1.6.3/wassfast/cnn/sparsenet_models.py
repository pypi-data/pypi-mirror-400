from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input
from tensorflow.keras.layers import Layer
from tensorflow.keras.layers import Dense, Dropout, LeakyReLU, ReLU, Activation, Flatten, Reshape, UpSampling2D, Add, Lambda, SeparableConv2D
from tensorflow.keras.layers import Convolution2D, SeparableConv2D, MaxPooling2D, Concatenate, Add, Multiply, Softmax, Conv2DTranspose, AveragePooling2D
from tensorflow.keras import backend as K
import tensorflow as tf
import tensorflow.keras.initializers 



###  A simple Bias-only layer implementation
###   we assume a channel-last layout
###
class Bias(Layer):

    def __init__(self, **kwargs):
        super(Bias, self).__init__(**kwargs)

    def build(self, input_shape):

        self.bias = self.add_weight(name='bias',
                            #shape=(input_shape[1],input_shape[2],input_shape[3]),
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
###
def sparse_conv_block( I, M, ksize, depth ):

    IM = Multiply( )([I,M] )

    IMc = Convolution2D( depth, ksize, 
                         padding='same', 
                         #kernel_initializer = tensorflow.keras.initializers.Constant( 1.0/(ksize[0]*ksize[1]) ),
                         use_bias=False, 
                         activation=None) ( IM )

    # A hack to convolve with a fixed "ones" kernel
    Mc = Convolution2D( 1, ksize, padding='same', use_bias=False, activation=None, 
                        kernel_initializer = 'ones',
                        trainable=False) ( M )


    Inorm = Lambda( lambda x: x[0]/(x[1]+1E-8) )( [IMc,Mc] )
    
    InormB = Bias( )(Inorm)

    #Mpooled = MaxPooling2D(pool_size=(2,2), strides=(1,1), padding='same')(M)
    Mpooled = MaxPooling2D(pool_size=ksize, strides=(1,1), padding='same')(M)

    return InormB, Mpooled

    

def create_sparseconv_256_model( N, input_layer=None, trainable=True ):

    if input_layer is None:
        input_data = Input( shape=(N,N,2) )
    else:
        input_data = input_layer
    
    I = Lambda( lambda x: K.expand_dims(x[:,:,:,0],axis=-1), name="I0" )( input_data )
    M = Lambda( lambda x: K.expand_dims(x[:,:,:,1],axis=-1), name="M0" )( input_data )
    
    I,M = sparse_conv_block( I, M, (11,11), 16)
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
    
    if not trainable:
        for l in model.layers:
            l.trainable = False
    
    return model

