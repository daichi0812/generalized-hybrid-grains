#define EIGEN_DISABLE_UNALIGNED_ARRAY_ASSERT
#define EIGEN_DONT_VECTORIZE

#include "uniformgrid2d.h"

UniformGrid2D::UniformGrid2D( const Eigen::Vector2d& in_min_coords, const Eigen::Vector2i& in_res, const double in_cell_width )
: m_nAllocCells(0), m_nData( nullptr ), m_nAllocPerCell( nullptr ), m_IDs( nullptr )
{
  reallocation( in_min_coords, in_res, in_cell_width );
}

UniformGrid2D::~UniformGrid2D()
{
  for( int i=0; i<m_nAllocCells; i++ ) free( m_IDs[i] );
	free( m_IDs );
	free( m_nData );
	free( m_nAllocPerCell );
}

void UniformGrid2D::reallocation( const Eigen::Vector2d& in_min_coords, const Eigen::Vector2i& in_res, const double in_cell_width )
{
  m_Res = in_res;
  m_CellWidth = in_cell_width;
  m_MinCoords = in_min_coords;
  
  const int newNCells = m_Res.x() * m_Res.y();
  if( m_nAllocCells >= newNCells )
  {
    clearData();
    return;
  }
  
  m_nData = ( int* )realloc( m_nData, sizeof(int) * newNCells );
  for( int i=0; i<newNCells; i++ ) m_nData[i] = 0;
  
  m_nAllocPerCell = ( int* )realloc( m_nAllocPerCell, sizeof(int) * newNCells );
  for( int i=m_nAllocCells; i<newNCells; i++ ) m_nAllocPerCell[i] = 0;
  
  m_IDs = ( int** )realloc( m_IDs, sizeof(int*) * newNCells );
  for( int i=m_nAllocCells; i<newNCells; i++ ) m_IDs[i] = nullptr;
  
  m_nAllocCells = newNCells;
}
	
void UniformGrid2D::clearData()
{
  const int nCells = m_Res.x() * m_Res.y();
	for( int i=0; i<nCells; i++ ) m_nData[i] = 0;
}

void UniformGrid2D::registerData( const Eigen::Vector2d& in_min_coords, const Eigen::Vector2d& in_max_coords, int id )
{
	Eigen::Vector2i idm; getGridID( in_min_coords, idm );
	Eigen::Vector2i idM; getGridID( in_max_coords, idM );
	
	for( unsigned j=idm.y(); j<=idM.y(); j++ )
  {
    for( unsigned i=idm.x(); i<=idM.x(); i++ )
    {
      const unsigned flat_idx = j * m_Res.x() + i;
      if( m_nAllocPerCell[flat_idx] <= m_nData[flat_idx] )
      {
        int newSize;
        if( m_nAllocPerCell[flat_idx] < 10 ) newSize = 16;
        else if( m_nAllocPerCell[flat_idx] < 2000 ) newSize = m_nAllocPerCell[flat_idx] * 2;
        else newSize = m_nAllocPerCell[flat_idx] + 1024;
			
        m_nAllocPerCell[flat_idx] = newSize;
        m_IDs[flat_idx] = ( int* )realloc( m_IDs[flat_idx], sizeof(int)*m_nAllocPerCell[flat_idx] );
      }
		
      m_IDs[flat_idx][m_nData[flat_idx]] = id;
      m_nData[flat_idx]++;
		}
	}
}

void UniformGrid2D::registerPointData( const Eigen::Vector2d& coords, int id )
{
	Eigen::Vector2i idm; getGridID(coords, idm);
	
	const unsigned flat_idx = idm.y() * m_Res.x() + idm.x();
	if(m_nAllocPerCell[flat_idx] <= m_nData[flat_idx])
	{
		int newSize;
		if( m_nAllocPerCell[flat_idx] < 10 ) newSize = 16;
		else if( m_nAllocPerCell[flat_idx] < 2000 ) newSize = m_nAllocPerCell[flat_idx] * 2;
		else newSize = m_nAllocPerCell[flat_idx] + 1024;
			
		m_nAllocPerCell[flat_idx] = newSize;
		m_IDs[flat_idx] = ( int* )realloc( m_IDs[flat_idx], sizeof(int)*m_nAllocPerCell[flat_idx] );
	}
		
	m_IDs[flat_idx][m_nData[flat_idx]] = id;
	m_nData[flat_idx]++;
}

void UniformGrid2D::getGridID( const Eigen::Vector2d& coords, Eigen::Vector2i& grid_idx ) const
{
  const Eigen::Vector2d _idx = ( coords - m_MinCoords ) / m_CellWidth;
	grid_idx(0) = std::max<int>( 0, std::min<int>( m_Res.x()-1, int(std::floor(_idx(0))) ) );
	grid_idx(1) = std::max<int>( 0, std::min<int>( m_Res.y()-1, int(std::floor(_idx(1))) ) );
}

void UniformGrid2D::getGridIDRange( const Eigen::Vector2d& in_min_coords, const Eigen::Vector2d& in_max_coords, Eigen::Vector2i& min_grid_idx, Eigen::Vector2i& max_grid_idx ) const
{
	getGridID( in_min_coords, min_grid_idx );
	getGridID( in_max_coords, max_grid_idx );
}

void UniformGrid2D::getIDs( const Eigen::Vector2i& grid_idx, int* out_nData, const int** out_IDs ) const
{
	if((grid_idx(0) >= m_Res.x()) || (grid_idx(1) >= m_Res.y()))
	{
		*out_nData = 0;
		*out_IDs = NULL;
	}
	else
	{
		const unsigned flat_idx = grid_idx(1) * m_Res.x() + grid_idx(0);
		*out_nData = m_nData[flat_idx];
		*out_IDs = m_IDs[flat_idx];
	}
}

Eigen::Vector2i UniformGrid2D::getFirstNonEmptyCell( int* out_nData, const int** out_IDs ) const
{
  for( int j=0; j<m_Res.y(); j++ )
  {
    for( int i=0; i<m_Res.x(); i++ )
    {
      const unsigned flat_idx = j * m_Res.x() + i;
      if( m_nData[flat_idx] > 0 )
      {
        *out_nData = m_nData[flat_idx];
        *out_IDs = m_IDs[flat_idx];
        return Eigen::Vector2i { i, j };
      }
    }
  }
  
  *out_nData = 0;
  *out_IDs = NULL;
  return Eigen::Vector2i { m_Res.x(), m_Res.y() };
}

Eigen::Vector2i UniformGrid2D::getNextNonEmptyCell( const Eigen::Vector2i& in_prev_cell, int* out_nData, const int** out_IDs ) const
{
  int x_start = in_prev_cell(0) + 1;
  for( int j=in_prev_cell(1); j<m_Res.y(); j++ )
  {
    for( int i=x_start; i<m_Res.x(); i++ )
    {
      const unsigned flat_idx = j * m_Res.x() + i;
      if( m_nData[flat_idx] > 0 )
      {
        *out_nData = m_nData[flat_idx];
        *out_IDs = m_IDs[flat_idx];
        return Eigen::Vector2i { i, j };
      }
    }
    x_start = 0;
  }
  
  *out_nData = 0;
  *out_IDs = NULL;
  return Eigen::Vector2i { m_Res.x(), m_Res.y() };
}

Eigen::Vector2i UniformGrid2D::getFirstCellWithMultipleElements( int* out_nData, const int** out_IDs ) const
{
  for( int j=0; j<m_Res.y(); j++ )
  {
    for( int i=0; i<m_Res.x(); i++ )
    {
      const unsigned flat_idx = j * m_Res.x() + i;
      if( m_nData[flat_idx] > 1 )
      {
        *out_nData = m_nData[flat_idx];
        *out_IDs = m_IDs[flat_idx];
        return Eigen::Vector2i { i, j };
      }
    }
  }
  
  *out_nData = 0;
  *out_IDs = NULL;
  return Eigen::Vector2i { m_Res.x(), m_Res.y() };
}

Eigen::Vector2i UniformGrid2D::getNextCellWithMultipleElements( const Eigen::Vector2i& in_prev_cell, int* out_nData, const int** out_IDs ) const
{
  int x_start = in_prev_cell(0) + 1;
  for( int j=in_prev_cell(1); j<m_Res.y(); j++ )
  {
    for( int i=x_start; i<m_Res.x(); i++ )
    {
      const unsigned flat_idx = j * m_Res.x() + i;
      if( m_nData[flat_idx] > 1 )
      {
        *out_nData = m_nData[flat_idx];
        *out_IDs = m_IDs[flat_idx];
        return Eigen::Vector2i { i, j };
      }
    }
    x_start = 0;
  }
  
  *out_nData = 0;
  *out_IDs = NULL;
  return Eigen::Vector2i { m_Res.x(), m_Res.y() };
}

bool UniformGrid2D::isAtEnd( const Eigen::Vector2i& cell ) const
{
  return cell(1) >= m_Res.y();
}
