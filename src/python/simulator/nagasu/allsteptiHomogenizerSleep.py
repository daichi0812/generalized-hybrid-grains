from struct import pack
from homogenizerti import TiHomogenizationGrid
from allforceh5 import *
from allgrainh5 import *
from allhomogenizationh5 import *
from removeoutlier import *
import os
import xml.etree.ElementTree as ET
import sys
import time
from csv import writer
import ctypes

def main(args):
    resume_xml_fn = args[1]
    dirname = os.path.dirname(args[1])
    tree = ET.parse(resume_xml_fn)
    root = tree.getroot()
    print("called main.")


    #２週目以降はファイルをロードする
    filename = root[1].attrib["post_stress"]

    element_fn = root[0].attrib["forces"]
    template_fn = root[0].attrib["templates"]

    homogenization_grid = TiHomogenizationGrid()

    while True:
        time.sleep(1.0)
        # forceファイルが生成された場合
        print("sleep...")
        if os.path.exists('./sleep_flag.txt'):
            path_to_element_fn = "." + dirname + "/" + element_fn
            path_to_filename =  "." + dirname + "/" + filename
            path_to_template = "." + dirname + "/" + template_fn
            print("element_fn: ", path_to_element_fn)
            print("filename: ",   path_to_filename)
            print("os.path.exists(path_to_element_fn): ", os.path.exists(path_to_element_fn))
            print("not(path_to_filename): ", os.path.exists(path_to_filename))
            if os.path.exists(path_to_element_fn) and not os.path.exists(path_to_filename):
                print("receive: ", filename)
                allstepHomogenize(root, homogenization_grid, path_to_filename, path_to_element_fn, path_to_template)
        if os.path.exists("./exit_flag.txt"):
            print("exit")
            os.remove("./exit_flag.txt")
            sys.exit()

def allstepHomogenize(root, homogenization_grid, filename, element_fn, template_fn):
    strain_fn = root[1].attrib["strain"]

    packing_fraction_threshold = float(root[3].attrib["packing_fraction_threshold"])
    distance_from_wall_threshold = float(root[3].attrib["distance_from_wall_threshold"])

    allforce_data = AllForceData()
    #load all step force
    #allforce_data.load(element_fn)

    allscene_data = AllSceneData()
    #load all step element
    #allscene_data.load(template_fn, element_fn)

    allhomogenization_data = AllHomogenizeData()
    strain_data = AllHomogenizeData()

    #gridのパラメータ
    grid_start_offset_ratio = np.array([0.0, 0.0])
    h = float(root[4].attrib["h"])

    #タイムステップ取得
    with h5py.File(element_fn, "r") as h5:
        keys = list(map(str, h5.keys()))
        keys.remove('force_num')
        keys = list(map(int, keys))
        sorted_keys = sorted(keys)
        start_timestep = sorted_keys[0]
        end_timestep = sorted_keys[-1] + 1
        for i in range(start_timestep, end_timestep):
            allhomogenization_data.all_timestep.append(i)
            strain_data.all_timestep.append(i)

    #全ステップの力を均質化する
    max_loop = force_data_num(element_fn)

    for i in range(max_loop):
        allforce_data.load_from_idx_for_simulation(element_fn, i)

        homogenization_data = HomogenizeData()

        remove_outlier = RemoveOutlier()

        homogenization_grid.setData(grid_start_offset_ratio, h, allforce_data)

        homogenization_grid.calcHomogenizeStress()

        homogenization_grid.saveStress(homogenization_data)

        strain_data.all_step_homogenization.append(copy.deepcopy(homogenization_data))

        allscene_data.load_from_idx_for_simulation(template_fn, element_fn,  i)

        remove_outlier.setData(allscene_data, homogenization_data)

        remove_outlier.removeGrid(homogenization_data, packing_fraction_threshold, distance_from_wall_threshold)

        allhomogenization_data.all_step_homogenization.append(homogenization_data)

    strain_data.save(strain_fn)

    allhomogenization_data.save(filename)

if __name__ == "__main__":
    main(sys.argv)

