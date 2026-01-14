cmake_minimum_required(VERSION 3.5 )
project(PointsReducer VERSION 1.0.1 )

# Setup default installation dir
#
IF(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
get_filename_component( INSTALL_DIR_ABS "${PROJECT_SOURCE_DIR}/dist" ABSOLUTE)
SET( CMAKE_INSTALL_PREFIX ${INSTALL_DIR_ABS} CACHE PATH "Install prefix" FORCE )
ENDIF()

set( CMAKE_EXPORT_COMPILE_COMMANDS 1 )


add_library(PointsReducer SHARED
    src/pointsreducer.cpp
    src/pointsreducer.h
)

set_target_properties(PointsReducer PROPERTIES VERSION ${PROJECT_VERSION})
set_target_properties(PointsReducer PROPERTIES SOVERSION 1)
set_target_properties(PointsReducer PROPERTIES PUBLIC_HEADER src/pointsreducer.h)


INSTALL( TARGETS PointsReducer DESTINATION lib PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE WORLD_READ WORLD_EXECUTE )


