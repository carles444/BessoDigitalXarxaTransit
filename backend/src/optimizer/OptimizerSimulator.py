from src.configuration.ConfigurationManager import ConfigurationManager
from src.graph.obj.Graph import Graph, Vertex, Edge
from src.Utils.Utils import prettify, get_last_dir_path, find_file_extension
import xml.etree.ElementTree as ET
from src.simulator.obj.Route import Route
from src.simulator.obj.Vehicle import Vehicle
import os, sys
import traci
import numpy as np
from src.logging.Logger import Logger
from src.simulator.SceneManager import SceneManager
from tqdm import tqdm

def init_SUMO():
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        sys.exit("please declare environment variable 'SUMO_HOME'")


class OptimizerSimulator:
    def __init__(self, scene_path) -> None:
        self.configuration_manager = ConfigurationManager.get_instance()
        self.scene_manager = SceneManager(scene_path)
        self.scene_path = scene_path
        self.traci_running = False
        self.running_vehicles = []
        self.stats = {}
        self.step = 0
        self.logger = Logger.get_instance()

    def find_config_file(self, extension : str = 'sumocfg') -> str:
        try:
            scene_files = os.listdir(self.scene_path)
            for file in scene_files:
                if file.endswith(extension):
                    return file
            return None
        except:
            raise Exception(f'Could not find the configuration file in the path: {self.scene_path}')

    def configure_simulation(self) -> list:
        init_SUMO()
        sumo_binary = self.configuration_manager.get_component_value('SUMO_bin_path')
        sumo_config_file = self.find_config_file()
        if sumo_config_file is None:
            raise Exception(f'Could not find the configuration file in the path: {self.scene_path}')

        cmd = [sumo_binary, '-c', os.path.join(self.scene_path, sumo_config_file)]
        return cmd
    
    def init_traci(self, scene_path : str=""):
        if self.traci_running:
            return
        if scene_path is not None and scene_path != "":
            self.scene_path = scene_path
        cmd = self.configure_simulation()
        traci.start(cmd)
        self.traci_running = True
    
    def close_traci(self):
        if self.traci_running:
            traci.close()

    def simulate(self, scene_path : str="") -> dict:
        if not self.traci_running:
            self.init_traci(scene_path)
        self.simulation_loop()
        self.close_traci()
        return self.stats

    def load_stats(self) -> None:
        if not self.traci_running:
            return
       
        edges = traci.edge.getIDList()
        if 'total_waiting_time' not in self.stats.keys():
            self.stats['total_waiting_time'] = 0
        for edge_id in edges:
            self.stats['total_waiting_time'] += traci.edge.getWaitingTime(edge_id)

    def simulation_loop(self) -> None:
        total_steps = self.configuration_manager.get_component_value('optimizer_simulation_steps')        
        self.logger.info(f'Simulating scene: {os.path.basename(self.scene_path)}...')
        for _ in range(total_steps):
            self.load_stats()
            traci.simulationStep()
            self.step += 1

    def get_graph(self) -> Graph:
        return self.scene_manager.get_graph(self.scene_path)
        

         
    


