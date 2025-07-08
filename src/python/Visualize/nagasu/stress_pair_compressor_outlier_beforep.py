import math

from allgrainh5 import *
from stresspairh5 import *
from tqdm import tqdm
import ctypes
from sklearn.linear_model import LinearRegression
import sys
from stress_plot_widget import *
import scipy.stats as stats
import cmath
import matplotlib.pyplot as plt

class StressPairEdit:
    def __init__(self):
        pass

    @staticmethod
    def compress(stress_fn: str, scene_fn: str, out_fn: str) -> None:
        key_list = AllSceneData.get_key_list(scene_fn)
        all_stress_pair_data = AllStressPairData()

        for i in tqdm(range(len(key_list) - 1)):
            all_stress_pair_data.clear()

            grid_p = np.array([0.0, 0.0]).transpose()
            h = 0.04
            resolution = np.array([0, 0]).transpose()

            for idx in range(key_list[i], key_list[i + 1]):
                all_stress_pair_data.load_from_idx(stress_fn, idx)

            for stress_pair_data in all_stress_pair_data.stress_pair_data_array:
                if not stress_pair_data.stress_pair_array:
                    continue
                resolution = np.maximum(resolution, stress_pair_data.resolution)

            cell_num = np.prod(resolution)
            count = np.zeros(cell_num, dtype=ctypes.c_int)
            pre_stress = np.zeros((cell_num, 2, 2), dtype=ctypes.c_float)
            post_stress = np.zeros((cell_num, 2, 2), dtype=ctypes.c_float)

            for stress_pair_data in all_stress_pair_data.stress_pair_data_array:
                if not stress_pair_data.stress_pair_array:
                    continue

                for stress_pair in stress_pair_data.stress_pair_array:
                    x = stress_pair.grid_idx % stress_pair_data.resolution[0]
                    y = int(stress_pair.grid_idx / stress_pair_data.resolution[0])
                    flat_idx = int(resolution[0] * y + x)

                    pre_stress[flat_idx] += stress_pair.pre_stress
                    post_stress[flat_idx] += stress_pair.post_stress
                    count[flat_idx] += 1

            stress_pair_array = []

            for j in range(len(count)):
                if count[j] != 0:
                    pre_stress[j] /= float(count[j])
                    post_stress[j] /= float(count[j])

                    stress_pair = StressPair()
                    stress_pair.pre_stress = pre_stress[j]
                    stress_pair.post_stress = post_stress[j]
                    stress_pair.grid_idx = j
                    stress_pair_array.append(stress_pair)

            result_stress_pair_data = StressPairData()
            result_stress_pair_data.grid_p = grid_p
            result_stress_pair_data.h = h
            result_stress_pair_data.resolution = resolution
            result_stress_pair_data.stress_pair_array = stress_pair_array
            result_stress_pair_data.save(out_fn, key_list[i])

    @staticmethod
    def compute_principal_stress(stress_pair: StressPair) -> tuple[ndarray, ndarray]:
        pre_l, pre_q = np.linalg.eig(stress_pair.pre_stress)
        post_l, post_q = np.linalg.eig(stress_pair.post_stress)

        if pre_l[0] >= pre_l[1]:
            pre_principal_stress = np.array([pre_l[0], pre_l[1]])
        else:
            pre_principal_stress = np.array([pre_l[1], pre_l[0]])

        if post_l[0] >= post_l[1]:
            post_principal_stress = np.array([post_l[0], post_l[1]])
        else:
            post_principal_stress = np.array([post_l[1], post_l[0]])

        return pre_principal_stress, post_principal_stress

    @staticmethod
    def is_out_of_scope(pre_stress: ndarray, post_stress: ndarray) -> bool:
        lim = 250

        #if pre_stress[0] > 0 > pre_stress[1]:
        if pre_stress[0] > 0 or post_stress[0] > 0:
            return True

        if post_stress[0] > 0 > post_stress[1]:
            return True

        if -lim <= pre_stress[0] <= lim and -lim <= pre_stress[1] <= lim:
            return True

        if -lim <= post_stress[0] <= lim and -lim <= post_stress[1] <= lim:
            return True

        return False

    @staticmethod
    def rot90_reverse() -> ndarray:
        return np.array([[0, 1], [-1, 0]])

    @staticmethod
    def rot90() -> ndarray:
        return np.array([[0, -1], [1, 0]])

    @staticmethod
    def output_data(out_fn: str, identifier: str, moving_average: ndarray, rot90_average: ndarray, count: int,
                    theta: float, dem_average: ndarray) -> None:

        with open(out_fn, mode='a') as f:
            f.write(identifier + "\n")
            f.write("moving_average: " + str(moving_average / count) + "\n")
            f.write("rot90_average : " + str(rot90_average / count) + "\n")
            f.write("dem_p_average : " + str(dem_average / count) + "\n")
            f.write("theta_average : " + str(theta / count) + " rad\n")
            f.write("theta_average : " + str(math.degrees(theta / count)) + " degree\n")
            f.write("count : " + str(count) + "\n\n")

    @staticmethod
    def compute_line(path_list: list[str], out_fn: str) -> None:
        all_stress_pair_data = AllStressPairData()
        total_moving = np.array([0.0, 0.0]).transpose()
        total_rot90_moving = np.array([0.0, 0.0]).transpose()
        total_dem_pos = np.array([0.0, 0.0]).transpose()
        total_theta = 0.0
        total_count = 0

        for path in tqdm(path_list):
            all_stress_pair_data.clear()
            all_stress_pair_data.pre_load(path)

            moving_average = np.array([0.0, 0.0]).transpose()
            rot90_average = np.array([0.0, 0.0]).transpose()
            dem_p_average = np.array([0.0, 0.0]).transpose()
            theta_average = 0.0
            count = 0
            DEM_p_list = []

            for key in tqdm(all_stress_pair_data.sorted_keys, leave=False):
                stress_pair_data = StressPairData()
                stress_pair_data.load(path, key)

                for stress_pair in stress_pair_data.stress_pair_array:

                    pre_principal_stress, post_principal_stress = StressPairEdit.compute_principal_stress(stress_pair)

                    if StressPairEdit.is_out_of_scope(pre_principal_stress, post_principal_stress):
                        continue
                    DEM_p_list.append(post_principal_stress[1])

            q25, q50, q75 = np.percentile(DEM_p_list, [25, 50, 75])

            iqr = q75 - q25

            for key in tqdm(all_stress_pair_data.sorted_keys, leave=False):
                stress_pair_data = StressPairData()
                stress_pair_data.load(path, key)

                for stress_pair in stress_pair_data.stress_pair_array:

                    pre_principal_stress, post_principal_stress = StressPairEdit.compute_principal_stress(stress_pair)

                    if StressPairEdit.is_out_of_scope(pre_principal_stress, post_principal_stress):
                        continue
                    if (q25 - 1.5 * iqr) <= post_principal_stress[1] <= (q75 + 1.5 * iqr):
                        dem_p_average += post_principal_stress
                        count += 1

            total_moving += moving_average
            total_rot90_moving += rot90_average
            total_theta += theta_average
            total_dem_pos += dem_p_average
            total_count += count
            StressPairEdit.output_data(out_fn, path, moving_average, rot90_average, count, theta_average, dem_p_average)

        StressPairEdit.output_data(out_fn, "total", total_moving, total_rot90_moving, total_count,
                                   total_theta, total_dem_pos)



        #回帰直線と点の角度の分散を算出
        angles_point_from_origin = np.zeros(total_count, dtype=ctypes.c_float)
        #mean_angle = math.atan2(model_lr.coef_, 1.0)
        mean_angle = math.atan2(total_dem_pos[1] / total_count, total_dem_pos[0] / total_count)
        print("mean_angle:", mean_angle)
        print("total_count:", total_count)
        total_simple_variance = 0.0
        idx = 0
        current = 0
        previous = 0
        for path in tqdm(path_list):
            all_stress_pair_data.clear()
            all_stress_pair_data.pre_load(path)
            DEM_p_list = []

            for key in tqdm(all_stress_pair_data.sorted_keys, leave=False):
                stress_pair_data = StressPairData()
                stress_pair_data.load(path, key)

                for stress_pair in stress_pair_data.stress_pair_array:
                    pre_principal_stress, post_principal_stress = StressPairEdit.compute_principal_stress(stress_pair)

                    if StressPairEdit.is_out_of_scope(pre_principal_stress, post_principal_stress):
                        continue
                    DEM_p_list.append(post_principal_stress[1])

            q25, q50, q75 = np.percentile(DEM_p_list, [25, 50, 75])

            iqr = q75 - q25

            for key in tqdm(all_stress_pair_data.sorted_keys, leave=False):
                stress_pair_data = StressPairData()
                stress_pair_data.load(path, key)

                for stress_pair in stress_pair_data.stress_pair_array:
                    pre_principal_stress, post_principal_stress = StressPairEdit.compute_principal_stress(stress_pair)

                    if StressPairEdit.is_out_of_scope(pre_principal_stress, post_principal_stress):
                        continue
                    if (q25 - 1.5 * iqr) <= post_principal_stress[1] <= (q75 + 1.5 * iqr):
                        angles_point_from_origin[idx] = math.atan2(post_principal_stress[1], post_principal_stress[0])
                        total_simple_variance = total_simple_variance + pow(angles_point_from_origin[idx] - mean_angle, 2)
                        idx += 1

        plt.hist(angles_point_from_origin, bins=100)
        plt.show()
        print("角度の分散（rad）:", total_simple_variance / idx)


    def Calc_distance(self, a, b, c, point_x, point_y):  # 直線ax+by+c=0 点(x0,y0)
        numer = abs(a * point_x + b * point_y + c)  # 分子
        denom = math.sqrt(pow(a, 2) + pow(b, 2))  # 分母
        return numer / denom  # 計算結果

def main():
    mode = 1  # 0 = 応力圧縮, 1 = 応力解析
    stress_pair_edit = StressPairEdit()

    # 応力圧縮
    if mode == 0:
        # 圧縮対象の応力データファイルへのパス
        stress_fn = "Output/stress_pair.h5"

        # 応力データに対応した粒子データファイルへのパス
        scene_fn = "Output/element_data.h5"

        # 圧縮後のファイル保存先
        compressed_stress_fn = "Output/compressed_stress.h5"
        
        stress_pair_edit.compress(stress_fn, scene_fn, compressed_stress_fn)

    # 応力解析
    if mode == 1:
        # 結果出力先
        
        # データ解析対象ファイルを列挙
        #stress_fn = ["Output/compressed_stress.h5"]

        if len(sys.argv) >= 1:
            stress_fn = ["IOData/" + str(sys.argv[1]) + "/11/compressed_stress.h5",
                         "IOData/" + str(sys.argv[1]) + "/12/compressed_stress.h5",
                         "IOData/" + str(sys.argv[1]) + "/13/compressed_stress.h5",
                         "IOData/" + str(sys.argv[1]) + "/21/compressed_stress.h5",
                         "IOData/" + str(sys.argv[1]) + "/31/compressed_stress.h5",
                         "IOData/" + str(sys.argv[1]) + "/22/compressed_stress.h5",
            ]


            # stress_fn = ["IOData/" + str(sys.argv[1]) + "/11/stress_pair.h5",
            #              "IOData/" + str(sys.argv[1]) + "/12/stress_pair.h5",
            #              "IOData/" + str(sys.argv[1]) + "/13/stress_pair.h5",
            #              "IOData/" + str(sys.argv[1]) + "/21/stress_pair.h5",
            #              "IOData/" + str(sys.argv[1]) + "/31/stress_pair.h5",
            #              "IOData/" + str(sys.argv[1]) + "/22/stress_pair.h5",
            #             ]

        #debug
        # if len(sys.argv) >= 1:
        #     stress_fn = ["IOData/" + str(sys.argv[1]) + "/11/compressed_stress.h5"]


            out_fn = "debug/debug_" + str(sys.argv[1]) + ".txt"

        with open(out_fn, mode='a') as f:
            f.write("--------------------------------\n\n")

        stress_pair_edit.compute_line(stress_fn, out_fn)


if __name__ == "__main__":
    main()
