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
import multiprocessing
import time

class Constraints:
    def __init__(self, max_edges_change : int = 3, max_nodes_change : int = 3):
        cm = ConfigurationManager.get_instance()
        self.max_edges_change = cm.get_component_value("optimizer_max_edges_change")
        self.max_nodes_change = cm.get_component_value("optimizer_max_nodes_change")
        self.min_lane_width = cm.get_component_value("optimizer_min_lane_width")
        self.max_lane_width = cm.get_component_value("optimizer_max_lane_width")
        self.nodes_position_sens = cm.get_component_value("optimizer_nodes_position_sens")


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
            x = random.randint(0, max_coords[0] // self.constraints.nodes_position_sens)
            y = random.randint(0, max_coords[1] // self.constraints.nodes_position_sens)
            x *= self.constraints.nodes_position_sens
            y *= self.constraints.nodes_position_sens
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
            lane_width = random.randint(self.constraints.min_lane_width, self.constraints.max_lane_width)
            graph.add_edge(Edge(self.id_generator.generate_id(), from_node_id, to_node_id, lanes=lane_width))
        else:
            edges_ids = list(graph.edges.keys())
            edge_id = edges_ids[random.randint(0, len(edges_ids) - 1)]
            graph.remove_edge(edge_id)
        graph.init_distance_edge_weights()

    def apply_random_modifications(self, graph : Graph) -> Graph:
        mod_graph = copy.deepcopy(graph)
        n_changes = random.randint(1, self.constraints.max_nodes_change)
        for _ in range(n_changes):
            self._randomize_vertex(mod_graph)

        n_changes = random.randint(1, self.constraints.max_edges_change)
        for _ in range(n_changes):
            self._randomize_edge(mod_graph)
        return mod_graph

    def create_optimized_scene(self, graph : Graph) -> None:
        dst_path = self.configuration_manager.get_component_value('optimizer_optimized_scene_path')
        if os.path.exists(dst_path):
            shutil.rmtree(dst_path)
        os.mkdir(dst_path)

        self.scene_manager.generate_nod_edg_files(graph, dst_path)
        self.scene_manager.generate_net_file(dst_path)
        self.scene_manager.generate_cfg_file(dst_path)
        steps = self.configuration_manager.get_component_value('optimizer_simulation_steps')
        RouteManager(dst_path).generate_random_trips(steps=steps)

    def _execute_simulation(self, simulator : OptimizerSimulator) -> dict:
        return simulator.simulate()

    def _crete_configurations(self, args):
        graph, configuration_number = args
        try:
            self.logger.info(f'Creating configuration {configuration_number}')
            # apply random modifications
            tmp_graph = self.apply_random_modifications(graph)

            # simulation path creation
            tmp_path = os.path.join(self.tmp_scenes_path, 'sim_' + str(configuration_number))
            os.mkdir(tmp_path)

            # generate scene configuration files
            self.scene_manager.generate_nod_edg_files(tmp_graph, tmp_path)
            self.scene_manager.generate_net_file(tmp_path)
            self.scene_manager.generate_cfg_file(tmp_path)
            
            # generate random trips
            steps = self.configuration_manager.get_component_value('optimizer_simulation_steps')
            RouteManager(tmp_path).generate_random_trips(steps=steps, period='1.2')

            return tmp_path
        except:
            return
            
    def optimize_escene(self):
        generation_size = self.configuration_manager.get_component_value('optimizer_generation_size')
        max_epochs = self.configuration_manager.get_component_value('optimizer_epochs')
        n_threads = self.configuration_manager.get_component_value('optimizer_concurrent_threads')
        graph = self.scene_manager.get_graph()
        
        epoch = 0
        while epoch < max_epochs:
            t_i = time.time()
            self.logger.info(f'===== EPOCH {epoch} =====')
            # tmp path creation
            if os.path.exists(self.tmp_scenes_path):
                shutil.rmtree(self.tmp_scenes_path)

            os.mkdir(self.tmp_scenes_path)

            graph_arguments = [graph for _ in range(generation_size)]
            pool = multiprocessing.Pool(processes=n_threads)
            simulation_folders = pool.map(self._crete_configurations, zip(graph_arguments, range(generation_size)))
            pool.close()
            pool.join()

            simulators = [OptimizerSimulator(sim_path) for sim_path in simulation_folders]

            try:  
                pool = multiprocessing.Pool(processes=n_threads)
                results = pool.map(self._execute_simulation, simulators)
                pool.close()
                pool.join()  
                best_simulation = min(results, key=lambda x : x['total_waiting_time'])
                graph = simulators[results.index(best_simulation)].get_graph()
            except:
                pass
            epoch += 1
            self.logger.info(f'EPCOH elapsed time: {time.time() - t_i}s')

        self.create_optimized_scene(graph)
        shutil.rmtree(self.tmp_scenes_path)

        


            

