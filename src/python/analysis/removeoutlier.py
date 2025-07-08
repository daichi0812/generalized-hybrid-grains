#http://www.not-enough.org/abe/manual/program-aa08/pyqt1.html

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

class RemoveOutlier:
    def __init__(self):
        self.grid_start = np.zeros(2, dtype=ctypes.c_float)
        self.h = 0.01
        self.resolution = np.zeros(2, dtype=ctypes.c_int)
        self.sigma = np.zeros((1, 2, 2), dtype=ctypes.c_float)

    def computeArea(self, vertex_list, size_mean):
        if vertex_list.shape[1] < 3:
            return math.pi * size_mean * size_mean
        else:
            area = 0.0
            for i in range(vertex_list.shape[1]):
                ip = (i+1) % vertex_list.shape[1]
                area += vertex_list[0, i] * vertex_list[1, ip] - vertex_list[0, ip] * vertex_list[1, i]
            return area

    def calcPackingfraction(self, scene_data):
        #set packing fraction data
        N = np.prod(self.resolution)
        packing_fraction = np.zeros(N,dtype=ctypes.c_float)
        for e in scene_data.elements:
            if e.static==True:
                continue
            cell_idx = np.floor((e.center_of_mass - self.grid_start) / self.h).astype(int)
            flat_idx = cell_idx[1] * self.resolution[0] + cell_idx[0]
            if flat_idx >= N or flat_idx < 0:   #剛体の中心が格子の外にある
                continue
            e_template = scene_data.templates[e.template_name]
            packing_fraction[flat_idx] += e.size_ratio * e.size_ratio * self.computeArea(e_template.vertex_list, e_template.size_mean)

        cell_volume = self.h * self.h
        for j in range(self.resolution[1]):
            for i in range(self.resolution[0]):
                flat_idx = j * self.resolution[0] + i
                packing_fraction[flat_idx] = packing_fraction[flat_idx] / cell_volume
        return packing_fraction

    def calcdistancefromwall(self, left_wall_position, floor_wall_position):
        N = np.prod(self.resolution)
        distance_from_wall = np.zeros(N,dtype=ctypes.c_float)
        for j in range(self.resolution[1]):
            for i in range(self.resolution[0]):
                grid_center_p = self.grid_start + self.h * np.array([i+0.5, j+0.5])
                flat_idx = j*self.resolution[0] + i
                if j >= i:
                    distance_from_wall[flat_idx] = math.fabs(left_wall_position[0]-grid_center_p[0])
                else :
                    distance_from_wall[flat_idx] = math.fabs(floor_wall_position[1]-grid_center_p[1])
        return distance_from_wall


    def setData(self, data, homogenization_data):
        self.grid_start = homogenization_data.homogenization[0].grid_p
        self.resolution = homogenization_data.homogenization[0].resolution
        self.h = homogenization_data.homogenization[0].h
        N = np.prod(self.resolution)
        self.packing_fraction = np.zeros(N,dtype=ctypes.c_float)
        self.distance_from_wall = np.zeros(N,dtype=ctypes.c_float)
        left_wall_position=[2]
        floor_wall_position=[2]
        left_wall_position[0] = None
        floor_wall_position[0] = None

        #壁の中心座標を取り出す
        for e in data.elements:
            if e.template_name == "left_wall":
                if  left_wall_position[0] == None:
                        left_wall_position=e.center_of_mass
                else:   print("WARNING:exist two left wall. rewrite this code.")
            if e.template_name == "floor_circle":
                if floor_wall_position[0] ==None or floor_wall_position.all() ==e.center_of_mass.all():
                    floor_wall_position = e.center_of_mass
                else: print("フロアの中心がずれています")

        #パッキング率を計算
        self.packing_fraction = self.calcPackingfraction(data)
        #グリッド中心から壁からの最短距離を求める
        self.distance_from_wall = self.calcdistancefromwall(left_wall_position, floor_wall_position)

    
    def removeGrid(self, homogenization_data, packing_fraction_threshold, distance_from_wall_threshold):
        self.resolution = homogenization_data.homogenization[0].resolution
        for j in range(self.resolution[1]):
            for i in range(self.resolution[0]):
                flat_idx = j * self.resolution[0] + i
                if self.packing_fraction[flat_idx] < packing_fraction_threshold or self.distance_from_wall[flat_idx]<distance_from_wall_threshold:
                        homogenization_data.homogenization[flat_idx].sigma=None


