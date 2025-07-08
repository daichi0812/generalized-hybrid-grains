import os
import time
import xml.etree.ElementTree as ET
import sys
import h5py
import numpy as np
import shutil

def main():
    args = sys.argv

    if len(args) < 2:
        print('piledSimulationEnv.py shape_ratio_name homogenize_stress_fn')
        exit(1)

    shape_ratio_name = str(args[1])
    Save_folder_name = "Save_" + shape_ratio_name

    if not(os.path.isdir(Save_folder_name)):
        os.mkdir(Save_folder_name)

    #DEM書き換え
    DEM_fn =  args[2]
    DEM_tree = ET.parse(DEM_fn)
    DEM_root = DEM_tree.getroot()
    DEM_root[3].attrib["templates"] = "init_data/" + shape_ratio_name + "_template.h5"
    DEM_root[3].attrib["objects"] = "init_data/"  + shape_ratio_name + ".h5"
    DEM_root[4].attrib["folder"] = Save_folder_name
    DEM_root[4].attrib["processing_time"] = Save_folder_name + "/DEM_Processing_Time_" + shape_ratio_name + ".csv"
    DEM_tree.write(DEM_fn)

    

if __name__ == "__main__":
    main()