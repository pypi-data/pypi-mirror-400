import numpy as np
from keras.utils import Sequence

class SparseSeriesDataGenerator( Sequence):
    'Generates data for Keras'
    
    def __init__(self, data, sampling_ratio, KxKy, angle, dt, to_fit=True, batch_size=32, dim=(256,256), n_channels=2, shuffle=True):
        
        'Initialization'
        self.data = data
        self.sampling_ratio = sampling_ratio
        #self.zminmax = zminmax
        self.to_fit = to_fit
        self.batch_size = batch_size
        self.dim = dim
        self.ndim = dim
        self.n_channels = n_channels
        self.shuffle = shuffle
        self.curr_idx = np.arange(data.shape[0])
        
        phmatrix = np.expand_dims( self._compute_phase_diff_matrix( KxKy[:,:,0], KxKy[:,:,1], angle, dt), axis=-1)
        phmatrix_conj = np.conj(phmatrix)
        
        phmatrix_concat = np.concatenate( (np.real(phmatrix), np.imag(phmatrix), np.real(phmatrix_conj), np.imag(phmatrix_conj)), axis=2 )
        
        self.ph_diff_mat = np.tile( phmatrix_concat, (self.batch_size, 1, 1, 1) )
        #print(self.ph_diff_mat.shape)
        
        if not isinstance(sampling_ratio, (list, tuple, np.ndarray)): #if sampling_ratio is a scalar
            self.sampling_ratio = (sampling_ratio, sampling_ratio)

        self.on_epoch_end() # if we want the generator to do something after every epoch
        
        
    def __len__(self):
        'Denotes the number of batches per epoch'
        return int(np.floor(self.data.shape[0] / self.batch_size))
    
    
    def __getitem__(self, index):
        """Generates one batch of data
            :param index: index of the batch
            :return: X and y when fitting. X only when predicting
            """
        # Generate indexes of the batch
        max_idx = np.minimum((index+1)*self.batch_size, self.data.shape[0]);
        indexes = self.curr_idx[ index*self.batch_size:max_idx ]
        indexes = np.sort(indexes)
        #print(indexes)
        
        # gt images
        gt_data = self.data[indexes,:,:,:]
        
        # scale data
        #gt_data = (gt_data - self.zminmax[0]) / (self.zminmax[1] - self.zminmax[0])
        
        #print(gt_data.shape)
        
        # Generate data
        X_p = self._generate_X(gt_data[:,:,:,0])
        X_c = self._generate_X(gt_data[:,:,:,1])
        X_n = self._generate_X(gt_data[:,:,:,2])
        
        X = np.concatenate((X_p, X_c, X_n), axis=3)
        
        # scale between batch min and max
        data_min = np.nanmin(X)
        data_max = np.nanmax(X)
        
        X = ( X - data_min) / (data_max - data_min)
        
        #print(np.nanmin(X))
        #print(np.nanmax(X))
        
        if self.to_fit:
            y = np.expand_dims(gt_data[:,:,:,1], axis=-1)
            y = (y - data_min) / (data_max - data_min)
            return [X, self.ph_diff_mat], y
        else:
            return [X, self.ph_diff_mat]
    
    
    def on_epoch_end(self):
        """Updates random indexes after each epoch if shuffle == true
        """
        if self.shuffle == True:
            np.random.shuffle(self.curr_idx)


    def _generate_X(self, gt_data):
        'Generates sparse data with binary masks'
        
        # same probability for all pixels
        #mask = np.random.binomial(1, self.sampling_ratio, gt_data.shape)
        
        P = np.random.rand(gt_data.shape[0],1,1) * (self.sampling_ratio[1] - self.sampling_ratio[0]) + self.sampling_ratio[0]
        P = np.tile(P, (1, gt_data.shape[1], gt_data.shape[2]))
                
        mask = np.random.binomial(1, P)
        #print(mask.dtype)
        
        mask = mask.astype('float')
        mask[mask == 0] = float('nan')
        sparse_data = mask * gt_data
        
        sparse_data = np.expand_dims(sparse_data, axis=3)
        mask = np.expand_dims(mask, axis=3)
        
        #X = np.concatenate((sparse_data, mask), axis=3)
        X = sparse_data

        return X

    
    def _compute_phase_diff_matrix( self, KX_ab, KY_ab, angle, dt, depth=np.inf, current_vector=[0.0, 0.0] ):
        'computes complex matrix for current scene'
        
        xsign = -np.sign(np.cos(angle))
        ysign = -np.sign(np.sin(angle))
        
        Kmag = np.sqrt( KX_ab*KX_ab + KY_ab*KY_ab )
        Ksign = np.sign( (xsign*KX_ab) + ( ysign*KY_ab) )

        omega_sq = 9.8 * Kmag * ( 1.0 if depth == np.inf else np.tanh( Kmag*depth )  )

        ph_diff = Ksign*( np.sqrt(omega_sq) + KX_ab*current_vector[0] + KY_ab*current_vector[1] )*dt
        ph_diff = np.triu(ph_diff) - np.tril(ph_diff )

        return np.exp(1j*np.fft.fftshift( ph_diff*( np.triu(-np.ones(KX_ab.shape)) + np.tril(+np.ones(KX_ab.shape)) ) ) )



'''
class SparseSeriesDataGenerator( Sequence):
    'Generates data for Keras'
    
    def __init__(self, data, sampling_ratio, to_fit=True, batch_size=32, dim=(256,256), n_channels=2, shuffle=True):
        
        'Initialization'
        self.data = data
        self.sampling_ratio = sampling_ratio
        self.to_fit = to_fit
        self.batch_size = batch_size
        self.dim = dim
        self.ndim = dim
        self.n_channels = n_channels
        self.shuffle = shuffle
        self.curr_idx = np.arange(data.shape[0])
        
        if not isinstance(sampling_ratio, (list, tuple, np.ndarray)): #if sampling_ratio is a scalar
            self.sampling_ratio = (sampling_ratio, sampling_ratio)

        self.on_epoch_end() # if we want the generator to do something after every epoch
        
        
    def __len__(self):
        'Denotes the number of batches per epoch'
        return int(np.floor(self.data.shape[0] / self.batch_size))
    
    
    def __getitem__(self, index):
        """Generates one batch of data
            :param index: index of the batch
            :return: X and y when fitting. X only when predicting
            """
    
        # Generate indexes of the batch
        max_idx = np.minimum((index+1)*self.batch_size, self.data.shape[0]);
        indexes = self.curr_idx[ index*self.batch_size:max_idx ]
        indexes = np.sort(indexes)
        
        #print(indexes)
        
        # gt images
        gt_data = self.data[indexes,:,:,:]
        
        #print(gt_data.shape)
        
        # Generate data
        X_p = self._generate_X(gt_data[:,:,:,0])
        X_c = self._generate_X(gt_data[:,:,:,1])
        X_n = self._generate_X(gt_data[:,:,:,2])
        
        X = np.concatenate((X_p, X_c, X_n), axis=3)

        if self.to_fit:
            y = np.expand_dims(gt_data[:,:,:,1], axis=3)
            #y= gt_data
            return X, y
        else:
            return X
    
    
    def on_epoch_end(self):
        """Updates random indexes after each epoch if shuffle == true
        """
        if self.shuffle == True:
            np.random.shuffle(self.curr_idx)


    def _generate_X(self, gt_data):
        'Generates sparse data with binary masks'
        
        # same probability for all pixels
        #mask = np.random.binomial(1, self.sampling_ratio, gt_data.shape)
        
        P = np.random.rand(gt_data.shape[0],1,1) * (self.sampling_ratio[1] - self.sampling_ratio[0]) + self.sampling_ratio[0]
        P = np.tile(P, (1, gt_data.shape[1], gt_data.shape[2]))
                
        mask = np.random.binomial(1, P)
        #print(mask.dtype)
        
        mask = mask.astype('float')
        mask[mask == 0] = float('nan')
        sparse_data = mask * gt_data
        
        sparse_data = np.expand_dims(sparse_data, axis=3)
        mask = np.expand_dims(mask, axis=3)
        
        #X = np.concatenate((sparse_data, mask), axis=3)
        X = sparse_data

        return X
'''