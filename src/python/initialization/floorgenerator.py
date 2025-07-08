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

class Setting:
    def __init__(self):
        self.anchor = [0.0, 0.0]
        self.extent = 2.0

class QTGLWidget2(QGLWidget):
    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(300, 300)
        self.data = SceneData()
        self.setting = Setting()
        self.height_reference = 540.0
        self.camera_x_pos = 0.0
        self.camera_zoom = 1.0
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

    def drawFloor(self):
        for c in self.data.elements:
            if c.template_name == 'floor_circle':
                self.drawCircle(c.center_of_mass, 0.5 * c.size_ratio * self.data.templates['floor_circle'].size_mean, c.rotation_angle, c.static)

    def drawGuide(self):
        half_height = self.computeHalfHeight(self.inner_height)

        glLineWidth(1.0)
        glBegin(GL_LINES)
        glColor3f(1.0, 0.3, 0.2)
        glVertex2d(self.setting.anchor[0], self.setting.anchor[1])
        glVertex2d(self.setting.extent, self.setting.anchor[1])

        i = 0
        glColor3f(0.8, 0.8, 0.8)
        while i < self.setting.extent:
            glVertex2d(i, self.setting.anchor[1] - 0.8 * half_height)
            glVertex2d(i, self.setting.anchor[1] + 0.8 * half_height)
            i += 1

        glEnd()

        glLineWidth(3.0)
        glBegin(GL_LINES)
        i = 0
        glColor3f(0.4, 0.4, 0.4)
        while i < self.setting.extent:
            glVertex2d(i, self.setting.anchor[1] - half_height)
            glVertex2d(i, self.setting.anchor[1] + half_height)
            i += 10

        glVertex2d(self.setting.extent, self.setting.anchor[1] - half_height)
        glVertex2d(self.setting.extent, self.setting.anchor[1] + half_height)

        glEnd()

    def pre_display(self):
        half_width = self.computeHalfWidth(self.inner_width)
        half_height = self.computeHalfHeight(self.inner_height)

        x_offset = self.camera_x_pos * self.setting.extent

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

        self.drawFloor()
        self.drawGuide()

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

    def setData(self, setting, data):
        self.setting = copy.deepcopy(setting)
        self.data = copy.deepcopy(data)
        self.updateGL()

    def setViewinfo(self, xpos, zoom):
        self.camera_x_pos = xpos
        self.camera_zoom = zoom
        self.updateGL()

class Ui_Widget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.setting = Setting()

        self.scene_data = SceneData()
        circle_template = ShapeTemplate()
        circle_template.density = 1000.0
        circle_template.size_mean = 0.1
        circle_template.size_std = 0.01
        circle_template.vertex_list = np.array([[0.0, 0.0]]).transpose()

        self.scene_data.templates.update([('floor_circle', circle_template)])

        self.gl = QTGLWidget2(self)
        self.gl.setData(self.setting, self.scene_data)

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

        self.extent_label = QtWidgets.QLabel()
        self.extent_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.extent_slider.setMinimum(1)
        self.extent_slider.setMaximum(100)
        self.extent_slider.setValue(70)
        self.extent_slider.valueChanged.connect(self.updateLabels)

        extent_box = QtWidgets.QHBoxLayout()
        extent_box.addWidget(self.extent_label)
        extent_box.addWidget(self.extent_slider)

        self.size_mean_label = QtWidgets.QLabel()
        self.size_mean_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.size_mean_slider.setMinimum(1)
        self.size_mean_slider.setMaximum(100)
        self.size_mean_slider.setValue(10)
        self.size_mean_slider.valueChanged.connect(self.updateLabels)

        size_mean_box = QtWidgets.QHBoxLayout()
        size_mean_box.addWidget(self.size_mean_label)
        size_mean_box.addWidget(self.size_mean_slider)

        self.size_std_label = QtWidgets.QLabel()
        self.size_std_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.size_std_slider.setMinimum(1)
        self.size_std_slider.setMaximum(100)
        self.size_std_slider.setValue(15)
        self.size_std_slider.valueChanged.connect(self.updateLabels)

        size_std_box = QtWidgets.QHBoxLayout()
        size_std_box.addWidget(self.size_std_label)
        size_std_box.addWidget(self.size_std_slider)

        regenerate_btn = QtWidgets.QPushButton('Regenerate', self)
        regenerate_btn.clicked.connect(self.updateData)
        save_btn = QtWidgets.QPushButton('Save file', self)
        save_btn.clicked.connect(self.save) #QtWidgets.qApp.quit

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(regenerate_btn)
        hbox.addWidget(save_btn)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.gl)
        vbox.addLayout(camera_x_pos_box)
        vbox.addLayout(camera_zoom_box)
        vbox.addLayout(extent_box)
        vbox.addLayout(size_mean_box)
        vbox.addLayout(size_std_box)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.updateLabels()

        self.resize(300, 350)

    def getSizeMean(self):
        return 0.001 * self.size_mean_slider.value()

    def getSizeStd(self):
        return 0.0001 * self.size_std_slider.value()

    def getExtent(self):
        return 0.1 * self.extent_slider.value()

    def regenerateElements(self):
        self.scene_data.elements.clear()
        std = self.scene_data.templates['floor_circle'].size_std
        mean = self.scene_data.templates['floor_circle'].size_mean

        width = 0.0
        while width < self.setting.extent:
            r = 0.5 * (mean + std * random.uniform(-1.0, 1.0))

            circle = Element()
            circle.template_name = 'floor_circle'
            circle.size_ratio = 2.0 * r / mean
            circle.center_of_mass = [width + r, 0.0]
            circle.rotation_angle = math.pi * random.random()
            circle.velocity = [0.0, 0.0]
            circle.angular_velocity = 0.0
            circle.static = True

            self.scene_data.elements.append(circle)

            width += 2.0 * r

    def updateLabels(self):
        self.scene_data.templates['floor_circle'].size_mean = self.getSizeMean()
        self.scene_data.templates['floor_circle'].size_std = self.getSizeStd()
        self.setting.extent = self.getExtent()

        self.extent_label.setText('extent: %.2f' % self.setting.extent)
        self.size_mean_label.setText('size_mean: %.3f' % self.scene_data.templates['floor_circle'].size_mean)
        self.size_std_label.setText('size_std: %.4f' % self.scene_data.templates['floor_circle'].size_std)

    def updateView(self):
        xpos = self.camera_x_pos_slider.value() / 100.0
        side_mag_level = 5 # 2^5 = 32x magnification
        zoom_level = math.pow(2.0, ( self.camera_zoom_slider.value() - 50.0 ) * side_mag_level / 50.0 )
        self.gl.setViewinfo(xpos, zoom_level)
        pass

    def updateData(self):
        self.regenerateElements()
        self.gl.setData(self.setting, self.scene_data)

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
