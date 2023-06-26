from xml.etree import ElementTree
from xml.dom import minidom
from src.graph.obj.Graph import *
from src.configuration.ConfigurationManager import ConfigurationManager
import os
import random
import shutil


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def get_last_dir_path(path):
    # return path[::-1][:path[::-1].find('/')][::-1]
    return os.path.basename(os.path.normpath(path))


def find_file_extension(dir_path, extension):
    files = os.listdir(dir_path)
    for file in files:
        if file.endswith(extension):
            return os.path.join(dir_path, file)
    return None

def parse_random_graphs(path_dir) -> list:
    from src.simulator.SceneManager import SceneManager
    from src.simulator.RouteManager import RouteManager
    dir = ConfigurationManager.get_instance().get_component_value('optimizer_test_dir')
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.mkdir(dir)

    scene_manager = SceneManager(dir)
    path_list = []
    file_names = os.listdir(path_dir)
    for i, file_name in enumerate(file_names):
        with open(os.path.join(path_dir, file_name), 'r') as file:
            graph = Graph()
            for line in file.readlines():
                line = line.replace('\n', '')
                if line[0] == 'V' and line != 'VERTICES':
                    args = line.split(' ')
                    v = Vertex(args[0], (float(args[1])/15, float(args[2])/15))
                    graph.add_vertex(v)
                elif line[0] == 'E' and line != 'EDGES':
                    args = line.split(' ')
                    e = Edge(args[0], args[2], args[3], lanes=random.randint(1, 3), speed=float(random.randint(5, 26)))
                    graph.add_edge(e)
                    e = Edge(args[0], args[3], args[2], lanes=random.randint(1, 3), speed=float(random.randint(5, 26)))
                    graph.add_edge(e)
            os.mkdir(os.path.join(dir, file_name.split('.')[0]))
            scene_manager = SceneManager(os.path.join(dir, file_name.split('.')[0]))
            scene_manager.generate_nod_edg_files(graph)
            scene_manager.generate_net_file()
            RouteManager(scene_manager.scene_path).generate_random_trips()
            scene_manager.generate_cfg_file()
            path_list.append(scene_manager.scene_path)
    return path_list

