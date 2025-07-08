from homogenizer import *
from allforceh5 import *
from allgrainh5 import *
from allhomogenizationh5 import *
from removeoutlier import *
import tkinter.filedialog
import math
import ctypes
import matplotlib.pyplot as plt

def main():
    scene_data1 = SceneData()
    scene_data2 = SceneData()
    t_fn = tkinter.filedialog.askopenfilename(filetypes=[("hdf file", "*.h5")])
    e_fn = tkinter.filedialog.askopenfilename(filetypes=[("hdf file", "*.h5")])
    scene_data1.load(t_fn, e_fn)
    e_fn = tkinter.filedialog.askopenfilename(filetypes=[("hdf file", "*.h5")])
    scene_data2.load(t_fn, e_fn)
    position_marker1 = np.zeros((2, len(scene_data1.elements)), dtype=ctypes.c_float)
    position_marker2 = np.zeros((2, len(scene_data2.elements)), dtype=ctypes.c_float)

    for i, p in enumerate(scene_data1.elements):
        if p.static == 0:
            position_marker1[:, i] = p.center_of_mass

    for i, p in enumerate(scene_data2.elements):
        if p.static == 0:
            position_marker2[:, i] = p.center_of_mass

    plt.figure(figsize=(5, 5))
    plt.scatter(position_marker1[0], position_marker1[1], c="red", s=10, alpha=0.5)
    plt.scatter(position_marker2[0], position_marker2[1], c="green", s=10, alpha=0.5)
    plt.xlabel("x")
    plt.ylabel("y")
    g = plt.subplot()

    #plot aspect ratio
    g.set_ylim([-0.5, 0.5])
    g.set_xlim([-0.5, 0.5])
    plt.show()

if __name__ == "__main__":
    main()