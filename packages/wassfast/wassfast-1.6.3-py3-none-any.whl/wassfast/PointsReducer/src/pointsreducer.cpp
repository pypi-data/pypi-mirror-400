#include <iostream>
#include <math.h>
#include <vector>
#include "pointsreducer.h"

using namespace std;

void _main();


unsigned int reduce_points( float* pt_data, unsigned int npts, float min_distance, unsigned int wsize, bool* keep_pts )
{

    const size_t buff_size = ceil( (wsize/2.0f) / min_distance );
    const size_t ext_buffer_size = buff_size + wsize + 1;
    double pt2buff_m = buff_size;
    double pt2buff_t = floor(wsize/2.0f) + buff_size/2.0f +1;

    /*
    std::cout << "Buff size: " << buff_size << std::endl;
    std::cout << "Ext buff size: " << ext_buffer_size << std::endl;
    std::cout << "Winsize: " << wsize << std::endl;
    /**/

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

    unsigned int npts_to_keep = 0;
#if 1

    // Process all points
    size_t kk=0;
    for( size_t i=0; i<npts*2; i+=2 )
    {
        const float xo = pt_data[i];
        const float yo = pt_data[i+1];
        //std::cout << xo << " ; " << yo <<  std::endl;
        
        if( xo<=-0.5 || xo>=0.5 || yo<=-0.5 || yo>=0.5) 
        {
            keep_pts[kk++] = false;
            continue;
        }

        const int x = floor( xo*pt2buff_m + pt2buff_t );
        const int y = floor( yo*pt2buff_m + pt2buff_t );
        //std::cout << x << " ; " << y <<  std::endl;

        if( b[y*ext_buffer_size + x]>0 )
        {
            keep_pts[kk++]=false;
        }
        else
        {
            size_t idx=0;
            keep_pts[kk++]=true;
            ++npts_to_keep;

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
#endif

    //std::cout << npts_to_keep << " points to keep" << std::endl;
    return npts_to_keep;
}
