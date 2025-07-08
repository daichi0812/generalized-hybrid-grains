from homogenizer import *
from allforceh5 import *
from allgrainh5 import *
from allhomogenizationh5 import *
from removeoutlier import *
import tkinter.filedialog
import math

def main():
    scene_data1 = SceneData()
    scene_data2 = SceneData()
    t_fn = tkinter.filedialog.askopenfilename(filetypes=[("hdf file", "*.h5")])
    e_fn = tkinter.filedialog.askopenfilename(filetypes=[("hdf file", "*.h5")])
    scene_data1.load(t_fn, e_fn)
    e_fn2 = tkinter.filedialog.askopenfilename(filetypes=[("hdf file", "*.h5")])
    scene_data2.load(t_fn, e_fn2)

    angular_velocity_error = 0.0
    center_of_mass_error = np.array([0.0, 0.0]).transpose()
    rotation_angle_error = 0.0
    velocity_error = np.array([0.0, 0.0]).transpose()

    for i, e in enumerate(scene_data1.elements):
        if e.static == scene_data2.elements[i].static:
            angular_velocity_error += abs(e.angular_velocity - scene_data2.elements[i].angular_velocity)
            center_of_mass_error += abs(e.center_of_mass - scene_data2.elements[i].center_of_mass)
            rotation_angle_error += abs(e.rotation_angle - scene_data2.elements[i].rotation_angle)
            velocity_error += abs(e.velocity - scene_data2.elements[i].velocity)

    print('average angular_velocity error:' + str(angular_velocity_error / len(scene_data1.elements)))
    print('average center_of_mass:' + str(center_of_mass_error / len(scene_data1.elements)))
    print('average rotation_angle:' + str(rotation_angle_error / len(scene_data1.elements)))
    print('average velocity:' + str(velocity_error / len(scene_data1.elements)))

if __name__ == "__main__":
    main()