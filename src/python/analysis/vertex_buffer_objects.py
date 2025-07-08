import numpy as np

from OpenGL.GL import *
from OpenGL.GLUT import *


class LineVBO:
    def __init__(self):
        self.VBOData_vertices = np.zeros(2, dtype=ctypes.c_float)
        self.VBOData_colors = np.zeros(4, dtype=ctypes.c_float)
        self.VBOData_indices = np.zeros(2, dtype=ctypes.c_uint)
        self.VBO_buffers = [3]
        self.VBO_buffers[0] = None
        self.vertex_num_offset = 0
        self.color_num_offset = 0
        self.index_num_offset = 0

    def set_num_elements(self, num_lines):
        self.VBOData_vertices = np.zeros(2 * num_lines * 2, dtype=ctypes.c_float)
        self.VBOData_colors = np.zeros(4 * num_lines * 2, dtype=ctypes.c_float)
        self.VBOData_indices = np.zeros(2 * num_lines, dtype=ctypes.c_uint)
        self.vertex_num_offset = 0
        self.color_num_offset = 0
        self.index_num_offset = 0

    def gen_buffers(self):
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

    def draw_vbo(self, line_width):
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        if self.VBO_buffers[0] is not None:
            glBindBuffer(GL_ARRAY_BUFFER, self.VBO_buffers[0])
            glVertexPointer(2, GL_FLOAT, 0, None)
            glBindBuffer(GL_ARRAY_BUFFER, self.VBO_buffers[1])
            glColorPointer(4, GL_FLOAT, 0, None)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.VBO_buffers[2])
            glLineWidth(line_width)
            glDrawElements(GL_LINES, self.VBOData_indices.shape[0], GL_UNSIGNED_INT, None)
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)

    def register_line_to_data_array(self, v0, v1, c0, c1):
        self.VBOData_vertices[(self.vertex_num_offset * 2):(self.vertex_num_offset * 2 + 2)] = v0
        self.VBOData_colors[(self.color_num_offset * 4):(self.color_num_offset * 4 + 4)] = c0
        self.VBOData_vertices[((self.vertex_num_offset + 1) * 2):((self.vertex_num_offset + 1) * 2 + 2)] = v1
        self.VBOData_colors[((self.color_num_offset + 1) * 4):((self.color_num_offset + 1) * 4 + 4)] = c1

        self.VBOData_indices[self.index_num_offset * 2] = self.vertex_num_offset
        self.VBOData_indices[self.index_num_offset * 2 + 1] = self.vertex_num_offset + 1

        self.vertex_num_offset += 2
        self.color_num_offset += 2
        self.index_num_offset += 1


class TriangleVBO:
    def __init__(self):
        self.VBOData_vertices = np.zeros(3, dtype=ctypes.c_float)
        self.VBOData_colors = np.zeros(4, dtype=ctypes.c_float)
        self.VBOData_indices = np.zeros(3, dtype=ctypes.c_uint)
        self.VBO_buffers = [3]
        self.VBO_buffers[0] = None
        self.vertex_num_offset = 0
        self.color_num_offset = 0
        self.index_num_offset = 0

    def set_num_elements(self, num_triangles):
        self.VBOData_vertices = np.zeros(2 * num_triangles * 3, dtype=ctypes.c_float)
        self.VBOData_colors = np.zeros(4 * num_triangles * 3, dtype=ctypes.c_float)
        self.VBOData_indices = np.zeros(3 * num_triangles, dtype=ctypes.c_uint)
        self.vertex_num_offset = 0
        self.color_num_offset = 0
        self.index_num_offset = 0

    def gen_buffers(self):
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

    def draw_vbo(self, line_width):
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        if self.VBO_buffers[0] is not None:
            glBindBuffer(GL_ARRAY_BUFFER, self.VBO_buffers[0])
            glVertexPointer(2, GL_FLOAT, 0, None)
            glBindBuffer(GL_ARRAY_BUFFER, self.VBO_buffers[1])
            glColorPointer(4, GL_FLOAT, 0, None)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.VBO_buffers[2])
            glLineWidth(line_width)
            glDrawElements(GL_TRIANGLES, self.VBOData_indices.shape[0], GL_UNSIGNED_INT, None)
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)

    def register_triangle_to_data_array(self, v_list, c_list):
        data_num = len(v_list)
        for i in range(data_num):
            self.VBOData_vertices[((self.vertex_num_offset + i) * 2):((self.vertex_num_offset + i) * 2 + 2)] = v_list[i]
            self.VBOData_colors[((self.color_num_offset + i) * 4):((self.color_num_offset + i) * 4 + 4)] = c_list[i]
            self.VBOData_indices[self.index_num_offset * 3 + i] = self.vertex_num_offset + i

        self.vertex_num_offset += data_num
        self.color_num_offset += data_num
        self.index_num_offset += round(data_num / 3)
