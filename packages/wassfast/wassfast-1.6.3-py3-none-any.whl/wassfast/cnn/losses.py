import tensorflow as tf
from tensorflow.keras import backend as K



def ms_ssim_loss(yTrue, yPred):
    return 1 - tf.image.ssim_multiscale(yTrue, yPred, max_val=1 )


def ssim_loss(yTrue, yPred):
    return 1 - tf.image.ssim(yTrue, yPred, max_val=1 )


def l2_loss(yTrue, yPred):
    return K.mean( K.square(yTrue - yPred) )


def l1_loss(yTrue, yPred):
    return K.mean( K.abs(yTrue - yPred) )


def combined_loss(yTrue, yPred, alpha=0.84):
    #return alpha * ms_ssim_loss(yTrue, yPred) + (1-alpha) * l1_loss(yTrue, yPred)
    return alpha * ssim_loss(yTrue, yPred) + (1-alpha) * l1_loss(yTrue, yPred)