#ifndef simulator_h
#define simulator_h
#include <vector>
#include "signeddistance2d.h"
#include "uniformgrid2d.h"
#include "collisiondetection2d.h"
#include "settings.h"
#include "RigidBody2DData.h"
#include "ForceData2D.h"

struct Simulator
{
  Simulator(): animation( false ), step_mode( false ), ugrd( nullptr ), prev_serialization_time( -1000.0 ), display_contact_normals( false ), display_collision_samples( false )
    //, tick_count( 0 ), time( 0.0 ), serialization_idx( -1 )
  {
    data.getProgressData().tick_count = 0;
    data.getProgressData().time = 0.0;
    data.getProgressData().serialization_idx = -1;
  }

  int window_width;
  int window_height;
  double frame_window_size_scale_x;
  double frame_window_size_scale_y;

  bool animation;
  bool step_mode;

  RigidBody2DData data;
  
  UniformGrid2D* ugrd;
  BroadPhaseActiveSet broad_phase_active_set;
  //int tick_count;
  //double time;
  //int serialization_idx;
  double prev_serialization_time;

  SimulatorSettings settings;
  
  bool display_contact_normals;
  bool display_collision_samples;
  
  ForceData2D force_data;
};

void stepSystemPhase1( Simulator& io_Simulator, double in_dt );
void stepSystemPhase2( Simulator& io_Simulator, double in_dt );

#endif
