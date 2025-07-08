import h5py
import numpy as np

class Force:
    def __init__(self):
        self.position = np.array([0.0, 0.0]).transpose()
        self.arm = np.array([0.0, 0.0]).transpose()
        self.force = np.array([0.0, 0.0]).transpose()

class ForceData:
    def __init__(self):
        self.forces = []

    def __load_forces(self, fileName):
        self.forces.clear()
        if fileName != "" and fileName[len(fileName)-3:] == ".h5":

            with h5py.File(fileName, 'r') as h5_forces:
                f_group = h5_forces['forces_2d']

                position_array = np.array(f_group['position'], dtype=np.float64)
                arm_array = np.array(f_group['arm'], dtype=np.float64)
                force_array = np.array(f_group['force'], dtype=np.float64)

                num_forces = position_array.shape[1]

                for i in range(num_forces):
                    f = Force()
                    f.position = position_array[:,i]
                    f.arm = arm_array[:,i]
                    f.force = force_array[:,i]
                    self.forces.append(f)

    def load(self, fn_element):
        self.__load_forces(fn_element)
