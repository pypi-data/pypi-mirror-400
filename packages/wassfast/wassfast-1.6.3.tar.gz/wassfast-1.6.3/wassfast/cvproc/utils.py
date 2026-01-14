import numpy as np
import cv2 as cv


def load_ocv_matrix( filename ):
    fs_read = cv.FileStorage( filename, cv.FILE_STORAGE_READ)
    arr_read = fs_read.getFirstTopLevelNode().mat()      
    fs_read.release()
    return arr_read


# Draw delaunay triangles
def rect_contains(rect, point) :
    if point[0] < rect[0] :
        return False
    elif point[1] < rect[1] :
        return False
    elif point[0] > rect[2] :
        return False
    elif point[1] > rect[3] :
        return False
    return True

def draw_delaunay(img, subdiv, delaunay_color ) :
 
    triangleList = subdiv.getTriangleList();
    size = img.shape
    r = (0, 0, size[1], size[0])
 
    for t in triangleList :
 
        pt1 = (int(t[0]), int(t[1]))
        pt2 = (int(t[2]), int(t[3]))
        pt3 = (int(t[4]), int(t[5]))
 
        if rect_contains(r, pt1) and rect_contains(r, pt2) and rect_contains(r, pt3) :
 
            cv.line(img, pt1, pt2, delaunay_color, 1)
            cv.line(img, pt2, pt3, delaunay_color, 1)
            cv.line(img, pt3, pt1, delaunay_color, 1)


# Debug extracted features in plane space
def debug_featuresP( matcher, I0p, I1p, outdir="dbg/", cam0name="cam0P_features", cam1name="cam1P_features", image_idx=0 ):
    I0p_aux = cv.cvtColor( I0p, cv.COLOR_GRAY2BGR )

    for idx in range(0,matcher.features_0P_all.shape[0]):
        #__import__("IPython").embed()
        cv.drawMarker(I0p_aux, tuple( matcher.features_0P_all[idx,:].astype(int) ), (0,0,0), markerType=cv.MARKER_TILTED_CROSS, markerSize=5  )

    subdiv = cv.Subdiv2D( (0,0,I0p_aux.shape[1],I0p_aux.shape[0]) )

    for idx in range(0,matcher.features_0P.shape[0]):
        p = tuple( matcher.features_0P[idx,:].astype(int) )
        subdiv.insert( (int(p[0]), int(p[1]) ) ) 
        cv.drawMarker(I0p_aux, p, (0,0,255), markerType=cv.MARKER_TILTED_CROSS, markerSize=5  )

    draw_delaunay( I0p_aux, subdiv, (0,0,255) ) 
    cv.imwrite("%s/%06d_%s.jpg"%(outdir,image_idx,cam0name), I0p_aux)

    I1p_aux = cv.cvtColor( I1p, cv.COLOR_GRAY2BGR )
    f1_int = np.round(matcher.features_1P)

    subdiv = cv.Subdiv2D( (0,0,I0p_aux.shape[1],I0p_aux.shape[0]) )

    for idx in range(0,f1_int.shape[0]):
        p = tuple( f1_int[idx,:].astype(int) )
        subdiv.insert( (int(p[0]), int(p[1]) ) ) 
        cv.drawMarker(I1p_aux, p, (0,0,255), markerType=cv.MARKER_TILTED_CROSS, markerSize=5  )

    draw_delaunay( I1p_aux, subdiv, (0,0,255) ) 
    cv.imwrite("%s/%06d_%s.jpg"%(outdir,image_idx,cam1name), I1p_aux)


# Debug features in camera space
def debug_features( I0, I1, features_0, features_1, outdir="dbg/"):
    I0_aux = cv.cvtColor( I0, cv.COLOR_GRAY2BGR )
    f0_int = np.round(features_0).astype(np.uint32)
    for idx in range(0,f0_int.shape[1]):
        cv.drawMarker(I0_aux, tuple( f0_int[:,idx] ), (255,0,0), markerType=cv.MARKER_TILTED_CROSS, markerSize=10  )
    cv.imwrite("%s/cam0_features.jpg"%outdir, I0_aux)

    I1_aux = cv.cvtColor( I1, cv.COLOR_GRAY2BGR )
    f1_int = np.round(features_1).astype(np.uint32)
    for idx in range(0,f1_int.shape[1]):
        cv.drawMarker(I1_aux, tuple( f1_int[:,idx] ), (255,0,0), markerType=cv.MARKER_TILTED_CROSS, markerSize=10  )
    cv.imwrite("%s/cam1_features.jpg"%outdir, I1_aux)


def debug_area( I0, I1, I0pshape, c2sH_cam0, c2sH_cam1, outdir="dbg/", line_thickness=10 ):
    area_extent_pts = np.array([ [0,0], [I0pshape[1],0], [I0pshape[1],I0pshape[0]] , [0, I0pshape[0]] ], dtype=np.float32  )
    area_extent_pts0 = c2sH_cam0.transform( area_extent_pts.T, inverse=True ).astype(np.int32)
    area_extent_pts1 = c2sH_cam1.transform( area_extent_pts.T, inverse=True ).astype(np.int32)

    I0_aux = cv.cvtColor( I0, cv.COLOR_GRAY2BGR )
    I1_aux = cv.cvtColor( I1, cv.COLOR_GRAY2BGR )
    for ii in range(4):
        cv.line( I0_aux, (area_extent_pts0[0][ii],area_extent_pts0[1][ii]), (area_extent_pts0[0][(ii+1)%4],area_extent_pts0[1][(ii+1)%4]), (0,0,255), line_thickness ) 
        cv.line( I1_aux, (area_extent_pts1[0][ii],area_extent_pts1[1][ii]), (area_extent_pts1[0][(ii+1)%4],area_extent_pts1[1][(ii+1)%4]), (0,0,255), line_thickness ) 

    cv.imwrite("%s/cam0_area.jpg"%outdir, I0_aux)
    cv.imwrite("%s/cam1_area.jpg"%outdir, I1_aux)
