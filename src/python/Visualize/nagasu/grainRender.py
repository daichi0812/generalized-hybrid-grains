import cairo
import math
import xml.etree.ElementTree as ET
from grainh5 import *
import os
import sys
from allgrainh5 import *
from tqdm import tqdm
import ctypes


class InputNodeData:
    def __init__(self):
        self.templates_fn = ""
        self.elements_template = ""
        self.bb = np.array([0.0, 0.0, 1.0, 1.0])
        self.start = 0
        self.end = -1

    def setFromXMLNode(self, node):
        self.templates_fn = node.attrib['templates']
        self.elements_template = node.attrib['elements']
        self.bb = np.array([float(e) for e in node.attrib['bb'].split(' ')])
        self.start = int(node.attrib['start'])
        self.end = int(node.attrib['end'])

    def show(self):
        print('*** Input ***')
        print('  templates: ' + self.templates_fn)
        print('  elements: ' + self.elements_template)
        print('  bb: ' + str(self.bb))
        print('  start: ' + str(self.start))
        print('  end: ' + str(self.end))


class OutputNodeData:
    def __init__(self):
        self.type = "PDF"
        self.folder = ""
        self.size = np.array([200.0, 112.5])

    def setFromXMLNode(self, node):
        self.type = node.attrib['type']
        self.folder = node.attrib['folder']
        self.size = np.array([float(e) for e in node.attrib['size'].split(' ')])

    def show(self):
        print('*** Output ***')
        print('  type: ' + self.type)
        print('  folder: ' + self.folder)
        print('  size: ' + str(self.size))


class GrainRender:
    def __init__(self):
        self.data = SceneData()

    def computeBBForCircle(self, center, radius):
        return center - radius, center + radius

    def drawCircle(self, context, line_width, center, radius, angle, isStatic):
        context.arc(center[0], -center[1], radius, 0.0, math.pi * 2.0)
        context.close_path()
        if isStatic:
            context.set_source_rgb(0.9, 0.9, 0.9)
        else:
            context.set_source_rgb(245.6 / 255.0, 98.0 / 255.0, 112.0 / 255.0)
        context.fill_preserve()

        if isStatic:
            context.set_source_rgb(0.7, 0.7, 0.7)
        else:
            context.set_source_rgb(0, 0, 0)
        context.set_line_width(line_width)
        context.stroke()

        v0 = [center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle)]
        v1 = [center[0] - radius * math.cos(angle), center[1] - radius * math.sin(angle)]

        context.move_to(v0[0], -v0[1])
        context.line_to(v1[0], -v1[1])
        if isStatic:
            context.set_source_rgb(0.7, 0.7, 0.7)
        else:
            context.set_source_rgb(0, 0, 0)
        context.set_line_width(line_width)
        context.stroke()

    def computeBBForPolygon(self, center, size_ratio, vertex_list, angle):
        rot_mat = np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])
        num_vertices = vertex_list.shape[1]

        v0 = center + size_ratio * rot_mat @ vertex_list[:, 0]
        bb_min = v0
        bb_max = v0

        for i in range(num_vertices - 1):
            v = center + size_ratio * rot_mat @ vertex_list[:, i + 1]
            bb_min = np.minimum(bb_min, v)
            bb_max = np.maximum(bb_max, v)

        return bb_min, bb_max

    def drawPolygon(self, context, line_width, center, size_ratio, vertex_list, angle, isStatic):
        rot_mat = np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])
        num_vertices = vertex_list.shape[1]

        v0 = center + size_ratio * rot_mat @ vertex_list[:, 0]
        context.move_to(v0[0], -v0[1])

        for i in range(num_vertices - 1):
            v = center + size_ratio * rot_mat @ vertex_list[:, i + 1]
            context.line_to(v[0], -v[1])

        context.close_path()

        if isStatic:
            context.set_source_rgb(0.9, 0.9, 0.9)
        else:
            context.set_source_rgb(245.6 / 255.0, 98.0 / 255.0, 112.0 / 255.0)
        context.fill_preserve()

        if isStatic:
            context.set_source_rgb(0.7, 0.7, 0.7)
        else:
            context.set_source_rgb(0, 0, 0)
        context.set_line_width(line_width)
        context.stroke()

    def drawElements(self, context, line_width):
        for e in self.data.elements:
            vertex_list_e = self.data.templates[e.template_name].vertex_list
            num_vertices = vertex_list_e.shape[1]
            if num_vertices < 3:
                self.drawCircle(context, line_width, e.center_of_mass,
                                e.size_ratio * 0.5 * self.data.templates[e.template_name].size_mean, e.rotation_angle,
                                e.static)
            else:
                self.drawPolygon(context, line_width, e.center_of_mass, e.size_ratio,
                                 self.data.templates[e.template_name].vertex_list, e.rotation_angle, e.static)

    def computeAverageSize(self):
        bb_sz = np.zeros(2)
        count = 1
        for e in self.data.elements:
            vertex_list_e = self.data.templates[e.template_name].vertex_list
            num_vertices = vertex_list_e.shape[1]
            count += 1
            if num_vertices < 3:
                _bb_min, _bb_max = self.computeBBForCircle(e.center_of_mass, e.size_ratio * 0.5 * self.data.templates[
                    e.template_name].size_mean)
                bb_sz += _bb_max - _bb_min
            else:
                _bb_min, _bb_max = self.computeBBForPolygon(e.center_of_mass, e.size_ratio,
                                                            self.data.templates[e.template_name].vertex_list,
                                                            e.rotation_angle)
                bb_sz += _bb_max - _bb_min

        return bb_sz / count

    def render_to_context(self, surface, bb, size, line_width):
        context = cairo.Context(surface)

        context.set_source_rgb(1, 1, 1)  # White
        context.rectangle(0, 0, size[0], size[1])  # clear background
        context.fill()

        bb_w = bb[2] - bb[0]
        bb_h = bb[3] - bb[1]

        scale = size[0] / bb_w
        offset_w = -bb[0] * scale
        offset_h = bb_h * scale + bb[1] * scale

        context.translate(offset_w, offset_h)
        context.scale(scale * 0.5, scale * 0.5)

        self.drawElements(context, line_width)

    def render(self, bb, type, output_fn, size):
        average_size = self.computeAverageSize()
        line_width = 0.5 * (average_size[0] + average_size[1]) * 0.04

        if type.casefold() == "pdf":
            with cairo.PDFSurface(output_fn, size[0], size[1]) as surface:
                self.render_to_context(surface, bb, size, line_width)

        elif type.casefold() == "png":
            int_size = size.astype(int)
            with cairo.ImageSurface(cairo.FORMAT_RGB24, int_size[0], int_size[1]) as surface:
                self.render_to_context(surface, bb, int_size, line_width)
                surface.write_to_png(output_fn)

        else:
            print('We only support PDF or PNG for output format')
            exit(-1)

    def setData(self, input_node_data, output_node_data, frame_rate):
        max_count = 10000000
        range_max = input_node_data.end + 1
        if range_max <= 0:
            range_max = max_count

        element_fn = input_node_data.elements_template + ".h5"
        key_list = AllSceneData.get_key_list(element_fn)
        self.all_scene_data = AllSceneData()
        output = 0
        for i in tqdm(range(len(key_list) - 1)):
            if (i % int(frame_rate)) == 0:
                self.all_scene_data.load_from_idx(input_node_data.templates_fn, element_fn, i)
                self.data = self.all_scene_data.all_step_elements[0]
                basename_without_ext = str(output)
                output_basename = basename_without_ext + '.' + output_node_data.type
                output_fn = os.path.join(output_node_data.folder, output_basename)
                print("##### processing ", i, " #####")
                print("  templates: ", input_node_data.templates_fn)
                print("  output: ", output_fn)
                self.render(input_node_data.bb, output_node_data.type, output_fn, output_node_data.size)
                output = output + 1

class GrainRenderManager:
    def __init__(self, file_name):
        self.scene_data = SceneData()
        self.renderer = GrainRender()

        print('[AGGrainRender2D] Parsing xml file: ' + str(file_name))
        tree = ET.parse(file_name)
        root = tree.getroot()
        if root.tag != 'AGGrainRender2D':
            print('[AGGrainRender2D] Could not find root note AGGrainRender2D. Exiting...')
            exit(-1)

        input = root.find('input')
        self.inputNodeData = InputNodeData()
        self.inputNodeData.setFromXMLNode(input)

        output = root.find('output')
        self.outputNodeData = OutputNodeData()
        self.outputNodeData.setFromXMLNode(output)

    def show(self):
        print('[AGGrainRender2D] XML Data:')
        self.inputNodeData.show()
        self.outputNodeData.show()

    def render(self, frame_rate):
        self.renderer.setData(self.inputNodeData, self.outputNodeData, frame_rate)


def main():
    if len(sys.argv) <= 1:
        print("usage: python grainrender.py <xml file>")
        exit(-1)
    # app = QtWidgets.QApplication(sys.argv)
    # sys.exit(app.exec_())
    rm = GrainRenderManager(sys.argv[1])
    rm.show()
    rm.render(sys.argv[2])


if __name__ == "__main__":
    main()