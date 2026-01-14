#include <iostream>
#include <math.h>
#include <vector>
#include "mex.h"

using namespace std;

void _main();



void mexFunction(
		 int          nlhs,
		 mxArray      *plhs[],
		 int          nrhs,
		 const mxArray *prhs[]
		 )
{

    /* Check for proper number of arguments */

    /*
    if (nrhs != 1) {
        mexErrMsgIdAndTxt("MATLAB:mexcpp:nargin",
                "MEXCPP requires one input arguments.");
    } else
    */
    if (nlhs != 1)
    {
        mexErrMsgIdAndTxt("PointReducer",
                "PointReducer requires one output argument.");
    }

    /* make sure the matrix type is double */
    if( !mxIsDouble(prhs[0]) )
    {
        mexErrMsgIdAndTxt("PointReducer","Input matrix must be type double.");
    }

    if( !mxIsDouble(prhs[1]) )
    {
        mexErrMsgIdAndTxt("PointReducer","Input min distance must by type double");
    }

    if( 2 != mxGetM( prhs[0] ) )
    {
        mexErrMsgIdAndTxt("PointReducer","Input matrix must have 2 rows.");
    }

    size_t wsize = 11;
    size_t npts = mxGetN( prhs[0] );
    double min_distance = mxGetScalar( prhs[1] );

    size_t buff_size = ceil( (wsize/2) / min_distance );

    //std::cout << npts << " points" << std::endl;
    //std::cout << min_distance << " min distance" << std::endl;
    //std::cout << "Buffer size: " << buff_size << "x" << buff_size << std::endl;

    size_t ext_buffer_size = buff_size + wsize + 1;
    double pt2buff_m = buff_size;
    double pt2buff_t = floor(wsize/2) + buff_size/2 +1;

    //std::cout << "Extended buffer size: " << ext_buffer_size << "x" << ext_buffer_size << std::endl;
    //std::cout << "pt 2 buffer transform: p*" << pt2buff_m << " + " << pt2buff_t << std::endl;

    double* pt_data = mxGetPr( prhs[0] );

    /* create the output matrix */
    plhs[0] = mxCreateLogicalMatrix(1,npts);
    /* get a pointer to the real data in the output matrix */
    mxLogical* keep_pts = mxGetLogicals(plhs[0]);


    std::vector< unsigned char > b( ext_buffer_size*ext_buffer_size, 0 );


    // Create circular mask window
    std::vector< unsigned char > wnd( wsize*wsize );
    const int iic = wsize/2;
    const int jjc = wsize/2;

    for( int ii=0; ii<wsize; ++ii)
    {
        for( int jj=0; jj<wsize; ++jj )
        {
            wnd[ii*wsize+jj] = (((ii-iic)*(ii-iic) + (jj-jjc)*(jj-jjc)) < (wsize*wsize*0.25) ) ? 255 : 0;
        }
    }


    // Process all points
    for( int i=0; i<npts*2; i+=2 )
    {
        //std::cout << pt_data[i] << " ; " << pt_data[i+1] <<  std::endl;
        
        const double& PTX = pt_data[i];
        const double& PTY = pt_data[i+1];
        
        if( PTX<=-0.5 || PTX >=0.5 || PTY<=-0.5 || PTY >=0.5 )
        {
            keep_pts[i/2]=false;
            continue;
        }

        const int x = floor( PTX*pt2buff_m + pt2buff_t );
        const int y = floor( PTY*pt2buff_m + pt2buff_t );
        //std::cout << x << " ; " << y <<  std::endl;

        if( b[y*ext_buffer_size + x]>0 )
        {
            keep_pts[i/2]=false;
        }
        else
        {
            size_t idx=0;
            keep_pts[i/2]=true;

            for( int yy=y-wsize/2; yy<=y+wsize/2; ++yy )
            {
                unsigned char* pt = &(b[yy*ext_buffer_size + x-wsize/2]);
                const unsigned char* ptend = pt + wsize;

                while( pt<ptend )
                {
                    *pt++ |= wnd[idx++];
                }
            }
        }
    }


    std::cout << "DONE" << std::endl;

    return;
}
