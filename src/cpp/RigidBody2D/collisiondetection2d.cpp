#define EIGEN_DISABLE_UNALIGNED_ARRAY_ASSERT
#define EIGEN_DONT_VECTORIZE

#include "collisiondetection2d.h"
#include "RigidBody2DData.h"
#include "signeddistance2d.h"
#include "constants.h"
#include <iostream>
#include <Eigen/Core>

bool boundingBoxIntersection( const BoundingBox2D& in_BB1, const BoundingBox2D& in_B2 )
{
  return ( in_BB1.bb_min(0) <= in_B2.bb_max(0) && in_BB1.bb_max(0) >= in_B2.bb_min(0) ) && ( in_BB1.bb_min(1) <= in_B2.bb_max(1) && in_BB1.bb_max(1) >= in_B2.bb_min(1) );
}

void resetUniformGrid( const std::vector< Element >& in_RigidBodies, const double in_ugrd_dx, UniformGrid2D** io_Ugrd )
{
  if( in_RigidBodies.size() == 0 ) return;
  BoundingBox2D bb; in_RigidBodies[0].getBoundingBox( bb );
  
  for( int i=1; i<in_RigidBodies.size(); i++ )
  {
    BoundingBox2D _bb; in_RigidBodies[i].getBoundingBox( _bb );
    bb.bb_min = bb.bb_min.cwiseMin( _bb.bb_min );
    bb.bb_max = bb.bb_max.cwiseMax( _bb.bb_max );
  }
  
  const Eigen::Vector2i res = ( ( bb.bb_max - bb.bb_min ) / in_ugrd_dx ).unaryExpr( [](const double& s){ using std::ceil; return ceil(s); } ).cast<int>().array() + 2;
  const Eigen::Vector2d center = ( bb.bb_max + bb.bb_min ) * 0.5;
  const Eigen::Vector2d minC = center - res.cast<double>() * 0.5 * in_ugrd_dx;
  
  if( *io_Ugrd == nullptr ) *io_Ugrd = new UniformGrid2D( minC, res, in_ugrd_dx );
  else (*io_Ugrd)->reallocation( minC, res, in_ugrd_dx );
}

void rasterizeObjects( const std::vector< Element >& in_RigidBodies, UniformGrid2D* io_Ugrd )
{
  for( int i=0; i<in_RigidBodies.size(); i++ )
  {
    BoundingBox2D _bb; in_RigidBodies[i].getBoundingBox( _bb );
    io_Ugrd->registerData( _bb.bb_min, _bb.bb_max, i );
  }
}


bool proxyCollisionDetection( const Element& in_Body1, const Element& in_Body2 )
{
  BoundingBox2D bb_1, bb_2;
  in_Body1.getBoundingBox( bb_1 );
  in_Body2.getBoundingBox( bb_2 );
  
  return boundingBoxIntersection( bb_1, bb_2 );
}


void narrowPhaseCollisionDetection( Element& io_TargetBody, const Element& in_BodyToBeTested, const int in_frame_idx )
{
  for( int i=0; i<io_TargetBody.numCollisionSamples(); i++ )
  {
    CollisionSample2D& sample = io_TargetBody.collisionSample(i);
    const Eigen::Vector2d current_p = io_TargetBody.getCurrentPosition(sample.x0);
    const double sd = in_BodyToBeTested.getSignedDistanceAt(current_p);
    
    if( sd < 0.0 )
    {
      auto p = sample.collision_cache.find( in_BodyToBeTested.getIndex() );
      if( p != sample.collision_cache.end() )
      {
        p->second.frame_idx = in_frame_idx;
        p->second.penetrationDepth = -sd;
        p->second.normal = in_BodyToBeTested.getNormalAt(current_p);
        p->second.tangent = rot90() * p->second.normal;
      }
      else
      {
        CollisionInfo2D info;
        info.frame_idx = in_frame_idx;
        info.penetrationDepth = -sd;
        info.normal = in_BodyToBeTested.getNormalAt(current_p);
        info.tangent = rot90() * info.normal;
        info.delta.setZero();
        
        sample.collision_cache.insert( std::pair< int, CollisionInfo2D >( in_BodyToBeTested.getIndex(), info ) );
      }
    }
  }
}

void clearOldCollisionInfo( std::vector< Element >& io_RigidBodies, const int in_frame_idx )
{
  for( int i=0; i<io_RigidBodies.size(); i++ )
  {
    for( int s=0; s<io_RigidBodies[i].numCollisionSamples(); s++ )
    {
      CollisionSample2D& sample = io_RigidBodies[i].collisionSample(s);
      
      for( auto p=sample.collision_cache.begin(); p!= sample.collision_cache.end(); )
      {
        if( p->second.frame_idx == in_frame_idx )
        {
          p++;
        }
        else
        {
          p = sample.collision_cache.erase(p);
        }
      }
    }
  }
}

void broadPhaseCollisionDetection( std::vector< Element >& io_RigidBodies, const double in_ugrd_dx, UniformGrid2D** io_Ugrd, BroadPhaseActiveSet& io_BroadPhaseActiveSet )
{
  resetUniformGrid( io_RigidBodies, in_ugrd_dx, io_Ugrd );
  rasterizeObjects( io_RigidBodies, *io_Ugrd );
  
  io_BroadPhaseActiveSet.setSize( io_RigidBodies.size() );
  io_BroadPhaseActiveSet.clear();
  
  int nData; const int* IDs;
  Eigen::Vector2i cell_id = (*io_Ugrd)->getFirstCellWithMultipleElements( &nData, &IDs );
  
  while( !(*io_Ugrd)->isAtEnd( cell_id ) )
  {
    for( int j=0; j<nData; j++ )
    {
      for( int i=j+1; i<nData; i++ )
      {
        const int idx_a = IDs[j];
        const int idx_b = IDs[i];
        const int idx0 = std::min( idx_a, idx_b );
        const int idx1 = std::max( idx_a, idx_b );
     
        io_BroadPhaseActiveSet.collision_pairs[idx0].insert(idx1);
      }
    }
    
    cell_id = (*io_Ugrd)->getNextCellWithMultipleElements( cell_id, &nData, &IDs );
  }
}

void collisionDetection( std::vector< Element >& io_RigidBodies, const double in_ugrd_dx, UniformGrid2D** io_Ugrd, BroadPhaseActiveSet& io_BroadPhaseActiveSet, const int in_frame_idx )
{
  broadPhaseCollisionDetection( io_RigidBodies, in_ugrd_dx, io_Ugrd, io_BroadPhaseActiveSet );
  
  for( int j=0; j<io_RigidBodies.size(); j++ )
  {
    for( auto q=io_BroadPhaseActiveSet.collision_pairs[j].begin(); q!=io_BroadPhaseActiveSet.collision_pairs[j].end(); q++ )
    {
      int idx_i = *q;
      if( io_RigidBodies[idx_i].getIsStatic() && io_RigidBodies[j].getIsStatic() ) continue;
      if( proxyCollisionDetection( io_RigidBodies[idx_i], io_RigidBodies[j] ) )
      {
        narrowPhaseCollisionDetection( io_RigidBodies[idx_i], io_RigidBodies[j], in_frame_idx );
        narrowPhaseCollisionDetection( io_RigidBodies[j], io_RigidBodies[idx_i], in_frame_idx );
      }
    }
  }
  
  clearOldCollisionInfo( io_RigidBodies, in_frame_idx );
}
