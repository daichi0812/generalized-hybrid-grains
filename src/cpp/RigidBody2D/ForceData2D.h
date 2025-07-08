//
//  ForceData2D.h
//  rigidbody2dsim
//
//  Created by Yonghao Yue on 2022/04/11.
//  Copyright © 2022 Yonghao Yue. All rights reserved.
//

#ifndef __FORCE_DATA_2D_H__
#define __FORCE_DATA_2D_H__

#include <Eigen/Core>
#include <vector>
#include "HDF5io.h"

struct SingleForceData2D
{
  SingleForceData2D( const Eigen::Vector2d& in_position, const Eigen::Vector2d& in_arm, const Eigen::Vector2d& in_force )
  : position( in_position ), arm( in_arm ), force( in_force ) {}
  
  Eigen::Vector2d position;
  Eigen::Vector2d arm;
  Eigen::Vector2d force;
};

class ForceData2D
{
public:
  ForceData2D() {}
  ~ForceData2D() {}
  
  void clear()
  {
    m_Forces.clear();
    debug_force.clear();
  }
  
  void storeForce( const Eigen::Vector2d& position, const Eigen::Vector2d& arm, const Eigen::Vector2d& force ) { m_Forces.emplace_back( position, arm, force ); }
  
  void storeDebugData( const Eigen::Vector2d& force ) { debug_force.emplace_back( force ); }
  
  void serializeForces( HDF5File& io_HDF5, const std::string& in_time_step = "" ) const
  {
    Eigen::Matrix2Xd position_array; position_array.resize( 2, m_Forces.size() );
    Eigen::Matrix2Xd arm_array; arm_array.resize( 2, m_Forces.size() );
    Eigen::Matrix2Xd force_array; force_array.resize( 2, m_Forces.size() );
    Eigen::Matrix2Xd debug_force_array; debug_force_array.resize( 2, debug_force.size() );
    
    const int num_forces = m_Forces.size();
    for( int i=0; i<num_forces; i++ )
    {
      position_array.col(i) = m_Forces[i].position;
      arm_array.col(i) = m_Forces[i].arm;
      force_array.col(i) = m_Forces[i].force;
    }

    const int num_debug_data = debug_force.size();
    for( int i=0; i<num_debug_data; i++ )
      debug_force_array.col(i) = debug_force[i];
    
    const std::string group_name_forces = in_time_step + "/forces_2d";
    io_HDF5.writeMatrix( group_name_forces, "position", position_array );
    io_HDF5.writeMatrix( group_name_forces, "arm", arm_array );
    io_HDF5.writeMatrix( group_name_forces, "force", force_array );

    const std::string group_name_debug = in_time_step + "/debug";
    io_HDF5.writeMatrix( group_name_debug, "force", debug_force_array );
  }
  
private:
  std::vector<SingleForceData2D> m_Forces;
  std::vector<Eigen::Vector2d> debug_force;
};


#endif
