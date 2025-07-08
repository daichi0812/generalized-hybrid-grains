#http://www.not-enough.org/abe/manual/program-aa08/pyqt1.html

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtOpenGL import *
import math
import copy
import random
from grainh5 import *

class QTGLWidget2(QGLWidget):
    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(300, 300)
        self.data = SceneData()
        self.height_reference = 540.0
        self.camera_x_pos = 0.0
        self.camera_y_pos = 0.0
        self.camera_zoom = 1.0
        self.extent = 1.0
        self.inner_width = 300
        self.inner_height = 300
        self.VBOData_vertices = np.zeros(2, dtype=ctypes.c_float)
        self.VBOData_colors = np.zeros(3, dtype=ctypes.c_float)
        self.VBOData_indices = np.zeros(2, dtype=ctypes.c_uint)

        self.VBO_buffers = None

    def registerLineToDataArray(self, v0, v1, c0, c1, vertex_data_array, color_data_array, index_data_array, vertex_num_offset, color_num_offset, index_num_offset):
        vertex_data_array[(vertex_num_offset*2):(vertex_num_offset*2+2)] = v0
        color_data_array[(color_num_offset*3):(color_num_offset*3+3)] = c0
        vertex_data_array[((vertex_num_offset+1)*2):((vertex_num_offset+1)*2+2)] = v1
        color_data_array[((color_num_offset+1)*3):((color_num_offset+1)*3+3)] = c1

        index_data_array[index_num_offset*2] = vertex_num_offset
        index_data_array[index_num_offset*2+1] = vertex_num_offset+1

        return vertex_num_offset + 2, color_num_offset + 2, index_num_offset + 1

    def numVerticesElementsForDrawCircle(self):
        num_segs = 128
        num_vertices = 2 + 2 * num_segs
        num_elements = 1 + num_segs
        return num_vertices, num_elements

    def computeVBOsForDrawCircle(self, vertex_data_array, color_data_array, index_data_array, vertex_num_offset, color_num_offset, index_num_offset, center, radius, angle, isStatic):
        num_segs = 128

        color = [0.0, 0.0, 0.0]
        if isStatic:
            color = [0.7, 0.7, 0.7]

        vn_offset = vertex_num_offset
        cn_offset = color_num_offset
        in_offset = index_num_offset

        v0 = [center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle)]
        v1 = [center[0] - radius * math.cos(angle), center[1] - radius * math.sin(angle)]

        vn_offset, cn_offset, in_offset = self.registerLineToDataArray(v0, v1, color, color, vertex_data_array, color_data_array, index_data_array, vn_offset, cn_offset, in_offset)

        for i in range(num_segs):
            t0 = angle + i * 2.0 * math.pi / num_segs
            t1 = angle + (i + 1) * 2.0 * math.pi / num_segs
            v0 = [center[0] + radius * math.cos(t0), center[1] + radius * math.sin(t0)]
            v1 = [center[0] + radius * math.cos(t1), center[1] + radius * math.sin(t1)]

            vn_offset, cn_offset, in_offset = self.registerLineToDataArray(v0, v1, color, color, vertex_data_array, color_data_array, index_data_array, vn_offset, cn_offset, in_offset)

        return vn_offset, cn_offset, in_offset

    def drawCircle(self, center, radius, angle, isStatic):
        num_segs = 128

        color = [0.0, 0.0, 0.0]
        if isStatic:
            color = [0.7, 0.7, 0.7]

        glColor(color)
        glBegin(GL_LINES)
        glVertex2d(center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle))
        glVertex2d(center[0] - radius * math.cos(angle), center[1] - radius * math.sin(angle))
        glEnd()

        glLineWidth(3.0)
        glColor(color)
        glBegin(GL_LINE_LOOP)
        for i in range(num_segs):
            t0 = angle + i * 2.0 * math.pi / num_segs
            glVertex2d(center[0] + radius * math.cos(t0), center[1] + radius * math.sin(t0))
        glEnd()

    def numVerticesElementsForDrawPolygon(self, vertex_list):
        num_vertices = 2 * vertex_list.shape[1]
        num_elements = num_vertices
        return num_vertices, num_elements

    def computeVBOsForDrawPolygon(self, vertex_data_array, color_data_array, index_data_array, vertex_num_offset, color_num_offset, index_num_offset, center, size_ratio, vertex_list, angle, isStatic):
        rot_mat = np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])
        num_vertices = vertex_list.shape[1]

        color = [0.0, 0.0, 0.0]
        if isStatic:
            color = [0.7, 0.7, 0.7]

        vn_offset = vertex_num_offset
        cn_offset = color_num_offset
        in_offset = index_num_offset

        for i in range(num_vertices):
            ip = (i+1) % num_vertices
            v0 = (center + size_ratio * rot_mat @ vertex_list[:,i]).flatten()
            v1 = (center + size_ratio * rot_mat @ vertex_list[:,ip]).flatten()
            vn_offset, cn_offset, in_offset = self.registerLineToDataArray(v0, v1, color, color, vertex_data_array, color_data_array, index_data_array, vn_offset, cn_offset, in_offset)

        return vn_offset, cn_offset, in_offset

    def drawPolygon(self, center, size_ratio, vertex_list, angle, isStatic):
        rot_mat = np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])
        num_vertices = vertex_list.shape[1]

        color = [0.0, 0.0, 0.0]
        if isStatic:
            color = [0.7, 0.7, 0.7]

        glLineWidth(3.0)
        glColor(color)
        glBegin(GL_LINE_LOOP)
        for i in range(num_vertices):
            v = center + size_ratio * rot_mat @ vertex_list[:,i]
            glVertex(v)
        glEnd()

    def drawElements(self):
        for e in self.data.elements:
            vertex_list_e = self.data.templates[e.template_name].vertex_list
            num_vertices = vertex_list_e.shape[1]
            if num_vertices < 3:
                self.drawCircle(e.center_of_mass, e.size_ratio * 0.5 * self.data.templates[e.template_name].size_mean, e.rotation_angle, e.static)
            else:
                self.drawPolygon(e.center_of_mass, e.size_ratio, self.data.templates[e.template_name].vertex_list, e.rotation_angle, e.static)

    def drawElementsVBO(self):
        glEnableClientState(GL_VERTEX_ARRAY);
        glEnableClientState(GL_COLOR_ARRAY);
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO_buffers[0]);
        glVertexPointer(2, GL_FLOAT, 0, None);
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO_buffers[1]);
        glColorPointer(3, GL_FLOAT, 0, None);
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.VBO_buffers[2]);
        glLineWidth(3.0)
        glDrawElements(GL_LINES, self.VBOData_indices.shape[0], GL_UNSIGNED_INT, None);
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY);

    def pre_display(self):
        half_width = self.computeHalfWidth(self.inner_width)
        half_height = self.computeHalfHeight(self.inner_height)

        x_offset = self.camera_x_pos * self.extent
        y_offset = self.camera_y_pos * self.extent

        glViewport(0, 0, self.inner_width, self.inner_height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(x_offset-half_width, x_offset+half_width, y_offset-half_height, y_offset+half_height, -1.0, 100.0)
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
        num_vertices = 0
        num_lines = 0
        for e in self.data.elements:
            vertex_list_e = self.data.templates[e.template_name].vertex_list
            num_vertices_shape = vertex_list_e.shape[1]
            if num_vertices_shape < 3:
                _nv, _nl = self.numVerticesElementsForDrawCircle()
                num_vertices += _nv
                num_lines += _nl
            else:
                _nv, _nl = self.numVerticesElementsForDrawPolygon(self.data.templates[e.template_name].vertex_list)
                num_vertices += _nv
                num_lines += _nl

        self.VBOData_vertices = np.zeros(2*num_vertices, dtype=ctypes.c_float)
        self.VBOData_colors = np.zeros(3*num_vertices, dtype=ctypes.c_float)
        self.VBOData_indices = np.zeros(2*num_lines, dtype=ctypes.c_uint)

        v_offset = 0
        c_offset = 0
        i_offset = 0

        for e in self.data.elements:
            vertex_list_e = self.data.templates[e.template_name].vertex_list
            num_vertices = vertex_list_e.shape[1]
            if num_vertices < 3:
                v_offset, c_offset, i_offset = self.computeVBOsForDrawCircle(self.VBOData_vertices, self.VBOData_colors, self.VBOData_indices, v_offset, c_offset, i_offset, e.center_of_mass, e.size_ratio * 0.5 * self.data.templates[e.template_name].size_mean, e.rotation_angle, e.static)
            else:
                v_offset, c_offset, i_offset = self.computeVBOsForDrawPolygon(self.VBOData_vertices, self.VBOData_colors, self.VBOData_indices, v_offset, c_offset, i_offset, e.center_of_mass, e.size_ratio, self.data.templates[e.template_name].vertex_list, e.rotation_angle, e.static)

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

    def setData(self, data):
        self.data = copy.deepcopy(data)
        self.extent = 1.0
        self.buildVBO()
        self.updateGL()

    def setViewinfo(self, xpos, ypos, zoom):
        self.camera_x_pos = xpos
        self.camera_y_pos = ypos
        self.camera_zoom = zoom
        self.updateGL()

class Ui_Widget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.scene_data = SceneData()

        self.camera_y_pos_label = QtWidgets.QLabel()
        self.camera_y_pos_label.setText('cp: ')
        self.camera_y_pos_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Vertical)
        self.camera_y_pos_slider.setMinimum(0)
        self.camera_y_pos_slider.setMaximum(100)
        self.camera_y_pos_slider.setValue(0)
        self.camera_y_pos_slider.valueChanged.connect(self.updateView)

        camera_y_pos_box = QtWidgets.QVBoxLayout()
        camera_y_pos_box.addWidget(self.camera_y_pos_label)
        camera_y_pos_box.addWidget(self.camera_y_pos_slider)

        self.gl = QTGLWidget2(self)
        self.gl.setData(self.scene_data)

        cy_gl_box = QtWidgets.QHBoxLayout()
        cy_gl_box.addLayout(camera_y_pos_box)
        cy_gl_box.addWidget(self.gl)

        self.camera_x_pos_label = QtWidgets.QLabel()
        self.camera_x_pos_label.setText('camera pos: ')
        self.camera_x_pos_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.camera_x_pos_slider.setMinimum(0)
        self.camera_x_pos_slider.setMaximum(100)
        self.camera_x_pos_slider.setValue(0)
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

        load_btn = QtWidgets.QPushButton('Load', self)
        load_btn.clicked.connect(self.load)
        #save_btn = QtWidgets.QPushButton('Save file', self)
        #save_btn.clicked.connect(self.save) #QtWidgets.qApp.quit

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(load_btn)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(cy_gl_box)
        vbox.addLayout(camera_x_pos_box)
        vbox.addLayout(camera_zoom_box)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.resize(300, 350)

    def updateView(self):
        xpos = self.camera_x_pos_slider.value() / 100.0
        ypos = self.camera_y_pos_slider.value() / 100.0
        side_mag_level = 5 # 2^5 = 32x magnification
        zoom_level = math.pow(2.0, ( self.camera_zoom_slider.value() - 50.0 ) * side_mag_level / 50.0 )
        self.gl.setViewinfo(xpos, ypos, zoom_level)

    def load(self):
        # template
        (template_fn, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(self, "Load templates", os.path.expanduser('~'), "HDF5 (*.h5)" )

        # elements
        (element_fn, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(self, "Load elements", os.path.expanduser('~'), "HDF5 (*.h5)" )

        self.scene_data.load(template_fn, element_fn)
        self.gl.setData(self.scene_data)

def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_Widget()
    ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
