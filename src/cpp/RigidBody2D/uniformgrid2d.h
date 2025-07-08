#ifndef UniformGrid_h
#define UniformGrid_h

#include <Eigen/Core>
#include <Eigen/Dense>

class UniformGrid2D
{
	UniformGrid2D();
public:
  UniformGrid2D( const Eigen::Vector2d& in_min_coords, const Eigen::Vector2i& in_res, const double in_cell_width);
	~UniformGrid2D();
  
  void reallocation( const Eigen::Vector2d& in_min_coords, const Eigen::Vector2i& in_res, const double in_cell_width );
	
	void clearData();
  void registerData( const Eigen::Vector2d& in_min_coords, const Eigen::Vector2d& in_max_coords, int id );
	void registerPointData( const Eigen::Vector2d& coords, int id );
	void getGridID( const Eigen::Vector2d& coords, Eigen::Vector2i& grid_idx ) const;
	void getGridIDRange( const Eigen::Vector2d& in_min_coords, const Eigen::Vector2d& in_max_coords, Eigen::Vector2i& min_grid_idx, Eigen::Vector2i& max_grid_idx ) const;
	void getIDs( const Eigen::Vector2i& grid_idx, int* out_nData, const int** out_IDs ) const;
	
  Eigen::Vector2i getFirstNonEmptyCell( int* out_nData, const int** out_IDs ) const;
  Eigen::Vector2i getNextNonEmptyCell( const Eigen::Vector2i& in_prev_cell, int* out_nData, const int** out_IDs ) const;
  Eigen::Vector2i getFirstCellWithMultipleElements( int* out_nData, const int** out_IDs ) const;
  Eigen::Vector2i getNextCellWithMultipleElements( const Eigen::Vector2i& in_prev_cell, int* out_nData, const int** out_IDs ) const;
  bool isAtEnd( const Eigen::Vector2i& cell ) const;
  
protected:
	Eigen::Vector2i m_Res;
	Eigen::Vector2d m_MinCoords;
  double m_CellWidth;
	
  int m_nAllocCells;
	int* m_nData;
	int* m_nAllocPerCell;
	int** m_IDs;
};

#endif
