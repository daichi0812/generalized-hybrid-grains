import ctypes
import math

from enum import Enum
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from stresspairh5 import *
from stress_pair_compressor import *
from tqdm import tqdm
from sklearn.linear_model import LinearRegression


class PlotMode(Enum):
    ALL = 0
    PLOT_PER_CELL = 1
    PLOT_PER_TIMESTEP = 2
    PLOT_PER_CELL_AND_TIMESTEP = 3


class StressPlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(1, 1, 1)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        self.all_stress_pair_data = AllStressPairData()
        self.cell_pos_list = np.zeros((0, 2), dtype=ctypes.c_int)
        self.plot_mode = PlotMode.ALL

        self.current_time = 0
        self.using_data_range = []
        self.using_cell_idx_array = np.zeros((0, 2), dtype=ctypes.c_int)

        self.max_lim = None
        self.current_lim = None

        self.line_width = 1.3
        self.stress_line_width = 0.1
        self.marker_size = 0.5

        self.stride = 1

        self.x_grad = 24.24894563
        self.y_grad = 0
        self.intercept = 0.0

        self.x_shift = 0.0
        self.y_shift = 0.0
        self.zoom = 0.0

        self.past_move_x = 0.0
        self.past_move_y = 0.0
        self.past_zoom = 1.0

        self.shift_volume = 1000.0
        self.max_len = 10.0

        self.residual_error = 0.0
        self.variance = 0.0

        self.current_lim = 2500


    def calc_moving_average(self):
        count = 0
        average = np.array([0.0, 0.0]).transpose()

        for i in tqdm(self.using_data_range):
            stress_pair_data = self.all_stress_pair_data.stress_pair_data_array[i]

            for stress_pair in stress_pair_data.stress_pair_array:
                pre_principal_stress, post_principal_stress = self.compute_principal_stress(stress_pair)
                moving = post_principal_stress - pre_principal_stress

                average += moving
                count += 1

        with open("./debug.txt", mode='a') as f:
            f.writelines("2:1")
            if count != 0:
                f.write(str(average / count) + "\n")

    def __plot_data(self):
        self.axes.cla()

        stress_pair_num = self.get_stress_num()
        lines = np.zeros((stress_pair_num, 2, 2), dtype=ctypes.c_float)
        idx = 0
        debug_outlier_num = 0

        current = 0
        previous = 0

        selected_cell_flat_idx = np.full(len(self.using_cell_idx_array), -1)
        is_all = True if selected_cell_flat_idx.size == 0 else False

        for i in tqdm(self.using_data_range):
            stress_pair_data = self.all_stress_pair_data.stress_pair_data_array[i]

            for j, cell_pos in enumerate(self.using_cell_idx_array):
                selected_cell_flat_idx[j] = stress_pair_data.resolution[0] * cell_pos[1] + cell_pos[0]

            for stress_pair in stress_pair_data.stress_pair_array:
                if stress_pair.grid_idx in selected_cell_flat_idx or is_all:
                    current += 1

                    if current - previous < self.stride:
                        continue

                    pre_principal_stress, post_principal_stress = self.compute_principal_stress(stress_pair)

                    if StressPairEdit.is_out_of_scope(pre_principal_stress, post_principal_stress):
                        continue

                    # if post_principal_stress[1] < -10000.0:
                    #     debug_outlier_num += 1
                    #     continue

                    lines[idx, 0] = np.array([pre_principal_stress[0], pre_principal_stress[1]])
                    lines[idx, 1] = np.array([post_principal_stress[0], post_principal_stress[1]])
                    idx += 1

                    previous = current

                    #begin 変化量を可視化
                    """
                    change = math.sqrt(math.pow(pre_principal_stress[0] - post_principal_stress[0], 2) + math.pow(pre_principal_stress[1] - post_principal_stress[1], 2))
                    if self.max_len > change:
                        color = [change / self.max_len, 0.0, 0.0]
                    else:
                        color = [1.0, 0.0, 0.0]

                    self.axes.plot([pre_principal_stress[0], post_principal_stress[0]], [pre_principal_stress[1], post_principal_stress[1]], color=color, linewidth=self.line_width)
                    """
                    #end 変化量を可視化



        """
        model_lr = LinearRegression()
        x = lines[:, 0, 0]
        y = lines[:, 0, 1]
        x = x.reshape(-1, 1)
        y = y.reshape(-1, 1)
        model_lr.fit(x, y)

        #回帰直線を引く

        print('モデル関数の回帰変数 w1: %.3f' % model_lr.coef_)
        print('モデル関数の切片 w2: %.3f' % model_lr.intercept_)
        print('y= %.3fx + %.3f' % (model_lr.coef_, model_lr.intercept_))
        print('決定係数 R^2： ', model_lr.score(x, y))
        self.x_grad = 1.0
        self.y_grad = float(model_lr.coef_)
        """
        fig, ax = plt.subplots()

        new_list = []

        q25, q50, q75 = np.percentile(lines[:, 0, 1], [25, 50, 75])

        iqr = q75 - q25

        print("q75:", q75)
        print("q75:", q50)
        print("q75:", q25)

        for i in lines[:, 0, 1]:
            if (q25 - 1.5 * iqr) <= i <= (q75 + 1.5 *iqr):
                new_list.append(i)
        bp = ax.boxplot(new_list)
        ax.set_xticklabels(['before flow principal stress 1'])

        plt.title('box')

        plt.grid()

        plt.show()

        self.axes.cla()

        stress_pair_num = self.get_stress_num()
        lines = np.zeros((stress_pair_num, 2, 2), dtype=ctypes.c_float)
        idx = 0
        current = 0
        previous = 0
        selected_cell_flat_idx = np.full(len(self.using_cell_idx_array), -1)
        is_all = True if selected_cell_flat_idx.size == 0 else False

        for i in tqdm(self.using_data_range):
            stress_pair_data = self.all_stress_pair_data.stress_pair_data_array[i]

            for j, cell_pos in enumerate(self.using_cell_idx_array):
                selected_cell_flat_idx[j] = stress_pair_data.resolution[0] * cell_pos[1] + cell_pos[0]

            for stress_pair in stress_pair_data.stress_pair_array:
                if stress_pair.grid_idx in selected_cell_flat_idx or is_all:
                    current += 1

                    if current - previous < self.stride:
                        continue


                    pre_principal_stress, post_principal_stress = self.compute_principal_stress(stress_pair)

                    if StressPairEdit.is_out_of_scope(pre_principal_stress, post_principal_stress):
                        continue
                    if (q25 - 1.5 * iqr) <= post_principal_stress[1] <= (q75 + 1.5 * iqr):
                        lines[idx, 0] = np.array([pre_principal_stress[0], pre_principal_stress[1]])
                        lines[idx, 1] = np.array([post_principal_stress[0], post_principal_stress[1]])
                        idx += 1
                        previous = current

                    # if post_principal_stress[1] < -10000.0:
                    #     debug_outlier_num += 1
                    #     continue








        lc = LineCollection(lines, colors="y", linewidths=self.stress_line_width)
        self.axes.add_collection(lc)
        self.axes.scatter(lines[:, 0, 0], lines[:, 0, 1], alpha = 0.1, facecolor="blue", s=self.marker_size)
        self.axes.scatter(lines[:, 1, 0], lines[:, 1, 1], alpha = 0.1, facecolor="red", s=self.marker_size)

        #self.axes.scatter(lines[:, 0, 0], lines[:, 0, 1], facecolor="None", s=self.marker_size)
        #self.axes.scatter(lines[:, 1, 0], lines[:, 1, 1], facecolor="None", s=self.marker_size)


        self.set_axis()
        self.axes.plot([0.0, -self.max_lim], [self.intercept, self.y(-self.max_lim) + self.intercept], color='m',linewidth=self.line_width)
        self.draw()



    def calcVariance(self):
        self.axes.cla()
        stress_pair_num = self.get_stress_num()
        selected_cell_flat_idx = np.full(len(self.using_cell_idx_array), -1)
        is_all = True if selected_cell_flat_idx.size == 0 else False
        # 回帰直線からの残差、点との分散を導出する
        total_variance = 0.0
        total_residual_error = 0.0
        idx = 0
        current = 0
        previous = 0
        for i in tqdm(self.using_data_range):
            stress_pair_data = self.all_stress_pair_data.stress_pair_data_array[i]

            for j, cell_pos in enumerate(self.using_cell_idx_array):
                selected_cell_flat_idx[j] = stress_pair_data.resolution[0] * cell_pos[1] + cell_pos[0]

            for stress_pair in stress_pair_data.stress_pair_array:
                if stress_pair.grid_idx in selected_cell_flat_idx or is_all:
                    current += 1

                    if current - previous < self.stride:
                        continue

                    pre_principal_stress, post_principal_stress = self.compute_principal_stress(stress_pair)

                    if StressPairEdit.is_out_of_scope(pre_principal_stress, post_principal_stress):
                        continue

                    total_variance += pow(
                        self.Calc_distance(self.y_grad / self.x_grad, -1, self.intercept, post_principal_stress[0],
                                           post_principal_stress[1]), 2)
                    total_residual_error += pow(
                        post_principal_stress[1] - (self.y_grad / self.x_grad * post_principal_stress[0] + self.intercept), 2)

                    idx += 1

                    previous = current
        self.variance = total_variance / idx
        self.residual_error = total_residual_error / idx
        print("残差(直線と点のy軸方向の差)：", self.residual_error)
        print("分散（点と直線の距離の分散）:", self.variance)

    # 点と直線の距離
    def Calc_distance(self, a, b, c, point_x, point_y):  # 直線ax+by+c=0 点(x0,y0)
        numer = abs(a * point_x + b * point_y + c)  # 分子
        denom = math.sqrt(pow(a, 2) + pow(b, 2))  # 分母
        return numer / denom  # 計算結果

    def set_move_plot_range_x(self, x_move):
        self.x_shift = self.x_shift + x_move - self.past_move_x
        self.past_move_x = x_move
        self.axes.axis(
            [(-self.current_lim + self.x_shift * self.shift_volume / self.current_lim),
             (self.current_lim + self.x_shift * self.shift_volume / self.current_lim),
             (-self.current_lim + self.y_shift * self.shift_volume / self.current_lim),
             (self.current_lim + self.y_shift * self.shift_volume / self.current_lim)])
        self.draw()

    def set_move_plot_range_y(self, y_move):
        self.y_shift = self.y_shift + y_move - self.past_move_y
        self.past_move_y = y_move
        self.axes.axis(
            [(-self.current_lim + self.x_shift * self.shift_volume / self.current_lim),
             (self.current_lim + self.x_shift * self.shift_volume / self.current_lim),
             (-self.current_lim + self.y_shift * self.shift_volume / self.current_lim),
             (self.current_lim + self.y_shift * self.shift_volume / self.current_lim)])
        self.draw()

    def set_zoom_plot(self, zoom):
        self.current_lim = self.current_lim * zoom / self.past_zoom
        self.past_zoom = zoom
        self.axes.axis(
            [(-self.current_lim + self.x_shift * self.shift_volume / self.current_lim),
             (self.current_lim + self.x_shift * self.shift_volume / self.current_lim),
             (-self.current_lim + self.y_shift * self.shift_volume / self.current_lim),
             (self.current_lim + self.y_shift * self.shift_volume / self.current_lim)])

        self.draw()


    @staticmethod
    def compute_principal_stress(stress_pair):
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

    def get_stress_num(self):
        stress_pair_num = 0
        current = 0
        previous = 0

        selected_cell_flat_idx = np.full(len(self.using_cell_idx_array), -1)
        is_all = True if selected_cell_flat_idx.size == 0 else False

        for i in self.using_data_range:
            stress_pair_data = self.all_stress_pair_data.stress_pair_data_array[i]

            for j, cell_pos in enumerate(self.using_cell_idx_array):
                selected_cell_flat_idx[j] = stress_pair_data.resolution[0] * cell_pos[1] + cell_pos[0]

            for stress_pair in stress_pair_data.stress_pair_array:
                if stress_pair.grid_idx in selected_cell_flat_idx or is_all:
                    current += 1

                    if current - previous < self.stride:
                        continue

                    stress_pair_num += 1
                    previous = current

        return stress_pair_num

    def y(self, x: float):
        return (self.y_grad / self.x_grad) * x

    def set_axis(self):
        if self.max_lim is None:
            self.max_lim = abs(max(self.axes.axis(), key=abs))
            self.current_lim = self.max_lim

        self.axes.spines["right"].set_color("none")
        self.axes.spines["top"].set_color("none")
        self.axes.spines["left"].set_position("zero")
        self.axes.spines["bottom"].set_position("zero")
        self.axes.set_aspect("equal")

        #self.axes.plot([0.0, -self.max_lim], [0.0, self.y(-self.max_lim)], color='m', linewidth=self.line_width)
        #self.axes.plot([0.0, -self.max_lim], [self.intercept, self.y(-self.max_lim) + self.intercept], color='m', linewidth=self.line_width)

        self.axes.axis(
            [(-self.current_lim + self.x_shift * self.shift_volume / self.current_lim),
             (self.current_lim + self.x_shift * self.shift_volume / self.current_lim),
             (-self.current_lim + self.y_shift * self.shift_volume / self.current_lim),
             (self.current_lim + self.y_shift * self.shift_volume / self.current_lim)])
        self.axes.grid()

    def replot(self):
        if self.plot_mode == PlotMode.ALL:
            self.using_data_range = range(len(self.all_stress_pair_data.stress_pair_data_array))
            self.using_cell_idx_array = []

        if self.plot_mode == PlotMode.PLOT_PER_TIMESTEP:
            self.using_data_range = [self.current_time]
            self.using_cell_idx_array = []

        if self.plot_mode == PlotMode.PLOT_PER_CELL:
            self.using_data_range = range(len(self.all_stress_pair_data.stress_pair_data_array))
            self.using_cell_idx_array = self.cell_pos_list

        if self.plot_mode == PlotMode.PLOT_PER_CELL_AND_TIMESTEP:
            self.using_data_range = [self.current_time]
            self.using_cell_idx_array = self.cell_pos_list

        self.__plot_data()
        # self.calc_moving_average()

    def get_plot_mode_text(self):
        if self.plot_mode == PlotMode.ALL:
            return "All"

        if self.plot_mode == PlotMode.PLOT_PER_TIMESTEP:
            return "TIMESTEP"

        if self.plot_mode == PlotMode.PLOT_PER_CELL:
            return "CELL"

        if self.plot_mode == PlotMode.PLOT_PER_CELL_AND_TIMESTEP:
            return "Cell And Timestep"

    def set_current_lim(self, lim, x_grad, y_grad, intercept, stride, width):
        self.current_lim = lim
        self.x_grad = x_grad
        self.y_grad = y_grad
        self.intercept = intercept
        self.stride = stride
        self.line_width = width
        self.init_slider_parameter()

        #リプロット
        self.replot()

        #self.calcVariance()

        #格子再設定のみ
        #self.set_axis()
        #self.axes.grid()

    def init_slider_parameter(self):
        self.x_shift = 0.0
        self.y_shift = 0.0
        self.past_move_x = 0.0
        self.past_move_y = 0.0
        self.past_zoom = 1.0

    def reset_current_lim(self):
        self.current_lim = self.max_lim
        self.replot()
        self.init_slider_parameter()

    def set_cell_pos(self, cell_pos):
        self.cell_pos_list = cell_pos
        self.replot()

    def set_grid(self, current_time):
        self.current_time = current_time
        self.replot()

    def set_all_stress_pair_data(self, all_stress_pair_data):
        self.all_stress_pair_data = all_stress_pair_data
        self.plot_mode = PlotMode.ALL
        # self.replot()

    def plot_all_data(self):
        self.plot_mode = PlotMode.ALL
        self.replot()

    def plot_data_per_timestep(self):
        self.plot_mode = PlotMode.PLOT_PER_TIMESTEP
        self.replot()

    def plot_data_per_cell(self):
        self.plot_mode = PlotMode.PLOT_PER_CELL
        self.replot()

    def plot_data_per_cell_and_timestep(self):
        self.plot_mode = PlotMode.PLOT_PER_CELL_AND_TIMESTEP
        self.replot()
