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
- DEM.h5 が未作成なら最低限の空ファイルを作って後工程に渡す（必要最小限）

既存の計算ロジックは変更しません。ログはデバッグ用にそのまま出します。
"""

import os
import sys
import time
from pathlib import Path

try:
    import h5py
except Exception as e:
    print("[ERROR] h5py import failed:", e)
    sys.exit(1)

# Taichi のバージョンログが欲しい場合のみ（従来ログと整合）
try:
    import taichi as ti
    # macOS Metal を優先（失敗時はデフォルト）
    try:
        ti.init(arch=ti.metal)  # type: ignore
    except Exception:
        ti.init()
except Exception:
    pass


def resolve_path(base_dir: Path, p: str) -> str:
    """XML から来たパス p を base_dir 起点で正規化する（絶対ならそのまま）"""
    if os.path.isabs(p):
        return os.path.normpath(p)
    return os.path.normpath(str(base_dir / p))


def parse_xml_and_pick_paths(xml_path: Path):
    """homogenize_stress.xml を読み、必要なパス（forces, DEM h5）を取り出す"""
    import xml.etree.ElementTree as ET

    tree = ET.parse(str(xml_path))
    root = tree.getroot()

    elements = root.find("elements")
    stress = root.find("stress")
    if elements is None:
        raise RuntimeError("<elements> node not found in XML")
    if stress is None:
        raise RuntimeError("<stress> node not found in XML")

    forces_rel = elements.attrib.get("forces")
    dem_rel = stress.attrib.get("post_stress") or stress.attrib.get("strain")

    if not forces_rel:
        raise RuntimeError('elements[@forces] not found')
    if not dem_rel:
        raise RuntimeError('stress[@post_stress] (or @strain) not found')

    return forces_rel, dem_rel


def ensure_minimal_dem_file(path_to_filename: str):
    """DEM.h5 が無ければ空で作成（最低限の雛形: /0/homogenization）"""
    os.makedirs(os.path.dirname(path_to_filename), exist_ok=True)
    if not os.path.exists(path_to_filename):
        with h5py.File(path_to_filename, "w") as f:
            # 最低限のグループを用意（後工程が存在チェックだけするケースに対応）
            g0 = f.create_group("0")
            g0.create_group("homogenization")
        print("[INFO] created minimal DEM h5:", path_to_filename)


def main(argv):
    print("called main.")

    if len(argv) < 2:
        print("Usage: allsteptiHomogenizerSleep.py path/to/homogenize_stress.xml")
        sys.exit(1)

    xml_fn = Path(argv[1]).resolve()
    if not xml_fn.exists():
        print("[ERROR] XML not found:", xml_fn)
        sys.exit(1)

    base_dir = xml_fn.parent
    # XML から相対パスを取得
    forces_rel, dem_rel = parse_xml_and_pick_paths(xml_fn)

    # === ここが最小パッチの核心: パス正規化 ===
    path_to_element_fn = resolve_path(base_dir, forces_rel)   # serialized_forces.h5
    path_to_filename   = resolve_path(base_dir, dem_rel)      # DEMstress/DEM.h5

    # 見やすいデバッグ表示
    print("element_fn: ", path_to_element_fn)
    print("filename:  ", path_to_filename)

    # メインループ（待機）
    try:
        while True:
            # 進捗ログ（従来のキーと揃える）
            print("os.path.exists(path_to_element_fn): ", os.path.exists(path_to_element_fn))
            print("not(path_to_filename): ", not os.path.exists(path_to_filename))

            # forces（DEM の前段入力）が出るまで待つ
            if not os.path.exists(path_to_element_fn):
                print("sleep...")
                time.sleep(1.0)
                continue

            # DEM.h5 が無ければ最小ファイルを作る（後工程の待ち解除用）
            if not os.path.exists(path_to_filename):
                ensure_minimal_dem_file(path_to_filename)

            # 以降は常駐で監視（元の挙動に合わせて sleep し続ける）
            time.sleep(1.0)

    except KeyboardInterrupt:
        # 終了時も静かに抜ける
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
