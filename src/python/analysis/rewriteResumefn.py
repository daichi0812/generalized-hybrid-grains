import xml.etree.ElementTree as ET
import sys
import h5py
import numpy as np
import shutil


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

    if resume_root[0].tag != "integrator":
        print("not integrator line")
        exit(1)

    current_max_time = float(resume_root[0].attrib["max_time"])
    next_max_time = current_max_time + interval

    resume_root[0].attrib["max_time"] = "{:.6f}".format(next_max_time)
    resume_tree.write(resume_xml_fn)

    if root[0].tag != "elements":
        print("not resume line")
        exit(1)

    if root[5].tag != "rolling":
        print("not rolling line")
        exit(1)

    forces_fn = root[0].attrib["forces"]
    stress_pair_fn = root[1].attrib["stress_pair"]

    base_elem_fn = root[5].attrib["base_elem"]
    base_stress_fn = root[5].attrib["base_stress"]
    rolling_time = float(root[5].attrib["rolling_time"])
    next_rolling_time = float(root[5].attrib["next_time"])

    with h5py.File(forces_fn, 'r') as h5_elements, h5py.File(base_elem_fn, 'a') as h5_out:
        idx = str(np.array(h5_elements["force_num/start"]))

        if h5_out.get(idx):
            del h5_out[idx]

        h5_out.create_group(idx)
        h5_elements.copy(idx + "/elements_2d", h5_out["/" + idx])
        h5_elements.copy(idx + "/progress_data", h5_out["/" + idx])
        h5_elements.copy(idx + "/template_name_dict", h5_out["/" + idx])

    if current_max_time < next_rolling_time:
        return

    time = "{:.6f}".format(next_rolling_time)
    rolling_elem_fn = base_elem_fn[:len(base_elem_fn) - 3] + "_" + time + base_elem_fn[len(base_elem_fn) - 3:]
    rolling_stress_fn = base_stress_fn[:len(base_stress_fn) - 3] + "_" + time + base_stress_fn[len(base_stress_fn) - 3:]

    shutil.copy2(base_elem_fn, rolling_elem_fn)
    shutil.copy2(stress_pair_fn, rolling_stress_fn)

    root[5].attrib["next_time"] = "{:.6f}".format(next_rolling_time + rolling_time)
    tree.write(homogenize_stress_fn)


if __name__ == "__main__":
    main()
