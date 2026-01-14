from specfit.gausswin import gausswin_m
import numpy as np
from pynfft import NFFT
import time

class SpecfitNFFT():

    def __init__( self, N, alpha=12 ):
        """
        N: spectrum size
        alpha: smoothness factor. low alpha -> smoother surface. (ie. spectrum is less forced to pass trough the points)
        """

        print("Initializing SpecfitNFFT with N=%d, alpha=%2.3f"%(N,alpha) )
        self.N = N
        self.M = 0
        self.SPECSIZE = N*N
        #self.w = gausswin_m( N, alpha )
        #self.w = np.expand_dims( self.w.flatten(order='C'), axis=1)
        self.set_alpha( alpha )


    def set_alpha( self, alpha ):
        self.w = gausswin_m( self.N, alpha )
        self.w[ int(self.N/2), int(self.N/2) ] = 0
        self.w = np.expand_dims( self.w.flatten(order='C'), axis=1)


    def setup( self, nodes, spec_sq, b ):

        assert( nodes.shape[1] == 2 )
        self.M = nodes.shape[0]
        self.initial_err = self.final_err = -1
        self.spec = np.expand_dims( spec_sq.flatten(order='C'), axis=1 )
        
        xv = self.w * self.spec
        self.XX = np.concatenate( (xv, np.expand_dims(np.random.randn( self.M ),axis=1) ) ).astype( np.complex64 )
        self.BB = np.concatenate( (xv, b) ).astype(np.complex64)

        #print("Type: ",nodes.dtype)

        #self.plan = NFFT( [self.N,self.N], self.M, flags=('FG_PSI','PRE_FG_PSI') )
        self.plan = NFFT( [self.N,self.N], self.M, flags=('PRE_PHI_HUT','PRE_FULL_PSI') )
        self.plan.x = nodes.astype( np.float32 )
        self.plan.precompute()




    def optimize( self, mit=2000, stol=1E-8, verbose=False ):
        start_time = time.time()

        SPECSIZE = self.SPECSIZE

        def bbA( XX, w, plan, OUT ):
            xv = XX[ 0:SPECSIZE ]
            lambdav = XX[ SPECSIZE: ]
            plan.f_hat = xv
            OUT[SPECSIZE:] = np.expand_dims( plan.trafo(), axis=1)
            plan.f = lambdav
            fhat = np.expand_dims( plan.adjoint().flatten(order='C'), axis=1 )
            OUT[0:SPECSIZE]= w*xv + fhat
            return OUT

        OUT = np.copy(self.BB)
        x = self.XX 
        prev_x = x
        hp = 0
        hpp = 0
        rp = 0
        rpp = 0
        u = 0
        k = 0
        
        ra = self.BB - bbA( self.XX, self.w, self.plan, OUT )
        err = np.linalg.norm(ra, None)
        self.initial_err = err
        if verbose:
            print(' Initial err: %e ' % err )
        nit=1

        while (err > stol):
            ha = ra; # <--- ha = C \ ra;
            k = k + 1
            if k == mit:
                if verbose:
                    print(' Max iters (%d) reached.' % mit)
                break
            
            hpp = hp
            rpp = rp
            hp = ha
            rp = ra
            t = np.sum(np.conj(rp)*hp)

            if k == 1:
                u = hp
            else:
                u = hp + (t / np.vdot(rpp,hpp)) * u
        
            Au = bbA( u, self.w, self.plan, OUT); # <--- Au = A * u;

            a = t / np.vdot( u,Au )
            x = x + a * u
            ra = rp - a * Au
            if k%150 == 0:
                prev_err = err
                err = np.linalg.norm(ra, None); 
                # print(err)
                if np.isnan(err) or prev_err < err:
                    x = prev_x
                    break
                prev_x = x

            nit = nit + 1   
            
        if verbose:
            print(' Final err: %e' % err )
            
        self.final_err = err
        self.spout = np.reshape( x[ 0:(self.plan.N[0]*self.plan.N[1]) ], self.plan.N, order='C' )
        end_time = time.time()
        return {"opt_time": ( end_time - start_time), "opt_nit": nit}


        

if __name__ == '__main__':
    print("Running specfit_nfft.py in TEST mode")
    import scipy.io as sio
    data = sio.loadmat('in.mat')
    specfit = SpecfitNFFT( np.asscalar(data["N"]), np.asscalar(data["alpha"]) )
    specfit.setup( data["nodes"], data["spec_sq"], data["b"] )
    specfit.optimize( np.asscalar(data["mit"]), np.asscalar(data["tol"]))
    sio.savemat( 'out.mat', {'spec_out3': specfit.spout })