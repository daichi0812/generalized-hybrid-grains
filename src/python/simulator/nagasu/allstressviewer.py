from sysconfig import parse_config_h
import plotly.graph_objects as go
from stresspairh5 import *
import xml.etree.ElementTree as ET
import sys
import numpy as np
import ctypes
import matplotlib.pyplot as plt


def main():
    args = sys.argv

    if len(args) < 2:
        print('allstressviewer.py homogenize_stress_fn')

    resume_xml_fn = args[1]
    tree = ET.parse(resume_xml_fn)
    root = tree.getroot()

    if root[1].tag != "stress":
        print("not stress line")

    stress_fn = root[1].attrib["stress_pair"]
    all_stress_pair_data = AllStressPairData()
    all_stress_pair_data.load(stress_fn)

    fig = go.Figure()

    for i, timestep in enumerate(all_stress_pair_data.loaded_timestep):
        stress_pair_data = all_stress_pair_data.stress_pair_data_array[i]

        stress_pair_num = len(stress_pair_data.stress_pair_array)

        pre_marker = np.zeros((stress_pair_num, 2), dtype=ctypes.c_float)
        post_marker = np.zeros((stress_pair_num, 2), dtype=ctypes.c_float)

        for j in range(stress_pair_num):
            pre_sigma = stress_pair_data.stress_pair_array[j].pre_stress
            post_sigma = stress_pair_data.stress_pair_array[j].post_stress

            pre_l, pre_q = np.linalg.eig(pre_sigma)
            post_l, post_q = np.linalg.eig(post_sigma)

            if pre_l[0] >= pre_l[1]:
                pre_principal_stress = np.array([pre_l[0], pre_l[1]])
            else:
                pre_principal_stress = np.array([pre_l[1], pre_l[0]])

            if post_l[0] >= post_l[1]:
                post_principal_stress = np.array([post_l[0], post_l[1]])
            else:
                post_principal_stress = np.array([post_l[1], post_l[0]])

            # matplotlib
            xs = np.array([pre_principal_stress[0], post_principal_stress[0]])
            ys = np.array([pre_principal_stress[1], post_principal_stress[1]])
            pre_marker[j] = np.array([pre_principal_stress[0], pre_principal_stress[1]])
            post_marker[j] = np.array([post_principal_stress[0], post_principal_stress[1]])
            # plt.scatter(pre_principal_stress[0], pre_principal_stress[1], facecolor="red", s=1)
            # plt.scatter(post_principal_stress[0], post_principal_stress[1], facecolor="blue", s=1)
            plt.plot(xs, ys, color='y', linewidth=0.05)

            # plotly
            # colors = ['#4169E1', "#FF0000"]
            # fig.add_trace(go.Scatter(x=xs, y=ys, line=dict(width=0.5, color="#FFA500"), marker=dict(size=2.5, color=colors)))
            # fig.update_layout(title='DEM = 赤, MPM = 青')

        plt.scatter(pre_marker[:, 0], pre_marker[:, 1], facecolor="blue", s=0.1)
        plt.scatter(post_marker[:, 0], post_marker[:, 1], facecolor="red", s=0.1)

    plt.show()
    # fig.show()


if __name__ == "__main__":
    main()
