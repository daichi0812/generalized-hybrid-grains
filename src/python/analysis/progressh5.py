import h5py
import numpy as np

class Progress:
    def __init__(self):
        self.dt = 1.0
        self.serialization_idx = 1
        self.tick_count = 1
        self.time = 1.0

class ProgressData:
    def __init__(self):
        self.progress = []

    def __load_progress(self, fileName):
        self.progress.clear()

        if fileName != "" and fileName[len(fileName)-3:] == ".h5":
            with h5py.File(fileName, 'r') as h5_templates:
                pg_group = h5_templates['progress_data']
                new_Progress = Progress()
                new_Progress.dt = np.double(pg_group['dt'])
                new_Progress.serialization_idx = np.int32(pg_group['serialization_idx'])
                new_Progress.tick_count = np.int32(pg_group['tick_count'])
                new_Progress.time = np.double(pg_group['time'])
                self.progress.append(new_Progress)
                


    def load(self, fn_element):
        self.__load_progress(fn_element)