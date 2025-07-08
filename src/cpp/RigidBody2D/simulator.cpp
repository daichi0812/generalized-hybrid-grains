#define EIGEN_DISABLE_UNALIGNED_ARRAY_ASSERT
#define EIGEN_DONT_VECTORIZE

#define _USE_MATH_DEFINES
#include <cmath>
#include <iostream>
#include <assert.h>
#include "simulator.h"
#include "RigidBody2DData.h"
#include "collisiondetection2d.h"
#include "constants.h"

inline double sgn( const double x )
{
  return x >= 0.0 ? 1.0 : -1.0;
}

double secondRootOfQuadratic( const double& a, const double& b, const double& c, const double& dscr_sqrt )
{
  double root;
  if( b > 0.0 )
  {
    assert( ( -b - dscr_sqrt ) != 0.0 );
    root = ( 2.0 * c ) / ( -b - dscr_sqrt );
    assert(root == root);
  }
  else
  {
    assert( a != 0.0 );
    root = ( -b + dscr_sqrt ) / ( 2.0 * a );
    assert(root == root);
  }
  return root;
}

void stepSystemPhase1( Simulator& io_Simulator, double in_dt )
{
  for( int i=0; i<io_Simulator.data.numElements(); i++ )
  {
    io_Simulator.data.getElement(i).clearForceAndTorque();
    //max_omega = std::max<double>( max_omega, fabs( io_Simulator.data.getElement(i).getAngularVelocity() ) );
  }
  
  if( io_Simulator.settings.serialization_serialize_forces )
    io_Simulator.force_data.clear();

  //collisionDetection( io_Simulator.rigid_bodies, io_Simulator.frame_idx );
  collisionDetection( io_Simulator.data.getElements(), io_Simulator.settings.ugrd_dx, &io_Simulator.ugrd, io_Simulator.broad_phase_active_set, io_Simulator.data.getProgressData().tick_count );

  for( int i=0; i<io_Simulator.data.numElements(); i++ )
  {
    //std::cout << "omega_719: " << io_Simulator.data.getElement(719).getAngularVelocity() << std::endl;

    for( int p=0; p<io_Simulator.data.getElement(i).numCollisionSamples(); p++ )
    {
      for( auto q=io_Simulator.data.getElement(i).collisionSample(p).collision_cache.begin(); q!=io_Simulator.data.getElement(i).collisionSample(p).collision_cache.end(); q++ )
      {
        const Eigen::Vector2d collision_point = io_Simulator.data.getElement(i).getCurrentPosition( io_Simulator.data.getElement(i).collisionSample(p).x0 );

        const Eigen::Vector2d arm_i = collision_point - io_Simulator.data.getElement(i).getCenterOfMass();
        const Eigen::Vector2d arm_j = collision_point - io_Simulator.data.getElement( q->first ).getCenterOfMass();

        const Eigen::Vector2d contact_normal = -q->second.normal;

        const Eigen::Vector2d v_rel = io_Simulator.data.getElement(i).getVelocity() + rot90() * arm_i * io_Simulator.data.getElement(i).getAngularVelocity() - io_Simulator.data.getElement( q->first ).getVelocity() - rot90() * arm_j * io_Simulator.data.getElement( q->first ).getAngularVelocity();
        const Eigen::Vector2d vn = contact_normal * contact_normal.dot( v_rel );

        const Eigen::Vector2d normal_force = -contact_normal * q->second.penetrationDepth * io_Simulator.settings.kN - vn * io_Simulator.settings.gammaN * 0.5;

        q->second.delta += v_rel * in_dt;
        q->second.delta -= q->second.normal * q->second.normal.dot( q->second.delta );
        const Eigen::Vector2d vt = v_rel - vn;

        Eigen::Vector2d friction_force = -q->second.delta * io_Simulator.settings.kT - vt * io_Simulator.settings.gammaT * 0.5;
        const double mu_fn = std::max<double>( 0.0, - io_Simulator.settings.mu * normal_force.norm() * sgn( normal_force.dot( contact_normal ) ) );
        const double ft = friction_force.norm();
        
        /*
        std::cout << "idx[" << i << ", " << q->first << "]" << std::endl;
        std::cout << "  collision_point: " << collision_point << std::endl;
        std::cout << "  normal_force: " << normal_force.transpose() << std::endl;
        std::cout << "    contact_normal: " << contact_normal.transpose() << std::endl;
        std::cout << "    penetrationDepth: " << q->second.penetrationDepth << std::endl;
        std::cout << "    kN: " << io_Simulator.settings.kN << std::endl;
        std::cout << "    vn: " << vn.transpose() << std::endl;
        std::cout << "    gammaN: " << io_Simulator.settings.gammaN << std::endl;
        std::cout << "    v_rel: " << v_rel.transpose() << std::endl;
        std::cout << "    vi: " << io_Simulator.data.getElement(i).getVelocity().transpose() << std::endl;
        std::cout << "    arm_i: " << arm_i.transpose() << std::endl;
        std::cout << "    omega_i: " << io_Simulator.data.getElement(i).getAngularVelocity() << std::endl;
        std::cout << "    j: " << q->first << std::endl;
        std::cout << "    vj: " << io_Simulator.data.getElement( q->first ).getVelocity().transpose() << std::endl;
        std::cout << "    arm_j: " << arm_j.transpose() << std::endl;
        std::cout << "    omega_j: " << io_Simulator.data.getElement( q->first ).getAngularVelocity() << std::endl;
        std::cout << "    mass_i: " << io_Simulator.data.getElement( i ).getMass() << std::endl;
        std::cout << "    mass_j: " << io_Simulator.data.getElement( q->first ).getMass() << std::endl;
        std::cout << "    I_i: " << io_Simulator.data.getElement( i ).getInertia() << std::endl;
        std::cout << "    I_j: " << io_Simulator.data.getElement( q->first ).getMass() << std::endl;
        std::cout << "  tentative_friction_force: " << friction_force.transpose() << std::endl;
        //*/
        
        if( 0.5 * io_Simulator.settings.gammaT * vt.norm() > mu_fn )
        {
          q->second.delta.setZero();
          friction_force = - vt;
          friction_force.normalize();
          friction_force *= mu_fn;
          
          //std::cout << "  Case I; friction_force: " << friction_force.transpose() << std::endl;
        }
        else if( ft > mu_fn )
        {
          const double a = io_Simulator.settings.kT * io_Simulator.settings.kT * q->second.delta.squaredNorm();
          assert( a >= 0.0 );
          const double b = io_Simulator.settings.kT * io_Simulator.settings.gammaT * q->second.delta.dot( vt );
          const double c = 0.25 * io_Simulator.settings.gammaT * io_Simulator.settings.gammaT * vt.squaredNorm() - mu_fn * mu_fn;
          const double dscr = b * b - 4.0 * a * c;
          assert( dscr >= 0.0 );
          const double dscr_sqrt = sqrt( dscr );
          double root = secondRootOfQuadratic( a, b, c, dscr_sqrt );
          if( root < 0.0 || root > 1.0 )
          {
            std::cout << "invalid root? " << root << std::endl;
            root = std::max<double>( 0.0, std::min<double>( 1.0, root ) );
          }
          assert( fabs( a * root * root + b * root + c ) <= 1.0e-5 );

          const Eigen::Vector2d new_delta = q->second.delta * root;
          const Eigen::Vector2d new_friction_force = -new_delta * io_Simulator.settings.kT - vt * 0.5 * io_Simulator.settings.gammaT;
          assert( fabs( new_friction_force.norm() - mu_fn ) <= 1.0e-5 );
          friction_force = new_friction_force;
          q->second.delta = new_delta;
          
          //std::cout << "  Case II; friction_force: " << friction_force.transpose() << std::endl;
        }

        const Eigen::Vector2d total_force = normal_force + friction_force;
        
        if( io_Simulator.settings.serialization_serialize_forces )
        {
          io_Simulator.force_data.storeForce( collision_point, arm_i, total_force );
          io_Simulator.force_data.storeForce( collision_point, arm_j, -total_force );
        }

        io_Simulator.data.getElement(i).accumulateForceAndTorque( total_force, cross2d( arm_i, total_force ) );
        io_Simulator.data.getElement( q->first ).accumulateForceAndTorque( -total_force, -cross2d( arm_j,  total_force ) );
      }
    }

    if( !io_Simulator.data.getElement(i).getIsStatic() )
      io_Simulator.force_data.storeDebugData( io_Simulator.data.getElement(i).force );
    
    // gravity
    io_Simulator.data.getElement(i).accumulateForceAndTorque( io_Simulator.settings.g * io_Simulator.data.getElement(i).getMass() , 0.0 );
  }
}

void stepSystemPhase2( Simulator& io_Simulator, double in_dt )
{
  for( int i=0; i<io_Simulator.data.numElements(); i++ )
  {
    if( io_Simulator.data.getElement(i).getIsStatic() ) continue;
    io_Simulator.data.getElement(i).stepSymplecticEuler( in_dt );
  }

  io_Simulator.data.getProgressData().tick_count++;
  io_Simulator.data.getProgressData().time += in_dt;
}
