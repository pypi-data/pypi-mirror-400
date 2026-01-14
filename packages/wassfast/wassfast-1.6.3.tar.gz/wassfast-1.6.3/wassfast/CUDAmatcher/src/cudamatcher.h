#include <stdbool.h>

#ifdef WIN32
#define DllExport   __declspec( dllexport )
#endif

extern "C"
{

    DllExport extern unsigned int reduce_points( float* pt_data, unsigned int npts, float min_distance, unsigned int wsize, bool* keep_pts );

}
