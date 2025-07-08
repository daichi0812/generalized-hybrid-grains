import os
import xml.etree.ElementTree as ET
import sys

args = sys.argv
DEM_fn = str(args[1])
DEM_tree = ET.parse(DEM_fn)
DEM_root = DEM_tree.getroot()
Save_folder_name = DEM_root[4].attrib["folder"]

if os.path.isfile('./sleep_flag.txt'):
    os.remove('./sleep_flag.txt')

if os.path.isfile(Save_folder_name + '/serialized_forces.h5'):
    os.remove(Save_folder_name + '/serialized_forces.h5')

if os.path.isfile(Save_folder_name + '/serialized_sigma.h5'):
    os.remove(Save_folder_name + '/serialized_sigma.h5')

if os.path.isfile('./DEMstress/DEM.h5'):
    os.remove('./DEMstress/DEM.h5')

if os.path.isfile('./DEMstress/DEM2.h5'):
    os.remove('./DEMstress/DEM2.h5')

if os.path.isfile('./MPMstress/MPM.h5'):
    os.remove('./MPMstress/MPM.h5')
