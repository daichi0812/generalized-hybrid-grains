import h5py
import numpy as np
from forceh5 import *

class AllForceData:
    def __init__(self):
        self.all_step_ForceData = []

    def __load_forces(self, fileName):
        if fileName != "" and fileName[len(fileName)-3:] == ".h5":
            
            with h5py.File(fileName, 'r') as h5_forces:
                keys = list(map(str, h5_forces.keys()))
                keys.remove('force_num')
                keys = list(map(int, keys))
                newlist = sorted(keys)
                for i in newlist:
                    data_group = h5_forces[str(i)]
                    f_group = data_group['forces_2d']
                    position_array = np.array(f_group['position'], dtype=np.float64)
                    arm_array = np.array(f_group['arm'], dtype=np.float64)
                    force_array = np.array(f_group['force'], dtype=np.float64)

                    num_forces = position_array.shape[1]

                    force = ForceData()
                    for i in range(num_forces):
                        f = Force()
                        f.position = position_array[:,i]
                        f.arm = arm_array[:,i]
                        f.force = force_array[:,i]
                        force.forces.append(f)
                    self.all_step_ForceData.append(force)
                

    def load(self, fn_element):
        self.__load_forces(fn_element)

    def __load_forces_from_idx(self, fileName, idx):
        if fileName != "" and fileName[len(fileName) - 3:] == ".h5":
            self.all_step_ForceData.clear()
            with h5py.File(fileName, 'r') as h5_forces:
                #idx番目のkeyを取得
                keys = list(map(str, h5_forces.keys()))
                keys.remove('force_num')
                keys = list(map(int, keys))
                newlist = sorted(keys)

                data_group = h5_forces[str(newlist[idx])]
                f_group = data_group['forces_2d']
                position_array = np.array(f_group['position'], dtype=np.float64)
                arm_array = np.array(f_group['arm'], dtype=np.float64)
                force_array = np.array(f_group['force'], dtype=np.float64)
                num_forces = position_array.shape[1]

                force = ForceData()
                for i in range(num_forces):
                    f = Force()
                    f.position = position_array[:, i]
                    f.arm = arm_array[:, i]
                    f.force = force_array[:, i]
                    force.forces.append(f)
                self.all_step_ForceData.append(force)
    def load_from_idx(self, fn_element, idx):
        self.__load_forces_from_idx(fn_element, idx)

def force_data_num(post_fn):
    with h5py.File(post_fn, 'r') as h5_forces:
        keys = list(map(str, h5_forces.keys()))
        keys.remove('force_num')
        keys = list(map(int, keys))
        newlist = sorted(keys)
        data_num = len(newlist)
    return data_num
