import h5py
import numpy as np


class Homogenization:
    def __init__(self):
        self.sigma = np.array([[0.0, 0.0], [0.0, 0.0]]).transpose()
        self.grid_p = np.array([0.0, 0.0]).transpose()
        self.resolution = np.array([0, 0]).transpose()
        self.h = 0.01


class HomogenizeData:
    def __init__(self):
        self.homogenization = []     

    def _load_homogenization(self, fileName):
        self.homogenization.clear()
        if fileName != "" and fileName[len(fileName)-3:] == ".h5":
            with h5py.File(fileName, 'r') as h5_homogenization:
                h_group = h5_homogenization['homogenization']
                    
                sigma_array = np.array(h_group['sigma'], dtype=np.float64)
                grid_p_array = np.array(h_group['grid_p'], dtype=np.float64)
                resolution = np.array(h_group['resolution'], dtype=np.int32)
                h = np.array(h_group['h'], dtype=np.float64)
                
                homogenize_num = len(h)
                
                for i in range(homogenize_num):
                    j = Homogenization()
                    j.sigma = sigma_array[:, :, i]
                    j.grid_p = grid_p_array[:, i]
                    j.resolution = resolution[:, i]
                    j.h = h[i]
                    self.homogenization.append(j)  

    def load(self, fn):
        self._load_homogenization(fn)
                      
    def save(self, file_name):
        with h5py.File(file_name, 'w') as h5_homogenization:
            h_group = h5_homogenization.create_group('homogenization')
            
            sigma_array = np.zeros((2, 2, len(self.homogenization)), dtype=np.float64)
            grid_p_array = np.zeros((2, len(self.homogenization)), dtype=np.float64)
            resolution = np.zeros((2, len(self.homogenization)), dtype=np.int32)
            h = np.zeros(len(self.homogenization), dtype=np.float64)
            
            for i in range(len(self.homogenization)):
                sigma_array[:, :, i] = self.homogenization[i].sigma
                grid_p_array[:, i] = self.homogenization[i].grid_p
                resolution[:, i] = self.homogenization[i].resolution
                h[i] = self.homogenization[i].h   
            
            h_group.create_dataset('sigma', data=sigma_array)
            h_group.create_dataset('grid_p', data=grid_p_array)
            h_group.create_dataset('resolution', data=resolution)
            h_group.create_dataset('h', data=h)
