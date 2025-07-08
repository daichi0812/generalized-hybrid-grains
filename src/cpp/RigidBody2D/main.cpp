#define EIGEN_DISABLE_UNALIGNED_ARRAY_ASSERT
#define EIGEN_DONT_VECTORIZE

#ifdef __APPLE__
#define GL_SILENCE_DEPRECATION
#include <GLUT/glut.h>
#include <OpenGL/OpenGL.h>
#else
#include <GL/glut.h>
#endif

#define _USE_MATH_DEFINES
#include<math.h>

#include <iostream>
#include <random>
#include <Eigen/Core>
#include "RigidBody2DData.h"
#include "PolygonTemplate2D.h"
#include "CircleTemplate2D.h"
#include "DiscreteElement2D.h"
#include "signeddistance2d.h"
#include "simulator.h"
#include "constants.h"
#include "collisiondetection2d.h"
#include "xmlparser.h"
#include <Eigen/Dense>
#include <string>
#include <filesystem>
#include "HDF5io.h"

Simulator g_Simulator;
HDF5File* h5File;

void getBoundingBox( const std::vector< Eigen::Vector2d >& in_vertices0, BoundingBox2D& out_bb );

void pre_display( const Simulator& in_Simulator )
{
  glViewport( 0, 0, in_Simulator.window_width * in_Simulator.frame_window_size_scale_x, in_Simulator.window_height * in_Simulator.frame_window_size_scale_y );
  
  glClearColor( 1.0, 1.0, 1.0, 0.0 );
  glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT );
  
  glMatrixMode( GL_PROJECTION );
  glLoadIdentity();
  const int height_reference = 540;
  const double half_width = 0.5 * double( in_Simulator.window_width ) / double( height_reference );
  const double half_height = 0.5 * double( in_Simulator.window_height ) / double( height_reference );
  //glOrtho( -half_width, half_width, -half_height, half_height, -1.0, 100.0 );
  glOrtho( -0.1, half_width * 2.0 * 0.7, -0.1, half_height * 2.0 * 0.7, -1.0, 100.0 );
  
  glMatrixMode( GL_MODELVIEW );
  glLoadIdentity();
}

void post_display()
{
  glutSwapBuffers();
}

void reshape_func( int width, int height )
{
  g_Simulator.window_height = width;
  g_Simulator.window_height = height;
}

void output_resume_file()
{
  if( !g_Simulator.settings.serialization_enabled ) return;
  
  if( g_Simulator.data.getProgressData().time < g_Simulator.prev_serialization_time + g_Simulator.settings.serialization_interval ) return;
  
  if( !g_Simulator.settings.serialization_serialize_forces )
    g_Simulator.data.getProgressData().serialization_idx++;
  
  char file_name[1024];
  sprintf( file_name, g_Simulator.settings.objects_file_template_for_serialization.c_str(), g_Simulator.data.getProgressData().serialization_idx );
  std::string fn = g_Simulator.settings.serialization_folder + "/" + file_name;
  g_Simulator.data.serializeElements( fn );
  
  g_Simulator.prev_serialization_time = g_Simulator.data.getProgressData().time;
}

void output_force_file()
{
  if( !g_Simulator.settings.serialization_enabled ) return;
  
  if( g_Simulator.data.getProgressData().time + g_Simulator.settings.dt < g_Simulator.prev_serialization_time + g_Simulator.settings.serialization_interval ) return;
  
  g_Simulator.data.getProgressData().serialization_idx++;
  g_Simulator.data.serializeForces( *h5File, g_Simulator.force_data, std::to_string( g_Simulator.data.getProgressData().serialization_idx ) );
  g_Simulator.prev_serialization_time = g_Simulator.data.getProgressData().time;
}

void output_force_num(bool isEnd)
{
  if( !g_Simulator.settings.serialization_enabled ) return;
  if( !g_Simulator.settings.serialization_serialize_forces ) return;

  if(isEnd)
    h5File->writeScalar("force_num", "end", g_Simulator.data.getProgressData().serialization_idx);
  else
    h5File->writeScalar("force_num", "start", g_Simulator.data.getProgressData().serialization_idx + 1);
}

void idle_func()
{
  if( g_Simulator.animation )
  {
    for( int i=0; i<100; i++ )
    {
      if( g_Simulator.settings.max_time > 0.0 && g_Simulator.data.getProgressData().time >= g_Simulator.settings.max_time )
      {
        output_resume_file();
        output_force_num(true);
        std::cout << "Simulation done" << std::endl;
        exit(0);
      }
      
      if(!g_Simulator.settings.serialization_serialize_forces)
        output_resume_file();
      
      stepSystemPhase1( g_Simulator, g_Simulator.settings.dt );
      
      if(g_Simulator.settings.serialization_serialize_forces)
        output_force_file();
      
      stepSystemPhase2( g_Simulator, g_Simulator.settings.dt );
      
      if( g_Simulator.step_mode )
      {
        g_Simulator.animation = false;
        std::cout << "paused" << std::endl;
        break;
      }
    }
    
    std::cout << "Stepped to " << g_Simulator.data.getProgressData().time << std::endl;
  }

  glutPostRedisplay();
}

/*
void drawSDF( const RigidBody2D* in_Body )
{
  const SignedDistanceFunction2D* _sdf = in_Body->getSDF();
  glBegin(GL_QUADS);
  for (int j = 0; j <= _sdf->resolution()(1); j++)
  {
    for (int i = 0; i <= _sdf->resolution()(0); i++)
    {
      const double sd00 = _sdf->signedDistance( Eigen::Vector2i{ i, j } );
      const double sd10 = _sdf->signedDistance( Eigen::Vector2i{ i + 1, j } );
      const double sd11 = _sdf->signedDistance( Eigen::Vector2i{ i + 1, j + 1 } );
      const double sd01 = _sdf->signedDistance( Eigen::Vector2i{ i, j + 1 } );
      
      
      const Eigen::Vector2d x00_t0 = _sdf->minVertex() + Eigen::Vector2d{ i, j } *_sdf->dx();
      const Eigen::Vector2d x10_t0 = _sdf->minVertex() + Eigen::Vector2d{ i + 1, j } *_sdf->dx();
      const Eigen::Vector2d x01_t0 = _sdf->minVertex() + Eigen::Vector2d{ i, j + 1 } *_sdf->dx();
      const Eigen::Vector2d x11_t0 = _sdf->minVertex() + Eigen::Vector2d{ i + 1, j + 1 } *_sdf->dx();
      
      const Eigen::Vector2d x00 = in_Body->getCurrentPosition( x00_t0 );
      const Eigen::Vector2d x10 = in_Body->getCurrentPosition( x10_t0 );
      const Eigen::Vector2d x01 = in_Body->getCurrentPosition( x01_t0 );
      const Eigen::Vector2d x11 = in_Body->getCurrentPosition( x11_t0 );
      
      if (sd00 > 0.0) glColor3d(1.0 - sd00, 1.0 - sd00, 1.0); else glColor3d(1.0, 1.0 + sd00, 1.0 + sd00);
      glVertex2d(x00(0), x00(1));
      if (sd10 > 0.0) glColor3d(1.0 - sd10, 1.0 - sd10, 1.0); else glColor3d(1.0, 1.0 + sd10, 1.0 + sd10);
      glVertex2d(x10(0), x10(1));
      if (sd11 > 0.0) glColor3d(1.0 - sd11, 1.0 - sd11, 1.0); else glColor3d(1.0, 1.0 + sd11, 1.0 + sd11);
      glVertex2d(x11(0), x11(1));
      if (sd01 > 0.0) glColor3d(1.0 - sd01, 1.0 - sd01, 1.0); else glColor3d(1.0, 1.0 + sd01, 1.0 + sd01);
      glVertex2d(x01(0), x01(1));
    }
  }
  glEnd();
}
//*/

void drawCollisionSamples( const Element& in_Body )
{
  glEnable( GL_POINT_SIZE );
  glPointSize( 5.0 );
  glBegin( GL_POINTS );
  
  for( int i = 0; i < in_Body.numCollisionSamples(); i++ )
  {
    const Eigen::Vector2d samplePoint0 = in_Body.collisionSample( i ).x0;
    const Eigen::Vector2d currentSamplePoint = in_Body.getCurrentPosition( samplePoint0 );
    if( !in_Body.collisionSample( i ).collision_cache.empty() )
      glColor3d( 0.0, 1.0, 0.0 );
    else
      glColor3d( 1.0, 0.8, 0.0 );
    glVertex2d( currentSamplePoint(0), currentSamplePoint(1) );
  }
  
  glEnd();
}


void drawContactNormals( const Element& in_Body )
{
  glLineWidth( 2.0 );
  glBegin( GL_LINES );
  for( int i = 0; i < in_Body.numCollisionSamples(); i++ )
  {
    const Eigen::Vector2d samplePoint0 = in_Body.collisionSample( i ).x0;
    const Eigen::Vector2d currentSamplePoint = in_Body.getCurrentPosition( samplePoint0 );
    
    for( auto q = in_Body.collisionSample(i).collision_cache.begin(); q != in_Body.collisionSample(i).collision_cache.end(); q++ )
    {
      const Eigen::Vector2d normalTip = currentSamplePoint + q->second.normal * 0.2;
      const Eigen::Vector2d tangentTip = currentSamplePoint + q->second.tangent * 0.2;
      glColor3d( 0.0, 0.0, 0.0 );
      glVertex2d( currentSamplePoint(0), currentSamplePoint(1) );
      glVertex2d( normalTip(0), normalTip(1) );
      glColor3d( 1.0, 1.0, 0.0 );
      glVertex2d( currentSamplePoint(0), currentSamplePoint(1) );
      glVertex2d( tangentTip(0), tangentTip(1) );
    }
  }
  glEnd();
}

void drawPolygon( const Element& in_body )
{
  const PolygonTemplate2D* body_template = reinterpret_cast< const PolygonTemplate2D* >( in_body.getTemplatePtr() );
  
  glEnable( GL_LINE_WIDTH );
  glLineWidth(3.0);
  glBegin( GL_LINE_LOOP );
  for( int k = 0; k < body_template->numVertices(); k++ )
  {
    glColor3d( 0.0, 0.0, 0.0 );
    const Eigen::Vector2d vk = in_body.getCurrentPosition( body_template->getVertexPosition0( k ) );
    glVertex2d( vk(0), vk(1) );
  }
  glEnd();
}

void drawCircle( const Element& in_body )
{
  const CircleTemplate2D* body_template = reinterpret_cast< const CircleTemplate2D* >( in_body.getTemplatePtr() );
  
  glEnable( GL_LINE_WIDTH );
  glLineWidth( 3.0 );
  glBegin( GL_LINE_LOOP );
  
  const int nSegs = 180;
  const double radius = body_template->getRadius0();
  for( int k = 0; k < nSegs; k++ )
  {
    glColor3d( 0.0, 0.0, 0.0 );
    const double theta = 2.0 * M_PI * ( k + 0.5 ) / nSegs;
    const Eigen::Vector2d _vk{ radius * cos( theta ), radius * sin( theta ) };
    const Eigen::Vector2d vk = in_body.getCurrentPosition( _vk );
    glVertex2d( vk(0), vk(1) );
  }
  glEnd();
}

void drawBorderLine() {
  glEnable( GL_LINE_WIDTH );
  glLineWidth( 3.0 );
  glBegin( GL_LINES );
  
  glColor3d( 1.0, 0.0, 0.0 );
  glVertex2d( -6.15, 0.0 );
  glVertex2d( 6.15, 0.0 );
  glEnd();
}

void display_func()
{
  pre_display( g_Simulator );
  
  glClear( GL_COLOR_BUFFER_BIT );
  
  for( int i = 0; i < g_Simulator.data.numElements(); i++ )
  {
    //drawSDF(g_Simulator.rigid_bodies[i]);
    if( g_Simulator.data.getElement(i).getTemplatePtr()->type() == POLYGON )
      drawPolygon( g_Simulator.data.getElement(i) );
    else if( g_Simulator.data.getElement(i).getTemplatePtr()->type() == CIRCLE )
      drawCircle( g_Simulator.data.getElement(i) );
    
    if( g_Simulator.display_collision_samples )
      drawCollisionSamples( g_Simulator.data.getElement(i) );
    if( g_Simulator.display_contact_normals )
      drawContactNormals( g_Simulator.data.getElement(i) );
  }
  
  drawBorderLine();
  
  post_display();
}

void getBoundingBox( const std::vector< Eigen::Vector2d >& in_vertices0, BoundingBox2D& out_bb )
{
  Eigen::Vector2d center_of_mass = Eigen::Vector2d::Zero();
  
  for( int i = 0; i < in_vertices0.size(); i++ )
  {
    center_of_mass(0) += in_vertices0[i](0);
    center_of_mass(1) += in_vertices0[i](1);
  }
  center_of_mass(0) /= in_vertices0.size();
  center_of_mass(1) /= in_vertices0.size();
  
  double radius = 0.0;
  for( int i = 0; i < in_vertices0.size(); i++ )
  {
    radius = std::max<double>( radius, ( in_vertices0[i] - center_of_mass ).norm() );
  }
  
  out_bb.bb_min << -radius, -radius;
  out_bb.bb_max << radius, radius;
}

bool overlapTest( const std::vector< BoundingBox2D >& bb_list, const BoundingBox2D& bb )
{
  for( int i = 0; i < bb_list.size(); i++ )
  {
    if( boundingBoxIntersection( bb_list[i], bb ) )
      return false;
  }
  return true;
}

void resumeSimulation()
{
  g_Simulator.data.deserializeData( g_Simulator.settings.templates_file_name_to_resume, g_Simulator.settings.objects_file_name_to_resume );
  
  const int numTemplates = g_Simulator.data.numTemplates();
  for( int i=0; i<numTemplates; i++ )
    g_Simulator.data.getTemplate( i )->computeSignedDistanceFunction( g_Simulator.settings.dx );
  
  const int numElements = g_Simulator.data.numElements();
  for( int i=0; i<numElements; i++ )
  {
    const int template_idx = g_Simulator.data.getElement( i ).template_idx;
    g_Simulator.data.getElement( i ).initialize( i, g_Simulator.data.getTemplate( template_idx ), g_Simulator.settings.dx_sample_points );
  }
  
  if( g_Simulator.data.getProgressData().dt < 0.0 )
  {
    g_Simulator.data.getProgressData().dt = g_Simulator.settings.dt;
    g_Simulator.prev_serialization_time = -1000.0;
  }
  else
  {
    g_Simulator.prev_serialization_time = g_Simulator.data.getProgressData().time;
    if( fabs( g_Simulator.data.getProgressData().dt - g_Simulator.settings.dt ) / g_Simulator.settings.dt >= 1.0e-6 )
    {
      std::cout << "WARNING: mismatch between dt in xml and dt in h5." << std::endl;
    }
  }
}

void key( unsigned char key, int x, int y )
{
  switch( key )
  {
    case ' ':
      g_Simulator.animation = !g_Simulator.animation;
      if( g_Simulator.animation ) { std::cout << "simulating..." << std::endl; }
      else { std::cout << "paused" << std::endl; }
      glutPostRedisplay();
      break;
    case 's':
    case 'S':
      g_Simulator.step_mode = !g_Simulator.step_mode;
      if( g_Simulator.step_mode ) { std::cout << "entering step mode" << std::endl; }
      else { std::cout << "leaving step mode" << std::endl; }
      glutPostRedisplay();
      break;
    case 'n':
    case 'N':
      g_Simulator.display_contact_normals = !g_Simulator.display_contact_normals;
      glutPostRedisplay();
      break;
    case 'c':
    case 'C':
      g_Simulator.display_collision_samples = !g_Simulator.display_collision_samples;
      glutPostRedisplay();
      break;
  }
}


int main( int argc, char* argv[] )
{
  if( argc != 2 )
  {
    std::cout << "Usage: " << argv[0] << " <xml file>" << std::endl;
    exit(0);
  }
  
  if( !openXMLFile( argv[1], g_Simulator.settings ) )
  {
    std::cout << "Failed to read xml: " << argv[1] << std::endl;
    exit(0);
  }
  
  if( g_Simulator.settings.serialization_serialize_forces )
  {
    if( g_Simulator.settings.dt < g_Simulator.settings.serialization_interval )
    {
      std::cout << "WARNING: Force serialization makes sense only when serialization is performed for every time step, which is not the case for the current setting of serialization interval." << std::endl;
    }
    
    std::string fn = g_Simulator.settings.serialization_folder + "/" + g_Simulator.settings.forces_file_name_for_serialization;
    static HDF5File hdf5( fn, HDF5AccessType::READ_WRITE );
    h5File = &hdf5;
  }
  else
  {
    h5File = nullptr;
  }
  
  resumeSimulation();
  
  output_force_num(false);
  
  glutInit( &argc, argv );
  
  g_Simulator.window_width = 2000;
  g_Simulator.window_height = 800;
  glutInitDisplayMode( GLUT_RGBA | GLUT_DOUBLE );
  glutInitWindowPosition( 100, 100 );
  glutInitWindowSize( g_Simulator.window_width, g_Simulator.window_height );
  glutCreateWindow( "AGRigidBody2D" );
  
  // With retina display, frame buffer size is twice the window size.
  // Viewport size should be set on the basis of the frame buffer size, rather than the window size.
  // g_FrameSize_WindowSize_Scale_x and g_FrameSize_WindowSize_Scale_y account for this factor.
  GLint dims[4] = { 0 };
  glGetIntegerv( GL_VIEWPORT, dims );
  g_Simulator.frame_window_size_scale_x = double( dims[2] ) / double( g_Simulator.window_width );
  g_Simulator.frame_window_size_scale_y = double( dims[3] ) / double( g_Simulator.window_height );
  
  glClearColor( 1.0f, 1.0f, 1.0f, 1.0f );
  glClear( GL_COLOR_BUFFER_BIT );
  glutSwapBuffers();
  glClear( GL_COLOR_BUFFER_BIT );
  glutSwapBuffers();
  
  glutDisplayFunc( display_func );
  glutReshapeFunc( reshape_func );
  glutIdleFunc( idle_func );
  glutKeyboardFunc( key );
  
  glutMainLoop();
   
  return 0;
}
