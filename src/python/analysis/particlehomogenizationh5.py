import h5py
import numpy as np
from homogenizationh5 import *

class ParticleHomogenization:
    def __init__(self):
        self.sigma = np.array([[0.0, 0.0],[0.0, 0.0]]).transpose()
        self.center_of_mass = np.array([0.0, 0.0]).transpose()
        self.resolution=np.array([0, 0]).transpose()
        self.h = 0.01
        self.density = 10.0
        self.volume = 0.000001

class ParticleToGridData:
    def __init__(self):
        self.force = np.array([0.0,0.0]).transpose()

class ParticleHomogenizeData:
    def __init__(self):
        self.particle_homogenization = []
        self.particle_to_grid_data = []

class AllParticleHomogenizeData:
    def __init__(self):
        self.all_step_particle_homogenization = []
        self.all_step_grid_data = []
    
    def _load_particle_homogenization(self, fileName):
        if fileName != "" and fileName[len(fileName)-3:] == ".h5":
            with h5py.File(fileName, 'r') as h5_homogenization:
                for i in h5_homogenization.keys():

                    data_group = h5_homogenization[str(i)]
                    h_group = data_group['homogenization']

                    center_of_mass_array = np.array(h_group['center_of_mass'], dtype=np.float64)
                    sigma_array = np.array(h_group['sigma'], dtype=np.float64)
                    resolution = np.array(h_group['resolution'], dtype=np.int32)
                    h = np.array(h_group['h'], dtype=np.float64)
                    density = np.array(h_group['density'], dtype=np.float64)
                    volume = np.array(h_group['volume'], dtype=np.float64)
                    group_name = str(i) + "/homogenization"

                    homogenization_data = ParticleHomogenizeData()
                    if h5_homogenization.get(group_name + "/force"):

                        force_array = np.array(h_group['force'], dtype=np.float64)
                        grid_num = len(force_array[0])
                        for k in range(grid_num):
                            j = ParticleToGridData()
                            j.force = force_array[:, k]
                            homogenization_data.particle_to_grid_data.append(j)
                        self.all_step_grid_data.append(homogenization_data)


                    homogenize_num = len(center_of_mass_array[0])

                    for k in range(homogenize_num):
                        j = ParticleHomogenization()
                        j.sigma = sigma_array[:, :, k]
                        j.center_of_mass = center_of_mass_array[:, k]
                        j.resolution = resolution
                        j.h = h
                        j.density = density[k]
                        j.volume = volume[k]
                        homogenization_data.particle_homogenization.append(j)
                    self.all_step_particle_homogenization.append(homogenization_data)


    
    def load(self, fn):
        self._load_particle_homogenization(fn)

    def _load_particle_homogenization_from_idx(self, fileName, idx):
        self.all_step_particle_homogenization.clear()
        if fileName != "" and fileName[len(fileName) - 3:] == ".h5":
            with h5py.File(fileName, 'r') as h5_homogenization:
                # idx番目のkeyを取得
                keys = list(map(int, h5_homogenization.keys()))
                newlist = sorted(keys)
                data_group = h5_homogenization[str(newlist[idx])]
                h_group = data_group['homogenization']

                center_of_mass_array = np.array(h_group['center_of_mass'], dtype=np.float64)
                sigma_array = np.array(h_group['sigma'], dtype=np.float64)
                resolution = np.array(h_group['resolution'], dtype=np.int32)
                h = np.array(h_group['h'], dtype=np.float64)
                density = np.array(h_group['density'], dtype=np.float64)
                volume = np.array(h_group['volume'], dtype=np.float64)
                group_name = str(newlist[idx]) + "/homogenization"
                homogenization_data = ParticleHomogenizeData()
                if h5_homogenization.get(group_name + "/force"):
                    force_array = np.array(h_group['force'], dtype=np.float64)
                    grid_num = len(force_array[0])
                    for k in range(grid_num):
                        j = ParticleToGridData()
                        j.force = force_array[:, k]
                        homogenization_data.particle_to_grid_data.append(j)
                    self.all_step_grid_data.append(homogenization_data)


                homogenize_num = len(center_of_mass_array[0])

                for k in range(homogenize_num):
                    j = ParticleHomogenization()
                    j.sigma = sigma_array[:, :, k]
                    j.center_of_mass = center_of_mass_array[:, k]
                    j.resolution = resolution
                    j.h = h
                    j.density = density[k]
                    j.volume = volume[k]
                    homogenization_data.particle_homogenization.append(j)
                self.all_step_particle_homogenization.append(homogenization_data)


    def load_from_idx(self, fn, idx):
            self._load_particle_homogenization_from_idx(fn, idx)

def MPM_data_num(fn):
    with h5py.File(fn, 'r') as h5_elements:
        keys = list(map(int,h5_elements.keys()))
        newlist = sorted(keys)
        data_num = len(newlist)
    return data_num

    