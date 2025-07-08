import h5py
import numpy as np

class ShapeTemplate:
    def __init__(self):
        self.density = 1.0
        self.size_mean = 0.1
        self.size_std = 0.01
        self.vertex_list = np.array([[0.0, 0.0]]).transpose()

class Element:
    def __init__(self):
        self.template_name = ""
        self.size_ratio = 0.1
        self.center_of_mass = np.array([0.0, 0.0]).transpose()
        self.rotation_angle = 0.0
        self.velocity = np.array([0.0, 0.0]).transpose()
        self.angular_velocity = 0.0
        self.static = True

class SceneData:
    def __init__(self):
        self.templates = {}
        self.elements = []

    def __load_templates(self, fileName):
        self.templates.clear()
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
        self.elements.clear()
        if fileName != "" and fileName[len(fileName)-3:] == ".h5":

            template_idx_to_name_dict = {}
            with h5py.File(fileName, 'r') as h5_elements:
                tn_group = h5_elements['template_name_dict']
                template_idxs = list(tn_group.keys())

                for i in template_idxs:
                    template_idx_to_name_dict.update([(int(i), tn_group[i][0].decode())])

                e_group = h5_elements['elements_2d']

                template_idx_array = np.array(e_group['template_idx'], dtype=np.int32)
                size_ratio_array = np.array(e_group['size_ratio'], dtype=np.float64)
                center_of_mass_array = np.array(e_group['center_of_mass'], dtype=np.float64)
                rotation_angle_array = np.array(e_group['rotation_angle'], dtype=np.float64)
                velocity_array = np.array(e_group['velocity'], dtype=np.float64)
                angular_velocity_array = np.array(e_group['angular_velocity'], dtype=np.float64)
                static_array = np.array(e_group['static'], dtype=np.int8)
                # static_array = np.array(e_group['static'], dtype=np.bool)

                num_elems = len(size_ratio_array)

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
                    self.elements.append(e)

    def load(self, fn_template, fn_element):
        self.__load_templates(fn_template)
        self.__load_elements(fn_element)

    def save(self, fn_templates, fn_elements):
        template_name_dict = {}
        count = 0

        with h5py.File(fn_templates, 'w') as h5_templates:
            st_group = h5_templates.create_group('shape_templates_2d')

            for t in self.templates:
                gt = st_group.create_group(t)
                gt.create_dataset('density', data = self.templates[t].density)
                gt.create_dataset('size_mean', data = self.templates[t].size_mean)
                gt.create_dataset('size_std', data = self.templates[t].size_std)
                gt.create_dataset('vertex_list', data = self.templates[t].vertex_list)
                template_name_dict.update([(t, count)])
                count += 1

        with h5py.File(fn_elements, 'w') as h5_elements:
            tn_group = h5_elements.create_group('template_name_dict')
            for tn in template_name_dict:
                ds = tn_group.create_dataset(str(template_name_dict[tn]), (1, ), dtype='S{}'.format(len(tn)), compression="gzip")
                ds[0] = tn.encode()

            e_group = h5_elements.create_group('elements_2d')

            template_idx_array = np.zeros(len(self.elements), dtype=np.int32)
            size_ratio_array = np.zeros(len(self.elements), dtype=np.float64)
            center_of_mass_array = np.zeros((2, len(self.elements)), dtype=np.float64)
            rotation_angle_array = np.zeros(len(self.elements), dtype=np.float64)
            velocity_array = np.zeros((2, len(self.elements)), dtype=np.float64)
            angular_velocity_array = np.zeros(len(self.elements), dtype=np.float64)
            static_array = np.zeros(len(self.elements), dtype=np.int8)

            for i in range(len(self.elements)):
                template_idx_array[i] = int(template_name_dict[self.elements[i].template_name])
                size_ratio_array[i] = self.elements[i].size_ratio
                center_of_mass_array[:,i] = self.elements[i].center_of_mass
                rotation_angle_array[i] = self.elements[i].rotation_angle
                velocity_array[:,i] = self.elements[i].velocity
                angular_velocity_array[i] = self.elements[i].angular_velocity
                static_array[i] = 0 if self.elements[i].static == False else 1

            e_group.create_dataset('template_idx', data = template_idx_array)
            e_group.create_dataset('size_ratio', data = size_ratio_array)
            e_group.create_dataset('center_of_mass', data = center_of_mass_array)
            e_group.create_dataset('rotation_angle', data = rotation_angle_array)
            e_group.create_dataset('velocity', data = velocity_array)
            e_group.create_dataset('angular_velocity', data = angular_velocity_array)
            e_group.create_dataset('static', data = static_array)
