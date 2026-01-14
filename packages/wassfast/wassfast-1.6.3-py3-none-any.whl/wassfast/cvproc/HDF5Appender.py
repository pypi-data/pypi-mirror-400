import h5py
import numpy as np


class HDF5Appender:

    def __init__( self, filename ):
        self.f = h5py.File( filename, "w")
        self.datasets = {} 


    def add_dataset( self, dataset_name, shape, dtype=np.float32, chunk_size=32 ):
        shape_array = [ k for k in shape ]  
        d = self.f.create_dataset( dataset_name, [0]+shape_array, maxshape=[None]+shape_array, dtype=dtype, chunks= tuple( [chunk_size]+shape_array) )
        self.datasets[dataset_name] = d

    def has_dataset( self, dataset_name ):
        return dataset_name in self.datasets

    def append( self, dataset_name, samples ):
        d = self.datasets[dataset_name]
        if samples.ndim == d.ndim - 1:
            samples = np.expand_dims( samples, axis=0 )
        
        assert samples.ndim == d.ndim, "Wrong sample shape"

        for ii in range(1,samples.ndim):
            assert d.shape[ii] == samples.shape[ii], "Wrong sample shape"

        d.resize( (d.shape[0] + samples.shape[0]), axis=0 )
        d[-samples.shape[0]:] = samples

    def close( self ):
        self.f.close()


# if __name__ == "__main__":
#     d = HDF5Appender("test.h5")
#     print(d.has_dataset("X"))
#     d.add_dataset("X", (3,4,1), np.float32)
#     print(d.has_dataset("X"))
#     d.add_dataset("Y", (3,3), np.float32)

#     sample = np.zeros( (10,3,4,1), dtype=np.float32 )
#     sample2 = np.zeros( (3,4,1), dtype=np.float32 )
#     sample3 = np.zeros( (100,3,3), dtype=np.float32 )

#     d.append( "X", sample )
#     d.append( "X", sample2 )
#     d.append( "Y", sample3 )

#     d.close()