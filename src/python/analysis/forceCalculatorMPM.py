import math

import h5py
import numpy
import numpy as np


def linear_integral(x):
    abs_x = math.fabs(x)
    if abs_x < 1.0:
        return abs_x * abs_x * abs_x * 0.5 - abs_x * abs_x + 2.0 / 3.0
    elif abs_x < 2.0:
        return -abs_x * abs_x * abs_x / 6.0 + abs_x * abs_x - 2.0 * abs_x + 4.0 / 3.0
    else:
        return 0.0


def linear_integral_grad(x):
    abs_x = math.fabs(x)
    sgn_x = 1.0 if x >= 0.0 else -1.0

    if abs_x < 1.0:
        return (abs_x * abs_x * 1.5 - 2.0 * abs_x) * sgn_x
    elif abs_x < 2.0:
        return (-abs_x * abs_x * 0.5 + 2.0 * abs_x - 2.0) * sgn_x
    else:
        return 0.0


class StencilIterator:
    def __init__(self, m_min, m_max):
        self.m_min = m_min
        self.m_max = m_max
        self.m_current = np.copy(self.m_min)
        self.stopFlag = False

    def __iter__(self):
        return self

    def __next__(self):
        if self.stopFlag:
            raise StopIteration()

        if numpy.all(self.m_current == self.m_max):
            self.stopFlag = True

        value = self.m_current.copy()

        self.m_current[0] += 1
        if self.m_current[0] > self.m_max[0]:
            self.m_current[0] = self.m_min[0]
            self.m_current[1] += 1

        return value


class ParticleData:
    def __init__(self):
        self.sigma = np.array([[0.0, 0.0], [0.0, 0.0]]).transpose()
        self.center_of_mass = np.array([0.0, 0.0]).transpose()
        self.density = 10.0
        self.volume = 0.000001
        self.J = 1.0


class Grid:
    def __init__(self):
        self.resolution = np.array([0.0, 0.0]).transpose()
        self.h = 0.01
        self.grid_max = np.array([0.0, 0.0]).transpose()
        self.grid_min = np.array([0.0, 0.0]).transpose()
        self.f = []

    def get_stencil(self, xp):
        start = np.floor((xp - self.grid_min) / self.h) - 2
        end = np.floor((xp - self.grid_min) / self.h) + 2
        grid_max = self.resolution - 1
        return StencilIterator(np.minimum(np.maximum(start, 0), grid_max), np.minimum(np.maximum(end, 0), grid_max))

    def weight_grad(self, xp, grid_idx):
        dx = xp - (self.grid_min + grid_idx * self.h + self.h / 2.0)

        wx = linear_integral(dx[0] / self.h)
        wy = linear_integral(dx[1] / self.h)

        grad_wx = wy * linear_integral_grad(dx[0] / self.h) / self.h
        grad_wy = wx * linear_integral_grad(dx[1] / self.h) / self.h

        return np.array([grad_wx, grad_wy])

    def flat_idx(self, grid_idx):
        return int(grid_idx[1] * self.resolution[0] + grid_idx[0])


class ForceCalculatorMPM:
    def __init__(self, file_name):
        self.particles = []
        self.grid = Grid()
        self.start_timestep = 0
        self.end_timestep = 0
        self.pre_load(file_name)

    def pre_load(self, file_name):
        with h5py.File(file_name, "r") as h5:
            keys = list(map(int, h5.keys()))
            sorted_keys = sorted(keys)
            self.start_timestep = sorted_keys[0]
            self.end_timestep = sorted_keys[-1] + 1

    def _load_data(self, file_name, timestep):
        self.particles.clear()
        self.grid.f.clear()

        if file_name != "" and file_name[len(file_name) - 3:] == ".h5":
            with h5py.File(file_name, "r") as h5:
                data_group = h5[str(timestep)]
                h_group = data_group['homogenization']

                center_of_mass_array = np.array(h_group['center_of_mass'], dtype=np.float64)
                grid_pos_array = np.array(h_group['grid_p'], dtype=np.float64)
                sigma_array = np.array(h_group['sigma'], dtype=np.float64)
                density_array = np.array(h_group['density'], dtype=np.float64)
                volume_array = np.array(h_group['volume'], dtype=np.float64)
                j_array = np.array(h_group['J'], dtype=np.float64)
                resolution = np.array(h_group['resolution'], dtype=np.int32)
                h = np.array(h_group['h'], dtype=np.float64)

                particle_num = len(center_of_mass_array[0])

                self.grid.grid_min = grid_pos_array[:, 0]
                self.grid.grid_max = grid_pos_array[:, len(grid_pos_array[0]) - 1]
                self.grid.h = h
                self.grid.resolution = resolution

                for i in range(self.grid.resolution[0] * self.grid.resolution[1]):
                    self.grid.f.append(np.array([0.0, 0.0]).transpose())

                for i in range(particle_num):
                    particle = ParticleData()
                    particle.sigma = sigma_array[:, :, i]
                    particle.center_of_mass = center_of_mass_array[:, i]
                    particle.density = density_array[i]
                    particle.volume = volume_array[i]
                    particle.J = j_array[i]
                    self.particles.append(particle)

    def load_from_timestep(self, file_name, timestep):
        self._load_data(file_name, timestep)

    def save(self, file_name, timestep):
        with h5py.File(file_name, 'a') as h5:
            force_array = np.zeros((2, len(self.grid.f)), dtype=np.float64)

            for i in range(len(self.grid.f)):
                force_array[:, i] = self.grid.f[i]

            group_name = str(timestep) + "/homogenization"

            if h5.get(group_name + "/force"):
                del h5[group_name + "/force"]

            h5.create_dataset(group_name + "/force", data=force_array)

    def compute_force(self):
        for particle in self.particles:
            grids = self.grid.get_stencil(particle.center_of_mass)
            for grid_idx in grids:
                wg = self.grid.weight_grad(particle.center_of_mass, grid_idx)
                idx = self.grid.flat_idx(grid_idx)
                self.grid.f[idx] -= particle.volume * particle.J * (particle.sigma @ wg)

    def get_range(self):
        return range(self.start_timestep, self.end_timestep)

    def print_particle_data(self):
        i = 0
        for particle in self.particles:
            print("--- " + str(i) + " ---")
            print("sigma: \n" + str(particle.sigma))
            print("position: \n" + str(particle.center_of_mass))
            print("volume: \n" + str(particle.volume))
            print("J: \n" + str(particle.J))
            print("density: \n" + str(particle.density))
            print()
            i += 1

    def print_grid_data(self):
        print("grid_max: \n" + str(self.grid.grid_max))
        print("grid_min: \n" + str(self.grid.grid_min))
        print("resolution: \n" + str(self.grid.resolution))
        print("h: \n" + str(self.grid.h))
        print("f: \n" + str(len(self.grid.f)))

    def print_data(self):
        self.print_particle_data()
        self.print_grid_data()


def main():
    file_name = "/Users/itotake/Documents/graduation/GeneralizedHybridGrainsResearch/build/Save/serialized_sigma.h5"

    force_calculator_mpm = ForceCalculatorMPM(file_name)
    time_steps = force_calculator_mpm.get_range()

    for timestep in time_steps:
        force_calculator_mpm.load_from_timestep(file_name, timestep)
        force_calculator_mpm.compute_force()
        force_calculator_mpm.save(file_name, timestep)
        print("ended: " + str(timestep))


if __name__ == "__main__":
    main()
