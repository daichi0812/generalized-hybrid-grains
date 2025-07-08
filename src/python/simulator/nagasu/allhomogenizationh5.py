import h5py
import numpy as np
from homogenizationh5 import *


class AllHomogenizeData:
    def __init__(self):
        self.all_step_homogenization = []
        self.all_timestep = []

    def _load_homogenization(self, file_name):
        if file_name != "" and file_name[len(file_name) - 3:] == ".h5":
            with h5py.File(file_name, 'r') as h5_homogenization:
                for key in h5_homogenization.keys():
                    data_group = h5_homogenization[str(key)]
                    h_group = data_group['homogenization']
                    sigma_array = np.array(h_group['sigma'], dtype=np.float64)
                    grid_p_array = np.array(h_group['grid_p'], dtype=np.float64)
                    resolution = np.array(h_group['resolution'], dtype=np.int32)
                    h = np.array(h_group['h'], dtype=np.float64)
                  
                    homogenize_num = len(h)
                    homogenization_data = HomogenizeData()
                    for i in range(homogenize_num):
                        j = Homogenization()
                        j.sigma = sigma_array[:, :, i]
                        j.grid_p = grid_p_array[:, i]
                        j.resolution = resolution[:, i]
                        j.h = h[i]
                        homogenization_data.homogenization.append(j)
                    self.all_step_homogenization.append(homogenization_data)  

    def set_timestep_from_file(self, file_name):
        self.all_timestep.clear()
        with h5py.File(file_name, "r") as h5:
            keys = list(map(int, h5.keys()))
            self.all_timestep = sorted(keys)

    def load(self, fn):
        self._load_homogenization(fn)

    def _load_homogenization_from_idx(self, file_name, idx):
        self.all_step_homogenization.clear()
        if file_name != "" and file_name[len(file_name) - 3:] == ".h5":
            with h5py.File(file_name, 'r') as h5_homogenization:
                # idx番目のkeyを取得する
                keys = list(map(int, h5_homogenization.keys()))
                newlist = sorted(keys)
                data_group = h5_homogenization[str(newlist[idx])]
                h_group = data_group['homogenization']
                sigma_array = np.array(h_group['sigma'], dtype=np.float64)
                grid_p_array = np.array(h_group['grid_p'], dtype=np.float64)
                resolution = np.array(h_group['resolution'], dtype=np.int32)
                h = np.array(h_group['h'], dtype=np.float64)

                homogenize_num = len(h)
                homogenization_data = HomogenizeData()
                for i in range(homogenize_num):
                    j = Homogenization()
                    j.sigma = sigma_array[:, :, i]
                    j.grid_p = grid_p_array[:, i]
                    j.resolution = resolution[:, i]
                    j.h = h[i]
                    homogenization_data.homogenization.append(j)
                self.all_step_homogenization.append(homogenization_data)

    def load_from_idx(self, fn, idx):
        self._load_homogenization_from_idx(fn, idx)
                      
    def save(self, file_name):
        with h5py.File(file_name, 'a') as h5_homogenization:
            dt_group_num = len(self.all_step_homogenization)
            for i in range(dt_group_num):
                data_group = h5_homogenization.create_group(str(self.all_timestep[i]))
                h_group = data_group.create_group('homogenization')
                homogenization = self.all_step_homogenization[i].homogenization
                sigma_array = np.zeros((2, 2, len(homogenization)), dtype=np.float64)
                grid_p_array = np.zeros((2, len(homogenization)), dtype=np.float64)
                resolution = np.zeros((2, len(homogenization)), dtype=np.int32)
                h = np.zeros(len(homogenization), dtype=np.float64)
                
                for j in range(len(homogenization)):
                    sigma_array[:, :, j] = homogenization[j].sigma
                    grid_p_array[:, j] = homogenization[j].grid_p
                    resolution[:, j] = homogenization[j].resolution
                    h[j] = homogenization[j].h
                
                h_group.create_dataset('sigma', data=sigma_array)
                h_group.create_dataset('grid_p', data=grid_p_array)
                h_group.create_dataset('resolution', data=resolution)
                h_group.create_dataset('h', data=h)
