from numpy import ndarray
from typing import Union

from homogenizationh5 import *


class StressPair:
    def __init__(self):
        self.pre_stress: ndarray = np.array([[0.0, 0.0], [0.0, 0.0]]).transpose()
        self.post_stress: ndarray = np.array([[0.0, 0.0], [0.0, 0.0]]).transpose()
        self.grid_idx: int = -1


class StressPairData:
    def __init__(self):
        self.stress_pair_array: list[StressPair] = []
        self.grid_p: ndarray = np.array([0.0, 0.0]).transpose()
        self.h: float = 0.04
        self.resolution: ndarray = np.array([0, 0]).transpose()

    def _load_homogenization(self, file_name: str, time_step: Union[int, str]) -> None:
        if file_name != "" and file_name[len(file_name) - 3:] == ".h5":
            with h5py.File(file_name, 'r') as h5_homogenization:

                if h5_homogenization.get(str(time_step)) is None:
                    return

                stress_group = h5_homogenization[str(time_step)]

                self.grid_p = np.array(stress_group['grid_p'])
                self.h = np.array(stress_group['h'])
                self.resolution = np.array(stress_group['resolution'])

                pre_stress_array = np.array(stress_group['preflow'], dtype=np.float64)
                post_stress_array = np.array(stress_group['postflow'], dtype=np.float64)
                grid_idx_array = np.array(stress_group['grid_idx'], dtype=np.int32)

                pair_num = len(grid_idx_array)

                for i in range(pair_num):
                    stress_pair = StressPair()
                    stress_pair.pre_stress = pre_stress_array[:, :, i]
                    stress_pair.post_stress = post_stress_array[:, :, i]
                    stress_pair.grid_idx = grid_idx_array[i]
                    self.stress_pair_array.append(stress_pair)
    
    def load(self, fn: str, time_step: Union[int, str]) -> None:
        self._load_homogenization(fn, time_step)

    def save(self, file_name: str, time_step: Union[int, str]) -> None:
        with h5py.File(file_name, 'a') as h5_homogenization:
            stress_group = h5_homogenization.create_group(str(time_step) + "/")

            pair_num = len(self.stress_pair_array)

            pre_sigma_array = np.zeros((2, 2, pair_num), dtype=np.float64)
            post_sigma_array = np.zeros((2, 2, pair_num), dtype=np.float64)
            grid_idx_array = np.zeros(pair_num, dtype=np.int32)

            for i in range(pair_num):
                pre_sigma_array[:, :, i] = self.stress_pair_array[i].pre_stress
                post_sigma_array[:, :, i] = self.stress_pair_array[i].post_stress
                grid_idx_array[i] = self.stress_pair_array[i].grid_idx

            stress_group.create_dataset('preflow', data=pre_sigma_array)
            stress_group.create_dataset('postflow', data=post_sigma_array)
            stress_group.create_dataset('grid_idx', data=grid_idx_array)
            stress_group.create_dataset('grid_p', data=self.grid_p)
            stress_group.create_dataset('h', data=self.h)
            stress_group.create_dataset('resolution', data=self.resolution)


class AllStressPairData:
    def __init__(self):
        self.stress_pair_data_array: list[StressPairData] = []
        self.loaded_timestep: list[int] = []
        self.sorted_keys: list[int] = []

    def clear(self) -> None:
        self.stress_pair_data_array.clear()
        self.loaded_timestep.clear()
        self.sorted_keys.clear()

    def pre_load(self, file_name: str) -> None:
        with h5py.File(file_name, "r") as h5:
            keys = list(map(int, h5.keys()))
            self.sorted_keys = sorted(keys)

    def load(self, file_name: str) -> None:
        self.clear()
        self.pre_load(file_name)

        for key in self.sorted_keys:
            self.load_from_idx(file_name, key)

    def load_from_idx(self, file_name: str, idx: Union[int, str]) -> None:
        stress_pair_data = StressPairData()
        stress_pair_data.load(file_name, idx)
        self.loaded_timestep.append(int(idx))
        self.stress_pair_data_array.append(stress_pair_data)
