from src.configuration.ConfigurationManager import ConfigurationManager
from src.graph.obj.Graph import Graph, Vertex, Edge
from src.Utils.Utils import prettify, get_last_dir_path, find_file_extension
import xml.etree.ElementTree as ET
from src.simulator.obj.Route import Route
from src.simulator.obj.Vehicle import Vehicle
import os, sys
import traci
import numpy as np


def init_SUMO():
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        sys.exit("please declare environment variable 'SUMO_HOME'")


class SUMOSimulator:
    __instance = None

    @staticmethod
    def get_instance():
        if SUMOSimulator.__instance is None:
            SUMOSimulator()
        return SUMOSimulator.__instance
    
    def __init__(self) -> None:
        if SUMOSimulator.__instance is not None:
            raise Exception("This class is a singleton, use get_instance() method to get the instance.")
        else:
            SUMOSimulator.__instance = self
        self.configuration_manager = ConfigurationManager.get_instance()
        self.scene_path = self.configuration_manager.get_component_value('default_simulation_path')
        self.traci_running = False
        self.to_add_routes = [] # touples list
        self.stats = {}

    def find_config_file(self, extension : str = 'sumocfg') -> str:
        try:
            scene_files = os.listdir(self.scene_path)
            for file in scene_files:
                if file.endswith(extension):
                    return file
            return None
        except:
            raise Exception(f'Could not find the configuration file in the path: {self.scene_path}')

    def configure_simulation(self, use_gui : bool = False) -> list:
        init_SUMO()
        if use_gui:
            sumo_binary = self.configuration_manager.get_component_value('SUMO_gui_path')
        else:
            sumo_binary = self.configuration_manager.get_component_value('SUMO_bin_path')
        sumo_config_file = self.find_config_file()
        if sumo_config_file is None:
            raise Exception(f'Could not find the configuration file in the path: {self.scene_path}')

        cmd = [sumo_binary, '-c', os.path.join(self.scene_path, sumo_config_file)]
        return cmd
    
    def init_traci(self, scene_path : str="", use_gui : bool = False):
        if self.traci_running:
            return
        if scene_path is not None and scene_path != "":
            self.scene_path = scene_path
        cmd = self.configure_simulation(use_gui)
        traci.start(cmd)
        self.traci_running = True
    
    def close_traci(self):
        if self.traci_running:
            traci.close()

    def simulate(self, scene_path : str="", use_gui : bool = None) -> None:
        use_gui = self.configuration_manager.get_component_value('use_gui')
        if not self.traci_running:
            self.init_traci(scene_path, use_gui)
        self.simulation_loop()
        self.close_traci()

    def add_route(self, route: Route, vehicle: Vehicle) -> None:
        self.to_add_routes.append((route, vehicle))

    def load_stats(self) -> None:
        if not self.traci_running:
            return
        #traci.simulation.getArrivedIDList
        veh_ids = traci.vehicle.getIDList()
        speeds = []
        for v in veh_ids:
            speeds.append(traci.vehicle.getSpeed(v))
        if len(speeds) > 0:
            self.stats['avg_speed'] = np.mean(np.array(speeds))
        else:
            self.stats['avg_speed'] = 0

        edges = traci.edge.getIDList()
        self.stats['edges_waiting_time'] = {}
        self.stats['edges_waiting_time']['total_waiting_time'] = 0
        for edge_id in edges:
            self.stats['edges_waiting_time']['total_waiting_time'] += traci.edge.getWaitingTime(edge_id)
            self.stats['edges_waiting_time'][edge_id] = traci.edge.getWaitingTime(edge_id)


    def check_routes(self) -> None:
        if not self.traci_running:
            return
        for route_vehicle in self.to_add_routes:
            route = route_vehicle[0]
            vehicle = route_vehicle[1]
            traci.route.add(route.id, route.path)
            traci.vehicle.add(vehicle.id, vehicle.route_id)
        self.to_add_routes = []

    def simulation_loop(self) -> None:
        total_steps = self.configuration_manager.get_component_value('simulation_steps')        
        junctions = traci.junction.getIDList()
        edges = traci.edge.getIDList()
        
        for step in range(total_steps):
            self.check_routes()
            if step % 1 == 0:
                self.load_stats()
            vehicles = traci.vehicle.getIDList()
            stopped_vehicles = 0
            for v_id in vehicles:
                if traci.vehicle.getSpeed(v_id) == 0:
                    stopped_vehicles += 1
            print(f'Step: {self.stats["avg_speed"]}')
            traci.simulationStep()

    def get_waiting_time(self, edges: list) -> float:
        stat_key = 'edges_waiting_time'
        total_time = 0
        if stat_key not in self.stats.keys():
            return total_time
        for edge_id in edges:
            if not edge_id in self.stats[stat_key].keys():
                continue
            total_time += self.stats[stat_key][edge_id]
        return total_time

    def get_graph(self) -> Graph:
        if self.scene_path is None:
            return None
        graph = Graph()
        nodes_file = find_file_extension(self.scene_path, 'nod.xml')
        edges_file = find_file_extension(self.scene_path, 'edg.xml')

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
                    edge = Edge(edge_id, edge_from, edge_to)
                    graph.add_edge(edge)

            graph.init_distance_edge_weights(distance_type='euclidean')
            return graph
        except Exception as e:
            raise(e)
        

         
    


