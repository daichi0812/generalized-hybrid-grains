#define EIGEN_DISABLE_UNALIGNED_ARRAY_ASSERT
#define EIGEN_DONT_VECTORIZE

#include "xmlparser.h"
#include <vector>
#include <iostream>
#include <fstream>

void setDefaultSetting( SimulatorSettings& setting )
{
  setting.dt = 0.000001;
  setting.dx = 0.04;
  setting.dx_sample_points = 0.04;
  setting.ugrd_dx = 0.1;
  setting.max_time = 10.0;
  
  setting.kN = 17720938.760736626;
  setting.gammaN = 4618.02;
  setting.kT = 478465346.5398889;
  setting.gammaT = 4618.02;
  setting.mu = 0.5;

  setting.g << 0.0, -9.81;
  
  setting.templates_file_name_to_resume = "";
  setting.objects_file_name_to_resume = "";
  
  setting.serialization_enabled = false;
  setting.serialization_interval = 1.0 / 30.0;
  setting.serialization_folder = "Save";
  setting.objects_file_template_for_serialization = "objects_%06d.h5";
  setting.serialization_serialize_forces = false;
}

void showSettings( const SimulatorSettings& setting )
{
  std::cout << "[AGRigidBody2D] Simulator settings" << std::endl;
  
  std::cout << "[AGRigidBody2D] ===== Integrator =====" << std::endl;
  std::cout << "[AGRigidBody2D]   dt: " << setting.dt << std::endl;
  std::cout << "[AGRigidBody2D]   dx: " << setting.dx << std::endl;
  std::cout << "[AGRigidBody2D]   dx_sample_points: " << setting.dx_sample_points << std::endl;
  std::cout << "[AGRigidBody2D]   ugrd_dx: " << setting.ugrd_dx << std::endl;
  std::cout << "[AGRigidBody2D]   max_time: " << setting.max_time << std::endl;
  
  std::cout << "[AGRigidBody2D] ===== Penalty impact map =====" << std::endl;
  std::cout << "[AGRigidBody2D]   kN: " << setting.dt << std::endl;
  std::cout << "[AGRigidBody2D]   gammaN: " << setting.gammaN << std::endl;
  std::cout << "[AGRigidBody2D]   kT: " << setting.kT << std::endl;
  std::cout << "[AGRigidBody2D]   gammaT: " << setting.gammaT << std::endl;
  std::cout << "[AGRigidBody2D]   mu: " << setting.mu << std::endl;
  
  std::cout << "[AGRigidBody2D] ===== Near earth gravity =====" << std::endl;
  std::cout << "[AGRigidBody2D]   g: " << setting.g.transpose() << std::endl;
  
  std::cout << "[AGRigidBody2D] ===== Resume =====" << std::endl;
  std::cout << "[AGRigidBody2D]   templates: " << setting.templates_file_name_to_resume << std::endl;
  std::cout << "[AGRigidBody2D]   objects: " << setting.objects_file_name_to_resume << std::endl;
  
  std::cout << "[AGRigidBody2D] ===== Serialization =====" << std::endl;
  std::cout << "[AGRigidBody2D]   enabled: " << setting.serialization_enabled << std::endl;
  std::cout << "[AGRigidBody2D]   interval: " << setting.serialization_interval << std::endl;
  std::cout << "[AGRigidBody2D]   folder: " << setting.serialization_folder << std::endl;
  std::cout << "[AGRigidBody2D]   objects: " << setting.objects_file_template_for_serialization << std::endl;
  std::cout << "[AGRigidBody2D]   forces: " << setting.forces_file_name_for_serialization << std::endl;
  std::cout << "[AGRigidBody2D]   serialize_forces: " << setting.serialization_serialize_forces << std::endl;
}

template<class T>
bool extractFromString( const std::string& str, T& res )
{
  std::stringstream input_strm( str );
  input_strm >> res;
  return !input_strm.fail();
}

template<>
bool extractFromString( const std::string& str, std::string& res )
{
  res = str;
  return true;
}

template<class T, int N>
bool extractFromString( const std::string& str, Eigen::Matrix<T, N, 1>& vec )
{
  std::stringstream input_strm( str );
  for( int i=0; i<vec.size(); i++ )
    input_strm >> vec(i);
  return !input_strm.fail();
}

template< typename T >
bool loadAttribute( const rapidxml::xml_node<>* const node, const std::string& node_string, const std::string& attribute_string, T& result )
{
  constexpr bool is_floating_point_v = std::is_floating_point<T>::value;
  constexpr bool is_integer_v = std::is_integral<T>::value;
  
  const rapidxml::xml_attribute<>* const attrib{ node->first_attribute( attribute_string.c_str() ) };
  if( !attrib )
  {
    std::cerr << "Failed to locate " << attribute_string << " attribute for " << node_string << " node." << std::endl;
    return false;
  }
  
  if( !extractFromString( std::string{ attrib->value() }, result ) )
  {
    std::string type_str;
    if constexpr ( is_floating_point_v ){ type_str = "real number"; }
    else if constexpr( is_integer_v ){ type_str = "integer number"; }
    else { int rows = result.rows(); int cols = result.cols(); type_str = std::to_string( rows ) + " x " + std::to_string( cols ) + " matrix"; }
    
    std::cerr << "Failed to load " << attribute_string << " attribute for " << node_string << " node. Must provide a " << type_str << "." << std::endl;
    return false;
  }
  
  return true;
}

bool loadAttribute( const rapidxml::xml_node<>* const node, const std::string& node_string, const std::string& attribute_string, std::string& result )
{
  const rapidxml::xml_attribute<>* const attrib{ node->first_attribute( attribute_string.c_str() ) };
  if( !attrib )
  {
    std::cerr << "Failed to locate " << attribute_string << " attribute for " << node_string << " node." << std::endl;
    return false;
  }
  
  if( !extractFromString( std::string{ attrib->value() }, result ) )
  {
    std::string type_str;
    std::cerr << "Failed to load " << attribute_string << " attribute for " << node_string << " node. Must provide a string." << std::endl;
    return false;
  }
  
  return true;
}

bool attributeExists( const rapidxml::xml_node<>* const node, const std::string& attribute_string )
{
  const rapidxml::xml_attribute<>* const attrib{ node->first_attribute( attribute_string.c_str() ) };
  if( !attrib ) return false;
  else return true;
}

bool loadIntegrator( const rapidxml::xml_node<>& node, SimulatorSettings& setting )
{
  const rapidxml::xml_node<>* const integrator_node{ node.first_node( "integrator" ) };
  if( integrator_node == nullptr )
  {
    std::cerr << "Failed to locate integrator node." << std::endl;
    return false;
  }
  
  if( !loadAttribute( integrator_node, "integrator", "dt", setting.dt ) ) return false;
  if( !loadAttribute( integrator_node, "integrator", "dx", setting.dx ) ) return false;
  if( !loadAttribute( integrator_node, "integrator", "dx_sample_points", setting.dx_sample_points ) ) return false;
  if( !loadAttribute( integrator_node, "integrator", "ugrd_dx", setting.ugrd_dx ) ) return false;
  if( !loadAttribute( integrator_node, "integrator", "max_time", setting.max_time ) ) return false;
    
  return true;
}

bool loadPenaltyImpactMap( const rapidxml::xml_node<>& node, SimulatorSettings& setting )
{
  const rapidxml::xml_node<>* const penalty_impact_map_node{ node.first_node( "penalty_impact_map" ) };
  if( penalty_impact_map_node == nullptr )
  {
    std::cerr << "Failed to locate penalty_impact_map node." << std::endl;
    return false;
  }
  
  if( !loadAttribute( penalty_impact_map_node, "penalty_impact_map", "kN", setting.kN ) ) return false;
  if( !loadAttribute( penalty_impact_map_node, "penalty_impact_map", "gammaN", setting.gammaN ) ) return false;
  if( !loadAttribute( penalty_impact_map_node, "penalty_impact_map", "kT", setting.kT ) ) return false;
  if( !loadAttribute( penalty_impact_map_node, "penalty_impact_map", "gammaT", setting.gammaT ) ) return false;
  if( !loadAttribute( penalty_impact_map_node, "penalty_impact_map", "mu", setting.mu ) ) return false;
  
  return true;
}

bool loadNearEarthGravity( const rapidxml::xml_node<>& node, SimulatorSettings& setting )
{
  const rapidxml::xml_node<>* const near_earth_gravity_node{ node.first_node( "near_earth_gravity" ) };
  if( near_earth_gravity_node == nullptr )
  {
    std::cerr << "Failed to locate near_earth_gravity node." << std::endl;
    return false;
  }
  
  if( !loadAttribute( near_earth_gravity_node, "near_earth_gravity", "g", setting.g ) ) return false;
  
  return true;
}

bool loadResume( const rapidxml::xml_node<>& node, SimulatorSettings& setting )
{
  const rapidxml::xml_node<>* const resume_node{ node.first_node( "resume" ) };
  if( resume_node == nullptr )
  {
    std::cerr << "Failed to locate resume node." << std::endl;
    return false;
  }
  
  if( !loadAttribute( resume_node, "resume", "templates", setting.templates_file_name_to_resume ) ) return false;
  if( !loadAttribute( resume_node, "resume", "objects", setting.objects_file_name_to_resume ) ) return false;
  
  return true;
}

bool loadSerialization( const rapidxml::xml_node<>& node, SimulatorSettings& setting )
{
  const rapidxml::xml_node<>* const serialization_node{ node.first_node( "serialization" ) };
  if( serialization_node == nullptr )
  {
    setting.serialization_enabled = false;
    setting.serialization_interval = 100.0;
    setting.serialization_folder = "";
    setting.objects_file_template_for_serialization = "";
    setting.forces_file_name_for_serialization = "";
    return true;
  }
  
  setting.serialization_enabled = true;
  setting.serialization_serialize_forces = false;
  if( !loadAttribute( serialization_node, "serialization", "interval", setting.serialization_interval ) ) return false;
  if( !loadAttribute( serialization_node, "serialization", "folder", setting.serialization_folder ) ) return false;
  if( !loadAttribute( serialization_node, "serialization", "objects", setting.objects_file_template_for_serialization ) ) return false;
  
  if( attributeExists( serialization_node, "serialize_forces" ) )
  {
    int res;
    if( !loadAttribute( serialization_node, "serialization", "serialize_forces", res ) ) return false;
    setting.serialization_serialize_forces = res == 0 ? false : true;
    if( !loadAttribute( serialization_node, "serialization", "forces", setting.forces_file_name_for_serialization ) ) return false;
  }
  
  return true;
}

bool openXMLFile( const std::string& filename, SimulatorSettings& setting )
{
  setDefaultSetting( setting );
    
  rapidxml::xml_document<> doc;
  doc.clear();
  // Read the xml file into a vector
  std::ifstream theFile( filename );
  if( !theFile.is_open() )
  {
    return false;
  }
  
  std::vector<char> buffer( ( std::istreambuf_iterator<char>( theFile ) ), std::istreambuf_iterator<char>() );
  buffer.push_back('\0');
    
  // Parse the buffer using the xml file parsing library into doc.
  try
  {
    doc.parse<0>( &buffer[0] );
  }
  catch( const rapidxml::parse_error& e )
  {
    std::cerr << "Failed to open xml file: " << filename << std::endl;
    std::cerr << "Error message: " << e.what() << std::endl;
    return false;
  }
  
  if( doc.first_node( "rigidbody2d" ) == nullptr )
  {
    std::cerr << "Failed to locate root node 'rigidbody2d' in xml file: " << filename << std::endl;
    return false;
  }
  const rapidxml::xml_node<>& root_node{ *doc.first_node( "rigidbody2d" ) };
    
  if( !loadIntegrator( root_node, setting ) )
  {
    return false;
  }
  
  if( !loadPenaltyImpactMap( root_node, setting ) )
  {
    return false;
  }
  
  if( !loadNearEarthGravity( root_node, setting ) )
  {
    return false;
  }
  
  if( !loadResume( root_node, setting ) )
  {
    return false;
  }
  
  if( !loadSerialization( root_node, setting ) )
  {
    return false;
  }
  
  showSettings( setting );
  
  return true;
}
