import xml.etree.ElementTree as ET 
import sys
from progressh5 import *


def main():
    args = sys.argv

    if len(args) < 2:
        print('rewriteResumefn.py homogenize_stress.xml')
        exit(1)

    homogenize_stress_fn = args[1]
    tree = ET.parse(homogenize_stress_fn)
    root = tree.getroot()

    if root[2].tag != "resume":
        print("not resume line")
        exit(1)

    resume_xml_fn = root[2].attrib["resume_fn"]
    interval = float(root[2].attrib["interval"])

    resume_tree = ET.parse(resume_xml_fn)
    resume_root = resume_tree.getroot()

    if resume_root[3].tag != "resume":
        print("not resume line")
        exit(1)

    # max_time変更
    # シミュレーションの初期時間を取り出す
    # progressがあるなら設定

    init_time = 0.0
    progress_fn = resume_root[3].attrib["objects"]

    if progress_fn != "" and progress_fn[len(progress_fn) - 3:] == ".h5":
        with h5py.File(progress_fn, 'r') as h5_progress:
            keys = list(map(str, h5_progress.keys()))
            if 'progress_data' in keys:
                progress_data = ProgressData()
                progress_data.load(progress_fn)
                init_time = progress_data.progress[0].time

    if resume_root[0].tag != "integrator":
        print("not integrator line")
        exit(1)

    resume_root[0].attrib["max_time"] = "{:.6f}".format(init_time + interval)

    next_rolling_time = 0.0
    rolling_time = float(root[5].attrib["rolling_time"])

    while init_time >= next_rolling_time:
        next_rolling_time += rolling_time

    root[5].attrib["next_time"] = "{:.6f}".format(next_rolling_time)

    resume_tree.write(resume_xml_fn)
    tree.write(homogenize_stress_fn)


if __name__ == "__main__":
    main()
