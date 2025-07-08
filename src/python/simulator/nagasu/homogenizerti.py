# http://www.not-enough.org/abe/manual/program-aa08/pyqt1.html
from homogenizationh5 import *
import time
import taichi as ti
from csv import writer
import ctypes

ti.init(arch=ti.gpu, default_fp=ti.f64)
#ti.init(arch=ti.cuda, default_fp=ti.f64)

@ti.data_oriented
class TiHomogenizationGrid:

    def __init__(self):
        self.estimate_force_num = 200000
        self.estimate_grid_num = 10000
        self.arm = ti.Vector.field(2, dtype=float, shape=self.estimate_force_num)
        self.force = ti.Vector.field(2, dtype=float, shape=self.estimate_force_num)
        self.position = ti.Vector.field(2, dtype=float, shape=self.estimate_force_num)
        self.cell = ti.Vector([0.0, 0.0])
        self.cell_idx = ti.Vector([0, 0])
        self.sigma = ti.Matrix.field(2, 2, dtype=float, shape=self.estimate_grid_num)
        self.sigma_numpy = np.array((self.estimate_grid_num, 2, 2), dtype=ctypes.c_float)
        self.grid_start = ti.Vector([0.0, 0.0])
        self.resolution = ti.Vector([0, 0])
        self.force_num = 0
        self.h = 0.0
    def setData(self, grid_start_offset_ratio, h, allforce_data):
        part_start_time = time.perf_counter_ns()
        if len(allforce_data.all_step_ForceData_position) == 0:
            return

        # fit grid to data
        min_c = np.array([1e6, 1e6])
        max_c = -min_c

        max_c[0] = np.amax(allforce_data.all_step_ForceData_position[:, 0])
        max_c[1] = np.amax(allforce_data.all_step_ForceData_position[:, 1])
        min_c[0] = np.amin(allforce_data.all_step_ForceData_position[:, 0])
        min_c[1] = np.amin(allforce_data.all_step_ForceData_position[:, 1])

        _i = (min_c / h + grid_start_offset_ratio).astype(int)
        numpy_grid_start = h * (_i - grid_start_offset_ratio)
        self.grid_start = numpy_grid_start
        self.grid_start = ti.Vector(numpy_grid_start)
        self.resolution = ti.Vector(np.ceil((max_c - self.grid_start) / h).astype(int))
        self.h = float(h)
        self.N = np.prod(self.resolution).astype(int)
        self.cell_volume = float(self.h ** 2)
        self.sigma.fill(0.0)

        self.arm.from_numpy(allforce_data.all_step_ForceData_arm)
        self.force.from_numpy(allforce_data.all_step_ForceData_force)
        self.position.from_numpy(allforce_data.all_step_ForceData_position)
        self.force_num = allforce_data.force_num

    @ti.kernel
    def fillForceDataZero(self):
        self.a.fill(0.0)
        self.f.fill(0.0)
        self.p.fill(0.0)
        self.sigma.fill(0.0)

    @ti.kernel
    def calcHomogenizeStress(self):
        # homogenization
        # compute homogenize stress (hybrid_grains algorithm 11)
        for f in range(self.force_num):
            cell = (self.position[f] - self.grid_start) / self.h
            cell_idx = ti.floor(cell)
            flat_idx = int(cell_idx[1]) * self.resolution[0] + int(cell_idx[0])

            #Christoffesen formula
            self.sigma[flat_idx] += 0.5 * (self.arm[f].outer_product(self.force[f]) + self.force[f].outer_product(self.arm[f])) / self.cell_volume  # REVIEW:重みづけ、接触点周囲に影響


    """
    @ti.kernel
    def calcStress(self, position:ti.types.ndarray(), arm:ti.types.ndarray(), force:ti.types.ndarray())->ti.float32:
        # homogenization
        # compute homogenize stress (hybrid_grains algorithm 11)
        dim = position.shape[1]-1
        print(dim)
        for f in range(self.force_num):
            for i in range(dim):
                self.cell[i] = (position[f, i] - self.grid_start[i]) / self.h
                self.cell_idx[i] = ti.floor(self.cell[i])
                #flat_idx = int(cell_idx[1]) * self.resolution[0] + int(cell_idx[0])
                # Christoffesen formula
                self.sigma[0] += 0.5 * (arm[f].outer_product(force[f]) + force[f].outer_product(
                    arm[f])) / self.cell_volume  # REVIEW:重みづけ、接触点周囲に影響
    """

    def saveStress(self, homogenization_data):
        # set h5 data
        self.sigma_numpy = self.sigma.to_numpy()
        resolution = self.resolution.to_numpy()
        grid_start = self.grid_start.to_numpy()
        for j in range(self.resolution[1]):
            for i in range(self.resolution[0]):
                k = Homogenization()
                flat_idx = j * self.resolution[0] + i
                k.h = self.h
                k.resolution = resolution
                k.grid_p = grid_start + self.h * np.array([i, j])
                k.sigma = self.sigma_numpy[flat_idx]
                homogenization_data.homogenization.append(k)

    """
    def calcSaveStress(self, homogenization_data):
        self.calcStress(self.p, self.a, self.f)
        # set h5 data
        resolution = self.resolution.to_numpy()
        grid_start = self.grid_start.to_numpy()
        for j in range(self.resolution[1]):
            for i in range(self.resolution[0]):
                k = Homogenization()
                flat_idx = j * self.resolution[0] + i
                k.h = self.h
                k.resolution = resolution
                k.grid_p = grid_start + self.h * np.array([i, j])
                k.sigma = self.sigma[flat_idx].to_numpy()
                homogenization_data.homogenization.append(k)
    """
