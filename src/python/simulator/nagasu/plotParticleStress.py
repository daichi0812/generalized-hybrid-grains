# http://www.not-enough.org/abe/manual/program-aa08/pyqt1.html

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtOpenGL import *
import math
import copy
from grainh5 import *
from forceh5 import *
from homogenizationh5 import *
from allhomogenizationh5 import *
from allforceh5 import *
from allgrainh5 import *
from homogenizer import *
from particlehomogenizationh5 import *
import pandas as pd
import plotly.express as px

class LineVBO:
    def __init__(self):
        self.VBOData_vertices = np.zeros(2, dtype=ctypes.c_float)
        self.VBOData_colors = np.zeros(3, dtype=ctypes.c_float)
        self.VBOData_indices = np.zeros(2, dtype=ctypes.c_uint)
        self.VBO_buffers = [3]
        self.VBO_buffers[0] = None
        self.vertex_num_offset = 0
        self.color_num_offset = 0
        self.index_num_offset = 0

    def setNumElements(self, num_lines):
        self.VBOData_vertices = np.zeros(2 * 2 * num_lines * 2, dtype=ctypes.c_float)
        self.VBOData_colors = np.zeros(2 * 3 * num_lines * 2, dtype=ctypes.c_float)
        self.VBOData_indices = np.zeros(2 * 2 * num_lines, dtype=ctypes.c_uint)
        self.vertex_num_offset = 0
        self.color_num_offset = 0
        self.index_num_offset = 0

    def genBuffers(self):
        self.VBO_buffers = glGenBuffers(3)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO_buffers[0])
        glBufferData(GL_ARRAY_BUFFER,
                     len(self.VBOData_vertices) * 4,  # byte size
                     (ctypes.c_float * len(self.VBOData_vertices))(*self.VBOData_vertices),
                     GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO_buffers[1])
        glBufferData(GL_ARRAY_BUFFER,
                     len(self.VBOData_colors) * 4,  # byte size
                     (ctypes.c_float * len(self.VBOData_colors))(*self.VBOData_colors),
                     GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.VBO_buffers[2])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                     len(self.VBOData_indices) * 4,  # byte size
                     (ctypes.c_uint * len(self.VBOData_indices))(*self.VBOData_indices),
                     GL_STATIC_DRAW)

    def drawVBO(self, line_width):
        glEnableClientState(GL_VERTEX_ARRAY);
        glEnableClientState(GL_COLOR_ARRAY);
        if self.VBO_buffers[0] != None:
            glBindBuffer(GL_ARRAY_BUFFER, self.VBO_buffers[0]);
            glVertexPointer(2, GL_FLOAT, 0, None);
            glBindBuffer(GL_ARRAY_BUFFER, self.VBO_buffers[1]);
            glColorPointer(3, GL_FLOAT, 0, None);
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.VBO_buffers[2]);
            glLineWidth(line_width)
            glDrawElements(GL_LINES, self.VBOData_indices.shape[0], GL_UNSIGNED_INT, None);
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY);

    def registerLineToDataArray(self, v0, v1, c0, c1):
        self.VBOData_vertices[(self.vertex_num_offset * 2):(self.vertex_num_offset * 2 + 2)] = v0
        self.VBOData_colors[(self.color_num_offset * 3):(self.color_num_offset * 3 + 3)] = c0
        self.VBOData_vertices[((self.vertex_num_offset + 1) * 2):((self.vertex_num_offset + 1) * 2 + 2)] = v1
        self.VBOData_colors[((self.color_num_offset + 1) * 3):((self.color_num_offset + 1) * 3 + 3)] = c1

        self.VBOData_indices[self.index_num_offset * 2] = self.vertex_num_offset
        self.VBOData_indices[self.index_num_offset * 2 + 1] = self.vertex_num_offset + 1

        self.vertex_num_offset += 2
        self.color_num_offset += 2
        self.index_num_offset += 1


class PlotStressGrid:
    def __init__(self):
        self.grid_start = np.zeros(2, dtype=ctypes.c_float)
        self.h = 0.01
        self.resolution = np.zeros(2, dtype=ctypes.c_int)
        self.sigma = np.zeros((1, 2, 2), dtype=ctypes.c_float)

    def uGIMPBase(self, particle_pos, grid_min, h):
        return np.round((particle_pos - grid_min) / h).astype(int)

    def setData(self, force_data, scene_data, particle_data):
        #sum MPM particle stress
        N = np.prod(particle_data.particle_homogenization[0].resolution)
        self.sigma = np.zeros((N, 2, 2), dtype=ctypes.c_float)
        self.resolution = particle_data.particle_homogenization[0].resolution
        self.h = particle_data.particle_homogenization[0].h

        min_c = np.array([1e6, 1e6])
        max_c = -min_c
        for f in force_data.forces:
            min_c = np.minimum(min_c, f.position)
            max_c = np.maximum(max_c, f.position)
        _i = (min_c / self.h).astype(int)
        self.grid_start = self.h * _i

        for p, e in enumerate(particle_data.particle_homogenization):
            base = self.uGIMPBase(e.center_of_mass, self.grid_start, self.h)
            if base[0] >= self.resolution[0] or base[1] >= self.resolution[1] or base[0] < 0 or base[1] < 0:
                continue
            flat_idx = base[1] * self.resolution[0] + base[0]
            grid_pos = self.grid_start + (base.astype(float) + np.array([0.5, 0.5])) * self.h
            self.sigma[flat_idx] += e.sigma

        #plot MPM particle stress and DEM
        principal_stress = np.zeros((N, 2), dtype=ctypes.c_float)
        for i in range(N):
            l, Q = np.linalg.eig(self.sigma[i])

            if l[0] >= l[1]:
                principal_stress[i] = np.array([l[0], l[1]])
            else:
                principal_stress[i] = np.array([l[1], l[0]])

        X = principal_stress[:,1]
        df = pd.DataFrame(data={'stress': X})

        fig = px.histogram(df,x="stress")
        fig.show()



    def numLinesForDraw(self):
        n_grid_lines = 0
        n_cells = 0
        if self.resolution[0] > 0 and self.resolution[1] > 0:
            n_grid_lines = self.resolution[0] + 1 + self.resolution[1] + 1
            n_cells = self.resolution[0] * self.resolution[1]

        return n_grid_lines + n_cells * 2

    def computeGridVBOsForDraw(self, VBO):
        if self.resolution[0] <= 0 or self.resolution[1] <= 0:
            return
        e1 = np.array([1, 0]).transpose()
        e2 = np.array([0, 1]).transpose()

        for i in range(self.resolution[0] + 1):
            v0 = self.grid_start + self.h * i * e1
            v1 = v0 + self.h * self.resolution[1] * e2
            color = [0.3, 0.3, 0.3]
            VBO.registerLineToDataArray(v0, v1, color, color)

        for i in range(self.resolution[1] + 1):
            v0 = self.grid_start + self.h * i * e2
            v1 = v0 + self.h * self.resolution[0] * e1
            color = [0.3, 0.3, 0.3]
            VBO.registerLineToDataArray(v0, v1, color, color)

    def computeVBOsForDraw(self, VBO):
        if self.resolution[0] <= 0 or self.resolution[1] <= 0:
            return

        for j in range(self.resolution[1]):
            for i in range(self.resolution[0]):
                flat_idx = j * self.resolution[0] + i
                l, Q = np.linalg.eig(self.sigma[flat_idx])
                vc = self.grid_start + self.h * np.array([i + 0.5, j + 0.5])
                v0 = vc - 0.05 * math.sqrt(math.fabs(l[0])) * Q[:, 0]
                v1 = vc + 0.05 * math.sqrt(math.fabs(l[0])) * Q[:, 0]
                color = [232.0 / 255.0, 158.0 / 255.0, 46.0 / 255.0]
                if l[0] < 0.0:
                    color = [183.0 / 255.0, 40.0 / 255.0, 245.0 / 255.0]
                VBO.registerLineToDataArray(v0, v1, color, color)

                v2 = vc - 0.05 * math.sqrt(math.fabs(l[1])) * Q[:, 1]
                v3 = vc + 0.05 * math.sqrt(math.fabs(l[1])) * Q[:, 1]
                color = [232.0 / 255.0, 158.0 / 255.0, 46.0 / 255.0]
                if l[1] < 0.0:
                    color = [183.0 / 255.0, 40.0 / 255.0, 245.0 / 255.0]
                VBO.registerLineToDataArray(v2, v3, color, color)


class QTGLWidget2(QGLWidget):
    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(300, 300)
        self.data = SceneData()
        self.force_data = ForceData()
        self.homogenization_grid = PlotStressGrid()
        self.particle_data = ParticleHomogenizeData()
        self.data = SceneData()

        self.grains_VBO = LineVBO()
        self.discrete_forces_VBO = LineVBO()
        self.homogenization_VBO = LineVBO()
        self.grid_VBO = LineVBO()

        self.draw_grains = True
        self.draw_forces = True
        self.draw_stresses = True
        self.draw_grid = True

        self.height_reference = 540.0
        self.camera_x_pos = 0.0
        self.camera_y_pos = 0.0
        self.camera_zoom = 1.0
        self.extent = 1.0
        self.center = np.zeros(2)
        self.inner_width = 300
        self.inner_height = 300

    def numLinesForDrawingCircle(self):
        num_segs = 128
        return 1 + num_segs

    def computeVBOsForDrawingCircle(self, VBO, center, radius, angle, isStatic):
        num_segs = 128

        color = [0.6, 0.6, 0.6]
        if isStatic:
            color = [0.9, 0.9, 0.9]

        v0 = [center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle)]
        v1 = [center[0] - radius * math.cos(angle), center[1] - radius * math.sin(angle)]

        VBO.registerLineToDataArray(v0, v1, color, color)

        for i in range(num_segs):
            t0 = angle + i * 2.0 * math.pi / num_segs
            t1 = angle + (i + 1) * 2.0 * math.pi / num_segs
            v0 = [center[0] + radius * math.cos(t0), center[1] + radius * math.sin(t0)]
            v1 = [center[0] + radius * math.cos(t1), center[1] + radius * math.sin(t1)]

            VBO.registerLineToDataArray(v0, v1, color, color)

    def computeCircleBB(self, center, radius):
        v_min = center - radius
        v_max = center + radius
        return v_min, v_max

    def numLinesForDrawingPolygon(self, vertex_list):
        return vertex_list.shape[1]

    def computeVBOsForDrawingPolygon(self, VBO, center, size_ratio, vertex_list, angle, isStatic):
        rot_mat = np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])
        num_vertices = vertex_list.shape[1]

        color = [0.6, 0.6, 0.6]
        if isStatic:
            color = [0.9, 0.9, 0.9]

        for i in range(num_vertices):
            ip = (i + 1) % num_vertices
            v0 = (center + size_ratio * rot_mat @ vertex_list[:, i]).flatten()
            v1 = (center + size_ratio * rot_mat @ vertex_list[:, ip]).flatten()
            VBO.registerLineToDataArray(v0, v1, color, color)

    def computePolygonBB(self, center, size_ratio, vertex_list, angle):
        v_min = center
        v_max = center

        rot_mat = np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])
        num_vertices = vertex_list.shape[1]

        for i in range(num_vertices):
            v = (center + size_ratio * rot_mat @ vertex_list[:, i])
            v_min = np.minimum(v_min, v)
            v_max = np.maximum(v_max, v)

        return v_min, v_max

    def numLinesForDrawingDiscreteForces(self):
        return 2 * len(self.force_data.forces)

    def computeVBOsForDrawingDiscreteForces(self, VBO):
        num_forces = len(self.force_data.forces)

        for i in range(num_forces):
            v0 = self.force_data.forces[i].position
            v1 = v0 - self.force_data.forces[i].arm
            color = [44.0 / 255.0, 0.0, 240.0 / 255.0]
            VBO.registerLineToDataArray(v1, v0, color, color)
            v1 = v0 + self.force_data.forces[i].force * 0.01
            color = [240.0 / 255.0, 148.0 / 255.0, 72.0 / 255.0]
            VBO.registerLineToDataArray(v0, v1, color, color)

    def drawElementsVBO(self):
        if self.draw_grains:
            self.grains_VBO.drawVBO(3.0)

        if self.draw_forces:
            self.discrete_forces_VBO.drawVBO(3.0)

        if self.draw_stresses:
            self.homogenization_VBO.drawVBO(3.0)

        if self.draw_grid:
            self.grid_VBO.drawVBO(3.0)

    def pre_display(self):
        half_width = self.computeHalfWidth(self.inner_width)
        half_height = self.computeHalfHeight(self.inner_height)

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

        # self.drawElements()
        self.drawElementsVBO()

        glFlush()

    def resizeGL(self, w, h):
        self.inner_width = w
        self.inner_height = h

    def initializeGL(self):
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClearDepth(1.0)

    def computeHalfWidth(self, w):
        return self.camera_zoom * w / self.height_reference

    def computeHalfHeight(self, h):
        return self.camera_zoom * h / self.height_reference

    def buildVBO(self):
        num_lines_grains = 0
        for e in self.data.elements:
            vertex_list_e = self.data.templates[e.template_name].vertex_list
            num_vertices_shape = vertex_list_e.shape[1]
            if num_vertices_shape < 3:
                num_lines_grains += self.numLinesForDrawingCircle()
            else:
                num_lines_grains += self.numLinesForDrawingPolygon(self.data.templates[e.template_name].vertex_list)

        self.grains_VBO.setNumElements(num_lines_grains)
        self.discrete_forces_VBO.setNumElements(self.numLinesForDrawingDiscreteForces())
        self.homogenization_VBO.setNumElements(self.homogenization_grid.numLinesForDraw())
        self.grid_VBO.setNumElements(self.homogenization_grid.numLinesForDraw())

        for e in self.data.elements:
            vertex_list_e = self.data.templates[e.template_name].vertex_list
            num_vertices = vertex_list_e.shape[1]
            if num_vertices < 3:
                self.computeVBOsForDrawingCircle(self.grains_VBO, e.center_of_mass,
                                                 e.size_ratio * 0.5 * self.data.templates[e.template_name].size_mean,
                                                 e.rotation_angle, e.static)
            else:
                self.computeVBOsForDrawingPolygon(self.grains_VBO, e.center_of_mass, e.size_ratio,
                                                  self.data.templates[e.template_name].vertex_list, e.rotation_angle,
                                                  e.static)

        self.computeVBOsForDrawingDiscreteForces(self.discrete_forces_VBO)
        self.homogenization_grid.computeVBOsForDraw(self.homogenization_VBO)
        self.homogenization_grid.computeGridVBOsForDraw(self.grid_VBO)

        self.grains_VBO.genBuffers()
        self.discrete_forces_VBO.genBuffers()
        self.homogenization_VBO.genBuffers()
        self.grid_VBO.genBuffers()

    def autoAdjustView(self):
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
                _v_min, _v_max = self.computeCircleBB(e.center_of_mass, e.size_ratio * 0.5 * self.data.templates[
                    e.template_name].size_mean)
                v_min = np.minimum(v_min, _v_min)
                v_max = np.maximum(v_max, _v_max)
            else:
                _v_min, _v_max = self.computePolygonBB(e.center_of_mass, e.size_ratio,
                                                       self.data.templates[e.template_name].vertex_list,
                                                       e.rotation_angle)
                v_min = np.minimum(v_min, _v_min)
                v_max = np.maximum(v_max, _v_max)

        if num_non_static_objects == 0:
            return

        self.extent = np.amax(v_max - v_min)
        self.center = (v_max + v_min) * 0.5

    def setData(self, force_data, scene_data, particle_data):
        self.force_data = copy.deepcopy(force_data)
        self.data = copy.deepcopy(scene_data)
        self.particle_data = copy.deepcopy(particle_data)
        self.homogenization_grid.setData(self.force_data, self.data, self.particle_data)
        self.autoAdjustView()
        self.buildVBO()
        self.updateGL()

    def updateHomogenization(self, force_data, scene_data, particle_data):
        self.force_data = copy.deepcopy(force_data)
        self.data = copy.deepcopy(scene_data)
        self.particle_data = copy.deepcopy(particle_data)
        self.homogenization_grid.setData(self.force_data, self.data, self.particle_data)
        self.homogenization_VBO.setNumElements(self.homogenization_grid.numLinesForDraw())
        self.homogenization_grid.computeVBOsForDraw(self.homogenization_VBO)
        self.homogenization_VBO.genBuffers()
        self.updateGL()

    def setViewinfo(self, xpos, ypos, zoom):
        self.camera_x_pos = 2.0 * xpos - 1.0
        self.camera_y_pos = 2.0 * ypos - 1.0
        self.camera_zoom = zoom
        self.updateGL()

    def toggleDraw(self, draw_grains, draw_forces, draw_stresses, draw_grid):
        self.draw_grains = draw_grains
        self.draw_forces = draw_forces
        self.draw_stresses = draw_stresses
        self.draw_grid = draw_grid
        self.updateGL()


class Ui_Widget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.data = SceneData()
        self.force_data = ForceData()
        self.homogenization_data = HomogenizeData()
        self.homogenization_stress_data = AllHomogenizeData()
        self.force_data = AllForceData()
        self.scene_data = AllSceneData()
        self.MPMParticles = AllParticleHomogenizeData()
        self.p_fn = ""
        self.f_fn = ""
        self.t_fn = ""

        self.camera_y_pos_label = QtWidgets.QLabel()
        self.camera_y_pos_label.setText('cp: ')
        self.camera_y_pos_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Vertical)
        self.camera_y_pos_slider.setMinimum(0)
        self.camera_y_pos_slider.setMaximum(100)
        self.camera_y_pos_slider.setValue(50)
        self.camera_y_pos_slider.valueChanged.connect(self.updateView)

        camera_y_pos_box = QtWidgets.QVBoxLayout()
        camera_y_pos_box.addWidget(self.camera_y_pos_label)
        camera_y_pos_box.addWidget(self.camera_y_pos_slider)

        self.gl = QTGLWidget2(self)

        cy_gl_box = QtWidgets.QHBoxLayout()
        cy_gl_box.addLayout(camera_y_pos_box)
        cy_gl_box.addWidget(self.gl)

        self.camera_x_pos_label = QtWidgets.QLabel()
        self.camera_x_pos_label.setText('camera pos: ')
        self.camera_x_pos_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.camera_x_pos_slider.setMinimum(0)
        self.camera_x_pos_slider.setMaximum(100)
        self.camera_x_pos_slider.setValue(50)
        self.camera_x_pos_slider.valueChanged.connect(self.updateView)

        camera_x_pos_box = QtWidgets.QHBoxLayout()
        camera_x_pos_box.addWidget(self.camera_x_pos_label)
        camera_x_pos_box.addWidget(self.camera_x_pos_slider)

        self.camera_zoom_label = QtWidgets.QLabel()
        self.camera_zoom_label.setText('camera zoom: ')
        self.camera_zoom_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.camera_zoom_slider.setMinimum(0)
        self.camera_zoom_slider.setMaximum(100)
        self.camera_zoom_slider.setValue(50)
        self.camera_zoom_slider.valueChanged.connect(self.updateView)

        camera_zoom_box = QtWidgets.QHBoxLayout()
        camera_zoom_box.addWidget(self.camera_zoom_label)
        camera_zoom_box.addWidget(self.camera_zoom_slider)

        self.grains_check_box = QtWidgets.QCheckBox("Grains")
        self.forces_check_box = QtWidgets.QCheckBox("Forces")
        self.stresses_check_box = QtWidgets.QCheckBox("Stresses")
        self.grid_check_box = QtWidgets.QCheckBox("Grid")
        self.grains_check_box.setChecked(True)
        self.forces_check_box.setChecked(True)
        self.stresses_check_box.setChecked(True)
        self.grid_check_box.setChecked(True)
        self.grains_check_box.stateChanged.connect(self.checkBoxChanged)
        self.forces_check_box.stateChanged.connect(self.checkBoxChanged)
        self.stresses_check_box.stateChanged.connect(self.checkBoxChanged)
        self.grid_check_box.stateChanged.connect(self.checkBoxChanged)

        checkboxes = QtWidgets.QHBoxLayout()
        checkboxes.addWidget(self.grains_check_box)
        checkboxes.addWidget(self.forces_check_box)
        checkboxes.addWidget(self.stresses_check_box)
        checkboxes.addWidget(self.grid_check_box)

        self.homogenization_x_offset_label = QtWidgets.QLabel()
        self.homogenization_x_offset_label.setText('hom. x offset: ')
        self.homogenization_x_offset_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.homogenization_x_offset_slider.setMinimum(0)
        self.homogenization_x_offset_slider.setMaximum(100)
        self.homogenization_x_offset_slider.setValue(0)
        self.homogenization_x_offset_slider.valueChanged.connect(self.updateLabels)

        homogenization_x_offset_box = QtWidgets.QHBoxLayout()
        homogenization_x_offset_box.addWidget(self.homogenization_x_offset_label)
        homogenization_x_offset_box.addWidget(self.homogenization_x_offset_slider)

        self.homogenization_y_offset_label = QtWidgets.QLabel()
        self.homogenization_y_offset_label.setText('hom. y offset: ')
        self.homogenization_y_offset_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.homogenization_y_offset_slider.setMinimum(0)
        self.homogenization_y_offset_slider.setMaximum(100)
        self.homogenization_y_offset_slider.setValue(0)
        self.homogenization_y_offset_slider.valueChanged.connect(self.updateLabels)

        homogenization_y_offset_box = QtWidgets.QHBoxLayout()
        homogenization_y_offset_box.addWidget(self.homogenization_y_offset_label)
        homogenization_y_offset_box.addWidget(self.homogenization_y_offset_slider)

        self.homogenization_h_label = QtWidgets.QLabel()
        self.homogenization_h_label.setText('hom. h: ')
        self.homogenization_h_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.homogenization_h_slider.setMinimum(0)
        self.homogenization_h_slider.setMaximum(100)
        self.homogenization_h_slider.setValue(50)
        self.homogenization_h_slider.valueChanged.connect(self.updateLabels)

        homogenization_h_box = QtWidgets.QHBoxLayout()
        homogenization_h_box.addWidget(self.homogenization_h_label)
        homogenization_h_box.addWidget(self.homogenization_h_slider)

        self.timestep_idx_label = QtWidgets.QLabel()
        self.timestep_idx_label.setText('Timestep idx: ')
        self.timestep_idx_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.timestep_idx_slider.setMinimum(0)
        self.timestep_idx_slider.setMaximum(100)
        self.timestep_idx_slider.setValue(1)
        self.timestep_idx_slider.valueChanged.connect(self.updateLabels)

        timestep_idx_box = QtWidgets.QHBoxLayout()
        timestep_idx_box.addWidget(self.timestep_idx_label)
        timestep_idx_box.addWidget(self.timestep_idx_slider)

        homogenization_btn = QtWidgets.QPushButton('Update homogenization', self)
        homogenization_btn.clicked.connect(self.update_homogenization)
        homogenization_box = QtWidgets.QHBoxLayout()
        homogenization_box.addWidget(homogenization_btn)

        load_btn = QtWidgets.QPushButton('Load', self)
        load_btn.clicked.connect(self.load)
        load_box = QtWidgets.QHBoxLayout()
        load_box.addWidget(load_btn)

        save_btn = QtWidgets.QPushButton('Save', self)
        save_btn.clicked.connect(self.save)
        save_box = QtWidgets.QHBoxLayout()
        save_box.addWidget(save_btn)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(cy_gl_box)
        vbox.addLayout(camera_x_pos_box)
        vbox.addLayout(camera_zoom_box)
        vbox.addLayout(checkboxes)
        vbox.addLayout(homogenization_x_offset_box)
        vbox.addLayout(homogenization_y_offset_box)
        vbox.addLayout(homogenization_h_box)
        vbox.addLayout(timestep_idx_box)
        vbox.addLayout(homogenization_box)
        vbox.addLayout(load_box)
        vbox.addLayout(save_box)

        self.setLayout(vbox)

        self.resize(300, 350)

    def updateLabels(self):
        offset_ratio = np.zeros(2)
        h = 0.08 * self.homogenization_h_slider.value() / 100.0
        offset_ratio[0] = self.homogenization_x_offset_slider.value() / 100.0
        offset_ratio[1] = self.homogenization_y_offset_slider.value() / 100.0
        dt_idx = int(self.timestep_idx_slider.value())
        self.homogenization_h_label.setText('hom. h: %.3f' % h)
        self.homogenization_x_offset_label.setText('hom. x offset: %.3f' % offset_ratio[0])
        self.homogenization_y_offset_label.setText('hom. y offset: %.3f' % offset_ratio[1])
        self.timestep_idx_label.setText('dt: %d' % dt_idx)
    def updateView(self):
        xpos = self.camera_x_pos_slider.value() / 100.0
        ypos = self.camera_y_pos_slider.value() / 100.0
        side_mag_level = 5  # 2^5 = 32x magnification
        zoom_level = math.pow(2.0, (self.camera_zoom_slider.value() - 50.0) * side_mag_level / 50.0)
        self.gl.setViewinfo(xpos, ypos, zoom_level)

    def checkBoxChanged(self, state):
        self.gl.toggleDraw(self.grains_check_box.isChecked(), self.forces_check_box.isChecked(),
                           self.stresses_check_box.isChecked(), self.grid_check_box.isChecked())

    def update_homogenization(self):
        offset_ratio = np.zeros(2)
        h = 0.08 * self.homogenization_h_slider.value() / 100.0
        offset_ratio[0] = self.homogenization_x_offset_slider.value() / 100.0
        offset_ratio[1] = self.homogenization_y_offset_slider.value() / 100.0
        dt_idx = int(self.timestep_idx_slider.value())
        self.force_data.load_from_idx(self.f_fn, dt_idx + 1)
        self.scene_data.load_from_idx(self.t_fn, self.f_fn, dt_idx)
        self.MPMParticles.load_from_idx(self.p_fn, dt_idx)
        self.gl.updateHomogenization(self.force_data.all_step_ForceData[0], self.scene_data.all_step_elements[0], self.MPMParticles.all_step_particle_homogenization[0])

    def load(self):
        #(self.t_fn, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(self, "Load templates", os.path.expanduser('~'), "HDF5 (*.h5)")
        #(self.f_fn, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(self, "Load  all forces",os.path.expanduser('~'), "HDF5 (*.h5)")
        #(self.p_fn, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(self, "Load  homogenization stress", os.path.expanduser('~'), "HDF5 (*.h5)")
        self.t_fn = "/Users/naoto/PycharmProjects/GeneralizedHybridGrainsResearch/src/python/analysis/Save/square_merge_template.h5"
        self.f_fn = "/Users/naoto/PycharmProjects/GeneralizedHybridGrainsResearch/src/python/analysis/Save/serialized_forces.h5"
        self.p_fn = "/Users/naoto/PycharmProjects/GeneralizedHybridGrainsResearch/src/python/analysis/Save/serialized_sigma.h5"

        dt_idx = int(self.timestep_idx_slider.value())

        self.force_data.load_from_idx(self.f_fn, dt_idx + 1)
        self.scene_data.load_from_idx(self.t_fn, self.f_fn, dt_idx)
        self.MPMParticles.load_from_idx(self.p_fn, dt_idx)

        self.gl.setData(self.force_data.all_step_ForceData[0], self.scene_data.all_step_elements[0], self.MPMParticles.all_step_particle_homogenization[0])

    def save(self):
        (fileName, selectedFilter) = QtWidgets.QFileDialog.getSaveFileName(self, "Save file", os.path.expanduser('~'),
                                                                           "HDF5 (*.h5)")
        self.homogenization_data.save(fileName)


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_Widget()
    ui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()