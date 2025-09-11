# 純正コード

# from struct import pack
# from homogenizerti import TiHomogenizationGrid
# from allforceh5 import *
# from allgrainh5 import *
# from allhomogenizationh5 import *
# from removeoutlier import *
# import os
# import xml.etree.ElementTree as ET
# import sys
# import time
# from csv import writer
# import ctypes

# def main(args):
#     resume_xml_fn = args[1]
#     dirname = os.path.dirname(args[1])
#     tree = ET.parse(resume_xml_fn)
#     root = tree.getroot()
#     print("called main.")


#     #２週目以降はファイルをロードする
#     filename = root[1].attrib["post_stress"]

#     element_fn = root[0].attrib["forces"]
#     template_fn = root[0].attrib["templates"]

#     homogenization_grid = TiHomogenizationGrid()

#     while True:
#         time.sleep(1.0)
#         # forceファイルが生成された場合
#         print("sleep...")
#         if os.path.exists('./sleep_flag.txt'):
#             path_to_element_fn = "." + dirname + "/" + element_fn
#             path_to_filename =  "." + dirname + "/" + filename
#             path_to_template = "." + dirname + "/" + template_fn
#             print("element_fn: ", path_to_element_fn)
#             print("filename: ",   path_to_filename)
#             print("os.path.exists(path_to_element_fn): ", os.path.exists(path_to_element_fn))
#             print("not(path_to_filename): ", os.path.exists(path_to_filename))
#             if os.path.exists(path_to_element_fn) and not os.path.exists(path_to_filename):
#                 print("receive: ", filename)
#                 allstepHomogenize(root, homogenization_grid, path_to_filename, path_to_element_fn, path_to_template)
#         if os.path.exists("./exit_flag.txt"):
#             print("exit")
#             os.remove("./exit_flag.txt")
#             sys.exit()

# def allstepHomogenize(root, homogenization_grid, filename, element_fn, template_fn):
#     strain_fn = root[1].attrib["strain"]

#     packing_fraction_threshold = float(root[3].attrib["packing_fraction_threshold"])
#     distance_from_wall_threshold = float(root[3].attrib["distance_from_wall_threshold"])

#     allforce_data = AllForceData()
#     #load all step force
#     #allforce_data.load(element_fn)

#     allscene_data = AllSceneData()
#     #load all step element
#     #allscene_data.load(template_fn, element_fn)

#     allhomogenization_data = AllHomogenizeData()
#     strain_data = AllHomogenizeData()

#     #gridのパラメータ
#     grid_start_offset_ratio = np.array([0.0, 0.0])
#     h = float(root[4].attrib["h"])

#     #タイムステップ取得
#     with h5py.File(element_fn, "r") as h5:
#         keys = list(map(str, h5.keys()))
#         keys.remove('force_num')
#         keys = list(map(int, keys))
#         sorted_keys = sorted(keys)
#         start_timestep = sorted_keys[0]
#         end_timestep = sorted_keys[-1] + 1
#         for i in range(start_timestep, end_timestep):
#             allhomogenization_data.all_timestep.append(i)
#             strain_data.all_timestep.append(i)

#     #全ステップの力を均質化する
#     max_loop = force_data_num(element_fn)

#     for i in range(max_loop):
#         allforce_data.load_from_idx_for_simulation(element_fn, i)

#         homogenization_data = HomogenizeData()

#         remove_outlier = RemoveOutlier()

#         homogenization_grid.setData(grid_start_offset_ratio, h, allforce_data)

#         homogenization_grid.calcHomogenizeStress()

#         homogenization_grid.saveStress(homogenization_data)

#         strain_data.all_step_homogenization.append(copy.deepcopy(homogenization_data))

#         allscene_data.load_from_idx_for_simulation(template_fn, element_fn,  i)

#         remove_outlier.setData(allscene_data, homogenization_data)

#         remove_outlier.removeGrid(homogenization_data, packing_fraction_threshold, distance_from_wall_threshold)

#         allhomogenization_data.all_step_homogenization.append(homogenization_data)

#     strain_data.save(strain_fn)

#     allhomogenization_data.save(filename)

# if __name__ == "__main__":
#     main(sys.argv)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
allsteptiHomogenizerSleep.py  (minimal patch)

目的:
- XML 内の相対パスを XML の所在ディレクトリ基準で絶対パス化する
- ファイル存在チェックの誤りを修正（not(path) → not os.path.exists(path)）
- DEM.h5 を全て計算された状態で出力する

既存の計算ロジックは変更しません。ログはデバッグ用にそのまま出します。
"""
# 2025-09-11 追加

import os, sys, time, copy
from pathlib import Path
import xml.etree.ElementTree as ET
import h5py
import numpy as np

# ★ CPUで初期化（f64対応）。Metal/Vulkanだとf64未対応で落ちる。
import taichi as ti

ti.init(arch=ti.cpu, default_fp=ti.f64)

from homogenizerti import TiHomogenizationGrid
from allforceh5 import *
from allgrainh5 import *
from allhomogenizationh5 import *
from removeoutlier import *

def resolve(base: Path, p: str) -> str:
    return os.path.normpath(p if os.path.isabs(p) else str(base / p))

def dem_has_sigma_any(fn: str) -> bool:
    """DEM.h5 に少なくとも /0/homogenization/sigma があるか"""
    if not os.path.exists(fn):
        return False
    try:
        with h5py.File(fn, "r") as f:
            if "0" not in f:
                return False
            g = f["0"]
            if "homogenization" not in g:
                return False
            hg = g["homogenization"]
            return "sigma" in hg
    except Exception:
        return False


def allstep_homogenize(root, out_dem_h5: str, forces_h5: str, template_h5: str):
    # 出力(歪み)ファイル
    strain_fn = root.find("stress").attrib["strain"]

    # outlier 閾値あ
    outlier = root.find("outlier")
    packing_fraction_threshold = float(outlier.attrib["packing_fraction_threshold"])
    distance_from_wall_threshold = float(outlier.attrib["distance_from_wall_threshold"])

    # グリッド設定
    grid = root.find("grid")
    h = float(grid.attrib["h"])
    grid_start_offset_ratio = np.array([0.0, 0.0])

    # データ入れ物
    allforce_data = AllForceData()
    allscene_data = AllSceneData()
    allhomogenization_data = AllHomogenizeData()
    strain_data = AllHomogenizeData()

    # タイムステップ列（forces のキーから組む）
    with h5py.File(forces_h5, "r") as h5:
        keys = [k for k in h5.keys() if k != "force_num"]
        if not keys:
            raise RuntimeError(f"No force steps in {forces_h5}")
        steps = sorted(map(int, keys))
        for i in steps:
            allhomogenization_data.all_timestep.append(i)
            strain_data.all_timestep.append(i)

    max_loop = force_data_num(forces_h5)
    homogenization_grid = TiHomogenizationGrid()

    for i in range(max_loop):
        # 力を1ステップロード
        allforce_data.load_from_idx_for_simulation(forces_h5, i)

        # 均質化
        homogenization_data = HomogenizeData()
        homogenization_grid.setData(grid_start_offset_ratio, h, allforce_data)
        homogenization_grid.calcHomogenizeStress()
        homogenization_grid.saveStress(homogenization_data)

        # 歪み側は outlier 前の生データを保存
        strain_data.all_step_homogenization.append(copy.deepcopy(homogenization_data))

        # 要素配置をロードして outlier 除去 → 応力側
        allscene_data.load_from_idx_for_simulation(template_h5, forces_h5, i)
        remove_outlier = RemoveOutlier()
        remove_outlier.setData(allscene_data, homogenization_data)
        remove_outlier.removeGrid(
            homogenization_data,
            packing_fraction_threshold,
            distance_from_wall_threshold,
        )
        allhomogenization_data.all_step_homogenization.append(homogenization_data)

    # 書き出し
    os.makedirs(os.path.dirname(out_dem_h5), exist_ok=True)
    # --- 2025-09-11 ここから追加 ---
    os.makedirs(os.path.dirname(strain_fn), exist_ok=True)
    # 既存ファイルがあれば削除して新規作成
    for fn in (strain_fn, out_dem_h5):
        try:
            os.remove(fn)
        except FileNotFoundError:
            pass
    # --- 2025-09-11 ここまで追加 ---
    strain_data.save(strain_fn)
    allhomogenization_data.save(out_dem_h5)
    print(f"[OK] wrote homogenization: {out_dem_h5}")


def main(argv):
    if len(argv) < 2:
        print("Usage: allsteptiHomogenizerSleep.py path/to/homogenize_stress.xml")
        sys.exit(1)

    xml_path = Path(argv[1]).resolve()
    base = xml_path.parent

    tree = ET.parse(str(xml_path))
    root = tree.getroot()
    elements = root.find("elements")
    stress = root.find("stress")

    forces_rel = elements.attrib["forces"]
    template_rel = elements.attrib["templates"]
    dem_rel = stress.attrib.get("post_stress") or stress.attrib["strain"]

    forces_h5 = resolve(base, forces_rel)
    template_h5 = resolve(base, template_rel)
    dem_h5 = resolve(base, dem_rel)

    print("called main.")
    print("element_fn: ", forces_h5)
    print("dem_file  : ", dem_h5)

    while True:
        # makeSleepFlag.py が置くフラグを見て起動
        if os.path.exists("./sleep_flag.txt"):
            ready = os.path.exists(forces_h5) and os.path.getsize(forces_h5) > 0
            need = not dem_has_sigma_any(dem_h5)
            print("ready_forces:", ready, "need_build_dem:", need)
            if ready and need:
                try:
                    allstep_homogenize(root, dem_h5, forces_h5, template_h5)
                except Exception as e:
                    print("[ERR] homogenize failed:", e)
        time.sleep(1.0)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
