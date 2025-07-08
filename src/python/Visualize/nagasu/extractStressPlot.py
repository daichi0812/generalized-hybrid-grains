# http://www.not-enough.org/abe/manual/program-aa08/pyqt1.html

import math
import re

from OpenGL.GLUT import *
from PyQt5 import QtCore, QtWidgets

from allgrainh5 import *
from qt_gl_widget2 import QTGLWidget2
from stress_plot_widget import StressPlotCanvas
from stresspairh5 import *


class UiWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self, flags=QtCore.Qt.Widget)

        self.all_stress_pair_data = AllStressPairData()
        self.all_scene_data = AllSceneData()
        self.scene_fn = ""
        self.template_fn = ""
        self.selected_cell_pos_list = np.zeros((0, 0), dtype=ctypes.c_int)

        self.stress_plot_canvas = StressPlotCanvas(self)
        self.gl = QTGLWidget2(self)

        self.camera_y_pos_label = QtWidgets.QLabel("cp: ")
        self.camera_y_pos_slider = self.create_slider(QtCore.Qt.Vertical, 0, 100, 50, self.update_camera_pos)

        self.plot_y_move_label = QtWidgets.QLabel("axis y: ")
        self.plot_y_move_slider = self.create_slider(QtCore.Qt.Vertical, -10000, 5000, 0, self.update_axis_y)

        self.camera_x_pos_label = QtWidgets.QLabel("camera pos: ")
        self.camera_x_pos_slider = self.create_slider(QtCore.Qt.Horizontal, 0, 100, 50, self.update_camera_pos)

        self.plot_x_move_label = QtWidgets.QLabel("axis x: ")
        self.plot_x_move_slider = self.create_slider(QtCore.Qt.Horizontal, -10000, 5000, 0, self.update_axis_x)

        self.camera_zoom_label = QtWidgets.QLabel("camera zoom: ")
        self.camera_zoom_slider = self.create_slider(QtCore.Qt.Horizontal, 0, 100, 50, self.update_camera_pos)

        self.plot_zoom_label = QtWidgets.QLabel("plot zoom: ")
        self.plot_zoom_slider = self.create_slider(QtCore.Qt.Horizontal, 0, 100, 50, self.update_plot_zoom)

        self.dt_plot_label = QtWidgets.QLabel("t: ")
        self.dt_plot_slider = self.create_slider(QtCore.Qt.Horizontal, 0, 1000, 0, self.update_dt)

        self.dt_gl_label = QtWidgets.QLabel("t: ")
        self.dt_gl_slider = self.create_slider(QtCore.Qt.Horizontal, 0, 1000, 0, self.update_view)

        self.grains_checkbox = self.create_checkbox("Grains", True, self.check_box_changed)
        self.grid_checkbox = self.create_checkbox("Grid", True, self.check_box_changed)
        self.selected_cell_checkbox = self.create_checkbox("Fill Cell", True, self.check_box_changed)

        self.current_plot_mode_label = QtWidgets.QLabel("")
        self.plot_both_btn = self.create_btn("Plot Per Both", self.plot_per_both)
        self.plot_cell_btn = self.create_btn("Plot Per Cell", self.plot_per_cell)
        self.plot_dt_btn = self.create_btn("Plot Per Timestep", self.plot_per_timestep)
        self.plot_all_btn = self.create_btn("Plot All", self.plot_all)
        self.load_btn = self.create_btn("Load", self.load)

        self.set_plot_lim_btn = self.create_btn("Apply", self.set_plot_lim)
        self.reset_plot_lim_btn = self.create_btn("Reset", self.reset_plot_lim)

        self.plot_scale_label, self.plot_scale_edit = self.create_line_edit_with_label("scale: ")
        self.plot_x_grad_label, self.plot_x_grad_edit = self.create_line_edit_with_label("x grad: ")
        self.plot_y_grad_label, self.plot_y_grad_edit = self.create_line_edit_with_label("y grad: ")
        self.plot_intercept_label, self.plot_intercept_edit = self.create_line_edit_with_label("intercept: ")
        self.plot_stride_label, self.plot_stride_edit = self.create_line_edit_with_label("stride: ")
        self.plot_width_label, self.plot_width_edit = self.create_line_edit_with_label("width: ")

        self.cell_idx_list = self.create_list(self.update_selected_cell_pos_list,
                                              QtWidgets.QAbstractItemView.MultiSelection)
        self.cell_idx_list.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)

        self.init_layout()

    def init_layout(self):
        camera_y_pos_box = QtWidgets.QVBoxLayout()
        camera_y_pos_box.addWidget(self.camera_y_pos_label, alignment=QtCore.Qt.Alignment())
        camera_y_pos_box.addWidget(self.camera_y_pos_slider, alignment=QtCore.Qt.Alignment())

        plot_move_y_pos_box = QtWidgets.QVBoxLayout()
        plot_move_y_pos_box.addWidget(self.plot_y_move_label, alignment=QtCore.Qt.Alignment())
        plot_move_y_pos_box.addWidget(self.plot_y_move_slider, alignment=QtCore.Qt.Alignment())

        dt_plot_box = QtWidgets.QHBoxLayout()
        dt_plot_box.addWidget(self.dt_plot_label, alignment=QtCore.Qt.Alignment())
        dt_plot_box.addWidget(self.dt_plot_slider, alignment=QtCore.Qt.Alignment())

        plot_move_x_pos_box = QtWidgets.QHBoxLayout()
        plot_move_x_pos_box.addWidget(self.plot_x_move_label, alignment=QtCore.Qt.Alignment())
        plot_move_x_pos_box.addWidget(self.plot_x_move_slider, alignment=QtCore.Qt.Alignment())

        plot_box = QtWidgets.QVBoxLayout()
        plot_box.addWidget(self.stress_plot_canvas, alignment=QtCore.Qt.Alignment())
        plot_box.addLayout(dt_plot_box)

        dt_gl_box = QtWidgets.QHBoxLayout()
        dt_gl_box.addWidget(self.dt_gl_label, alignment=QtCore.Qt.Alignment())
        dt_gl_box.addWidget(self.dt_gl_slider, alignment=QtCore.Qt.Alignment())

        gl_box = QtWidgets.QVBoxLayout()
        gl_box.addWidget(self.gl, alignment=QtCore.Qt.Alignment())
        gl_box.addLayout(dt_gl_box)

        upper_box = QtWidgets.QHBoxLayout()
        upper_box.addLayout(plot_box)
        upper_box.addLayout(plot_move_y_pos_box)
        upper_box.addLayout(gl_box)
        upper_box.addLayout(camera_y_pos_box)

        label_box = QtWidgets.QVBoxLayout()
        label_box.addWidget(self.camera_x_pos_label, alignment=QtCore.Qt.Alignment())
        label_box.addWidget(self.camera_zoom_label, alignment=QtCore.Qt.Alignment())
        label_box.addWidget(self.plot_zoom_label, alignment=QtCore.Qt.Alignment())

        slider_box = QtWidgets.QVBoxLayout()
        slider_box.addWidget(self.camera_x_pos_slider, alignment=QtCore.Qt.Alignment())
        slider_box.addWidget(self.camera_zoom_slider, alignment=QtCore.Qt.Alignment())
        slider_box.addWidget(self.plot_zoom_slider, alignment=QtCore.Qt.Alignment())

        slider_label_box = QtWidgets.QHBoxLayout()
        slider_label_box.addLayout(label_box)
        slider_label_box.addLayout(slider_box)
        slider_label_box.addLayout(plot_move_x_pos_box)

        checkboxes = QtWidgets.QHBoxLayout()
        checkboxes.addWidget(self.grains_checkbox, alignment=QtCore.Qt.Alignment())
        checkboxes.addWidget(self.selected_cell_checkbox, alignment=QtCore.Qt.Alignment())
        checkboxes.addWidget(self.grid_checkbox, alignment=QtCore.Qt.Alignment())

        btn_box = QtWidgets.QHBoxLayout()
        btn_box.addWidget(self.current_plot_mode_label, alignment=QtCore.Qt.Alignment())
        btn_box.addWidget(self.plot_both_btn, alignment=QtCore.Qt.Alignment())
        btn_box.addWidget(self.plot_cell_btn, alignment=QtCore.Qt.Alignment())
        btn_box.addWidget(self.plot_dt_btn, alignment=QtCore.Qt.Alignment())
        btn_box.addWidget(self.plot_all_btn, alignment=QtCore.Qt.Alignment())

        plot_label_box = QtWidgets.QVBoxLayout()
        plot_label_box.addWidget(self.plot_scale_label, alignment=QtCore.Qt.Alignment())
        plot_label_box.addWidget(self.plot_x_grad_label, alignment=QtCore.Qt.Alignment())
        plot_label_box.addWidget(self.plot_y_grad_label, alignment=QtCore.Qt.Alignment())
        plot_label_box.addWidget(self.plot_intercept_label, alignment=QtCore.Qt.Alignment())
        plot_label_box.addWidget(self.plot_stride_label, alignment=QtCore.Qt.Alignment())
        plot_label_box.addWidget(self.plot_width_label, alignment=QtCore.Qt.Alignment())

        plot_line_edit_box = QtWidgets.QVBoxLayout()
        plot_line_edit_box.addWidget(self.plot_scale_edit, alignment=QtCore.Qt.Alignment())
        plot_line_edit_box.addWidget(self.plot_x_grad_edit, alignment=QtCore.Qt.Alignment())
        plot_line_edit_box.addWidget(self.plot_y_grad_edit, alignment=QtCore.Qt.Alignment())
        plot_line_edit_box.addWidget(self.plot_intercept_edit, alignment=QtCore.Qt.Alignment())
        plot_line_edit_box.addWidget(self.plot_stride_edit, alignment=QtCore.Qt.Alignment())
        plot_line_edit_box.addWidget(self.plot_width_edit, alignment=QtCore.Qt.Alignment())

        plot_lim_btn_box = QtWidgets.QHBoxLayout()
        plot_lim_btn_box.addWidget(self.set_plot_lim_btn, alignment=QtCore.Qt.Alignment())
        plot_lim_btn_box.addWidget(self.reset_plot_lim_btn, alignment=QtCore.Qt.Alignment())

        plot_edit_box = QtWidgets.QHBoxLayout()
        plot_edit_box.addLayout(plot_label_box)
        plot_edit_box.addLayout(plot_line_edit_box)

        plot_lim_box = QtWidgets.QVBoxLayout()
        plot_lim_box.addLayout(plot_edit_box)
        plot_lim_box.addLayout(plot_lim_btn_box)

        ul_box = QtWidgets.QVBoxLayout()
        ul_box.addLayout(slider_label_box)
        ul_box.addLayout(checkboxes)
        ul_box.addLayout(btn_box)
        ul_box.addWidget(self.load_btn, alignment=QtCore.Qt.Alignment())

        under_box = QtWidgets.QHBoxLayout()
        under_box.addLayout(ul_box)
        under_box.addLayout(plot_lim_box)
        under_box.addWidget(self.cell_idx_list, alignment=QtCore.Qt.Alignment())

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(upper_box)
        vbox.addLayout(under_box)

        self.setLayout(vbox)
        self.resize(300, 350)

    def create_slider(self, orientation, min_value, max_value, default_value, connect_func):
        slider = QtWidgets.QSlider(orientation, self)
        slider.setMinimum(min_value)
        slider.setMaximum(max_value)
        slider.setValue(default_value)
        slider.valueChanged.connect(connect_func)
        return slider

    def create_checkbox(self, label, is_checked, connect_func):
        checkbox = QtWidgets.QCheckBox(label, self)
        checkbox.setChecked(is_checked)
        checkbox.stateChanged.connect(connect_func)
        return checkbox

    def create_btn(self, label, connect_func):
        btn = QtWidgets.QPushButton(label, self)
        btn.clicked.connect(connect_func)
        return btn

    def create_list(self, connect_func, selection_mode):
        qlist = QtWidgets.QListWidget(self)
        qlist.itemClicked.connect(connect_func)
        qlist.setSelectionMode(selection_mode)
        return qlist

    def create_line_edit_with_label(self, label):
        label = QtWidgets.QLabel(label)
        line_edit = QtWidgets.QLineEdit(self)
        line_edit.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        return label, line_edit

    def update_idx_list(self, dt):
        self.cell_idx_list.clear()
        stress_pair_data = self.all_stress_pair_data.stress_pair_data_array[dt]

        for stress_pair in stress_pair_data.stress_pair_array:
            x = int(stress_pair.grid_idx) % int(stress_pair_data.resolution[0])
            y = int(stress_pair.grid_idx / stress_pair_data.resolution[0])
            self.cell_idx_list.addItem(f"{x}, {y}")

        self.update_selected_cell_pos_list()

    def update_selected_cell_pos_list(self):
        selected_idx_array = self.cell_idx_list.selectedIndexes()

        idx_num = len(selected_idx_array)
        self.selected_cell_pos_list = np.zeros((idx_num, 2), dtype=ctypes.c_int)

        for i in range(idx_num):
            label = self.cell_idx_list.itemFromIndex(selected_idx_array[i]).text()
            cell_pos = re.findall(r"\d+", label)
            self.selected_cell_pos_list[i] = np.array([int(cell_pos[0]), int(cell_pos[1])])

        self.stress_plot_canvas.set_cell_pos(self.selected_cell_pos_list)
        self.gl.set_cell_pos_list(self.selected_cell_pos_list)

    def update_view(self):
        dt = self.dt_gl_slider.value()
        self.dt_gl_label.setText('t: %.3d' % dt)
        self.dt_plot_slider.setValue(dt)
        self.all_scene_data.load_from_idx(self.template_fn, self.scene_fn, dt)
        self.update_idx_list(dt)
        self.gl.set_data(self.all_stress_pair_data.stress_pair_data_array[dt], self.all_scene_data.all_step_elements[0])

    def update_dt(self):
        dt = self.dt_plot_slider.value()
        self.dt_plot_label.setText('t: %.3d' % dt)
        self.stress_plot_canvas.set_grid(dt)

    def update_camera_pos(self):
        x_pos = self.camera_x_pos_slider.value() / 100.0
        y_pos = self.camera_y_pos_slider.value() / 100.0
        side_mag_level = 5  # 2^5 = 32x magnification
        zoom_level = math.pow(2.0, (self.camera_zoom_slider.value() - 50.0) * side_mag_level / 50.0)
        self.gl.set_view_info(x_pos, y_pos, zoom_level)

    def update_plot_zoom(self):
        side_mag_level = 5  # 2^5 = 32x magnification
        zoom_level = math.pow(2.0, (self.plot_zoom_slider.value() - 50.0) * side_mag_level / 50.0)
        self.stress_plot_canvas.set_zoom_plot(zoom_level)

    def check_box_changed(self):
        self.gl.toggle_draw(self.grains_checkbox.isChecked(), self.selected_cell_checkbox.isChecked(),
                            self.grid_checkbox.isChecked())

    def set_plot_mode_label(self):
        self.current_plot_mode_label.setText(self.stress_plot_canvas.get_plot_mode_text())

    def set_plot_lim_edit(self):
        self.plot_scale_edit.setText(format(self.stress_plot_canvas.current_lim, ".6f"))
        self.plot_x_grad_edit.setText(format(self.stress_plot_canvas.x_grad, ".6f"))
        self.plot_y_grad_edit.setText(format(self.stress_plot_canvas.y_grad, ".6f"))
        self.plot_intercept_edit.setText(format(self.stress_plot_canvas.y_grad, ".6f"))
        self.plot_width_edit.setText(format(self.stress_plot_canvas.line_width, ".6f"))
        self.plot_stride_edit.setText(str(self.stress_plot_canvas.stride))

    def set_plot_lim(self):
        self.stress_plot_canvas.set_current_lim(float(self.plot_scale_edit.text()), float(self.plot_x_grad_edit.text()),
                                                float(self.plot_y_grad_edit.text()), float(self.plot_intercept_edit.text()), int(self.plot_stride_edit.text()),
                                                float(self.plot_width_edit.text()))

    def reset_plot_lim(self):
        self.stress_plot_canvas.reset_current_lim()
        self.set_plot_lim_edit()

    def init_dt_slider(self):
        self.dt_plot_label.setText('t: %.3d' % self.dt_plot_slider.value())
        self.dt_plot_slider.setMaximum(len(self.all_stress_pair_data.stress_pair_data_array) - 1)
        self.dt_gl_slider.setMaximum(len(self.all_stress_pair_data.stress_pair_data_array) - 1)

    def load(self):
        # stress_fn = "Save/stress_pair.h5"
        # self.scene_fn = "Save/serialized_forces.h5"

        # プロット用応力データ
        stress_fn = "Save_square11_flow/compressed_stress.h5"

        # 描画用粒子データ
        self.scene_fn = "Rolling_square11_flow/element_data.h5"

        # テンプレートファイル
        self.template_fn = "Save_square11_flow/square11_flow_template.h5"

        if len(sys.argv) >= 1:
                stress_fn = "IOData/" + str(sys.argv[1]) + "/" + str(sys.argv[2]) + "/compressed_stress.h5"
                self.scene_fn = "IOData/" + str(sys.argv[1]) + "/" + str(sys.argv[2]) + "/Output/element_data.h5"
                self.template_fn = "IOData/" + str(sys.argv[1]) + "/" + str(sys.argv[2]) + "/" + str(sys.argv[1]).lower() + str(sys.argv[2]) + "_flow_template.h5"

        self.all_stress_pair_data.load(stress_fn)
        self.stress_plot_canvas.set_all_stress_pair_data(self.all_stress_pair_data)
        self.update_view()
        self.set_plot_lim_edit()
        self.init_dt_slider()
        self.set_plot_mode_label()

    def update_axis_x(self):
        self.x_move = float(self.plot_x_move_slider.value())
        self.stress_plot_canvas.set_move_plot_range_x(self.x_move)

    def update_axis_y(self):
        self.y_move = float(self.plot_y_move_slider.value())
        self.stress_plot_canvas.set_move_plot_range_y(self.y_move)


    def plot_per_timestep(self):
        self.stress_plot_canvas.plot_data_per_timestep()
        self.set_plot_mode_label()

    def plot_per_cell(self):
        self.stress_plot_canvas.plot_data_per_cell()
        self.set_plot_mode_label()

    def plot_all(self):
        self.stress_plot_canvas.plot_all_data()
        self.set_plot_mode_label()

    def plot_per_both(self):
        self.stress_plot_canvas.plot_data_per_cell_and_timestep()
        self.set_plot_mode_label()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = UiWidget()
    ui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
