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

        circle_template = ShapeTemplate()
        circle_template.density = 1000.0
        circle_template.size_mean = 0.25
        circle_template.size_std = 0.0
        circle_template.vertex_list = np.array([[0.0, 0.0]]).transpose()

        self.scene_data.templates.update([('circle', circle_template)])

        triangle_template = ShapeTemplate()
        triangle_template.density = 1000.0
        triangle_template.size_mean = 0.01616025403
        triangle_template.size_std = 0.001616025403
        triangle_template.vertex_list = np.array([[-0.0086602540378, -0.005], [0.0086602540378, -0.005], [0.0, 0.01]]).transpose()

        self.scene_data.templates.update([('triangle', triangle_template)])

        square_template = ShapeTemplate()
        square_template.density = 1000.0
        square_template.size_mean = 0.01
        square_template.size_std = 0.001
        square_template.vertex_list = np.array([[-0.005, -0.005], [0.005, -0.005], [0.005, 0.005], [-0.005, 0.005]]).transpose()

        self.scene_data.templates.update([('square', square_template)])

        L_template = ShapeTemplate()
        L_template.density = 1000.0
        L_template.size_mean = 0.0075005
        L_template.size_std = 0.00075005
        L_template.vertex_list = np.array([[-0.003667, -0.002], [0.006334, -0.002], [0.006334, -0.001], [-0.002667, -0.001], [-0.002667, 0.003], [-0.003667, 0.003]]).transpose()

        self.scene_data.templates.update([('L', L_template)])

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


        self.template_names = []
        self.size_mean_labels = []
        self.size_mean_sliders = []
        self.size_std_labels = []
        self.size_std_sliders = []
        self.number_ratio_labels = []
        self.number_ratio_sliders = []
        self.template_default_size = []
        self.template_current_size = []

        scroll_area = QtWidgets.QScrollArea()
        scroll_area_vbox = QtWidgets.QVBoxLayout()

        for t in self.scene_data.templates:
            self.template_names.append(t)

            if self.scene_data.templates[t].vertex_list.shape[1] >= 3:
                min_coord = self.scene_data.templates[t].vertex_list.min(1)
                max_coord = self.scene_data.templates[t].vertex_list.max(1)
                size_coord = max_coord - min_coord
                self.scene_data.templates[t].size_mean = (size_coord[0] + size_coord[1]) * 0.5

            self.template_default_size.append(self.scene_data.templates[t].size_mean)
            self.template_current_size.append(self.scene_data.templates[t].size_mean)

            size_mean_label = QtWidgets.QLabel()
            size_mean_label.setText('size_mean: ')
            size_mean_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
            size_mean_slider.setMinimum(0)
            size_mean_slider.setMaximum(100)
            size_mean_slider.setValue(50)
            size_mean_slider.valueChanged.connect(self.updateTemplateSetting)

            self.size_mean_labels.append(size_mean_label)
            self.size_mean_sliders.append(size_mean_slider)

            hbox_mean = QtWidgets.QHBoxLayout()
            hbox_mean.addWidget(size_mean_label)
            hbox_mean.addWidget(size_mean_slider)

            size_std_label = QtWidgets.QLabel()
            size_std_label.setText('size_std: ')
            size_std_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
            size_std_slider.setMinimum(0)
            size_std_slider.setMaximum(100)
            size_std_slider.setValue(50)
            size_std_slider.valueChanged.connect(self.updateTemplateSetting)

            self.size_std_labels.append(size_std_label)
            self.size_std_sliders.append(size_std_slider)

            hbox_std = QtWidgets.QHBoxLayout()
            hbox_std.addWidget(size_std_label)
            hbox_std.addWidget(size_std_slider)

            number_ratio_label = QtWidgets.QLabel()
            number_ratio_label.setText('number_ratio: ')
            number_ratio_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
            number_ratio_slider.setMinimum(0)
            number_ratio_slider.setMaximum(100)
            number_ratio_slider.setValue(0)
            number_ratio_slider.valueChanged.connect(self.updateTemplateSetting)

            self.number_ratio_labels.append(number_ratio_label)
            self.number_ratio_sliders.append(number_ratio_slider)

            hbox_number_ratio = QtWidgets.QHBoxLayout()
            hbox_number_ratio.addWidget(number_ratio_label)
            hbox_number_ratio.addWidget(number_ratio_slider)

            group_vbox = QtWidgets.QVBoxLayout()
            group_vbox.addLayout(hbox_mean)
            group_vbox.addLayout(hbox_std)
            group_vbox.addLayout(hbox_number_ratio)

            groupbox = QtWidgets.QGroupBox(t)
            groupbox.setLayout(group_vbox)

            scroll_area_vbox.addWidget(groupbox)

        inner = QtWidgets.QWidget()
        inner.resize(500, inner.height())
        inner.setLayout(scroll_area_vbox)

        scroll_area.setWidget(inner)

        self.min_x_label = QtWidgets.QLabel()
        self.min_x_label.setText('min x: ')
        self.min_x_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.min_x_slider.setMinimum(0)
        self.min_x_slider.setMaximum(100)
        self.min_x_slider.setValue(50)
        self.min_x_slider.valueChanged.connect(self.updateTemplateSetting)

        min_x_box = QtWidgets.QHBoxLayout()
        min_x_box.addWidget(self.min_x_label)
        min_x_box.addWidget(self.min_x_slider)

        self.max_x_label = QtWidgets.QLabel()
        self.max_x_label.setText('max x: ')
        self.max_x_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.max_x_slider.setMinimum(0)
        self.max_x_slider.setMaximum(100)
        self.max_x_slider.setValue(50)
        self.max_x_slider.valueChanged.connect(self.updateTemplateSetting)

        max_x_box = QtWidgets.QHBoxLayout()
        max_x_box.addWidget(self.max_x_label)
        max_x_box.addWidget(self.max_x_slider)

        self.min_y_label = QtWidgets.QLabel()
        self.min_y_label.setText('min y: ')
        self.min_y_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.min_y_slider.setMinimum(0)
        self.min_y_slider.setMaximum(100)
        self.min_y_slider.setValue(50)
        self.min_y_slider.valueChanged.connect(self.updateTemplateSetting)

        min_y_box = QtWidgets.QHBoxLayout()
        min_y_box.addWidget(self.min_y_label)
        min_y_box.addWidget(self.min_y_slider)

        self.total_mass_label = QtWidgets.QLabel()
        self.total_mass_label.setText('total mass: ')
        self.total_mass_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.total_mass_slider.setMinimum(0)
        self.total_mass_slider.setMaximum(400)
        self.total_mass_slider.setValue(50)
        self.total_mass_slider.valueChanged.connect(self.updateTemplateSetting)

        total_mass_box = QtWidgets.QHBoxLayout()
        total_mass_box.addWidget(self.total_mass_label)
        total_mass_box.addWidget(self.total_mass_slider)

        generate_btn = QtWidgets.QPushButton('Generate', self)
        generate_btn.clicked.connect(self.generate)
        save_btn = QtWidgets.QPushButton('Save', self)
        save_btn.clicked.connect(self.save) #QtWidgets.qApp.quit

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(generate_btn)
        hbox.addWidget(save_btn)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.gl)
        vbox.addLayout(camera_x_pos_box)
        vbox.addLayout(camera_zoom_box)
        vbox.addWidget(scroll_area)
        vbox.addLayout(min_x_box)
        vbox.addLayout(max_x_box)
        vbox.addLayout(min_y_box)
        vbox.addLayout(total_mass_box)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.updateTemplateSetting()

        self.resize(300, 350)

    def getSize(self, value):
        return value * 0.001

    def getStd(self, value):
        return value * 0.0001

    def getRatio(self, value):
        return value * 1

    def getRatioSliderValue(self, ratio):
        return ratio / 1

    def getMass(self, value):
        return value * 1.0 #[kg]

    def getExtentCoord(self, value):
        return value * 0.01

    def updateTemplateSetting(self):
        for i in range(len(self.template_names)):
            size_mean = self.getSize(self.size_mean_sliders[i].value())
            size_std = self.getStd(self.size_std_sliders[i].value())
            number_ratio = self.getRatio(self.number_ratio_sliders[i].value())

            self.size_mean_labels[i].setText('size_mean: %.3f' % size_mean)
            self.size_std_labels[i].setText('size_std: %.4f' % size_std)
            self.number_ratio_labels[i].setText('number_ratio: %.1f%%' % number_ratio)

            self.template_current_size[i] = self.scene_data.templates[self.template_names[i]].size_mean
            self.scene_data.templates[self.template_names[i]].size_mean = size_mean
            self.scene_data.templates[self.template_names[i]].vertex_list *= size_mean / self.template_current_size[i]

        number_ratio_tot = 0
        for i in range(len(self.template_names)-1):
            number_ratio_tot += self.getRatio(self.number_ratio_sliders[i].value())
        if number_ratio_tot > 100:
            QtWidgets.QMessageBox.information(self, "Warning", "Number ratio exceeds 100%")
        else:
            self.number_ratio_sliders[len(self.template_names)-1].setValue(int(self.getRatioSliderValue(100-number_ratio_tot)))

        self.min_x_label.setText('min x: %.2f' % self.getExtentCoord(self.min_x_slider.value()))
        self.max_x_label.setText('max x: %.2f' % self.getExtentCoord(self.max_x_slider.value()))
        self.min_y_label.setText('min y: %.2f' % self.getExtentCoord(self.min_y_slider.value()))
        self.total_mass_label.setText('total mass: %.3f' % self.getMass(self.total_mass_slider.value()))

    def computeBBSizeAndMin(self, vertex_list, size_mean, angle, size_ratio):
        if vertex_list.shape[1] < 3:
            return np.array([size_mean, size_mean]).transpose(), np.array([-size_mean*0.5, -size_mean*0.5]).transpose()
        else:
            rot_mat = np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])
            vertices = size_ratio * rot_mat @ vertex_list
            return np.max(vertices, axis=1) - np.min(vertices, axis=1), np.min(vertices, axis=1)

    def computeArea(self, vertex_list, size_mean):
        if vertex_list.shape[1] < 3:
            return 0.25 * math.pi * size_mean * size_mean
        else:
            area = 0.0
            for i in range(vertex_list.shape[1]):
                ip = (i+1) % vertex_list.shape[1]
                area += vertex_list[0, i] * vertex_list[1, ip] - vertex_list[0, ip] * vertex_list[1, i]
            return 0.5 * area

    def acceptTempElems(self, temp_elem_list, temp_bb_sizes, temp_width, temp_height, left, bottom, width):
        space_x_per_elem = (width - temp_width) / len(temp_elem_list)
        for i in range(len(temp_elem_list)):
            e_ = copy.deepcopy(temp_elem_list[i])
            space_y = temp_height - temp_bb_sizes[i][1]
            e_.center_of_mass[0] += left + (i+random.random()) * space_x_per_elem
            e_.center_of_mass[1] += bottom + random.random() * space_y

            self.scene_data.elements.append(e_)

    def generate(self):
        self.scene_data.elements.clear()
        region_left = self.getExtentCoord(self.min_x_slider.value())
        extent_width = self.getExtentCoord(self.max_x_slider.value()) - region_left
        region_bottom = self.getExtentCoord(self.min_y_slider.value())

        target_mass = self.getMass(self.total_mass_slider.value())
        total_mass = 0.0

        sampling_look_up_table = np.zeros(100, dtype = np.int32)
        template_areas = np.zeros(len(self.template_names))
        pp = 0
        for i in range(len(self.template_names)):
            template_areas[i] = self.computeArea(self.scene_data.templates[self.template_names[i]].vertex_list, self.scene_data.templates[self.template_names[i]].size_mean)
            for j in range(self.number_ratio_sliders[i].value()):
                sampling_look_up_table[pp + j] = i
            pp += self.number_ratio_sliders[i].value()


        print(template_areas)

        temp_elem_list = []
        temp_bb_sizes = []
        temp_height = 0.0
        temp_width = 0.0

        while total_mass < target_mass:
            # random sampling a template
            r = random.randint(0, 99)
            template_idx = sampling_look_up_table[r]
            t = self.template_names[template_idx]

            # determine its size, angle
            size = self.scene_data.templates[t].size_mean + random.uniform(-1.0, 1.0) * self.scene_data.templates[t].size_std
            angle = random.random() * 2.0 * math.pi
            size_ratio = size / self.scene_data.templates[t].size_mean

            # compute its bb
            bb_size, bb_min = self.computeBBSizeAndMin(self.scene_data.templates[t].vertex_list, self.scene_data.templates[t].size_mean, angle, size_ratio)
            mass = size_ratio * size_ratio * template_areas[template_idx] * self.scene_data.templates[t].density
            print('bb_size: ' + str(bb_size))
            print('mass: ' + str(mass))

            if temp_width + bb_size[0] > extent_width:
                self.acceptTempElems(temp_elem_list, temp_bb_sizes, temp_width, temp_height, region_left, region_bottom, extent_width)
                region_bottom += temp_height
                temp_elem_list.clear()
                temp_bb_sizes.clear()
                temp_height = 0.0
                temp_width = 0.0

            # pack the element into the region
            e = Element()
            e.template_name = t
            e.size_ratio = size_ratio
            e.center_of_mass = np.array([temp_width - bb_min[0], - bb_min[1]]).transpose()
            e.rotation_angle = angle
            e.velocity = np.array([0.0, 0.0]).transpose()
            e.angular_velocity = 0.0
            e.static = False
            temp_elem_list.append(e)

            temp_bb_sizes.append(bb_size)
            temp_width += bb_size[0]
            temp_height = max([temp_height, bb_size[1]])

            total_mass += mass

        if len(temp_elem_list) > 0:
            self.acceptTempElems(temp_elem_list, temp_bb_sizes, temp_width, temp_height, region_left, region_bottom, extent_width)

        self.gl.setData(self.scene_data)

    def updateView(self):
        xpos = self.camera_x_pos_slider.value() / 100.0
        side_mag_level = 5 # 2^5 = 32x magnification
        zoom_level = math.pow(2.0, ( self.camera_zoom_slider.value() - 50.0 ) * side_mag_level / 50.0 )
        self.gl.setViewinfo(xpos, zoom_level)

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
