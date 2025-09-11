# # --- 2025-09-11 コメントアウト ---
# from allgrainh5 import*
# from progressh5 import *
# from allhomogenizationh5 import *
# from interpolateMPMStress import *
# from particlehomogenizationh5 import *
# import xml.etree.ElementTree as ET 
# import sys
# import subprocess
# import time
# import ctypes

# #全ステップの力をロード
# args = sys.argv
# resume_xml_fn = args[1]
# tree = ET.parse(resume_xml_fn)
# root = tree.getroot()

# element_fn = root[0].attrib["MPMstress"]
# allelements = AllParticleHomogenizeData()
# #全ステップ粒子ロードする
# #allelements.load(element_fn)
# allhomogenization_data = AllHomogenizeData()

# pre_fn = root[1].attrib["pre_stress"]
# #２週目以降はファイルをロードする
# """
# is_file = os.path.isfile(pre_fn)
# if is_file:
#     allhomogenization_data.load(pre_fn)
# """

# #grid_startを取ってくる
# post_fn = root[1].attrib["post_stress"]
# allpost_homogenization_data = AllHomogenizeData()
# allpost_homogenization_data.load(post_fn)

# #gridのパラメータ
# h = float(root[4].attrib["h"])

# #density
# # XMLファイルを解析
# resume_fn = root[2].attrib["resume_MPM_fn"]
# resume_tree = ET.parse(resume_fn)
# resume_root = resume_tree.getroot()
# density = float(resume_root[2].attrib["density"])

# #タイムステップ取得
# #print(os.path.getsize(element_fn))
# #print(os.path.exists(element_fn))

# with h5py.File(element_fn, "r") as h5:
#     keys = list(map(int, h5.keys()))
#     sorted_keys = sorted(keys)
#     start_timestep = sorted_keys[0]
#     end_timestep = sorted_keys[-1] + 1
#     for i in range(start_timestep, end_timestep):
#         allhomogenization_data.all_timestep.append(i)

# max_loop = MPM_data_num(element_fn)
# for i in range(max_loop):
#     allelements.load_from_idx(element_fn, i)
#     particle_force = allelements.all_step_particle_homogenization[0]
#     homogenization_data = HomogenizeData()
#     #粒子の応力を格子の中心に補完する
#     #比較対象となるDEM格子のgrid_startを取り出す。
#     grid_start = allpost_homogenization_data.all_step_homogenization[i].homogenization[0].grid_p

#     interpolate_stress = interpolateMPMStress(h, particle_force, grid_start)
#     interpolate_stress.interpolateStress()
#     interpolate_stress.saveStress(homogenization_data)
#     allhomogenization_data.all_step_homogenization.append(homogenization_data)

# allhomogenization_data.save(pre_fn)

# # --- 2025-09-11 コメントアウト ここまで ---

# --- 2025-09-11 追加 ---
from allgrainh5 import*
from progressh5 import *
from allhomogenizationh5 import *
from interpolateMPMStress import *
from particlehomogenizationh5 import *
import xml.etree.ElementTree as ET 
import sys
import subprocess
import time
import ctypes

#全ステップの力をロード
args = sys.argv
resume_xml_fn = args[1]
tree = ET.parse(resume_xml_fn)
root = tree.getroot()

element_fn = root[0].attrib["MPMstress"]
allelements = AllParticleHomogenizeData()
allhomogenization_data = AllHomogenizeData()

pre_fn = root[1].attrib["pre_stress"]

# --- 既存 pre を消すだけ（ここでは save しない） ---
import os, h5py
os.makedirs(os.path.dirname(pre_fn), exist_ok=True)
try:
    os.remove(pre_fn)
except FileNotFoundError:
    pass
# （※ここで allhomogenization_data.save(pre_fn) を呼ばない）

#grid_startを取ってくる
post_fn = root[1].attrib["post_stress"]
allpost_homogenization_data = AllHomogenizeData()
allpost_homogenization_data.load(post_fn)

#gridのパラメータ
h = float(root[4].attrib["h"])

#density
resume_fn = root[2].attrib["resume_MPM_fn"]
resume_tree = ET.parse(resume_fn)
resume_root = resume_tree.getroot()
density = float(resume_root[2].attrib["density"])

# --- forces が書かれるまで待つ ---
def wait_for_forces(h5_fn, min_frames=1, timeout_sec=600, poll_sec=0.5):
    t0 = time.time()
    last = -1
    while True:
        try:
            n = MPM_data_num(h5_fn)
        except Exception:
            n = 0
        if n >= min_frames:
            return n
        if time.time() - t0 > timeout_sec:
            raise TimeoutError(f"Timeout waiting for {h5_fn} to have >= {min_frames} frames (last n={n})")
        # 進捗が見えるようにたまにログ出し
        if n != last:
            print(f"[WAIT] serialized_forces: {n} frames (waiting for >= {min_frames})")
            last = n
        time.sleep(poll_sec)

# === タイムステップ決定（post 側は既に 1000 ある想定） ===
n_forces = wait_for_forces(element_fn, min_frames=1)  # まず1フレーム来るまでブロック
n_post   = len(allpost_homogenization_data.all_step_homogenization)

max_loop = min(n_forces, n_post)
if max_loop <= 0:
    raise RuntimeError(f"No frames to process: forces={n_forces}, post={n_post}")

print(f"[INFO] frames: forces={n_forces}, post={n_post}, process={max_loop}")

# /homogenization/<timestep> の作成順
allhomogenization_data.all_timestep = list(range(max_loop))

# === メインループ ===
for i in range(max_loop):
    allelements.load_from_idx(element_fn, i)
    particle_force = allelements.all_step_particle_homogenization[0]

    # post 側の grid_start を使用
    grid_start = allpost_homogenization_data.all_step_homogenization[i].homogenization[0].grid_p

    interpolate_stress = interpolateMPMStress(h, particle_force, grid_start)
    interpolate_stress.interpolateStress()

    homogenization_data = HomogenizeData()
    interpolate_stress.saveStress(homogenization_data)
    allhomogenization_data.all_step_homogenization.append(homogenization_data)

# 最後に一度だけ保存
allhomogenization_data.save(pre_fn)
print(f"[OK] wrote pre_stress to: {pre_fn}")
# --- 2025-09-11 追加 ここまで ---