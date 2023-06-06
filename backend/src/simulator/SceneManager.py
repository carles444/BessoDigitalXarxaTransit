from src.configuration.ConfigurationManager import ConfigurationManager
from src.Utils.Utils import find_file_extension
from src.graph.obj.Graph import Graph, Vertex, Edge
import xml.etree.ElementTree as ET
from src.logging.Logger import Logger
import subprocess
import os

class SceneManager:
    def __init__(self, scene_path : str = None):
        self.scene_path = scene_path
        self.cnfg_manager = ConfigurationManager.get_instance()
        self.logger = Logger()

    def set_scena_path(self, scene_path : str) -> None:
        self.scene_path = scene_path

    def generate_cfg_file(self, scene_path : str = "") -> None:
        try:
            if scene_path == "":
                scene_path = self.scene_path
            sim_name = os.path.basename(scene_path)
            net_file = sim_name + '.net.xml'
            route_file = sim_name + '.rou.xml'
            sumocfg_file = os.path.join(scene_path, sim_name + '.sumocfg')

            configuration_root = ET.Element('configuration')
            input_el = ET.SubElement(configuration_root, 'input')
            ET.SubElement(input_el, 'net-file', {'value': net_file})
            ET.SubElement(input_el, 'route-files', {'value': route_file})
            time_el = ET.SubElement(configuration_root, 'time')
            ET.SubElement(time_el, 'begin', {'value': '0'})
            ET.ElementTree(configuration_root).write(sumocfg_file)
        except:
            self.logger.error(f'Could not generate .suomcfg file in the following path: {sumocfg_file}')



    def generate_net_file(self, scene_path : str = "") -> None:
        if scene_path == "" or scene_path is None:
            scene_path = self.scene_path
        if not os.path.exists(scene_path):
            self.logger.error(f'Error generating net file, scene path \"{scene_path}\" does not exist')
            return
        try:
            nodes_file = find_file_extension(scene_path, 'nod.xml')
            edges_file = find_file_extension(scene_path, 'edg.xml')
            net_file = os.path.join(scene_path, os.path.basename(scene_path) + '.net.xml')

            command = f'netconvert --node-files={nodes_file} --edge-files={edges_file}' \
                        f' --output-file={net_file}' \


            subprocess.run(command, shell=True)
        except Exception as e:
            self.logger.error('Could not generate randomTrips.py')

    def get_graph(self, scene_path : str = "") -> Graph:
        if scene_path == "":
            scene_path = self.scene_path
        if self.scene_path is None or not os.path.exists(scene_path):
            self.logger.error("Scene path does not exist")
            return
        graph = Graph()
        nodes_file = find_file_extension(scene_path, 'nod.xml')
        edges_file = find_file_extension(scene_path, 'edg.xml')

        try:
            with open(nodes_file, 'r') as file:
                nodes_tree = ET.parse(file)
                root = nodes_tree.getroot()
                for node in root.iter('node'):
                    node_id = node.get('id')
                    node_x = float(node.get('x'))
                    node_y = float(node.get('y'))
                    vertex = Vertex(node_id, (node_x, node_y))
                    graph.add_vertex(vertex)

            with open(edges_file, 'r') as file:
                nodes_tree = ET.parse(file)
                root = nodes_tree.getroot()
                for edg in root.iter('edge'):
                    edge_id = edg.get('id')
                    edge_from = edg.get('from')
                    edge_to = edg.get('to')
                    num_lanes = int(edg.get('numLanes'))
                    speed = float(edg.get('speed'))
                    edge = Edge(edge_id, edge_from, edge_to, weight=0, lanes=num_lanes, speed=speed)
                    graph.add_edge(edge)

            graph.init_distance_edge_weights(distance_type='euclidean')
            return graph
        except Exception as e:
            self.logger.error('Error generating graph from path: ' + scene_path)
            raise(e)
        
    def generate_nod_edg_files(self, graph : Graph, scene_path : str = "") -> None:
        if scene_path == "":
            scene_path = self.scene_path

        if not os.path.exists(scene_path):
            self.logger.error('Error generating .nod and .edg files, scene path not found')
            return
        try:
            scene_name = os.path.basename(scene_path)
            nod_file_path = os.path.join(scene_path, scene_name + '.nod.xml')
            edg_file_path = os.path.join(scene_path, scene_name + '.edg.xml')

            nod_root = ET.Element('nodes')
            for vertex in graph.vertices.values():
                ET.SubElement(nod_root, 'node', {
                    'id': vertex.id,
                    'x': str(vertex.position[0]),
                    'y': str(vertex.position[1]),
                    'type': vertex.type
                })

            edg_root = ET.Element('edges')
            for edge in graph.edges.values():
                ET.SubElement(edg_root, 'edge', {
                    'id': edge.id,
                    'from': edge.origin_vertex,
                    'to': edge.dst_vertex,
                    'num_lanes': str(edge.lanes),
                    'speed': str(edge.speed)
                })

            ET.ElementTree(nod_root).write(nod_file_path)
            ET.ElementTree(edg_root).write(edg_file_path)
        except Exception as e:
            self.logger.error('Error generating.nod and .edg files: ' + e)


