from src.Utils.Utils import prettify, get_last_dir_path, find_file_extension
from src.graph.obj.Graph import Graph, Vertex, Edge
import xml.etree.ElementTree as ET
from src.logging.Logger import Logger
import random
import copy
from src.Utils.UniqueIDGenerator import UniqueIDGenerator 
from src.simulator.SceneManager import SceneManager
from src.configuration.ConfigurationManager import ConfigurationManager
import os
import shutil
from src.simulator.RouteManager import RouteManager
from src.optimizer.OptimizerSimulator import OptimizerSimulator

class Constraints:
    def __init__(self, max_edges_change : int = 3, max_nodes_change : int = 3):
        self.max_edges_change = max_edges_change
        self.max_nodes_change = max_nodes_change
        self.min_edge_lanes = 1
        self.max_edge_lanes = 3
        self.max_lane_width = 3
        self.nodes_position_sens = 50


class Optimizer:
    def __init__(self, scene_path):
        self.scene_path = scene_path
        self.logger = Logger.get_instance()
        self.constraints = Constraints()
        self.id_generator = UniqueIDGenerator()
        self.scene_manager = SceneManager(scene_path)
        self.configuration_manager = ConfigurationManager.get_instance()
        self.tmp_scenes_path = self.configuration_manager.get_component_value('optimizer_tmp_scenes_path')
    
    def _randomize_vertex(self, graph : Graph) -> None:
        add_vertex = random.random() > 0.5
        if add_vertex:
            max_coords = graph.get_max_coords()
            x = random.randint(0, max_coords[0])
            y = random.randint(0, max_coords[1])
            id = self.id_generator.generate_id()
            graph.add_vertex(Vertex(id, (x, y)))
        else:
            n_vertices = len(graph.vertices.keys())
            vertex_index = random.randint(0, n_vertices - 1)
            vertex_id = list(graph.vertices.keys())[vertex_index]
            graph.remove_vertex(vertex_id)

    def _randomize_edge(self, graph : Graph) -> None:
        if len(graph.vertices.keys()) <= 1:
            return
        add_edge = random.random() > 0.5
        if add_edge:
            from_node_id, to_node_id = -1, -1
            exists_connection = True
            tries = 0
            while (from_node_id == to_node_id or exists_connection) and tries < 5:
                vertices_ids = list(graph.vertices.keys())
                from_node_id = vertices_ids[random.randint(0, len(vertices_ids) - 1)]
                to_node_id = vertices_ids[random.randint(0, len(vertices_ids) - 1)]
                exists_connection = [from_node_id, to_node_id] in graph.connections
                tries += 1
            if from_node_id == to_node_id or exists_connection:
                return
            lane_width = random.randint(1, self.constraints.max_lane_width)
            graph.add_edge(Edge(self.id_generator.generate_id(), from_node_id, to_node_id, lanes=lane_width))
        else:
            edges_ids = list(graph.edges.keys())
            edge_id = edges_ids[random.randint(0, len(edges_ids) - 1)]
            graph.remove_edge(edge_id)
        graph.init_distance_edge_weights()

    def apply_random_modifications(self, graph : Graph) -> Graph:
        mod_graph = copy.deepcopy(graph)
        n_changes = random.randint(1, self.constraints.max_nodes_change)
        for i in range(n_changes):
            modify_vertex = random.random() < 0.50
            if modify_vertex:
                self._randomize_vertex(mod_graph)
            else:
                self._randomize_edge(mod_graph)
        return mod_graph


    def optimize_escene(self):
        generation_size = self.configuration_manager.get_component_value('optimizer_generation_size')
        max_epochs = self.configuration_manager.get_component_value('optimizer_epochs')
        graph = self.scene_manager.get_graph()
        
        epoch = 0
        while epoch <= max_epochs:
            self.logger.info(f'===== EPOCH {epoch} =====')
            # tmp path creation
            if os.path.exists(self.tmp_scenes_path):
                shutil.rmtree(self.tmp_scenes_path)

            os.mkdir(self.tmp_scenes_path)
            simulation_folders = []

            for i in range(generation_size):
                self.logger.info(f'Creating configuration {i}')
                # apply random modifications
                tmp_graph = self.apply_random_modifications(graph)

                # simulation path creation
                tmp_path = os.path.join(self.tmp_scenes_path, 'sim_' + str(i))
                simulation_folders.append(tmp_path)
                os.mkdir(tmp_path)

                # generate scene configuration files
                self.scene_manager.generate_nod_edg_files(tmp_graph, tmp_path)
                self.scene_manager.generate_net_file(tmp_path)
                self.scene_manager.generate_cfg_file(tmp_path)
                
                # generate random trips
                steps = self.configuration_manager.get_component_value('optimizer_simulation_steps')
                RouteManager(tmp_path).generate_random_trips(steps=steps)
            
            simulators = []
            for simulation_path in simulation_folders:
                simulation = OptimizerSimulator(simulation_path)
                simulation.simulate()
                simulators.append(simulation)
            
            for simulator in simulators:
                print(simulator.stats['total_waiting_time'])

            epoch += 1
        


            

