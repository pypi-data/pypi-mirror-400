import unittest
from netCDF4 import Dataset
import numpy as np
from types import SimpleNamespace
import cv2 as cv


#NETCDF_MODEL_FILE = "D:\\dev\\wassfast_testdata\\wassfast_output.nc"
#NETCDF_COMPARE_FILE = "D:\\dev\\wassfast_testdata\\wassfast_output_master_5bfc3cf4.nc"
NETCDF_MODEL_FILE = "D:\\dev\\wassfast_testdata\\wassfast_output.nc"
NETCDF_COMPARE_FILE = "D:\\dev\\wassfast_testdata\\wassfast_pu_output.nc"


class NetCDFTestCase( unittest.TestCase ):
    def setUp(self):
        self.A = SimpleNamespace()
        self.B = SimpleNamespace()

        self.A.rootgrp = Dataset( NETCDF_MODEL_FILE, "r", format="NETCDF4")
        self.B.rootgrp = Dataset( NETCDF_COMPARE_FILE, "r", format="NETCDF4")
        pass

    def test_generator( self ):
        self.assertEqual( self.A.rootgrp.generator, "WASSFast" )
        self.assertEqual( self.B.rootgrp.generator, "WASSFast" )


    def test_dimension_X( self ):
        self.assertEqual( self.A.rootgrp.dimensions["X"].size,  self.A.rootgrp.dimensions["X"].size )


    def test_dimension_Y( self ):
        self.assertEqual( self.A.rootgrp.dimensions["Y"].size,  self.A.rootgrp.dimensions["Y"].size )


    def test_dimension_count( self ):
        self.assertEqual( self.A.rootgrp.dimensions["count"].size,  self.A.rootgrp.dimensions["count"].size )


    def test_grids( self ):
        try:
            np.testing.assert_allclose( np.array( self.A.rootgrp.variables["X_grid"]),  np.array( self.B.rootgrp.variables["X_grid"]) )
            np.testing.assert_allclose( np.array( self.A.rootgrp.variables["Y_grid"]),  np.array( self.B.rootgrp.variables["Y_grid"]) )
            self.assertTrue(True)
        except AssertionError:
            self.assertTrue( False )


    def test_images( self ):
        images = self.A.rootgrp.variables["cam0images"]
        W,H = self.A.rootgrp["/meta"].image_width, self.A.rootgrp["/meta"].image_height
        I = cv.imdecode( images[0], cv.IMREAD_UNCHANGED )
        cv.imshow("image",I)
        cv.waitKey(0)
        

    def test_Zshape( self ):
        self.assertEqual( self.A.rootgrp.variables["Z"].shape, self.B.rootgrp.variables["Z"].shape )

    # def test_Z( self ):
    #     try:
    #         for ii in range(3, self.A.rootgrp.variables["Z"].shape[0] ):
    #             import matplotlib.pyplot as plt
    #             Asurf = np.array( self.A.rootgrp.variables["Z"][ii,:,:])
    #             Bsurf = np.array( self.B.rootgrp.variables["Z"][ii,:,:])

    #             diff = np.abs( Asurf - Bsurf )

    #             plt.figure()
    #             plt.imshow(Asurf)
    #             plt.show()

    #             plt.figure()
    #             plt.imshow(Bsurf)
    #             plt.show()

    #             plt.figure()
    #             plt.imshow( diff )
    #             plt.colorbar()
    #             plt.show()

    #             self.assertTrue( True )
    #     except AssertionError:
    #         self.assertTrue( False )

    def test_timeseries(self):
        
        sh = self.A.rootgrp.variables["Z"].shape
        rj = int(sh[1]/5)

        for offI in range(-rj,rj):
            for offJ in range(-rj,rj):
                sampleI = int(sh[1]/2)+offI
                sampleJ = int(sh[2]/2)+offJ

                #print("%d - %d"%(sampleI,sampleJ) )
                minlen = np.amin( [self.A.rootgrp.variables["Z"].shape[0],self.B.rootgrp.variables["Z"].shape[0]] )

                timeserieA = np.array( self.A.rootgrp.variables["Z"][:minlen,sampleI,sampleJ] )
                timeserieB = np.array( self.B.rootgrp.variables["Z"][:minlen,sampleI,sampleJ] )

                timeserieA -= np.mean( timeserieA )
                timeserieB -= np.mean( timeserieB )

                err = np.amax( np.abs( timeserieA-timeserieB ) )

                if err>2.0:
                    print(err)
                    import matplotlib.pyplot as plt
                    plt.figure()
                    plt.plot( timeserieA,'-r' )
                    plt.plot( timeserieB,'.k' )
                    plt.title("Timeserie at %d-%d max error: %3.3f"%(sampleI, sampleJ,err) )
                    plt.legend( "out", "gt" )
                    plt.grid("minor")
                    plt.show()

                if offI==0 and offJ==0:
                    import matplotlib.pyplot as plt
                    plt.figure()
                    plt.plot( timeserieA,'-r' )
                    plt.plot( timeserieB,'.k' )
                    plt.title("Timeserie at %d-%d max error: %3.3f"%(sampleI, sampleJ,err) )
                    plt.legend( "out", "gt" )
                    plt.grid("minor")
                    plt.show()


                self.assertLess( err, 2.0 )


    def tearDown(self):
        self.A.rootgrp.close()
        self.B.rootgrp.close()
        pass


if __name__ == '__main__':
    unittest.main()