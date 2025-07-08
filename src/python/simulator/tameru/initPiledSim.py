import os
import time
import xml.etree.ElementTree as ET
import sys
import h5py
import numpy as np
import shutil

def main():
    args = sys.argv
    # print("args[2]: ", args[2])
    if len(args) < 2:
        print('piledSimulationEnv.py shape_ratio_name homogenize_stress_fn')
        exit(1)
    working_dir = str(args[1])
    print("working_dir", working_dir)

    shape_file = working_dir + str(args[2])
    template_file = working_dir + str(args[3])
    save_folder_name = working_dir + "output"
    print("save_folder_name",save_folder_name)
    

    if not(os.path.isdir(save_folder_name)):
        os.mkdir(save_folder_name)

    #DEM書き換え
    DEM_fn =  args[4]
    DEM_tree = ET.parse(DEM_fn)
    DEM_root = DEM_tree.getroot()
    DEM_root[3].attrib["objects"] = shape_file
    DEM_root[3].attrib["templates"] = template_file
    DEM_root[4].attrib["folder"] = save_folder_name
    DEM_root[4].attrib["processing_time"] = save_folder_name + "/DEM_Processing_Time_" + shape_file + ".csv"
    DEM_tree.write(DEM_fn)

    

if __name__ == "__main__":
    main()