cmake_minimum_required( VERSION 3.16 )
project( MPM2D )

include( CMakeSourceFiles.txt )

set( CMAKE_CXX_STANDARD 17 )
add_definitions( -std=c++17 -Wall )
set( CMAKE_CXX_FLAGS_RELEASE "-O2 -DNDEBUG")
set( CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake )

# Track the Git commit within the source
include( GetGitRevisionDescription )
get_git_head_revision( GIT_REFSPEC GIT_SHA1 )

# Track the build time
string( TIMESTAMP BUILD_DATE_TIME "%Y-%m-%d %H:%M:%S" )

# Create a file with build information
configure_file( "${CMAKE_CURRENT_SOURCE_DIR}/CompileDefinitions.h.in" "${CMAKE_CURRENT_SOURCE_DIR}/CompileDefinitions.h" @ONLY )

add_executable( ${PROJECT_NAME} ${Headers} ${Sources} )

# Add a reliable indicator of the current compiler
if( "${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU" )
  target_compile_definitions( ${PROJECT_NAME} PUBLIC CMAKE_DETECTED_GNU_COMPILER )
elseif( "${CMAKE_CXX_COMPILER_ID}" STREQUAL "Intel" )
  target_compile_definitions( ${PROJECT_NAME} PUBLIC CMAKE_DETECTED_INTEL_COMPILER )
elseif( "${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang" )
  target_compile_definitions( ${PROJECT_NAME} PUBLIC CMAKE_DETECTED_CLANG_COMPILER )
elseif( "${CMAKE_CXX_COMPILER_ID}" STREQUAL "AppleClang" )
  target_compile_definitions( ${PROJECT_NAME} PUBLIC CMAKE_DETECTED_CLANG_COMPILER )
elseif( "${CMAKE_CXX_COMPILER_ID}" STREQUAL "MSVC" )
  target_compile_definitions( ${PROJECT_NAME} PUBLIC CMAKE_DETECTED_MSVC_COMPILER )
else()
  message( FATAL_ERROR "Unsupported C++ compiler ${CMAKE_CXX_COMPILER_ID}. Please email the maintainer." )
endif()

# Eigen3 is header only and required for callers
find_package(Eigen3 REQUIRED)
target_include_directories( ${PROJECT_NAME} SYSTEM PUBLIC ${EIGEN3_INCLUDE_DIR} )
# Disable Eigen's built in multithreading as we will use OpenMP around Eigen
target_compile_definitions( ${PROJECT_NAME} PUBLIC EIGEN_DONT_PARALLELIZE )
# EIGEN_DONT_ALIGN also enables EIGEN_DONT_VECTORIZE
target_compile_definitions( ${PROJECT_NAME} PUBLIC EIGEN_DONT_ALIGN EIGEN_INITIALIZE_MATRICES_BY_NAN )
target_link_libraries( ${PROJECT_NAME} Eigen3::Eigen )

find_package( HDF5 REQUIRED )
if( NOT ${HDF5_FOUND} )
  message( FATAL_ERROR "HDF5 not found." )
endif()
target_include_directories( ${PROJECT_NAME} SYSTEM PUBLIC ${HDF5_INCLUDE_DIRS} )
target_compile_definitions( ${PROJECT_NAME} PUBLIC USE_HDF5 )
target_link_libraries( ${PROJECT_NAME} ${HDF5_LIBRARIES} )

find_package( RapidXML REQUIRED )
target_include_directories( ${PROJECT_NAME} SYSTEM PUBLIC ${RapidXML_INCLUDE_DIR} )

find_package( OpenGL REQUIRED )
find_package( GLUT REQUIRED )
# include_directories( ${OPENGL_INCLUDE_DIRS} ${GLUT_INCLUDE_DIRS} )
# target_link_libraries( ${PROJECT_NAME} ${OPENGL_LIBRARIES} ${GLUT_LIBRARY} )
# target_link_libraries( ${PROJECT_NAME} OpenGL::OpenGL GLUT::GLUT )
target_link_libraries( ${PROJECT_NAME} OpenGL::GL GLUT::GLUT )
