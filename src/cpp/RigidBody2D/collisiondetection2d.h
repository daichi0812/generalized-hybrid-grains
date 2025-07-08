#ifndef collision_detection_2d_h
#define collision_detection_2d_h

#include <vector>
#include <set>
#include "collisionsample2d.h"
#include "uniformgrid2d.h"

struct Element;

struct BroadPhaseActiveSet
{
  void clear()
  {
    for( int i=0; i<collision_pairs.size(); i++ )
      collision_pairs[i].clear();
  }
  
  void setSize( const int size )
  {
    collision_pairs.resize( size );
  }
  
  // idx0: idx1. idx0 < idx1
  std::vector< std::set< int > > collision_pairs;
};

bool boundingBoxIntersection( const BoundingBox2D& in_BB1, const BoundingBox2D& in_B2 );
void collisionDetection( std::vector< Element >& io_RigidBodies, const double in_ugrd_dx, UniformGrid2D** io_Ugrd, BroadPhaseActiveSet& io_BroadPhaseActiveSet, const int in_frame_idx );

#endif
