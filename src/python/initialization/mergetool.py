# https://fereria.github.io/reincarnation_tech/11_PySide/01_PySide_Basic/00_Tutorial/08_widget_sample_04/

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtOpenGL import *
import math
import copy
import os
from grainh5 import *

class QTGLWidget2(QGLWidget):
    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(300, 300)
        self.data = SceneData()
        self.height_reference = 540.0
        self.camera_x_pos = 0.0
        self.camera_zoom = 1.0
        self.extent = 1.0
        self.inner_width = 300
        self.inner_height = 300

    def drawCircle(self, center, radius, angle, isStatic):
        num_segs = 128

        color = [0.0, 0.0, 0.0]
        if isStatic:
            color = [0.7, 0.7, 0.7]

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

    def pre_display(self):
        half_width = self.computeHalfWidth(self.inner_width)
        half_height = self.computeHalfHeight(self.inner_height)

        x_offset = self.camera_x_pos * self.extent

        glViewport(0, 0, self.inner_width, self.inner_height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(x_offset-half_width, x_offset+half_width, -half_height, half_height, -1.0, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.pre_display()

        self.drawElements()

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

    def setData(self, data):
        self.data = copy.deepcopy(data)
        self.extent = 1.0
        self.updateGL()

    def setViewinfo(self, xpos, zoom):
        self.camera_x_pos = xpos
        self.camera_zoom = zoom
        self.updateGL()

class Ui_Widget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.scene_data = SceneData()
        self.scene_dict = {}

        self.gl = QTGLWidget2(self)
        self.listView = QtWidgets.QListView()
        load_btn = QtWidgets.QPushButton('Load', self)
        delete_selected_btn = QtWidgets.QPushButton('Delete selected', self)
        merge_and_save_btn = QtWidgets.QPushButton('Save', self)

        h_btns_1 = QtWidgets.QHBoxLayout()
        h_btns_1.addWidget(load_btn)
        h_btns_1.addWidget(delete_selected_btn)

        h_btns_2 = QtWidgets.QHBoxLayout()
        h_btns_2.addWidget(merge_and_save_btn)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.gl)
        vbox.addLayout(h_btns_1)
        vbox.addWidget(self.listView)
        vbox.addLayout(h_btns_2)
        self.setLayout(vbox)
        self.resize(300, 350)

        self.gl.setData(self.scene_data)

        self.listViewModel = QtCore.QStringListModel()
        self.listViewModel.setStringList([])
        self.listView.setModel(self.listViewModel)
        self.listView.clicked.connect(self.listClicked)

        self.listViewSelected = ""

        load_btn.clicked.connect(self.load)
        delete_selected_btn.clicked.connect(self.delete_selected)
        merge_and_save_btn.clicked.connect(self.save)

    def listClicked(self, index):
        self.listViewSelected = index.data()

    def updateLiseView(self):
        stringList = []
        for nm in self.scene_dict:
            stringList.append(nm)

        self.listViewModel.setStringList(stringList)
        self.listView.setModel(self.listViewModel)

    def load(self):
        scene_data = SceneData()
        # template
        (path_to_template, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(self, "Load templates", os.path.expanduser('~'), "HDF5 (*.h5)" )
        # elements
        (path_to_elements, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(self, "Load elements", os.path.expanduser('~'), "HDF5 (*.h5)" )

        scene_data.load(path_to_template, path_to_elements)

        templates_fn = os.path.splitext(os.path.basename(path_to_template))[0]
        elements_fn = os.path.splitext(os.path.basename(path_to_elements))[0]

        self.scene_dict.update([(templates_fn+'-'+elements_fn, scene_data)])

        self.updateLiseView()
        self.merge()

    def delete_selected(self):
        self.scene_dict.pop(self.listViewSelected, None)
        self.updateLiseView()
        self.merge()

    def merge(self):
        self.scene_data.templates.clear()
        self.scene_data.elements.clear()

        for s in self.scene_dict:
            sd = self.scene_dict[s]
            self.scene_data.templates.update(sd.templates)
            self.scene_data.elements.extend(sd.elements)

        self.gl.setData(self.scene_data)

    def save(self):
        (fileName, selectedFilter) = QtWidgets.QFileDialog.getSaveFileName(self, "Save file", os.path.expanduser('~'), "HDF5 (*.h5)" )
        if fileName != "" and fileName[len(fileName)-3:] == ".h5":
            fileName_template = fileName[:len(fileName)-3] + "_template.h5"

            self.scene_data.save(fileName_template, fileName)

def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_Widget()
    ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
