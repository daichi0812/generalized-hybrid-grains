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
from particlehomogenizationh5 import *


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


class CompareForceGrid:
    def __init__(self):
        self.grid_start = np.zeros(2, dtype=ctypes.c_float)
        self.h = 0.01
        self.stencil = 3
        self.g = -9.8
        self.resolution = np.zeros(2, dtype=ctypes.c_int)
        self.sigma = np.zeros((1, 2, 2), dtype=ctypes.c_float)
        self.grid_m = np.zeros(1 , dtype=ctypes.c_float)
        self.grid_f = np.zeros((1, 2), dtype=ctypes.c_float)
        self.grid_density = np.zeros(1, dtype=ctypes.c_float)

    def N(self, dx):
        absx = math.fabs(dx)
        if absx < 1.0:
            return absx*absx*absx*0.5 - absx*absx + 2.0/3.0
        elif absx < 2.0:
            return -absx * absx * absx / 6.0 + absx * absx - 2.0 * absx + 4.0 / 3.0
        else:
            return 0.0
    def dN(self, dx):
        absx = math.fabs(dx)
        if dx >= 0.0:
            sgnx = 1.0
        else :
            sgnx = -1.0

        if absx < 1.0:
            return (absx*absx*1.5 - 2.0*absx) * sgnx
        elif absx < 2.0:
            return (-absx * absx * 0.5 + 2.0 * absx - 2.0) * sgnx
        else:
            return 0.0

    def uGIMPBase(self, particle_pos, grid_min, h):
        return np.round((particle_pos - grid_min) / h).astype(int)

    def Weight(self, particle_pos, grid_pos, h):
        dx = particle_pos - grid_pos
        wx = self.N(dx[0] / h)
        wy = self.N(dx[1] / h)
        weight = wx * wy
        return weight

    def WeightGrad(self, particle_pos, grid_pos, h):
        dx = particle_pos - grid_pos
        wx = self.N(dx[0] / h)
        wy = self.N(dx[1] / h)

        return np.array([wy * self.dN(dx[0] / h) / h, wx * self.dN(dx[1] / h) / h])
    def computeArea(self, vertex_list, size_mean):
        if vertex_list.shape[1] < 3:
            return math.pi * size_mean * size_mean
        else:
            area = 0.0
            for i in range(vertex_list.shape[1]):
                ip = (i+1) % vertex_list.shape[1]
                area += vertex_list[0, i] * vertex_list[1, ip] - vertex_list[0, ip] * vertex_list[1, i]
            return area
    def computeDEMGridForce(self, homogenize_data, scene_data):
        self.grid_start = homogenize_data.homogenization[0].grid_p
        self.h = homogenize_data.homogenization[0].h
        self.resolution = homogenize_data.homogenization[0].resolution
        N = np.prod(self.resolution)
        self.grid_f = np.zeros((N, 2), dtype=ctypes.c_float)
        particle_tau = np.zeros((2, 2), dtype=ctypes.c_float)

        # compute grid gravity

        #using grid stress
        for j in range(self.resolution[1]):
            for i in range(self.resolution[0]):
                flat_idx = j * self.resolution[0] + i
                cell_volume = 0.04 * 0.04
                base = np.array([i, j])
                grid_pos = self.grid_start + ((base).astype(float) + np.array([0.5, 0.5])) * self.h
                weight_grad = self.WeightGrad(grid_pos, grid_pos, self.h)
                if (np.isnan(homogenize_data.homogenization[flat_idx].sigma)).any() == True:
                    continue
                particle_sigma = homogenize_data.homogenization[flat_idx].sigma * cell_volume
                self.grid_f[flat_idx] -= cell_volume * particle_sigma @ weight_grad

        #using grid to particle to grid stress
        """
        for p in scene_data.elements:
            if p.static ==1:
                continue
            base = self.uGIMPBase(p.center_of_mass, self.grid_start, self.h)
            for i in range(-self.stencil, self.stencil+1):
                for j in range(-self.stencil, self.stencil+1):
            offset = np.array([i, j])
            if (i + base[0]) >= self.resolution[0] or (j + base[1]) >= self.resolution[1] or (
                    i + base[0]) < 0 or (j + base[1]) < 0:
                continue
            flat_idx = (offset + base)[1] * self.resolution[0] + (offset + base)[0]

            p_template = scene_data.templates[p.template_name]
            volume = p.size_ratio * p.size_ratio * self.computeArea(p_template.vertex_list,
                                                                    p_template.size_mean)

            grid_pos = self.grid_start + ((base + offset).astype(float) + np.array([0.5, 0.5])) * self.h
            weight_grad = self.WeightGrad(p.center_of_mass, grid_pos, self.h)
            if (np.isnan(homogenize_data.homogenization[flat_idx].sigma)).any() == True:
                continue
            particle_sigma = homogenize_data.homogenization[flat_idx].sigma * volume
            self.grid_f[flat_idx] -= volume * particle_sigma @ weight_grad
        """


    def setMPMData(self, particle_data, homogenize_data):
        # fit grid to data
        #grid_startのみDEMからとってくる
        self.grid_start = homogenize_data.homogenization[0].grid_p
        self.h = homogenize_data.homogenization[0].h
        self.resolution = particle_data.particle_homogenization[0].resolution
        N = np.prod(self.resolution)
        self.grid_m = np.zeros(N, dtype=ctypes.c_float)
        self.grid_f = np.zeros((N, 2), dtype=ctypes.c_float)
        self.sigma = np.zeros((N, 2, 2), dtype=ctypes.c_float)
        self.grid_density = np.zeros(N, dtype=ctypes.c_float)
        #TODO: detection outlier finding sigma = NaN

        for p in particle_data.particle_homogenization:
            base = self.uGIMPBase(p.center_of_mass, self.grid_start, self.h)
            for i in range(-self.stencil, self.stencil+1):
                for j in range(-self.stencil, self.stencil+1):
                    offset = np.array([i, j])
                    if (i + base[0]) >= self.resolution[0] or (j + base[1]) >= self.resolution[1] or (
                            i + base[0]) < 0 or (j + base[1]) < 0:
                        continue
                    flat_idx = (offset + base)[1] * self.resolution[0] + (offset + base)[0]
                    grid_pos = self.grid_start + ((base + offset).astype(float) + np.array([0.5, 0.5])) * self.h
                    weight = self.Weight(p.center_of_mass, grid_pos, self.h)
                    self.grid_m[flat_idx] += weight * p.density * p.volume

        # grid m to grid density
        cell_volume = self.h * self.h
        for j in range(self.resolution[1]):
            for i in range(self.resolution[0]):
                flat_idx = j * self.resolution[0] + i
                self.grid_density[flat_idx] = self.grid_m[flat_idx] / cell_volume

        cell_volume = 0.04 * 0.04
        for i, g in enumerate(particle_data.particle_to_grid_data):
            self.grid_f[i] = g.force / cell_volume

    def setDEMData(self, homogenize_data, scene_data, particle_data):
        N = np.prod(self.resolution)
        self.grid_start = homogenize_data.homogenization[0].grid_p
        self.h = homogenize_data.homogenization[0].h
        self.resolution = homogenize_data.homogenization[0].resolution
        N = np.prod(self.resolution)
        self.grid_f = np.zeros((N, 2), dtype=ctypes.c_float)
        self.grid_m = np.zeros(N, dtype=ctypes.c_float)
        self.grid_density = np.zeros(N, dtype=ctypes.c_float)
        #detection outlier finding sigma = NaN
        self.sigma = np.zeros((N, 2, 2), dtype=ctypes.c_float)
        for i in range(len(homogenize_data.homogenization)):
            self.sigma[i] = homogenize_data.homogenization[i].sigma

        #compute grid_m
        """
        for p in scene_data.elements:
            if p.static ==1:
                continue
            p_template = scene_data.templates[p.template_name]
            base = self.uGIMPBase(p.center_of_mass, self.grid_start, self.h)
            weight_test = 0.0
            for i in range(-self.stencil, self.stencil+1):
                for j in range(-self.stencil, self.stencil+1):
                    offset = np.array([i, j])
                    if (i + base[0]) >= self.resolution[0] or (j + base[1]) >= self.resolution[1] or (
                            i + base[0]) < 0 or (j + base[1]) < 0:
                        continue
                    flat_idx = (offset + base)[1] * self.resolution[0] + (offset + base)[0]

                    density = p_template.density
                    e_template = scene_data.templates[p.template_name]
                    volume = p.size_ratio * p.size_ratio * self.computeArea(e_template.vertex_list, e_template.size_mean)

                    grid_pos = self.grid_start + ((base + offset).astype(float) + np.array([0.5, 0.5])) * self.h
                    weight = self.Weight(p.center_of_mass, grid_pos, self.h)
                    #particle m to grid m
                    self.grid_m[flat_idx] += weight * density * volume
                    weight_test += weight
        """

        #grid_m from MPMParticle
        for p in particle_data.particle_homogenization:
            base = self.uGIMPBase(p.center_of_mass, self.grid_start, self.h)
            for i in range(-self.stencil, self.stencil + 1):
                for j in range(-self.stencil, self.stencil + 1):
                    offset = np.array([i, j])
                    if (i + base[0]) >= self.resolution[0] or (j + base[1]) >= self.resolution[1] or (
                            i + base[0]) < 0 or (j + base[1]) < 0:
                        continue
                    flat_idx = (offset + base)[1] * self.resolution[0] + (offset + base)[0]
                    grid_pos = self.grid_start + ((base + offset).astype(float) + np.array([0.5, 0.5])) * self.h
                    weight = self.Weight(p.center_of_mass, grid_pos, self.h)
                    self.grid_m[flat_idx] += weight * p.density * p.volume

        #grid m to grid density
        cell_volume = self.h * self.h
        for j in range(self.resolution[1]):
            for i in range(self.resolution[0]):
                flat_idx = j * self.resolution[0] + i
                self.grid_density[flat_idx] = self.grid_m[flat_idx] / cell_volume



        #compute grid f
        dx = np.zeros(2, dtype=ctypes.c_float)
        sigma_diff = np.zeros((2, 2), dtype=ctypes.c_float)
        for j in range(self.resolution[1]-1):
            for i in range(self.resolution[0]):
                upper_idx = self.resolution[0] * (j + 1) + i
                lower_idx = self.resolution[0] * j + i
                dx = (self.grid_start+(np.array([i + 0.5, (j + 1) + 0.5])).astype(float) * self.h) - (self.grid_start + (np.array([i + 0.5, j + 0.5])).astype(float) * self.h)
                sigma_diff = self.sigma[upper_idx] - self.sigma[lower_idx]
                if (np.isnan(sigma_diff)).any() == True:
                    continue
                self.grid_f[lower_idx][1] = sigma_diff[1][1] / dx[1]

                #print("sigma diff:", sigma_diff)
                #print("dx:", dx)
                #print("grid_density * g:", self.grid_density[lower_idx] * self.g)
                #print("grid_f",self.grid_f[lower_idx][1])



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

        #draw gravity line
        for j in range(self.resolution[1]-1):
            for i in range(self.resolution[0]):
                flat_idx = j * self.resolution[0] + i
                #remove outlier
                if (np.isnan(self.sigma[flat_idx])).any() == True:
                    continue
                #remove outlier right wall
                if i==self.resolution[0]-1 or i == self.resolution[0]-2:
                    continue
                vc = self.grid_start + self.h * np.array([i + 0.5, j + 0.5])
                v0 = vc - np.array([0.5 * self.h, 0.5 * self.h])
                v1 = vc + np.array([0.5 * self.h, 0.5 * self.h])
                error = math.fabs(self.grid_f[flat_idx][1] + self.grid_density[flat_idx] * self.g) * 0.0001
                #print("grid_density * g", self.grid_density[flat_idx] * self.g)
                #print("grid_f", self.grid_f[flat_idx][1])
                color = [error, 0.0 / 255.0, 0.0 / 255.0]
                if i==3 and j==3:
                    print(self.grid_f[flat_idx][1])
                    color = [0.0, 0.0, 0.0]

                VBO.registerLineToDataArray(v0, v1, color, color)
                v2 = vc - np.array([0.5 * self.h, -0.5 * self.h])
                v3 = vc + np.array([0.5 * self.h, -0.5 * self.h])
                color = [error, 0.0 / 255.0, 0.0 / 255.0]
                VBO.registerLineToDataArray(v2, v3, color, color)

        #draw force line
        """
        for j in range(self.resolution[1]):
            for i in range(self.resolution[0]):
                # remove outlier
                flat_idx = j * self.resolution[0] + i
                if (np.isnan(self.sigma[flat_idx])).any() == True:
                    continue
                vc = self.grid_start + self.h * np.array([i + 0.5, j + 0.5])
                v0 = vc - np.array([0.5 * self.h, 0.5 * self.h])
                v1 = vc + np.array([0.5 * self.h, 0.5 * self.h])
                color = [self.grid_f[flat_idx][1] / 255.0, 158.0 / 255.0, 46.0 / 255.0]
                VBO.registerLineToDataArray(v0, v1, color, color)

                v2 = vc - np.array([0.5 * self.h, -0.5 * self.h])
                v3 = vc + np.array([0.5 * self.h, -0.5 * self.h])
                color = [self.grid_f[flat_idx][1] / 255.0, 158.0 / 255.0, 46.0 / 255.0]
                VBO.registerLineToDataArray(v2, v3, color, color)
        """

    def computeForceVBOsForDraw(self, VBO):
        if self.resolution[0] <= 0 or self.resolution[1] <= 0:
            return

        # draw force line
        for j in range(self.resolution[1]):
            for i in range(self.resolution[0]):
                flat_idx = j * self.resolution[0] + i
                if (np.isnan(self.sigma[flat_idx])).any() == True:
                    continue
                vc = self.grid_start + self.h * np.array([i + 0.5, j + 0.5])
                v0 = vc - np.array([self.grid_f[flat_idx][0], 0.0])
                v1 = vc + np.array([self.grid_f[flat_idx][0], 0.0], )
                color = [232.0 / 255.0, 158.0 / 255.0, 46.0 / 255.0]
                VBO.registerLineToDataArray(v0, v1, color, color)

                v2 = vc - np.array([0.0, self.grid_f[flat_idx][1]])
                v3 = vc + np.array([0.0, self.grid_f[flat_idx][1]])
                color = [232.0 / 255.0, 158.0 / 255.0, 46.0 / 255.0]
                VBO.registerLineToDataArray(v2, v3, color, color)

class QTGLWidget2(QGLWidget):
    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(300, 300)
        self.data = SceneData()
        self.force_data = ForceData()
        self.homogenization_grid = CompareForceGrid()
        self.particle_data = ParticleHomogenizeData()
        self.homogenize_data = AllHomogenizeData()
        self.scene_data = SceneData()

        self.grains_VBO = LineVBO()
        self.discrete_forces_VBO = LineVBO()
        self.homogenization_VBO = LineVBO()
        self.grid_VBO = LineVBO()
        self.homogenization_force_VBO = LineVBO()

        self.draw_grains = True
        self.draw_forces = True
        self.draw_stresses = True
        self.draw_grid = True
        self.draw_homogenization_force = False

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

        if self.draw_homogenization_force:
            self.homogenization_force_VBO.drawVBO(3.0)

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
        self.homogenization_force_VBO.setNumElements(self.homogenization_grid.numLinesForDraw())

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
        self.homogenization_grid.computeForceVBOsForDraw(self.homogenization_force_VBO)
        self.homogenization_grid.computeGridVBOsForDraw(self.grid_VBO)

        self.grains_VBO.genBuffers()
        self.discrete_forces_VBO.genBuffers()
        self.homogenization_VBO.genBuffers()
        self.grid_VBO.genBuffers()
        self.homogenization_force_VBO.genBuffers()

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

    def setMPMData(self, particle_data, homogenize_data):
        self.particle_data = copy.deepcopy(particle_data)
        self.homogenize_data = copy.deepcopy(homogenize_data)
        self.homogenization_grid.setMPMData(self.particle_data, self.homogenize_data)
        self.autoAdjustView()
        self.buildVBO()
        self.updateGL()

    def setDEMData(self, homogenize_data, scene_data, particle_data):
        self.particle_data = copy.deepcopy(particle_data)
        self.homogenize_data = copy.deepcopy(homogenize_data)
        self.scene_data = copy.deepcopy(scene_data)
        self.data = copy.deepcopy(scene_data)
        self.homogenization_grid.setDEMData(self.homogenize_data, self.scene_data, self.particle_data)
        self.autoAdjustView()
        self.buildVBO()
        self.updateGL()


    def setViewinfo(self, xpos, ypos, zoom):
        self.camera_x_pos = 2.0 * xpos - 1.0
        self.camera_y_pos = 2.0 * ypos - 1.0
        self.camera_zoom = zoom
        self.updateGL()

    def toggleDraw(self, draw_grains, draw_forces, draw_stresses, draw_grid, draw_homogenization_force):
        self.draw_grains = draw_grains
        self.draw_forces = draw_forces
        self.draw_stresses = draw_stresses
        self.draw_grid = draw_grid
        self.draw_homogenization_force = draw_homogenization_force
        self.updateGL()


class Ui_Widget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.data = SceneData()
        self.force_data = ForceData()
        self.particle_data = AllParticleHomogenizeData()
        self.all_scene_data = AllSceneData()
        self.all_homogenize_data = AllHomogenizeData()
        self.p_fn = ""
        self.h_fn = ""
        self.t_fn = ""
        self.e_fn = ""

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
        self.homogenization_check_box = QtWidgets.QCheckBox("homogenization forces")
        self.grains_check_box.setChecked(True)
        self.forces_check_box.setChecked(True)
        self.stresses_check_box.setChecked(True)
        self.grid_check_box.setChecked(True)
        self.homogenization_check_box.setChecked(False)
        self.grains_check_box.stateChanged.connect(self.checkBoxChanged)
        self.forces_check_box.stateChanged.connect(self.checkBoxChanged)
        self.stresses_check_box.stateChanged.connect(self.checkBoxChanged)
        self.grid_check_box.stateChanged.connect(self.checkBoxChanged)
        self.homogenization_check_box.stateChanged.connect(self.checkBoxChanged)

        checkboxes = QtWidgets.QHBoxLayout()
        checkboxes.addWidget(self.grains_check_box)
        checkboxes.addWidget(self.forces_check_box)
        checkboxes.addWidget(self.stresses_check_box)
        checkboxes.addWidget(self.grid_check_box)
        checkboxes.addWidget(self.homogenization_check_box)

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

        loadMPM_btn = QtWidgets.QPushButton('LoadMPM', self)
        loadMPM_btn.clicked.connect(self.loadMPM)
        loadMPM_box = QtWidgets.QHBoxLayout()
        loadMPM_box.addWidget(loadMPM_btn)

        loadDEM_btn = QtWidgets.QPushButton('LoadDEM', self)
        loadDEM_btn.clicked.connect(self.loadDEM)
        loadDEM_box = QtWidgets.QHBoxLayout()
        loadDEM_box.addWidget(loadDEM_btn)

        loadAllStepMPM_btn = QtWidgets.QPushButton('LoadMPM to view force per cell', self)
        loadAllStepMPM_btn.clicked.connect(self.loadAllStepMPM)
        loadAllStepMPM_box = QtWidgets.QHBoxLayout()
        loadAllStepMPM_box.addWidget(loadAllStepMPM_btn)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(cy_gl_box)
        vbox.addLayout(camera_x_pos_box)
        vbox.addLayout(camera_zoom_box)
        vbox.addLayout(checkboxes)
        vbox.addLayout(timestep_idx_box)
        vbox.addLayout(loadMPM_box)
        vbox.addLayout(loadDEM_box)
        vbox.addLayout(loadAllStepMPM_box)

        self.setLayout(vbox)

        self.resize(300, 350)

    def updateLabels(self):
        dt_idx = int(self.timestep_idx_slider.value())
        self.timestep_idx_label.setText('dt: %d' % dt_idx)

    def updateView(self):
        xpos = self.camera_x_pos_slider.value() / 100.0
        ypos = self.camera_y_pos_slider.value() / 100.0
        side_mag_level = 5  # 2^5 = 32x magnification
        zoom_level = math.pow(2.0, (self.camera_zoom_slider.value() - 50.0) * side_mag_level / 50.0)
        self.gl.setViewinfo(xpos, ypos, zoom_level)

    def checkBoxChanged(self, state):
        self.gl.toggleDraw(self.grains_check_box.isChecked(), self.forces_check_box.isChecked(),
                           self.stresses_check_box.isChecked(), self.grid_check_box.isChecked(), self.homogenization_check_box.isChecked())

    def loadMPM(self):
        # load all step homogenization file
        #(self.p_fn, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(self, "Load  particle homogenization stress",os.path.expanduser('~'), "HDF5 (*.h5)")
        #(self.h_fn, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(self, "Load  DEM homogenization stress for grid start data", os.path.expanduser('~'), "HDF5 (*.h5)")
        self.p_fn = "Save/serialized_sigma.h5"
        self.h_fn = "DEMstress/DEM.h5"
        dt_idx = int(self.timestep_idx_slider.value())
        self.particle_data.load_from_idx(self.p_fn, dt_idx)
        self.all_homogenize_data.load_from_idx(self.h_fn, dt_idx)
        self.gl.setMPMData(self.particle_data.all_step_particle_homogenization[0], self.all_homogenize_data.all_step_homogenization[0])

    def loadDEM(self):
        # load all step homogenization file
        #(self.h_fn, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(self,"Load  DEM homogenization stress",os.path.expanduser('~'), "HDF5 (*.h5)")
        #(self.t_fn, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(self,"Load  template",os.path.expanduser('~'), "HDF5 (*.h5)")
        #(self.e_fn, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(self,"Load  all force data",os.path.expanduser('~'), "HDF5 (*.h5)")
        self.h_fn = "DEMstress/DEM.h5"
        self.t_fn = "Save/square_merge_template.h5"
        self.e_fn = "Save/serialized_forces.h5"
        self.p_fn = "Save/serialized_sigma.h5"
        dt_idx = int(self.timestep_idx_slider.value())
        self.all_homogenize_data.load_from_idx(self.h_fn, dt_idx)
        self.all_scene_data.load_from_idx(self.t_fn, self.e_fn, dt_idx)
        self.particle_data.load_from_idx(self.p_fn, dt_idx)

        self.gl.setDEMData(self.all_homogenize_data.all_step_homogenization[0], self.all_scene_data.all_step_elements[0], self.particle_data.all_step_particle_homogenization[0])

    def loadAllStepMPM(self):
        # load all step homogenization file
        # (self.p_fn, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(self, "Load  particle homogenization stress",os.path.expanduser('~'), "HDF5 (*.h5)")
        # (self.h_fn, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(self, "Load  DEM homogenization stress for grid start data", os.path.expanduser('~'), "HDF5 (*.h5)")
        self.p_fn = "Save/serialized_sigma.h5"
        self.h_fn = "DEMstress/DEM.h5"
        dt_idx = int(self.timestep_idx_slider.value())
        for i in range(dt_idx):
            self.particle_data.load_from_idx(self.p_fn, i)
            self.all_homogenize_data.load_from_idx(self.h_fn, i)
            self.gl.setMPMData(self.particle_data.all_step_particle_homogenization[0], self.all_homogenize_data.all_step_homogenization[0])

def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_Widget()
    ui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
