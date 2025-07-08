import copy
import math

from PyQt5.QtOpenGL import *

from vertex_buffer_objects import *
from allgrainh5 import *
from stresspairh5 import *


class QTGLWidget2(QGLWidget):
    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(300, 300)
        self.stress_pair_data = StressPairData()
        self.data = SceneData()
        self.cell_pos_list = np.zeros((0, 2), dtype=ctypes.c_int)

        self.grid_VBO = LineVBO()
        self.grains_VBO = LineVBO()
        self.cell_VBO = TriangleVBO()

        self.draw_grains = True
        self.fill_cell = True
        self.draw_grid = True

        self.height_reference = 540.0
        self.camera_x_pos = 0.0
        self.camera_y_pos = 0.0
        self.camera_zoom = 1.0
        self.extent = 1.0
        self.center = np.zeros(2)
        self.inner_width = 300
        self.inner_height = 300

        self.alpha = 0.5

    @staticmethod
    def num_lines_for_drawing_circle():
        num_seg = 128
        return 1 + num_seg

    @staticmethod
    def compute_vbo_for_drawing_circle(vbo, center, angle, is_static, radius):
        num_seg = 128

        color = [0.6, 0.6, 0.6, 1.0]
        if is_static:
            color = [0.9, 0.9, 0.9, 1.0]

        v0 = [center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle)]
        v1 = [center[0] - radius * math.cos(angle), center[1] - radius * math.sin(angle)]

        vbo.register_line_to_data_array(v0, v1, color, color)

        for i in range(num_seg):
            t0 = angle + i * 2.0 * math.pi / num_seg
            t1 = angle + (i + 1) * 2.0 * math.pi / num_seg
            v0 = [center[0] + radius * math.cos(t0), center[1] + radius * math.sin(t0)]
            v1 = [center[0] + radius * math.cos(t1), center[1] + radius * math.sin(t1)]

            vbo.register_line_to_data_array(v0, v1, color, color)

    @staticmethod
    def compute_circle_bb(center, radius):
        v_min = center - radius
        v_max = center + radius
        return v_min, v_max

    @staticmethod
    def num_lines_for_drawing_polygon(vertex_list):
        return vertex_list.shape[1]

    @staticmethod
    def compute_vbo_for_drawing_polygon(vbo, center, angle, is_static, vertex_list, size_ratio):
        rot_mat = np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])
        num_vertices = vertex_list.shape[1]

        color = [0.6, 0.6, 0.6, 1.0]
        if is_static:
            color = [0.9, 0.9, 0.9, 1.0]

        for i in range(num_vertices):
            ip = (i + 1) % num_vertices
            v0 = (center + size_ratio * rot_mat @ vertex_list[:, i]).flatten()
            v1 = (center + size_ratio * rot_mat @ vertex_list[:, ip]).flatten()
            vbo.register_line_to_data_array(v0, v1, color, color)

    @staticmethod
    def compute_polygon_bb(center, size_ratio, vertex_list, angle):
        v_min = center
        v_max = center

        rot_mat = np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])
        num_vertices = vertex_list.shape[1]

        for i in range(num_vertices):
            v = (center + size_ratio * rot_mat @ vertex_list[:, i])
            v_min = np.minimum(v_min, v)
            v_max = np.maximum(v_max, v)

        return v_min, v_max

    def num_lines_for_drawing_grid(self):
        n_grid_lines = 0
        n_cells = 0
        if self.stress_pair_data.resolution[0] > 0 and self.stress_pair_data.resolution[1] > 0:
            n_grid_lines = self.stress_pair_data.resolution[0] + 1 + self.stress_pair_data.resolution[1] + 1
            n_cells = self.stress_pair_data.resolution[0] * self.stress_pair_data.resolution[1]

        return n_grid_lines + n_cells * 2

    def compute_vbo_for_drawing_grid(self, vbo):
        resolution = self.stress_pair_data.resolution
        h = self.stress_pair_data.h
        grid_start = self.stress_pair_data.grid_p

        if resolution[0] <= 0 or resolution[1] <= 0:
            return

        e1 = np.array([1, 0]).transpose()
        e2 = np.array([0, 1]).transpose()

        for i in range(resolution[0] + 1):
            v0 = grid_start + h * i * e1
            v1 = v0 + h * resolution[1] * e2
            color = [0.3, 0.3, 0.3, 1.0]
            vbo.register_line_to_data_array(v0, v1, color, color)

        for i in range(resolution[1] + 1):
            v0 = grid_start + h * i * e2
            v1 = v0 + h * resolution[0] * e1
            color = [0.3, 0.3, 0.3, 1.0]
            vbo.register_line_to_data_array(v0, v1, color, color)

        for stress_pair in self.stress_pair_data.stress_pair_array:
            i = int(stress_pair.grid_idx) % int(resolution[0])
            j = int(stress_pair.grid_idx / resolution[0])

            color = [232.0 / 255.0, 158.0 / 255.0, 46.0 / 255.0, 1.0]
            vc = grid_start + h * np.array([i + 0.5, j + 0.5])

            v0 = vc + h * np.array([0.5, 0.5])
            v1 = vc + h * np.array([-0.5, -0.5])
            vbo.register_line_to_data_array(v0, v1, color, color)

            v2 = vc + h * np.array([-0.5, 0.5])
            v3 = vc + h * np.array([0.5, -0.5])
            vbo.register_line_to_data_array(v2, v3, color, color)

    def num_triangles_for_filling_cell(self):
        return self.cell_pos_list.size

    def compute_vbo_for_filling_cell(self, vbo):
        h = self.stress_pair_data.h
        grid_start = self.stress_pair_data.grid_p

        color = [0.0 / 255.0, 128.0 / 255.0, 0.0 / 255.0, self.alpha]

        for cell_pos in self.cell_pos_list:
            vc = grid_start + h * np.array([cell_pos[0] + 0.5, cell_pos[1] + 0.5])

            v_list = [vc + h * np.array([0.5, 0.5]), vc + h * np.array([-0.5, 0.5]), vc + h * np.array([-0.5, -0.5])]
            c_list = [color, color, color]
            vbo.register_triangle_to_data_array(v_list, c_list)

            v_list = [vc + h * np.array([-0.5, -0.5]), vc + h * np.array([0.5, -0.5]), vc + h * np.array([0.5, 0.5])]
            c_list = [color, color, color]
            vbo.register_triangle_to_data_array(v_list, c_list)

    def draw_elements_vbo(self):
        if self.draw_grains:
            self.grains_VBO.draw_vbo(3.0)

        if self.draw_grid:
            self.grid_VBO.draw_vbo(3.0)

        if self.fill_cell:
            self.cell_VBO.draw_vbo(0.01)

    def pre_display(self):
        half_width = self.compute_half_width(self.inner_width)
        half_height = self.compute_half_height(self.inner_height)

        x_offset = self.camera_x_pos * self.extent * 0.5
        y_offset = self.camera_y_pos * self.extent * 0.5

        glViewport(0, 0, self.inner_width, self.inner_height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.center[0] + x_offset - half_width, self.center[0] + x_offset + half_width,
                self.center[1] + y_offset - half_height, self.center[1] + y_offset + half_height, -1.0, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.pre_display()
        self.draw_elements_vbo()

        glFlush()

    def resizeGL(self, w, h):
        self.inner_width = w
        self.inner_height = h

    def initializeGL(self):
        #glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClearDepth(1.0)

    def compute_half_width(self, w):
        return self.camera_zoom * w / self.height_reference

    def compute_half_height(self, h):
        return self.camera_zoom * h / self.height_reference

    def build_vbo_element(self):
        num_lines_grains = 0
        for e in self.data.elements:
            vertex_list_e = self.data.templates[e.template_name].vertex_list
            num_vertices_shape = vertex_list_e.shape[1]
            if num_vertices_shape < 3:
                num_lines_grains += self.num_lines_for_drawing_circle()
            else:
                num_lines_grains += self.num_lines_for_drawing_polygon(self.data.templates[e.template_name].vertex_list)

        self.grains_VBO.set_num_elements(num_lines_grains)

        for e in self.data.elements:
            vertex_list_e = self.data.templates[e.template_name].vertex_list
            num_vertices = vertex_list_e.shape[1]
            if num_vertices < 3:
                self.compute_vbo_for_drawing_circle(self.grains_VBO, e.center_of_mass, e.rotation_angle, e.static,
                                                    e.size_ratio * 0.5 * self.data.templates[e.template_name].size_mean)
            else:
                self.compute_vbo_for_drawing_polygon(self.grains_VBO, e.center_of_mass, e.rotation_angle, e.static,
                                                     self.data.templates[e.template_name].vertex_list, e.size_ratio)

        self.grains_VBO.gen_buffers()

    def build_vbo_grid(self):
        self.grid_VBO.set_num_elements(self.num_lines_for_drawing_grid())
        self.compute_vbo_for_drawing_grid(self.grid_VBO)
        self.grid_VBO.gen_buffers()

    def build_vbo_cell(self):
        self.cell_VBO.set_num_elements(self.num_triangles_for_filling_cell())
        self.compute_vbo_for_filling_cell(self.cell_VBO)
        self.cell_VBO.gen_buffers()

    def auto_adjust_view(self):
        v_min = np.array([1.0e6, 1.0e6])
        v_max = np.array([-1.0e6, -1.0e6])
        num_non_static_objects = 0

        for e in self.data.elements:
            if e.static:
                continue

            num_non_static_objects += 1
            vertex_list_e = self.data.templates[e.template_name].vertex_list
            num_vertices_shape = vertex_list_e.shape[1]
            if num_vertices_shape < 3:
                _v_min, _v_max = self.compute_circle_bb(e.center_of_mass, e.size_ratio * 0.5 * self.data.templates[
                    e.template_name].size_mean)
                v_min = np.minimum(v_min, _v_min)
                v_max = np.maximum(v_max, _v_max)
            else:
                _v_min, _v_max = self.compute_polygon_bb(e.center_of_mass, e.size_ratio,
                                                         self.data.templates[e.template_name].vertex_list,
                                                         e.rotation_angle)
                v_min = np.minimum(v_min, _v_min)
                v_max = np.maximum(v_max, _v_max)

        if num_non_static_objects == 0:
            return

        self.extent = np.amax(v_max - v_min)
        self.center = (v_max + v_min) * 0.5

    def set_cell_pos_list(self, cell_pos):
        self.cell_pos_list = cell_pos
        self.auto_adjust_view()
        self.build_vbo_cell()
        self.updateGL()

    def set_data(self, stress_pair_data, scene_data):
        self.data = copy.deepcopy(scene_data)
        self.stress_pair_data = copy.deepcopy(stress_pair_data)
        self.auto_adjust_view()
        self.build_vbo_element()
        self.build_vbo_grid()
        self.updateGL()

    def set_view_info(self, x_pos, y_pos, zoom):
        self.camera_x_pos = 2.0 * x_pos - 1.0
        self.camera_y_pos = 2.0 * y_pos - 1.0
        self.camera_zoom = zoom
        self.updateGL()

    def toggle_draw(self, draw_grains, fill_cell, draw_grid):
        self.draw_grains = draw_grains
        self.fill_cell = fill_cell
        self.draw_grid = draw_grid
        self.updateGL()
