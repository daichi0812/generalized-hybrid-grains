import h5py
import numpy as np
from grainh5 import *


class AllSceneData:
    def __init__(self):
        self.templates = {}
        self.all_step_elements = []

    def __load_templates(self, fileName):
        if fileName != "" and fileName[len(fileName)-3:] == ".h5":
            with h5py.File(fileName, 'r') as h5_templates:
                st_group = h5_templates['shape_templates_2d']
                template_names = list(st_group.keys())
                #print(template_names)

                for t in template_names:
                    new_template = ShapeTemplate()
                    new_template.density = np.double(st_group[t]['density'])
                    new_template.size_mean = np.double(st_group[t]['size_mean'])
                    new_template.size_std = np.double(st_group[t]['size_std'])
                    new_template.vertex_list = np.array(st_group[t]['vertex_list'])

                    self.templates.update([(t, new_template)])

    def __load_elements(self, fileName):
        if fileName != "" and fileName[len(fileName)-3:] == ".h5":

            template_idx_to_name_dict = {}
            with h5py.File(fileName, 'r') as h5_elements:
                keys = list(map(str, h5_elements.keys()))
                keys.remove('force_num')
                keys = list(map(int, keys))
                newlist = sorted(keys)
                for t in newlist:
                    data_group = h5_elements[str(t)]
                    e_group = data_group['elements_2d']
                    tn_group = data_group['template_name_dict']
                    template_idxs = list(tn_group.keys())
                
                    for i in template_idxs:
                        template_idx_to_name_dict.update([(int(i), tn_group[i][0].decode())])

                    template_idx_array = np.array(e_group['template_idx'], dtype=np.int32)
                    size_ratio_array = np.array(e_group['size_ratio'], dtype=np.float64)
                    center_of_mass_array = np.array(e_group['center_of_mass'], dtype=np.float64)
                    rotation_angle_array = np.array(e_group['rotation_angle'], dtype=np.float64)
                    velocity_array = np.array(e_group['velocity'], dtype=np.float64)
                    angular_velocity_array = np.array(e_group['angular_velocity'], dtype=np.float64)
                    static_array = np.array(e_group['static'], dtype=np.int8)
                    # static_array = np.array(e_group['static'], dtype=np.bool)

                    num_elems = len(size_ratio_array)

                    scene_data = SceneData()
                    for i in range(num_elems):
                        e = Element()
                        e.template_name = template_idx_to_name_dict[template_idx_array[i]]
                        e.size_ratio = size_ratio_array[i]
                        e.center_of_mass = center_of_mass_array[:,i]
                        e.rotation_angle = rotation_angle_array[i]
                        e.velocity = velocity_array[:,i]
                        # e.angular_velocity = angular_velocity_array[i]
                        e.static = False if static_array[i] == 0 else True
                        e.static = static_array[i]
                        scene_data.elements.append(e)
                    scene_data.templates = self.templates
                    self.all_step_elements.append(scene_data)
                    

    def load(self, fn_template, fn_element):
        self.__load_templates(fn_template)
        self.__load_elements(fn_element)

    def __load_elements_from_idx(self, fileName, idx):
        self.all_step_elements.clear()
        if fileName != "" and fileName[len(fileName) - 3:] == ".h5":

            template_idx_to_name_dict = {}
            with h5py.File(fileName, 'r') as h5_elements:
                #idx番目のkeyを取得する
                keys = list(map(str, h5_elements.keys()))
                if 'force_num' in keys:
                    keys.remove('force_num')
                keys = list(map(int, keys))
                newlist = sorted(keys)

                data_group = h5_elements[str(newlist[idx])]
                e_group = data_group['elements_2d']
                tn_group = data_group['template_name_dict']
                template_idxs = list(tn_group.keys())

                for i in template_idxs:
                    template_idx_to_name_dict.update([(int(i), tn_group[i][0].decode())])

                template_idx_array = np.array(e_group['template_idx'], dtype=np.int32)
                size_ratio_array = np.array(e_group['size_ratio'], dtype=np.float64)
                center_of_mass_array = np.array(e_group['center_of_mass'], dtype=np.float64)
                rotation_angle_array = np.array(e_group['rotation_angle'], dtype=np.float64)
                velocity_array = np.array(e_group['velocity'], dtype=np.float64)
                angular_velocity_array = np.array(e_group['angular_velocity'], dtype=np.float64)
                static_array = np.array(e_group['static'], dtype=np.int8)
                # static_array = np.array(e_group['static'], dtype=np.bool)

                num_elems = len(size_ratio_array)

                scene_data = SceneData()
                for i in range(num_elems):
                    e = Element()
                    e.template_name = template_idx_to_name_dict[template_idx_array[i]]
                    e.size_ratio = size_ratio_array[i]
                    e.center_of_mass = center_of_mass_array[:, i]
                    e.rotation_angle = rotation_angle_array[i]
                    e.velocity = velocity_array[:, i]
                    # e.angular_velocity = angular_velocity_array[i]
                    e.static = False if static_array[i] == 0 else True
                    e.static = static_array[i]
                    scene_data.elements.append(e)
                scene_data.templates = self.templates
                self.all_step_elements.append(scene_data)

    def load_from_idx(self, fn_template, fn_element, idx):
        self.__load_templates(fn_template)
        self.__load_elements_from_idx(fn_element, idx)

    @staticmethod
    def get_key_list(filename):
        if filename == "" or filename[len(filename) - 3:] != ".h5":
            return

        with h5py.File(filename, 'r') as h5_elements:
            keys = list(map(str, h5_elements.keys()))

            if 'force_num' in keys:
                keys.remove('force_num')

            return sorted(list(map(int, keys)))


def grain_data_num(pre_fn):
    with h5py.File(pre_fn, 'r') as h5_elements:
        keys = list(map(str, h5_elements.keys()))
        keys.remove('force_num')
        keys = list(map(int, keys))
        newlist = sorted(keys)
        data_num = len(newlist)
    return data_num
