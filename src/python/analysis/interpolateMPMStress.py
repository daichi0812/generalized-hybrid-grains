import numpy as np
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
class interpolateMPMStress:
    def __init__(self,  h, particle_data, grid_start):
        self.resolution = np.zeros(2, dtype=ctypes.c_int)
        # fit grid to data
        min_c = np.array([1e6, 1e6])
        max_c = -min_c
        for f in particle_data.particle_homogenization:
            max_c = np.maximum(max_c, f.center_of_mass)
        self.h = float(h)
        self.grid_start = grid_start
        self.resolution = np.ceil((max_c - self.grid_start) / h).astype(int)
        N = np.prod(self.resolution)

        self.stencil = 3
        self.cell_volume = self.h**2
        self.center_of_mass = np.zeros((len(particle_data.particle_homogenization), 2), dtype=ctypes.c_float)
        self.particle_sigma = np.zeros((len(particle_data.particle_homogenization), 2, 2), dtype=ctypes.c_float)
        self.particle_volume = np.zeros(len(particle_data.particle_homogenization), dtype=ctypes.c_float)
        self.density = np.zeros(len(particle_data.particle_homogenization), dtype=ctypes.c_float)
        self.particle_mass = np.zeros(len(particle_data.particle_homogenization), dtype=ctypes.c_float)
        self.sigma = np.zeros((N, 2, 2), dtype=ctypes.c_float)
        for i in range(len(particle_data.particle_homogenization)):
            self.center_of_mass[i] = particle_data.particle_homogenization[i].center_of_mass
            self.particle_sigma[i] = particle_data.particle_homogenization[i].sigma
            self.particle_hl = 0.5 * self.h / 2
            self.particle_volume[i] = particle_data.particle_homogenization[i].volume
            self.density[i] = particle_data.particle_homogenization[i].density
            self.particle_mass[i] = self.density[i] * self.particle_volume[i]

    def N(self, dx):
        absx = math.fabs(dx)
        if absx < 1.0:
            return absx * absx * absx * 0.5 - absx * absx + 2.0 / 3.0
        elif absx < 2.0:
            return -absx * absx * absx / 6.0 + absx * absx - 2.0 * absx + 4.0 / 3.0
        else:
            return 0.0

    def dN(self, dx):
        absx = math.fabs(dx)
        if dx >= 0.0:
            sgnx = 1.0
        else:
            sgnx = -1.0

        if absx < 1.0:
            return (absx * absx * 1.5 - 2.0 * absx) * sgnx
        elif absx < 2.0:
            return (-absx * absx * 0.5 + 2.0 * absx - 2.0) * sgnx
        else:
            return 0.0

    def uGIMPBase(self, particle_pos, grid_min, h):
        return np.floor((particle_pos - grid_min) / h).astype(int)

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

    def interpolateStress(self):
        count = np.zeros(np.prod(self.resolution), dtype=ctypes.c_int)
        #linear interpolation: particle stress to center grid
        for p, e in enumerate(self.particle_sigma):
            # base = self.uGIMPBase(self.center_of_mass[p], self.grid_start, self.h)
            # for i in range(-self.stencil, self.stencil+1):
            #     for j in range(-self.stencil, self.stencil+1):
            #
            #         offset = np.array([i, j])
            #         if (i + base[0]) >= self.resolution[0] or (j + base[1]) >= self.resolution[1] or (i + base[0]) < 0 or (j + base[1]) < 0:
            #             continue
            #         flat_idx = (offset + base)[1] * self.resolution[0] + (offset + base)[0]
            #         grid_pos = self.grid_start + ((base + offset).astype(float) + np.array([0.5, 0.5])) * self.h
            #         weight = self.Weight(self.center_of_mass[p], grid_pos, self.h)
            #         self.sigma[flat_idx] += self.particle_sigma[p] * weight
            base = self.uGIMPBase(self.center_of_mass[p], self.grid_start, self.h)
            flat_idx = base[1] * self.resolution[0] + base[0]
            self.sigma[flat_idx] += self.particle_sigma[p]
            count[flat_idx] += 1

        for i in range(len(count)):
            if count[i] != 0:
                self.sigma[i] /= float(count[i])

    def saveStress(self, homogenization_data):
        #set h5 data
        grid_min = self.grid_start
        for j in range(self.resolution[1]):
            for i in range(self.resolution[0]):
                k = Homogenization()
                flat_idx = j * self.resolution[0] + i
                k.h = self.h
                k.resolution = self.resolution
                k.grid_p = grid_min + self.h * np.array([i, j])
                k.sigma = self.sigma[flat_idx]
                homogenization_data.homogenization.append(k)
