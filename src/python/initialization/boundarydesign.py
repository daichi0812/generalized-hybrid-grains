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
        self.floor_extent = [0.0, 7.0]

        leftwall_template = ShapeTemplate()
        leftwall_template.density = 1000.0
        leftwall_template.size_mean = 0.25
        leftwall_template.size_std = 0.0
        leftwall_template.vertex_list = np.array([[-0.05, -0.2], [0.05, -0.2], [0.05, 0.2], [-0.05, 0.2]]).transpose()

        self.scene_data.templates.update([('left_wall', leftwall_template)])

        rightwall_template = ShapeTemplate()
        rightwall_template.density = 1000.0
        rightwall_template.size_mean = 0.25
        rightwall_template.size_std = 0.0
        rightwall_template.vertex_list = np.array([[-0.05, -0.2], [0.05, -0.2], [0.05, 0.2], [-0.05, 0.2]]).transpose()

        self.scene_data.templates.update([('right_wall', rightwall_template)])

        leftwall_element = Element()
        leftwall_element.template_name = "left_wall"
        leftwall_element.size_ratio = 1.0
        leftwall_element.center_of_mass = np.array([-0.05, 0.2]).transpose()
        leftwall_element.rotation_angle = 0.0
        leftwall_element.velocity = np.array([0.0, 0.0]).transpose()
        leftwall_element.angular_velocity = 0.0
        leftwall_element.static = True

        self.scene_data.elements.append(leftwall_element)

        rightwall_element = Element()
        rightwall_element.template_name = "right_wall"
        rightwall_element.size_ratio = 1.0
        rightwall_element.center_of_mass = np.array([7.05, 0.2]).transpose()
        rightwall_element.rotation_angle = 0.0
        rightwall_element.velocity = np.array([0.0, 0.0]).transpose()
        rightwall_element.angular_velocity = 0.0
        rightwall_element.static = True

        self.scene_data.elements.append(rightwall_element)

        self.gl = QTGLWidget2(self)
        self.gl.setData(self.scene_data)

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

        # left wall
        self.leftwall_width_label = QtWidgets.QLabel()
        self.leftwall_width_label.setText('width: ')
        self.leftwall_width_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.leftwall_width_slider.setMinimum(0)
        self.leftwall_width_slider.setMaximum(100)
        self.leftwall_width_slider.setValue(100)
        self.leftwall_width_slider.valueChanged.connect(self.updateWall)

        self.leftwall_height_label = QtWidgets.QLabel()
        self.leftwall_height_label.setText('height: ')
        self.leftwall_height_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.leftwall_height_slider.setMinimum(0)
        self.leftwall_height_slider.setMaximum(400)
        self.leftwall_height_slider.setValue(80)
        self.leftwall_height_slider.valueChanged.connect(self.updateWall)

        self.leftwall_right_label = QtWidgets.QLabel()
        self.leftwall_right_label.setText('right: ')
        self.leftwall_right_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.leftwall_right_slider.setMinimum(0)
        self.leftwall_right_slider.setMaximum(100)
        self.leftwall_right_slider.setValue(0)
        self.leftwall_right_slider.valueChanged.connect(self.updateWall)

        self.leftwall_bottom_label = QtWidgets.QLabel()
        self.leftwall_bottom_label.setText('bottom: ')
        self.leftwall_bottom_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.leftwall_bottom_slider.setMinimum(0)
        self.leftwall_bottom_slider.setMaximum(100)
        self.leftwall_bottom_slider.setValue(50)
        self.leftwall_bottom_slider.valueChanged.connect(self.updateWall)

        leftwall_width_box = QtWidgets.QHBoxLayout()
        leftwall_width_box.addWidget(self.leftwall_width_label)
        leftwall_width_box.addWidget(self.leftwall_width_slider)

        leftwall_height_box = QtWidgets.QHBoxLayout()
        leftwall_height_box.addWidget(self.leftwall_height_label)
        leftwall_height_box.addWidget(self.leftwall_height_slider)

        leftwall_right_box = QtWidgets.QHBoxLayout()
        leftwall_right_box.addWidget(self.leftwall_right_label)
        leftwall_right_box.addWidget(self.leftwall_right_slider)

        leftwall_bottom_box = QtWidgets.QHBoxLayout()
        leftwall_bottom_box.addWidget(self.leftwall_bottom_label)
        leftwall_bottom_box.addWidget(self.leftwall_bottom_slider)

        self.leftwall_groupbox = QtWidgets.QGroupBox("Left wall")
        self.leftwall_groupbox.setCheckable(True)
        leftwall_vbox = QtWidgets.QVBoxLayout()
        self.leftwall_groupbox.setLayout(leftwall_vbox)
        leftwall_vbox.addLayout(leftwall_width_box)
        leftwall_vbox.addLayout(leftwall_height_box)
        leftwall_vbox.addLayout(leftwall_right_box)
        leftwall_vbox.addLayout(leftwall_bottom_box)

        # right wall
        self.rightwall_width_label = QtWidgets.QLabel()
        self.rightwall_width_label.setText('width: ')
        self.rightwall_width_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.rightwall_width_slider.setMinimum(0)
        self.rightwall_width_slider.setMaximum(100)
        self.rightwall_width_slider.setValue(100)
        self.rightwall_width_slider.valueChanged.connect(self.updateWall)

        self.rightwall_height_label = QtWidgets.QLabel()
        self.rightwall_height_label.setText('height: ')
        self.rightwall_height_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.rightwall_height_slider.setMinimum(0)
        self.rightwall_height_slider.setMaximum(400)
        self.rightwall_height_slider.setValue(80)
        self.rightwall_height_slider.valueChanged.connect(self.updateWall)

        self.rightwall_left_label = QtWidgets.QLabel()
        self.rightwall_left_label.setText('left: ')
        self.rightwall_left_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.rightwall_left_slider.setMinimum(0)
        self.rightwall_left_slider.setMaximum(100)
        self.rightwall_left_slider.setValue(70)
        self.rightwall_left_slider.valueChanged.connect(self.updateWall)

        self.rightwall_bottom_label = QtWidgets.QLabel()
        self.rightwall_bottom_label.setText('bottom: ')
        self.rightwall_bottom_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.rightwall_bottom_slider.setMinimum(0)
        self.rightwall_bottom_slider.setMaximum(100)
        self.rightwall_bottom_slider.setValue(50)
        self.rightwall_bottom_slider.valueChanged.connect(self.updateWall)

        rightwall_width_box = QtWidgets.QHBoxLayout()
        rightwall_width_box.addWidget(self.rightwall_width_label)
        rightwall_width_box.addWidget(self.rightwall_width_slider)

        rightwall_height_box = QtWidgets.QHBoxLayout()
        rightwall_height_box.addWidget(self.rightwall_height_label)
        rightwall_height_box.addWidget(self.rightwall_height_slider)

        rightwall_left_box = QtWidgets.QHBoxLayout()
        rightwall_left_box.addWidget(self.rightwall_left_label)
        rightwall_left_box.addWidget(self.rightwall_left_slider)

        rightwall_bottom_box = QtWidgets.QHBoxLayout()
        rightwall_bottom_box.addWidget(self.rightwall_bottom_label)
        rightwall_bottom_box.addWidget(self.rightwall_bottom_slider)

        self.rightwall_groupbox = QtWidgets.QGroupBox("Right wall")
        self.rightwall_groupbox.setCheckable(True)
        rightwall_vbox = QtWidgets.QVBoxLayout()
        self.rightwall_groupbox.setLayout(rightwall_vbox)
        rightwall_vbox.addLayout(rightwall_width_box)
        rightwall_vbox.addLayout(rightwall_height_box)
        rightwall_vbox.addLayout(rightwall_left_box)
        rightwall_vbox.addLayout(rightwall_bottom_box)

        load_btn = QtWidgets.QPushButton('Load floor', self)
        load_btn.clicked.connect(self.load)
        save_btn = QtWidgets.QPushButton('Save all', self)
        save_btn.clicked.connect(self.save) #QtWidgets.qApp.quit

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(load_btn)
        hbox.addWidget(save_btn)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.gl)
        vbox.addLayout(camera_x_pos_box)
        vbox.addLayout(camera_zoom_box)
        wallshbox = QtWidgets.QHBoxLayout()
        wallshbox.addWidget(self.leftwall_groupbox)
        wallshbox.addWidget(self.rightwall_groupbox)
        vbox.addLayout(wallshbox)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.resize(300, 350)

    def getWallWidth(self, value):
        return value * 0.001

    def getWallHeight(self, value):
        return value * 0.01

    def getWallLeftRight(self, value):
        return value * 0.05

    def getWallBottom(self, value):
        return (value - 50) * 0.002

    def updateView(self):
        xpos = self.camera_x_pos_slider.value() * (self.floor_extent[1] - self.floor_extent[0]) / 100.0
        side_mag_level = 5 # 2^5 = 32x magnification
        zoom_level = math.pow(2.0, ( self.camera_zoom_slider.value() - 50.0 ) * side_mag_level / 50.0 )
        self.gl.setViewinfo(xpos, zoom_level)

    def updateWall(self):
        lwidth = self.getWallWidth(self.leftwall_width_slider.value())
        lheight = self.getWallHeight(self.leftwall_height_slider.value())
        self.scene_data.templates['left_wall'].vertex_list = np.array([[-0.5*lwidth, -0.5*lheight],[0.5*lwidth, -0.5*lheight],[0.5*lwidth, 0.5*lheight],[-0.5*lwidth, 0.5*lheight]]).transpose()
        self.scene_data.templates['left_wall'].size_mean = 0.5 * ( lwidth + lheight )

        rwidth = self.getWallWidth(self.rightwall_width_slider.value())
        rheight = self.getWallHeight(self.rightwall_height_slider.value())
        self.scene_data.templates['right_wall'].vertex_list = np.array([[-0.5*rwidth, -0.5*rheight],[0.5*rwidth, -0.5*rheight],[0.5*rwidth, 0.5*rheight],[-0.5*rwidth, 0.5*rheight]]).transpose()
        self.scene_data.templates['right_wall'].size_mean = 0.5 * ( rwidth + rheight )

        self.leftwall_width_label.setText('width: %.3f' % lwidth)
        self.leftwall_height_label.setText('height: %.3f' % lheight)

        self.rightwall_width_label.setText('width: %.3f' % rwidth)
        self.rightwall_height_label.setText('height: %.3f' % rheight)

        lright = self.getWallLeftRight(self.leftwall_right_slider.value())
        lbottom = self.getWallBottom(self.leftwall_bottom_slider.value())

        lcenter = np.array([lright-lwidth*0.5, lbottom+0.5*lheight]).transpose()
        for e in self.scene_data.elements:
            if e.template_name == 'left_wall':
                e.center_of_mass = lcenter
                break

        rleft = self.getWallLeftRight(self.rightwall_left_slider.value())
        rbottom = self.getWallBottom(self.rightwall_bottom_slider.value())

        rcenter = np.array([rleft+rwidth*0.5, rbottom+0.5*rheight]).transpose()
        for e in self.scene_data.elements:
            if e.template_name == 'right_wall':
                e.center_of_mass = rcenter
                break

        self.leftwall_right_label.setText('right: %.3f' % lright)
        self.leftwall_bottom_label.setText('bottom: %.3f' % lbottom)

        self.rightwall_left_label.setText('left: %.3f' % rleft)
        self.rightwall_bottom_label.setText('bottom: %.3f' % rbottom)

        self.gl.setData(self.scene_data)

    def load(self):
        # template
        (template_fn, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(self, "Load templates", os.path.expanduser('~'), "HDF5 (*.h5)" )

        # elements
        (element_fn, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(self, "Load elements", os.path.expanduser('~'), "HDF5 (*.h5)" )

        self.scene_data.templates = {k: v for k, v in self.scene_data.templates.items() if k == 'left_wall' or k == 'right_wall'}
        self.scene_data.elements = [e for e in self.scene_data.elements if e.template_name == 'left_wall' or e.template_name == 'right_wall']

        sd = SceneData()
        sd.load(template_fn, element_fn)

        self.scene_data.templates.update(sd.templates)
        self.scene_data.elements.extend(sd.elements)

        self.gl.setData(self.scene_data)

    def save(self):
        (fileName, selectedFilter) = QtWidgets.QFileDialog.getSaveFileName(self, "Save file", os.path.expanduser('~'), "HDF5 (*.h5)" )
        if fileName != "" and fileName[len(fileName)-3:] == ".h5":
            fileName_template = fileName[:len(fileName)-3] + "_template.h5"
            #QtWidgets.QMessageBox.information(self, "File", fileName_template)

        self.scene_data.save(fileName_template, fileName)

def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_Widget()
    ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
