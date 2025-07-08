from allgrainh5 import*
from progressh5 import *
from allhomogenizationh5 import *
from interpolateMPMStress import *
from particlehomogenizationh5 import *
import xml.etree.ElementTree as ET 
import sys
import subprocess

#全ステップの力をロード
args = sys.argv
if len(args) < 2:
    print('rewriteResumefn.py homogenize_stress_fn')
resume_xml_fn = args[1]
tree = ET.parse(resume_xml_fn)
root = tree.getroot()
if root[0].tag !="elements":
    print("not resume line")
element_fn = root[0].attrib["MPMstress"]
allelements = AllParticleHomogenizeData()
#全ステップ粒子ロードする
#allelements.load(element_fn)


allhomogenization_data = AllHomogenizeData()

if root[1].tag !="stress":
    print("not stress line")
pre_fn = root[1].attrib["pre_stress"]
#２週目以降はファイルをロードする
"""
is_file = os.path.isfile(pre_fn)
if is_file:
    allhomogenization_data.load(pre_fn)
"""

#grid_startを取ってくる
if root[1].tag !="stress":
    print("not resume line")
post_fn = root[1].attrib["post_stress"]
allpost_homogenization_data = AllHomogenizeData()
allpost_homogenization_data.load(post_fn)

#gridのパラメータ
if root[4].tag !="grid":
    print("not grid line")
h = float(root[4].attrib["h"])

#density
# XMLファイルを解析
if root[2].tag !="resume":
    print("not resume line")
resume_fn = root[2].attrib["resume_MPM_fn"]
resume_tree = ET.parse(resume_fn)
resume_root = resume_tree.getroot()
if resume_root[2].tag !="particles":
    print("not particles line")
density = float(resume_root[2].attrib["density"])

#タイムステップ取得
with h5py.File(element_fn, "r") as h5:
    keys = list(map(int, h5.keys()))
    sorted_keys = sorted(keys)
    start_timestep = sorted_keys[0]
    end_timestep = sorted_keys[-1] + 1
    for i in range(start_timestep, end_timestep):
        allhomogenization_data.all_timestep.append(i)

max_loop = MPM_data_num(element_fn)
for i in range(max_loop):
    allelements.load_from_idx(element_fn, i)
    particle_force = allelements.all_step_particle_homogenization[0]
    homogenization_data = HomogenizeData()
    #粒子の応力を格子の中心に補完する
    #比較対象となるDEM格子のgrid_startを取り出す。
    grid_start = allpost_homogenization_data.all_step_homogenization[i].homogenization[0].grid_p

    interpolate_stress = interpolateMPMStress(h, particle_force, grid_start)
    interpolate_stress.interpolateStress()
    interpolate_stress.saveStress(homogenization_data)
    allhomogenization_data.all_step_homogenization.append(homogenization_data)
    print(i)
allhomogenization_data.save(pre_fn)

    