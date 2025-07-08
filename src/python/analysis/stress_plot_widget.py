import ctypes
import math

from enum import Enum
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.collections import LineCollection
from stresspairh5 import *
from stress_pair_compressor import *
from tqdm import tqdm


class PlotMode(Enum):
    ALL = 0
    PLOT_PER_CELL = 1
    PLOT_PER_TIMESTEP = 2
    PLOT_PER_CELL_AND_TIMESTEP = 3


class StressPlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(1, 1, 1)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        self.all_stress_pair_data = AllStressPairData()
        self.cell_pos_list = np.zeros((0, 2), dtype=ctypes.c_int)
        self.plot_mode = PlotMode.ALL

        self.current_time = 0
        self.using_data_range = []
        self.using_cell_idx_array = np.zeros((0, 2), dtype=ctypes.c_int)

        self.max_lim = None
        self.current_lim = None

        self.line_width = 0.3
        self.marker_size = 1.0

        self.stride = 1

        self.x_grad = 24.24894563
        self.y_grad = 0

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

                    lines[idx, 0] = np.array([pre_principal_stress[0], pre_principal_stress[1]])
                    lines[idx, 1] = np.array([post_principal_stress[0], post_principal_stress[1]])
                    idx += 1

                    previous = current

        lc = LineCollection(lines, colors="y", linewidths=self.line_width)
        self.axes.add_collection(lc)

        self.axes.scatter(lines[:, 0, 0], lines[:, 0, 1], facecolor="blue", s=self.marker_size)
        self.axes.scatter(lines[:, 1, 0], lines[:, 1, 1], facecolor="red", s=self.marker_size)

        self.set_axis()
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

        self.axes.plot([0.0, -self.max_lim], [0.0, self.y(-self.max_lim)], color='m', linewidth=self.line_width)

        self.axes.axis([-self.current_lim, self.current_lim, -self.current_lim, self.current_lim])
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

    def set_current_lim(self, lim, x_grad, y_grad, stride, width):
        self.current_lim = lim
        self.x_grad = x_grad
        self.y_grad = y_grad
        self.stride = stride
        self.line_width = width
        self.replot()

    def reset_current_lim(self):
        self.current_lim = self.max_lim
        self.replot()

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
