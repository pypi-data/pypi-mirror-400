from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import os.path
from mako.template import Template
import dateutil.parser
from tqdm import tqdm
import cv2 as cv
import glob


class NetCDFAnalysis():

    def __init__(self, ncfile, upload_url="", fps=None ):
        self.NCFILE = ncfile
        _, self.ncfilef = os.path.split(self.NCFILE)

        self.upload_url = upload_url
        self.root = Dataset( self.NCFILE, "r", format="NETCDF4" )

        self.scriptpath, _ = os.path.split( __file__ )
        self.htmltemplate =  Template(filename=os.path.join(self.scriptpath,"analysis_template.html"), strict_undefined=True)

        self.timestring = "unknown"
        self.datadatetime = None 
        self.fps = fps

        try:
            if self.fps is None:
                # Try to read fps data from netCDF meta attributes
                self.fps = self.root["/meta"].getncattr("fps")
                if self.fps == 0:
                    self.fps = None
                    print("Unable to infer dataset fps from meta attributes")

            self.timestring = self.root["/meta"].getncattr("timestring")
            self.datadatetime = dateutil.parser.parse(self.timestring)
        except (AttributeError,IndexError,dateutil.parser.ParserError):
            print("Unable to read /meta/timestring from nc file.")


    def get_ncfile_info( self ):
        S = ""
        S += "Dataset: %s\n"%self.ncfilef
        S += "------------------------------------------------------\n"
        S += "/ Variables:\n"
        for v in self.root.variables:
            S += " - %s\n"%v
        S += "Attributes:\n"
        for a in self.root.ncattrs():
            S += " - %s = %s\n"%(a,self.root.getncattr(a))
        S += "Groups: \n"
        for g in self.root.groups:
            S += " %s\n"%self.root[g].path
            S += "  Variables:\n"
            for v in self.root[g].variables:
                S += "    - %s\n"%v
            S += "  ncattrs:\n"
            for a in self.root[g].ncattrs():
                S += " - %s = %s\n"%(a,self.root[g].getncattr(a))
        return S


    def filetobase64( filename ):
        import base64
        with open(filename,'rb') as f:
            
            fb64 = base64.b64encode( f.read() )
            return fb64


    def analyse( self ):

        print("--------------------------------------")
        print("Analysing %s"%self.ncfilef )
        
        plt.rcParams.update({'font.size': 18})

        nsamples = self.root["/Z"].shape[0]
        gridsize = self.root["/Z"].shape[1:3]

        halfgridsize_i = int( gridsize[0]/2)
        halfgridsize_j = int( gridsize[1]/2)
        valid_samples_i = range( halfgridsize_i-5, halfgridsize_i+6 )
        valid_samples_j = range( halfgridsize_j-5, halfgridsize_j+6 )

        print(" - Creating frame image")
        try:
            I0 = cv.imdecode( self.root["/cam0images"][1], cv.IMREAD_GRAYSCALE )
            I0 = cv.pyrDown(I0)
            cv.imwrite( os.path.join(self.scriptpath,"frame.jpg"),I0)
            I0 = None
        except:
            print("   NetCDF file contains no frame data")
            # We write a null image instead
            cv.imwrite(os.path.join(self.scriptpath,"frame.jpg"), np.ones( (2,3), dtype=np.uint8 )*255)


        # -------------------------------------------------------------------------- TIMESERIE
        print(" - Computing statistics on the grid center timeserie")
        t = np.array(self.root["/time"])
        dt = t[2]-t[1]
        if dt==0.0 and (self.fps is None):
            print("Zero dt between frames, and no FPS specified. Aborting.")
            return 

        if not self.fps is None:
            dt = 1.0/self.fps
            t = np.arange( 0, t.shape[0])*dt

        print("   dt: %1.5f  (%d FPS)"%(dt,np.round(1/dt)))


        timeserie = self.root["/Z"][:,halfgridsize_i,halfgridsize_j] * 1E-3
        timeserie = timeserie - np.mean(timeserie)

        def crossings_nonzero_pos2neg(data):
            pos = data > 0
            return (pos[:-1] & ~pos[1:]).nonzero()[0]

        crossings = crossings_nonzero_pos2neg(timeserie)

        if len(crossings)<2:
            print("Too few zero crossings found. Sequence too short?")
            print("Aborting")
            return

        dmins = []
        dmaxs = []
        for ii in range( np.size(crossings)-1 ):
            datarange = np.arange(crossings[ii], crossings[ii+1])
            data = timeserie[ datarange ]
            dmax = np.argmax(data)
            dmin = np.argmin(data)
            dmins.append( datarange[dmin] )
            dmaxs.append( datarange[dmax] )
            
        waveheights = np.array(timeserie[dmaxs]) - np.array(timeserie[dmins])
        q = np.quantile( waveheights, 2.0/3.0)
        print("   timeserie quantile: ", q)

        highestthirdwaves = waveheights[ waveheights>q ]
        H13 = np.mean(highestthirdwaves)
        print("   H1/3: ", H13)

        plt.figure( figsize=(20,10))
        plt.plot(t, timeserie )
        plt.scatter( t[crossings], np.zeros_like(crossings), c="r")
        plt.scatter( t[dmins], timeserie[dmins], c="b")
        plt.scatter( t[dmaxs], timeserie[dmaxs], c="g")
        plt.grid()
        plt.title("Timeserie at grid center. %d waves"%np.size(waveheights))
        plt.xlabel("Time (secs.)")
        plt.ylabel("Height (m)")
        plt.savefig(os.path.join(self.scriptpath,"timeserie.png"))

        Zcube = np.array( self.root["/Z"][:,valid_samples_i,valid_samples_j] * 1E-3 )
        Hs = 4.0*np.std( Zcube-np.mean(Zcube) )
        print("   Hs: ", Hs)
        Zcube = None

        # -------------------------------------------------------------------------- 1D SPECTRUM
        print(" - Analyzing 1D spectrum")

        import scipy.signal

        f, S = scipy.signal.csd(timeserie, timeserie, 1.0/dt, nperseg=512 )

        for ii in tqdm(valid_samples_i):
            for jj in valid_samples_j:
                timeserie_neigh = self.root["/Z"][:,ii,jj] * 1E-3
                timeserie_neigh = timeserie_neigh - np.mean(timeserie_neigh)
                _, S_neig = scipy.signal.csd(timeserie_neigh, timeserie_neigh, 1.0/dt, nperseg=512 )
                S += S_neig

        S = S / float( np.size(valid_samples_i)*np.size(valid_samples_j) + 1)

        plt.figure( figsize=(10,10) )
        plt.loglog( f, S)
        plt.xticks([1E-2,1E-1,1E0,1E1])
        plt.grid(which='minor')
        plt.ylabel("S (m^2s)")
        plt.xlabel("f_a (1/s)")
        plt.title("Spectrum (Welch method) averaged in central grid region")
        plt.savefig(os.path.join(self.scriptpath,"spectrum.png"))

        # Compute Hs
        dFreq = np.gradient( f )
        m0 = np.sum( S*dFreq )
        m1 = np.sum( f*S*dFreq )
        Hm0 = 4.0 * np.sqrt( m0 )
        print("   Hm0: ", Hm0)

        # Peak frequency
        pp = f[np.argmax( S )]
        print("   Peak frequency (Hz): ", pp)

        # Average Period Tm01
        Tm01 = m0/m1
        print("   Tm01: ", Tm01)


        # -------------------------------------------------------------------------- 3D SPECTRUM
        print(" - Analyzing space-time 3D spectrum")
        Z = self.root["/Z"][3,:,:]
        N = Z.shape[0]
        Nm = int( N/2 )
        dy = (self.root["/Y_grid"][2,0] - self.root["/Y_grid"][1,0])/1000.0
        dx = (self.root["/X_grid"][0,2] - self.root["/X_grid"][0,1])/1000.0
        print("   grid dx,dy: ", dx,dy)

        if np.abs( dx-dy ) < 1E-3:
            dy = dx  # force dx = dy if very close to avoid numerical errors

        # Extract a central part of the Zcube
        N = 140
        min_freq = 0.25
        max_freq = 0.7
        num_plots = 10
        segments = 5 

        sequence_length = np.size(timeserie)
        Nt = int(sequence_length / segments)
        if Nt%2 > 0:
            Nt+=1
        seg_shift = int(Nt/2)

        Zcube_mr = int( self.root["/Z"].shape[1] / 2 )
        Zcube_mc = int( self.root["/Z"].shape[2] / 2 )
        r_start, r_end = Zcube_mr-int(N/2)-20, Zcube_mr+int(N/2)-20+1
        c_start, c_end = Zcube_mc-int(N/2), Zcube_mc+int(N/2)+1 

        Nx = r_end - r_start
        Ny = c_end - c_start
        print("   Nx,Ny,Nt: ",Nx,Ny,Nt)

        kx_max=(2.0*np.pi/dx)/2.0
        ky_max=(2.0*np.pi/dy)/2.0
        f_max= (1.0/dt)/2.0
        dkx=2.0*np.pi/(dx*np.floor(Nx/2.0)*2.0)
        dky=2.0*np.pi/(dy*np.floor(Ny/2.0)*2.0)
        df =1.0/(dt*np.floor(Nt/2.0)*2.0)

        #print("   kx_max, ky_max, f_max, dkx, dky, df: ", kx_max, ky_max, f_max, dkx, dky, df)

        assert( Nx%2 != 0)
        assert( Ny%2 != 0)
        assert( Nt%2 == 0)

        kx=np.arange(-kx_max,kx_max+dkx,dkx)
        ky=np.arange(-ky_max,ky_max+dky,dky)

        if Nt%2==0:
            f=np.arange(-f_max, f_max, df)
        else:
            f=np.arange(-f_max, f_max+df, df)

        KX, KY = np.meshgrid( kx, ky )
        dkx=kx[3]-kx[2]
        dky=ky[3]-ky[2]
        KXY=np.sqrt(KX**2+KY**2)
        print("   kdx, dky: ", dkx, dky)


        hanningx = scipy.signal.windows.hann(KX.shape[0])
        hanningy = scipy.signal.windows.hann(KX.shape[1])
        hanningt = scipy.signal.windows.hann(Nt)

        Win3Dhann = np.tile( np.expand_dims( hanningx, axis=-1) * hanningy, (Nt,1,1) ) *  np.tile( np.expand_dims( np.expand_dims( hanningt, axis=-1 ), axis=-1 ), (1, KX.shape[0], KX.shape[1]) )
        assert( KX.shape == Win3Dhann.shape[1:] )

        #  window correction factors
        wc2x = 1.0/np.mean(hanningx**2)
        wc2y = 1.0/np.mean(hanningy**2)
        wc2t = 1.0/np.mean(hanningt**2)
        wc2xy  = wc2x *wc2y
        wc2xyt = wc2xy*wc2t

        print("   dt, dkx, dky, df: ",dt, dkx, dky, df)

        # Fix for rounding errors
        r_end = r_start + Win3Dhann.shape[1]
        c_end = c_start + Win3Dhann.shape[2]

        S_welch = np.zeros_like( Win3Dhann )
        n_samples = 0
        print("   Computing 3D FFT via Welch's method... ", end="")
        for ii in tqdm(range(segments*2)):
            #print("Welch sample %d/%d"%(ii+1,segments*2))
            Zcube_small = np.array( self.root["/Z"][(ii*seg_shift):(ii*seg_shift+Nt), r_start:r_end, c_start:c_end ] )
            if Zcube_small.shape[0] != Nt:
                break
                
            Zcube_w = (Zcube_small - np.mean(Zcube_small) ) * Win3Dhann
            
            S = np.fft.fftshift( np.fft.fftn( Zcube_w, norm="ortho" ) )
            S /= (S.shape[0]*S.shape[1]*S.shape[2])
            S = np.abs(S)**2 / (dkx*dky*df)
            #-----------------------------
            #%%%%% corrects for window
            #----------------------------
            #%% FABIEN
            S *= wc2xyt
            
            # Store
            S_welch += S    
            n_samples += 1
            
        S_welch /= n_samples    
        print(" Done!")


        start_freq_ii = np.argmin( np.abs(f-min_freq) )
        end_freq_ii = np.argmin( np.abs(f-max_freq) )
        indices = np.round( np.linspace(start_freq_ii, end_freq_ii, num_plots ) ).astype(np.uint32)

        print("  Generating plots")
        kk=0
        for ii in tqdm(indices):

            plt.figure( figsize=(11,10))    

            #dummy = np.flipud( 2* np.mean(S_welch[ mdt+ii-1:mdt+ii+2,:,:], axis=0) )    
            dummy = 2* np.mean(S_welch[ ii-1:ii+2,:,:], axis=0) 
            
            dummy_cen = np.copy(dummy)
            dummy_cen[ int(dummy_cen.shape[0]/2)-1:int(dummy_cen.shape[0]/2)+1, int(dummy_cen.shape[1]/2)-1:int(dummy_cen.shape[1]/2)+1 ] = 0
            maxidx = np.unravel_index( np.argmax(dummy_cen), dummy_cen.shape )
            
            qp=( np.arctan2( KY[ maxidx[0],maxidx[1] ], KX[ maxidx[0],maxidx[1] ]) )/np.pi*180.0
            if qp<0:
                qp=qp+360

            kp=np.sqrt( KX[ maxidx[0],maxidx[1] ]**2 + KY[ maxidx[0],maxidx[1] ]**2 );

            plt.pcolor(KX,KY, 10*np.log10(dummy) )
            plt.clim( 10*np.array([-4.0 + np.amax(np.log10(dummy)), -0+np.amax(np.log10(dummy))]) )
            plt.colorbar()

            plt.scatter( [KX[ maxidx[0],maxidx[1] ]], [KY[ maxidx[0],maxidx[1] ]], marker="x", s=100, c="k" )

            plt.ylim([-3.0,3.0])
            plt.xlim([-3.0,3.0])

            plt.xlabel("Kx (rad/m)")
            plt.ylabel("Ky (rad/m)")
            plt.title("S_kx_ky, fa=%3.2f (Hz).\n Peak angle: %3.0f°, mag: %2.3f (rad/m)\n"%( f[ii],qp,kp ) )
            plt.savefig(os.path.join(self.scriptpath,"spectrum_dir_%03d.png"%kk))
            kk+=1



        # -------------------------------------------------------------------------- REPORT 

        print(" - Generating report")
        datafile = ""
        try:
            datafile = self.root["/meta"].getncattr("datafile") 
        except:
            pass

        location = "unknown"
        try:
            location = self.root["/meta"].getncattr("location") 
        except:
            pass

        T = self.htmltemplate.render(   title="%s wave analysis"%self.ncfilef,
                                        framedata=NetCDFAnalysis.filetobase64(os.path.join(self.scriptpath,"frame.jpg")).decode("ascii"),
                                        timeseriedata=NetCDFAnalysis.filetobase64(os.path.join(self.scriptpath,"timeserie.png")).decode("ascii"),
                                        spectrumdata=NetCDFAnalysis.filetobase64(os.path.join(self.scriptpath,"spectrum.png")).decode("ascii"),
                                        dirspectrumdata1=NetCDFAnalysis.filetobase64(os.path.join(self.scriptpath,"spectrum_dir_000.png")).decode("ascii"),
                                        dirspectrumdata2=NetCDFAnalysis.filetobase64(os.path.join(self.scriptpath,"spectrum_dir_001.png")).decode("ascii"),
                                        dirspectrumdata3=NetCDFAnalysis.filetobase64(os.path.join(self.scriptpath,"spectrum_dir_002.png")).decode("ascii"),
                                        dirspectrumdata4=NetCDFAnalysis.filetobase64(os.path.join(self.scriptpath,"spectrum_dir_003.png")).decode("ascii"),
                                        dirspectrumdata5=NetCDFAnalysis.filetobase64(os.path.join(self.scriptpath,"spectrum_dir_004.png")).decode("ascii"),
                                        dirspectrumdata6=NetCDFAnalysis.filetobase64(os.path.join(self.scriptpath,"spectrum_dir_005.png")).decode("ascii"),
                                        dirspectrumdata7=NetCDFAnalysis.filetobase64(os.path.join(self.scriptpath,"spectrum_dir_006.png")).decode("ascii"),
                                        dirspectrumdata8=NetCDFAnalysis.filetobase64(os.path.join(self.scriptpath,"spectrum_dir_007.png")).decode("ascii"),
                                        dirspectrumdata9=NetCDFAnalysis.filetobase64(os.path.join(self.scriptpath,"spectrum_dir_008.png")).decode("ascii"),
                                        dirspectrumdata10=NetCDFAnalysis.filetobase64(os.path.join(self.scriptpath,"spectrum_dir_009.png")).decode("ascii"),
                                        hs="%2.3f"%Hs,
                                        hm0="%2.3f"%Hm0,
                                        pp="%2.3f"%pp,
                                        Tm01="%3.3f"%Tm01,
                                        location=location,
                                        date=self.datadatetime.date() if self.datadatetime else "unknown",
                                        time=self.datadatetime.time() if self.datadatetime else "unknown",
                                        ncfile="%s (%s)"%(self.ncfilef,datafile ),
                                        duration="%d secs."%(t[-1]-t[0]),
                                        fps="%3.1f"%(1.0/dt),
                                        meta=self.get_ncfile_info( ).replace('\n','<br />'))

        outfile =  self.NCFILE.replace(".nc",".html")
        print(" - Writing ", outfile)
        with open( outfile,"w") as f:
            f.write(T)

        pngfiles = glob.glob( os.path.join(self.scriptpath,"*.png") )
        jpgfiles = glob.glob( os.path.join(self.scriptpath,"*.jpg") )

        for f in pngfiles:
            os.remove( os.path.join(self.scriptpath, f ) )

        for f in jpgfiles:
            os.remove( os.path.join(self.scriptpath, f ) )


        if self.upload_url:
            import subprocess

            try:
                for attempts in range(3):
                    callarr = ["curl.exe" if os.name=="nt" else "curl", "-F", "the_file=@%s"%outfile, self.upload_url ]
                    #print("Calling ", callarr)
                    print(" - Uploading to ", self.upload_url )
                    cp = subprocess.run(callarr)
                    if cp.returncode == 0:
                        break
                    else:
                        print("    Bad return code, trying again...")
            except:
                print("   ERROR: Unable to call curl!")


        print(" - All done!")





if __name__ == "__main__":
    #nca = NetCDFAnalysis( "D:\\dev\\wassfast\\analysis\\wass__20181006_140000_step03.nc")
    #nca = NetCDFAnalysis("D:\\dev\\wassfast\\analysis\\wassfast__20181006_140000_smooth_0.35.nc")
    nca = NetCDFAnalysis("D:\\dev\\wassfast_testdata\\wassfast_output.nc")
    nca.analyse()
