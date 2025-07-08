from sysconfig import parse_config_h
from stresspairh5 import *
import xml.etree.ElementTree as ET
import sys
import numpy as np
import ctypes
from csv import writer

def main():
    args = sys.argv

    if len(args) < 2:
        print('compareStressPairs.py stress_pairs1_fn stress_pairs2_fn')

    processing_time_fn = "Save_heptagon_025_05/stress_error.csv"

    # load stress pairs
    stress_pair1_fn = args[1]
    stress_pair2_fn = args[2]
    all_stress_pair_data1 = AllStressPairData()
    all_stress_pair_data1.load(stress_pair1_fn)
    all_stress_pair_data2 = AllStressPairData()
    all_stress_pair_data2.load(stress_pair2_fn)

    if len(all_stress_pair_data1.loaded_timestep) != len(all_stress_pair_data2.loaded_timestep):
        print("no match timestep num")

    if all_stress_pair_data1.loaded_timestep[0] != all_stress_pair_data2.loaded_timestep[0]:
        print("no match start timestep")

    for i, timestep in enumerate(all_stress_pair_data1.loaded_timestep):
        stress_pair_data1 = all_stress_pair_data1.stress_pair_data_array[i]
        stress_pair_data2 = all_stress_pair_data2.stress_pair_data_array[i]

        stress_pair_num = len(stress_pair_data1.stress_pair_array)


        error = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        for j in range(stress_pair_num):
            # calc principal stress 1
            pre_sigma = stress_pair_data1.stress_pair_array[j].pre_stress
            post_sigma = stress_pair_data1.stress_pair_array[j].post_stress
            principal_stress_list1 = np.array([pre_sigma[0][0], pre_sigma[0][1], pre_sigma[1][0], pre_sigma[1][1]
                                                  , post_sigma[0][0], post_sigma[0][1], post_sigma[1][0], post_sigma[1][1]], )
            pre_sigma = stress_pair_data2.stress_pair_array[j].pre_stress
            post_sigma = stress_pair_data2.stress_pair_array[j].post_stress
            principal_stress_list2 = np.array([pre_sigma[0][0], pre_sigma[0][1], pre_sigma[1][0], pre_sigma[1][1]
                                                  , post_sigma[0][0], post_sigma[0][1], post_sigma[1][0], post_sigma[1][1]], )
            if j != (stress_pair_num - 1):
                error += np.abs(principal_stress_list1 - principal_stress_list2)

        with open(processing_time_fn, 'a', newline='') as f:
            writer_object = writer(f)
            writer_object.writerow(error / float(stress_pair_num))
            f.close()

    #主応力として比較
    """
    for i, timestep in enumerate(all_stress_pair_data1.loaded_timestep):
        stress_pair_data1 = all_stress_pair_data1.stress_pair_data_array[i]
        stress_pair_data2 = all_stress_pair_data2.stress_pair_data_array[i]

        stress_pair_num = len(stress_pair_data1.stress_pair_array)

        pre_marker = np.zeros((stress_pair_num, 2), dtype=ctypes.c_float)
        post_marker = np.zeros((stress_pair_num, 2), dtype=ctypes.c_float)

        error = [0.0, 0.0, 0.0, 0.0]

        for j in range(stress_pair_num):
            #calc principal stress 1
            pre_sigma = stress_pair_data1.stress_pair_array[j].pre_stress
            post_sigma = stress_pair_data1.stress_pair_array[j].post_stress

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
            principal_stress_list1 = np.array([pre_principal_stress[0], pre_principal_stress[1], post_principal_stress[0], post_principal_stress[1]])

            # calc principal stress 2
            pre_sigma = stress_pair_data2.stress_pair_array[j].pre_stress
            post_sigma = stress_pair_data2.stress_pair_array[j].post_stress

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
            principal_stress_list2 = np.array([pre_principal_stress[0], pre_principal_stress[1], post_principal_stress[0], post_principal_stress[1]])
            error += np.abs(principal_stress_list1 - principal_stress_list2)

        error = error / float(stress_pair_num)
        print(error)
        with open(processing_time_fn, 'a', newline='') as f:
            writer_object = writer(f)
            writer_object.writerow(error)
            f.close()
        """


if __name__ == "__main__":
    main()
