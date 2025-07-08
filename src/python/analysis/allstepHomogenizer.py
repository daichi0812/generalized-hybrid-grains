from struct import pack
from homogenizer import *
from allforceh5 import *
from allgrainh5 import *
from allhomogenizationh5 import *
from removeoutlier import *
import os
import xml.etree.ElementTree as ET 
import sys

#全ステップの力をロードする。allforce[step]=forceData()
args = sys.argv
if len(args) < 2:
    print('rewriteResumefn.py homogenize_stress_fn')
resume_xml_fn = args[1]
tree = ET.parse(resume_xml_fn)
root = tree.getroot()
if root[0].tag !="elements":
    print("not elements line")
template_fn = root[0].attrib["templates"]
element_fn = root[0].attrib["forces"]

if root[1].tag != "stress":
    print("not stress line")
strain_fn = root[1].attrib["strain"]

if root[3].tag != "outlier":
    print("not outlier line")
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

#２週目以降はファイルをロードする
if root[1].tag !="stress":
    print("not resume line")
filename = root[1].attrib["post_stress"]
"""
is_file = os.path.isfile(filename)
if is_file:
    allhomogenization_data.load(filename)
"""

#gridのパラメータ
grid_start_offset_ratio = np.array([0.0, 0.0])
if root[4].tag !="grid":
    print("not grid line")
h = float(root[4].attrib["h"])

#タイムステップ取得
with h5py.File(element_fn, "r") as h5:
    keys = list(map(str, h5.keys()))
    keys.remove('force_num')
    keys = list(map(int, keys))
    sorted_keys = sorted(keys)
    start_timestep = sorted_keys[0]
    end_timestep = sorted_keys[-1] + 1
    for i in range (start_timestep, end_timestep):
        allhomogenization_data.all_timestep.append(i)
        strain_data.all_timestep.append(i)

#全ステップの力を均質化する
max_loop = force_data_num(element_fn)
for i in range(max_loop):
    allforce_data.load_from_idx(element_fn, i)
    force_data = allforce_data.all_step_ForceData[0]
    homogenization_data = HomogenizeData()
    homogenization_grid = HomogenizationGrid()
    remove_outlier = RemoveOutlier()
    homogenization_grid.setData(grid_start_offset_ratio, h, force_data, homogenization_data)
    strain_data.all_step_homogenization.append(copy.deepcopy(homogenization_data))

    allscene_data.load_from_idx(template_fn, element_fn,  i)
    scene_data = allscene_data.all_step_elements[0]
    remove_outlier.setData(scene_data, homogenization_data)
    remove_outlier.removeGrid(homogenization_data, packing_fraction_threshold, distance_from_wall_threshold)
    allhomogenization_data.all_step_homogenization.append(homogenization_data)

allhomogenization_data.save(filename)
strain_data.save(strain_fn)
