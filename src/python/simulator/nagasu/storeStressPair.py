from sysconfig import parse_config_h
from allhomogenizationh5 import *
from progressh5 import *
from stresspairh5 import *
import xml.etree.ElementTree as ET 
import sys
import os
import ctypes
import time


def main():
    args = sys.argv

    resume_xml_fn = args[1]
    tree = ET.parse(resume_xml_fn)
    root = tree.getroot()

    pre_fn = root[1].attrib["pre_stress"]
    post_fn = root[1].attrib["post_stress"]
    stress_pair_fn = root[1].attrib["stress_pair"]

    all_pre_homogenization_data = AllHomogenizeData()
    all_post_homogenization_data = AllHomogenizeData()

    all_pre_homogenization_data.set_timestep_from_file(pre_fn)
    all_pre_homogenization_data.load(pre_fn)
    all_post_homogenization_data.load(post_fn)

    max_loop = len(all_pre_homogenization_data.all_step_homogenization)

    for i in range(max_loop):
        stress_pair_data = StressPairData()

        pre_homogenization_data = all_pre_homogenization_data.all_step_homogenization[i]
        post_homogenization_data = all_post_homogenization_data.all_step_homogenization[i+1]

        dem_resolution = post_homogenization_data.homogenization[0].resolution
        mpm_resolution = pre_homogenization_data.homogenization[0].resolution
        resolution = np.minimum(dem_resolution, mpm_resolution)

        stress_pair_data.resolution = resolution
        stress_pair_data.grid_p = post_homogenization_data.homogenization[0].grid_p
        stress_pair_data.h = post_homogenization_data.homogenization[0].h

        for y in range(resolution[1]):
            for x in range(resolution[0]):
                pre_sigma = pre_homogenization_data.homogenization[y * mpm_resolution[0] + x].sigma
                post_sigma = post_homogenization_data.homogenization[y * dem_resolution[0] + x].sigma

                if (np.isnan(post_sigma)).any():
                    continue
                else:
                    stress_pair = StressPair()
                    stress_pair.grid_idx = y * resolution[0] + x
                    stress_pair.pre_stress = pre_sigma
                    stress_pair.post_stress = post_sigma
                    stress_pair_data.stress_pair_array.append(stress_pair)

        stress_pair_data.save(stress_pair_fn, all_pre_homogenization_data.all_timestep[i])

if __name__ == "__main__":
    main()
