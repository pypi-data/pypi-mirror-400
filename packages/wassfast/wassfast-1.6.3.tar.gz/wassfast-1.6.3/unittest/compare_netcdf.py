import numpy as np
import scipy
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import tqdm
import glob
import os


NETCDF_WASS = "./gridding/gridded.nc"
method1 = "WASS"

NETCDF_WASSFAST = "./gridding/gridded_wassfast_fnbk.nc"
ptsdir = "./pts_fnbk"
OUTDIR = "./comparison/"
method2 = "WASSfast FNBK"

def delete_files_in_directory(directory_path):
   try:
     files = glob.glob(os.path.join(directory_path, '*'))
     for file in files:
       if os.path.isfile(file):
         os.remove(file)
     print("All files deleted successfully.")
   except OSError:
     print("Error occurred while deleting files.")


def main():
    print("Deleting all previously existing files in %s"%OUTDIR)
    delete_files_in_directory(OUTDIR)
    
    print("Opening NetCDF files: ")
    print(NETCDF_WASS)
    print(NETCDF_WASSFAST)
    root_w = Dataset( NETCDF_WASS, mode="r")
    root_wf = Dataset( NETCDF_WASSFAST, mode="r")

    stereo_baseline = root_w["scale"][0]
    print("Baseline=",stereo_baseline)
    assert root_wf["scale"][0] == stereo_baseline

    t = np.array(root_w["time"])
    ZZ_w = root_w["Z"]
    ZZ_wf = root_wf["Z"]
    XX = np.array( root_w["X_grid"] )/1000.0
    YY = np.array( root_w["Y_grid"] )/1000.0

    zmean_w = root_w["meta"].zmean
    zmin_w = root_w["meta"].zmin
    zmax_w = np.abs(zmin_w)

    zmean_wf = root_wf["meta"].zmean
    print("Zmean WASS     = ",zmean_w)
    print("Zmean WASSFast = ",zmean_wf)

    ts_w = ZZ_w[:,ZZ_w.shape[1]//2,ZZ_w.shape[2]//2] / 1000.0
    ts_wf = ZZ_wf[:,ZZ_wf.shape[1]//2,ZZ_wf.shape[2]//2] / 1000.0

    zmean_w = np.nanmean( ts_w )
    zmean_wf = np.nanmean( ts_wf )

    print("Considering central timeserie:")
    print("Zmean WASS     = ",zmean_w)
    print("Zmean WASSFast = ",zmean_wf)

    ## Plot central timeserie
    ts_w -= zmean_w
    ts_wf -= zmean_wf

    f,ax = plt.subplots( layout="constrained", figsize=(20,5) )
    ax.plot( t, ts_w, "k", label="WASS" )
    ax.plot( t, ts_wf, "b", label="WASSfast")
    f.suptitle("$\\rho$=%1.5f"%(np.corrcoef( ts_w, ts_wf )[-1,0]) )
    ax.legend()
    ax.grid(True)
    f.savefig("%s/timeserie.png"%(OUTDIR))
    plt.close(f)



    for idx in tqdm.trange(0,ZZ_w.shape[0]):

        p3d = np.loadtxt( "%s/%06d_point_cloud.txt"%(ptsdir,idx) )
        p3d[:,2] -= zmean_wf

        Z_w = np.squeeze(ZZ_w[idx,:,:])/1000.0 - zmean_w 
        Z_wf = np.squeeze(ZZ_wf[idx,:,:])/1000.0 - zmean_wf
        Z_w[ np.isnan(Z_wf) ] = np.nan

        (imax, jmax) = np.unravel_index( np.nanargmax( Z_w ), Z_w.shape) 
        xmax, ymax = XX[imax,jmax], YY[imax,jmax]

        pts_distances = np.linalg.norm( p3d[:,:2]-np.array([xmax,ymax]), axis=1 )
        pts_mindist = np.amin(pts_distances)
        nearest_pt_index = np.argmin( pts_distances )

        ## Create surface comparison plot
        f, (ax1,ax2) = plt.subplots(1,2, layout="constrained", figsize=(20,10))
        pc = ax1.pcolor(XX,YY,Z_w, vmin=zmin_w, vmax=zmax_w)
        cnt = ax1.contour(XX,YY,Z_w,levels=[-3.0,-2.0,0.0,2.0,3.0],colors="k")
        sc = ax1.scatter( xmax, ymax, s=150, c="k", marker='o')
        ax1.text(xmax+2.5,ymax,"%1.5f (m)"%Z_w[imax,jmax], fontsize="x-large", bbox={'facecolor': 'white', 'alpha': 0.9, 'pad': 3})
        ax1.set_title("%s"%method1)
        ax1.set_xlim(XX[0,0],XX[0,-1])
        ax1.set_ylim(YY[0,0],YY[-1,0])
        cb = f.colorbar(pc)
        cb.add_lines( cnt )

        pc = ax2.pcolor(XX,YY,Z_wf, vmin=zmin_w, vmax=zmax_w, alpha=0.5)
        cnt = ax2.contour(XX,YY,Z_wf,levels=[-3.0,-2.0,0.0,2.0,3.0],colors="k")
        cnt = ax2.contour(XX,YY,Z_w,levels=[-3.0,-2.0,0.0,2.0,3.0],colors="r")
        sc = ax2.scatter( xmax, ymax, s=150, c="k", marker='x')
        scp = ax2.scatter( p3d[:,0], p3d[:,1], s=1.0, c=p3d[:,2], vmin=zmin_w, vmax=zmax_w )
        ax2.annotate("Interp value %1.5f $\\Delta$ %1.5f (m)"%(Z_wf[imax,jmax],Z_wf[imax,jmax]-Z_w[imax,jmax]),
                     (xmax,ymax),
                     xytext=(3,-1),
                     textcoords="offset fontsize",
                     arrowprops=dict(facecolor='black', shrink=0.01),
                     fontsize="x-large", bbox={'facecolor': 'white', 'alpha': 0.9, 'pad': 3})

        ax2.annotate("Closest point %1.3f $\\Delta$ %1.8f \n distance: %1.3f (m)"%(p3d[nearest_pt_index,2],p3d[nearest_pt_index,2]-Z_w[imax,jmax],pts_mindist),
                     (p3d[nearest_pt_index,0],p3d[nearest_pt_index,1]),
                     xytext=(3,3),
                     textcoords="offset fontsize",
                     arrowprops=dict(facecolor='black', shrink=0.01),
                     fontsize="x-large", bbox={'facecolor': 'white', 'alpha': 0.9, 'pad': 3})

        ax2.set_title("%s"%method2)
        ax2.set_xlim(XX[0,0],XX[0,-1])
        ax2.set_ylim(YY[0,0],YY[-1,0])
        cb = f.colorbar(pc)
        cb.add_lines( cnt )

        f.suptitle("Frame %d"%idx)

        f.savefig("%s/surface_%06d.png"%(OUTDIR,idx))
        plt.close(f)


        ## Create surface interpolation error plot

        # interpolate the surface at point location
        interp = scipy.interpolate.RegularGridInterpolator( (YY[:,0],XX[0,:]), Z_wf, bounds_error=False )
        p3d_interp = interp(p3d[:,[1,0]])

        f, (ax,ax2) = plt.subplots( 1,2, layout="constrained", figsize=(15,10) )
        #pc = ax.pcolor(XX,YY,Z_wf, vmin=zmin_w, vmax=zmax_w, alpha=0.8)
        cnt = ax.contour(XX,YY,Z_wf,levels=[-3.0,-2.0,0.0,2.0,3.0],colors="k")
        s = ax.scatter( p3d[:,0], p3d[:,1], s=100, c=(p3d[:,2]-p3d_interp), vmin=-0.5, vmax=0.5 )
        cb = f.colorbar(s)
        cb.set_label("Zpt - Zsurface (m)")
        ax.set_title("Interpolated Surface Error")

        h = ax2.hist( (p3d[:,2]-p3d_interp), bins=51, range=(-0.7,0.7), density=True )
        ax2.set_title("Error distribution")
        ax2.grid(True)
        f.savefig("%s/pterror_%06d.png"%(OUTDIR,idx))
        plt.close(f)



if __name__ == "__main__":
    main()
