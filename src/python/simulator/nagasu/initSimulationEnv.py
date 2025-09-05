# import os
# import time
# import xml.etree.ElementTree as ET
# import sys
# import h5py
# import numpy as np
# import shutil

# def main():
#     args = sys.argv

#     if len(args) < 2:
#         print('initSimulationEnv.py shape_ratio_name homogenize_stress_fn')
#         exit(1)

#     shape_ratio_name = str(args[1])
#     Save_folder_name = "Save_" + shape_ratio_name
#     Rolling_folder_name = "Rolling_" + shape_ratio_name
#     #形状_比フォルダ作成
#     if not(os.path.isdir(Save_folder_name)):
#         os.mkdir(Save_folder_name)
#     if not(os.path.isdir(Rolling_folder_name)):
#         os.mkdir(Rolling_folder_name)
#     if not(os.path.isdir('./DEMstress')):
#         os.mkdir('DEMstress')
#     if not(os.path.isdir('./MPMstress')):
#         os.mkdir('MPMstress')

#     #homogenize_stress書き換え
#     homogenize_stress_fn = args[2]
#     homogenize_tree = ET.parse(homogenize_stress_fn)
#     homogenize_root = homogenize_tree.getroot()
#     homogenize_root[0].attrib["templates"] = Save_folder_name + "/" + shape_ratio_name + "_template.h5"
#     homogenize_root[0].attrib["forces"] = Save_folder_name + "/serialized_forces.h5"
#     homogenize_root[0].attrib["MPMstress"] = Save_folder_name + "/serialized_sigma.h5"
#     homogenize_root[1].attrib["stress_pair"] = Save_folder_name + "/stress_pair.h5"
#     homogenize_root[5].attrib["base_elem"] = Rolling_folder_name + "/element_data.h5"
#     homogenize_root[5].attrib["base_stress"] = Rolling_folder_name + "/stress_pair.h5"
#     if homogenize_root[6].attrib["mode"] == 1:
#         homogenize_root[6].attrib["processing_time"] = Save_folder_name + "/Homogenize_Processing_Time_" + shape_ratio_name + ".csv"
#         homogenize_root[6].attrib["homogenize_time"] = Save_folder_name + "/Homogenize_DEM_Time_" + shape_ratio_name + ".csv"
#     homogenize_tree.write(homogenize_stress_fn)

#     #DEM書き換え
#     DEM_fn = homogenize_root[2].attrib["resume_fn"]
#     DEM_tree = ET.parse(DEM_fn)
#     DEM_root = DEM_tree.getroot()
#     DEM_root[3].attrib["templates"] = Save_folder_name + "/" + shape_ratio_name + "_template.h5"
#     DEM_root[3].attrib["objects"] = Save_folder_name + "/" + shape_ratio_name + ".h5"
#     DEM_root[4].attrib["folder"] = Save_folder_name
#     DEM_root[4].attrib["objects"] = shape_ratio_name + ".h5"
#     DEM_root[4].attrib["processing_time"] = Save_folder_name + "/DEM_Processing_Time_" + shape_ratio_name + ".csv"
#     DEM_tree.write(DEM_fn)

#     #MPM書き換え
#     MPM_fn = homogenize_root[2].attrib["resume_MPM_fn"]
#     MPM_tree = ET.parse(MPM_fn)
#     MPM_root = MPM_tree.getroot()
#     MPM_root[5].attrib["templates"] = Save_folder_name + "/" + shape_ratio_name + "_template.h5"
#     MPM_root[5].attrib["forces"] = Save_folder_name + "/" + "serialized_forces.h5"
#     MPM_root[6].attrib["folder"] = Save_folder_name
#     if MPM_root[6].attrib["mode"] == "11":
#         MPM_root[6].attrib["processing_time"] = Save_folder_name + "/MPM_Processing_Time_" + shape_ratio_name + ".csv"

#     MPM_tree.write(MPM_fn)


# if __name__ == "__main__":
#     main()

#!/usr/bin/env python3
import os
import sys
import shutil
import argparse
import xml.etree.ElementTree as ET

def ensure_dir(p: str):
    if p and not os.path.isdir(p):
        os.makedirs(p, exist_ok=True)

def backup(path: str):
    if os.path.isfile(path):
        shutil.copy2(path, path + ".bak")

def set_if_present(elem, key, value):
    if elem is not None and key in elem.attrib:
        elem.attrib[key] = value

def find_first_with_attrs(root, required_attrs):
    for e in root.iter():
        if all(a in e.attrib for a in required_attrs):
            return e
    return None

def main():
    parser = argparse.ArgumentParser(description="Initialize paths for a run without clobbering fixed stress outputs.")
    parser.add_argument("shape_ratio_name", help="e.g., square11_flow")
    parser.add_argument("homogenize_stress_fn", help="path to homogenize_stress.xml")
    parser.add_argument("--save-dir", default=None, help="override Save_XXX folder (default: Save_<shape>)")
    parser.add_argument("--rolling-dir", default=None, help="override Rolling_XXX folder (default: Rolling_<shape>)")
    # 以下は明示指定があるときだけ固定出力先を更新する
    parser.add_argument("--mpmstress-dir", default=None, help="override MPMstress dir (default: do not touch)")
    parser.add_argument("--demstress-dir", default=None, help="override DEMstress dir (default: do not touch)")
    args = parser.parse_args()

    shape = str(args.shape_ratio_name)
    save_dir = args.save_dir or f"Save_{shape}"
    rolling_dir = args.rolling_dir or f"Rolling_{shape}"

    # ディレクトリ作成（恒久出力先は既存レイアウトを尊重）
    ensure_dir(save_dir)
    ensure_dir(rolling_dir)
    ensure_dir("./DEMstress")
    ensure_dir("./MPMstress")

    # -------- homogenize_stress.xml 更新 --------
    h_fn = args.homogenize_stress_fn
    backup(h_fn)
    h_tree = ET.parse(h_fn)
    h_root = h_tree.getroot()

    elements = h_root.find("elements")
    stress = h_root.find("stress")
    resume = h_root.find("resume")
    rolling = h_root.find("rolling")
    test = h_root.find("test")

    # Save_* に置くべきものだけ更新
    set_if_present(elements, "templates", f"{save_dir}/{shape}_template.h5")
    set_if_present(elements, "forces", f"{save_dir}/serialized_forces.h5")
    # MPMstress は固定先を尊重（--mpmstress-dir 指定時のみ変更）
    if args.mpmstress_dir:
        elements.attrib["MPMstress"] = os.path.join(args.mpmstress_dir, "MPM.h5")

    set_if_present(stress, "stress_pair", f"{save_dir}/stress_pair.h5")
    # pre/post/strain は固定先を尊重（--*stress-dir 指定時のみ変更）
    if args.mpmstress_dir:
        stress.attrib["pre_stress"] = os.path.join(args.mpmstress_dir, "MPM.h5")
    if args.demstress_dir:
        stress.attrib["post_stress"] = os.path.join(args.demstress_dir, "DEM.h5")
        stress.attrib["strain"] = os.path.join(args.demstress_dir, "DEM.h5")

    set_if_present(rolling, "base_elem", f"{rolling_dir}/element_data.h5")
    set_if_present(rolling, "base_stress", f"{rolling_dir}/stress_pair.h5")

    # test の mode は文字列で比較
    if test is not None and test.attrib.get("mode") == "1":
        test.attrib["processing_time"] = f"{save_dir}/Homogenize_Processing_Time_{shape}.csv"
        test.attrib["homogenize_time"] = f"{save_dir}/Homogenize_DEM_Time_{shape}.csv"

    h_tree.write(h_fn, encoding="utf-8", xml_declaration=True)

    # -------- DEM の設定ファイル（resume_fn）更新 --------
    dem_fn = resume.attrib.get("resume_fn") if resume is not None else None
    if dem_fn and os.path.isfile(dem_fn):
        backup(dem_fn)
        dem_tree = ET.parse(dem_fn)
        dem_root = dem_tree.getroot()

        # （1）テンプレート/オブジェクト参照を Save_* 側に
        node_tpl_obj = find_first_with_attrs(dem_root, ["templates", "objects"])
        if node_tpl_obj is not None:
            node_tpl_obj.attrib["templates"] = f"{save_dir}/{shape}_template.h5"
            node_tpl_obj.attrib["objects"] = f"{save_dir}/{shape}.h5"

        # （2）シリアライズ（中間物/ログ類）は Save_* 側に
        node_ser = find_first_with_attrs(dem_root, ["folder", "objects"])
        if node_ser is not None:
            node_ser.attrib["folder"] = save_dir
            node_ser.attrib["objects"] = f"{shape}.h5"
            if "processing_time" in node_ser.attrib:
                node_ser.attrib["processing_time"] = f"{save_dir}/DEM_Processing_Time_{shape}.csv"

        dem_tree.write(dem_fn, encoding="utf-8", xml_declaration=True)

    # -------- MPM の設定ファイル（resume_MPM_fn）更新 --------
    mpm_fn = resume.attrib.get("resume_MPM_fn") if resume is not None else None
    if mpm_fn and os.path.isfile(mpm_fn):
        backup(mpm_fn)
        mpm_tree = ET.parse(mpm_fn)
        mpm_root = mpm_tree.getroot()

        mpm_resume = mpm_root.find("resume")
        mpm_serial = mpm_root.find("serialization")

        # MPM の resume はテンプレ/forces だけ Save_* に。homogenization は固定先尊重。
        if mpm_resume is not None:
            mpm_resume.attrib["templates"] = f"{save_dir}/{shape}_template.h5"
            mpm_resume.attrib["forces"] = f"{save_dir}/serialized_forces.h5"
            if args.demstress_dir:
                mpm_resume.attrib["homogenization"] = os.path.join(args.demstress_dir, "DEM.h5")

        # serialization は folder（MPMstress）を基本維持。--mpmstress-dir 指定時のみ変更。
        if mpm_serial is not None:
            if args.mpmstress_dir:
                mpm_serial.attrib["folder"] = args.mpmstress_dir
            # mode は "1" で比較（もともと "11" になっていたバグを回避）
            if mpm_serial.attrib.get("mode") in ("1", 1):
                mpm_serial.attrib["processing_time"] = f"{save_dir}/MPM_Processing_Time_{shape}.csv"

        mpm_tree.write(mpm_fn, encoding="utf-8", xml_declaration=True)

    # 画面表示
    print("[OK] Initialized.")
    print("  Save dir    :", save_dir)
    print("  Rolling dir :", rolling_dir)
    print("  MPMstress   :", args.mpmstress_dir or "(unchanged)")
    print("  DEMstress   :", args.demstress_dir or "(unchanged)")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: initSimulationEnv.py shape_ratio_name homogenize_stress_fn [--mpmstress-dir MPMstress] [--demstress-dir DEMstress]")
        sys.exit(1)
    main()
