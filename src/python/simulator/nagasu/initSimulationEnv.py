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
        print('initSimulationEnv.py shape_ratio_name homogenize_stress_fn')
        exit(1)

    shape_ratio_name = str(args[1])
    Save_folder_name = "Save_" + shape_ratio_name
    Rolling_folder_name = "Rolling_" + shape_ratio_name
    #形状_比フォルダ作成
    if not(os.path.isdir(Save_folder_name)):
        os.mkdir(Save_folder_name)
    if not(os.path.isdir(Rolling_folder_name)):
        os.mkdir(Rolling_folder_name)
    if not(os.path.isdir('./DEMstress')):
        os.mkdir('DEMstress')
    if not(os.path.isdir('./MPMstress')):
        os.mkdir('MPMstress')

    #homogenize_stress書き換え
    homogenize_stress_fn = args[2]
    homogenize_tree = ET.parse(homogenize_stress_fn)
    homogenize_root = homogenize_tree.getroot()
    homogenize_root[0].attrib["templates"] = Save_folder_name + "/" + shape_ratio_name + "_template.h5"
    homogenize_root[0].attrib["forces"] = Save_folder_name + "/serialized_forces.h5"
    homogenize_root[0].attrib["MPMstress"] = Save_folder_name + "/serialized_sigma.h5"
    homogenize_root[1].attrib["stress_pair"] = Save_folder_name + "/stress_pair.h5"
    homogenize_root[5].attrib["base_elem"] = Rolling_folder_name + "/element_data.h5"
    homogenize_root[5].attrib["base_stress"] = Rolling_folder_name + "/stress_pair.h5"
    if homogenize_root[6].attrib["mode"] == 1:
        homogenize_root[6].attrib["processing_time"] = Save_folder_name + "/Homogenize_Processing_Time_" + shape_ratio_name + ".csv"
        homogenize_root[6].attrib["homogenize_time"] = Save_folder_name + "/Homogenize_DEM_Time_" + shape_ratio_name + ".csv"
    homogenize_tree.write(homogenize_stress_fn)

    #DEM書き換え
    DEM_fn = homogenize_root[2].attrib["resume_fn"]
    DEM_tree = ET.parse(DEM_fn)
    DEM_root = DEM_tree.getroot()
    DEM_root[3].attrib["templates"] = Save_folder_name + "/" + shape_ratio_name + "_template.h5"
    DEM_root[3].attrib["objects"] = Save_folder_name + "/" + shape_ratio_name + ".h5"
    DEM_root[4].attrib["folder"] = Save_folder_name
    DEM_root[4].attrib["objects"] = shape_ratio_name + ".h5"
    DEM_root[4].attrib["processing_time"] = Save_folder_name + "/DEM_Processing_Time_" + shape_ratio_name + ".csv"
    DEM_tree.write(DEM_fn)

    #MPM書き換え
    MPM_fn = homogenize_root[2].attrib["resume_MPM_fn"]
    MPM_tree = ET.parse(MPM_fn)
    MPM_root = MPM_tree.getroot()
    MPM_root[5].attrib["templates"] = Save_folder_name + "/" + shape_ratio_name + "_template.h5"
    MPM_root[5].attrib["forces"] = Save_folder_name + "/" + "serialized_forces.h5"
    MPM_root[6].attrib["folder"] = Save_folder_name
    if MPM_root[6].attrib["mode"] == "1":
        MPM_root[6].attrib["processing_time"] = Save_folder_name + "/MPM_Processing_Time_" + shape_ratio_name + ".csv"

    MPM_tree.write(MPM_fn)


if __name__ == "__main__":
    main()