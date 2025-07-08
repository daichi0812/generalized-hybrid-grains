#http://www.not-enough.org/abe/manual/program-aa08/pyqt1.html

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtOpenGL import *
import math
import copy
from homogenizationh5 import *
import plotly.graph_objects as go
import numpy as np

class LineVBO:
    def __init__(self):
        self.VBOData_vertices = np.zeros(2, dtype=ctypes.c_float)
        self.VBOData_colors = np.zeros(3, dtype=ctypes.c_float)
        self.VBOData_indices = np.zeros(2, dtype=ctypes.c_uint)
        self.VBO_buffers =[3]
        self.VBO_buffers[0] = None
        self.vertex_num_offset = 0
        self.color_num_offset = 0
        self.index_num_offset = 0

    def setNumElements(self, num_lines):
        self.VBOData_vertices = np.zeros(2*num_lines*2, dtype=ctypes.c_float)
        self.VBOData_colors = np.zeros(3*num_lines*2, dtype=ctypes.c_float)
        self.VBOData_indices = np.zeros(2*num_lines, dtype=ctypes.c_uint)
        self.vertex_num_offset = 0
        self.color_num_offset = 0
        self.index_num_offset = 0

    def genBuffers(self):
        self.VBO_buffers = glGenBuffers(3)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO_buffers[0])
        glBufferData(GL_ARRAY_BUFFER,
            len(self.VBOData_vertices)*4,  # byte size
            (ctypes.c_float*len(self.VBOData_vertices))(*self.VBOData_vertices),
            GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO_buffers[1])
        glBufferData(GL_ARRAY_BUFFER,
            len(self.VBOData_colors)*4, # byte size
            (ctypes.c_float*len(self.VBOData_colors))(*self.VBOData_colors),
            GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.VBO_buffers[2])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,
            len(self.VBOData_indices)*4, # byte size
            (ctypes.c_uint*len(self.VBOData_indices))(*self.VBOData_indices),
            GL_STATIC_DRAW)

    def drawVBO(self, line_width):
        glEnableClientState(GL_VERTEX_ARRAY);
        glEnableClientState(GL_COLOR_ARRAY);
        if self.VBO_buffers[0]!=None:
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
        self.VBOData_vertices[(self.vertex_num_offset*2):(self.vertex_num_offset*2+2)] = v0
        self.VBOData_colors[(self.color_num_offset*3):(self.color_num_offset*3+3)] = c0
        self.VBOData_vertices[((self.vertex_num_offset+1)*2):((self.vertex_num_offset+1)*2+2)] = v1
        self.VBOData_colors[((self.color_num_offset+1)*3):((self.color_num_offset+1)*3+3)] = c1

        self.VBOData_indices[self.index_num_offset*2] = self.vertex_num_offset
        self.VBOData_indices[self.index_num_offset*2+1] = self.vertex_num_offset+1

        self.vertex_num_offset += 2
        self.color_num_offset += 2
        self.index_num_offset += 1


class StressPlot:
    def __init__(self):
        self.grid_start = np.zeros(2, dtype=ctypes.c_float)
        self.h = 0.01
        self.resolution = np.zeros(2, dtype=ctypes.c_int)
        self.pre_sigma = np.zeros((1, 2, 2), dtype=ctypes.c_float)
        self.post_sigma = np.zeros((1, 2, 2), dtype=ctypes.c_float)
        self.pre_principal_stress = np.zeros((1, 2), dtype=ctypes.c_float)
        self.post_principal_stress = np.zeros((1, 2), dtype=ctypes.c_float)
    
    def setData(self, pre_homogenization_data, post_homogenization_data, fig):
        self.grid_start = post_homogenization_data.homogenization[0].grid_p
        self.h = post_homogenization_data.homogenization[0].h
        self.resolution = post_homogenization_data.homogenization[0].resolution
        N = np.prod(self.resolution)
        index_offset = pre_homogenization_data.homogenization[0].resolution[0]-self.resolution[0]
        self.pre_sigma = np.zeros((N, 2, 2), dtype=ctypes.c_float)
        self.post_sigma = np.zeros((N, 2, 2), dtype=ctypes.c_float)
        
        for j in range(self.resolution[1]):
            for i in range(self.resolution[0]):
                flat_idx = j * self.resolution[0] + i
                self.pre_sigma[flat_idx] = pre_homogenization_data.homogenization[flat_idx+index_offset*j].sigma
                self.post_sigma[flat_idx] = post_homogenization_data.homogenization[flat_idx].sigma

        self.pre_principal_stress = np.zeros((N, 2), dtype=ctypes.c_float)
        self.post_principal_stress = np.zeros((N, 2), dtype=ctypes.c_float)

        for j in range(self.resolution[1]):
            for i in range(self.resolution[0]):
                flat_idx = j * self.resolution[0] + i
                if (np.isnan(self.post_sigma[flat_idx])).any() == True:
                    continue
                else :
                    pre_l, pre_Q = np.linalg.eig(self.pre_sigma[flat_idx])
                    post_l, post_Q = np.linalg.eig(self.post_sigma[flat_idx])
                    if pre_l[0]>=pre_l[1]:
                        self.pre_principal_stress[flat_idx]=np.array([pre_l[0],pre_l[1]])
                    else :
                        self.pre_principal_stress[flat_idx]=np.array([pre_l[1],pre_l[0]])
                    
                    if post_l[0]>=post_l[1]:
                        self.post_principal_stress[flat_idx]=np.array([post_l[0],post_l[1]])
                    else :
                        self.post_principal_stress[flat_idx]=np.array([post_l[1],post_l[0]])
                    
                    xs = np.array([self.pre_principal_stress[flat_idx][0]
                    ,self.post_principal_stress[flat_idx][0]
                    ])
                    ys = np.array([self.pre_principal_stress[flat_idx][1]
                    ,self.post_principal_stress[flat_idx][1]
                    ])
                    colors = ['#4169E1',"#FF0000"]
                    fig.add_trace(go.Scatter(x=xs,y=ys, line=dict(width=0.5, color="#FFA500"), marker=dict(size=2.5,color=colors)))
        fig.update_layout(showlegend=False)
        
        fig.update_xaxes(title="s1")
        fig.update_yaxes(title="s2")
        fig.update_layout(title="Principal stress space")
        

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

class QTGLWidget2(QGLWidget):
    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(300, 300)
        self.pre_homogenization_data = HomogenizeData()
        self.post_homogenization_data = HomogenizeData()
        self.stress_plot = StressPlot()

        self.homogenization_VBO = LineVBO()
        self.grid_VBO=LineVBO()

        self.draw_stresses = True
        self.draw_grid=True

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
            ip = (i+1) % num_vertices
            v0 = (center + size_ratio * rot_mat @ vertex_list[:,i]).flatten()
            v1 = (center + size_ratio * rot_mat @ vertex_list[:,ip]).flatten()
            VBO.registerLineToDataArray(v0, v1, color, color)

    def computePolygonBB(self, center, size_ratio, vertex_list, angle):
        v_min = center
        v_max = center

        rot_mat = np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])
        num_vertices = vertex_list.shape[1]

        for i in range(num_vertices):
            v = (center + size_ratio * rot_mat @ vertex_list[:,i])
            v_min = np.minimum(v_min, v)
            v_max = np.maximum(v_max, v)

        return v_min, v_max



    def drawElementsVBO(self):

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
        glOrtho(self.center[0] + x_offset-half_width, self.center[0] + x_offset+half_width, self.center[1] + y_offset-half_height, self.center[1] + y_offset+half_height, -1.0, 100.0)
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
        self.homogenization_VBO.setNumElements(self.stress_plot.numLinesForDraw())
        self.grid_VBO.setNumElements(self.stress_plot.numLinesForDraw())
        
        self.stress_plot.computeGridVBOsForDraw(self.grid_VBO)

        self.homogenization_VBO.genBuffers()
        self.grid_VBO.genBuffers()


    def setData(self, pre_homogenization_data,post_homogenization_data):
        self.pre_homogenization_data = copy.deepcopy(pre_homogenization_data)
        self.post_homogenization_data = copy.deepcopy(post_homogenization_data)
        fig = go.Figure()
        self.stress_plot.setData(self.pre_homogenization_data,self.post_homogenization_data,fig)
        fig.show()
        self.buildVBO()
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
        self.draw_grid=draw_grid
        self.updateGL()

class Ui_Widget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.pre_homogenization_data = HomogenizeData()
        self.post_homogenization_data = HomogenizeData()

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


        load_btn = QtWidgets.QPushButton('Load', self)
        load_btn.clicked.connect(self.load)
        load_box = QtWidgets.QHBoxLayout()
        load_box.addWidget(load_btn)
        

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(cy_gl_box)
        vbox.addLayout(camera_x_pos_box)
        vbox.addLayout(camera_zoom_box)
        vbox.addLayout(checkboxes)
        vbox.addLayout(load_box)

        self.setLayout(vbox)

        self.resize(300, 350)

    def updateView(self):
        xpos = self.camera_x_pos_slider.value() / 100.0
        ypos = self.camera_y_pos_slider.value() / 100.0
        side_mag_level = 5 # 2^5 = 32x magnification
        zoom_level = math.pow(2.0, ( self.camera_zoom_slider.value() - 50.0 ) * side_mag_level / 50.0 )
        self.gl.setViewinfo(xpos, ypos, zoom_level)

    def checkBoxChanged(self, state):
        self.gl.toggleDraw(self.grains_check_box.isChecked(), self.forces_check_box.isChecked(), self.stresses_check_box.isChecked(),self.grid_check_box.isChecked())


    def load(self):
        # stress deta
        (h_fn1, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(self, "Load homogenize data before plastic flow", os.path.expanduser('~'), "HDF5 (*.h5)" )
        (h_fn2, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(self, "Load homogenize data after plastic flow", os.path.expanduser('~'), "HDF5 (*.h5)" )
        #h_fn1="/Users/naoto/CG/AGRigidBody2D-master/AGRigidBody2D-master/rigidbody2dsim/build/Save_Force/homogenize_data.h5"
        #h_fn2="/Users/naoto/CG/AGRigidBody2D-master/AGRigidBody2D-master/rigidbody2dsim/build/Save_Force/homogenize_data2.h5"
        self.pre_homogenization_data.load(h_fn1)
        self.post_homogenization_data.load(h_fn2)
        self.gl.setData(self.pre_homogenization_data, self.post_homogenization_data)
        
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_Widget()
    ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()