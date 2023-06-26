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
import numpy as np
import json

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
        self.depart_times = []
        self.stats = {}
        self.step = 1
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

        cmd = [sumo_binary, '--ignore-route-errors', '--no-warnings', '-c', os.path.join(self.scene_path, sumo_config_file)]
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
        
        speeds = []
        co2_emissions = []
        nox_emissions = []
        pmx_emissions = []
        fuel_consumptions = []

        not_ended_index = []
        i = 0
        for v_id, d_step in zip(self.running_vehicles, self.depart_times):
            if v_id in traci.vehicle.getIDList():
                not_ended_index.append(i)
                i+=1
                continue
            if 'avg_route_end_time' not in self.stats.keys():
                self.stats['avg_route_end_time'] = self.step - d_step
                self.stats['total_routes_time'] = self.step - d_step
                self.stats['ended_routes'] = 1
            else:
                self.stats['total_routes_time'] += (self.step - d_step)
                self.stats['ended_routes'] += 1
                end_mean =  self.stats['total_routes_time'] / self.stats['ended_routes']
                self.stats['avg_route_end_time'] = end_mean
            i+=1
        self.running_vehicles = [self.running_vehicles[y] for y in not_ended_index]   
        self.depart_times = [self.depart_times[y] for y in not_ended_index]   

        for v_id in traci.vehicle.getIDList():
            if v_id not in self.running_vehicles:
                self.running_vehicles.append(v_id)
                self.depart_times.append(self.step)
            fuel_consumptions.append(traci.vehicle.getFuelConsumption(v_id))
            co2_emissions.append(traci.vehicle.getCO2Emission(v_id))
            nox_emissions.append(traci.vehicle.getNOxEmission(v_id))
            speeds.append(traci.vehicle.getSpeed(v_id))
            pmx_emissions.append(traci.vehicle.getPMxEmission(v_id))

        if 'co2_emission' not in self.stats.keys():
            self.stats['co2_emission'] = sum(co2_emissions)
        else:
            self.stats['co2_emission'] += sum(co2_emissions)
        
        if 'nox_emission' not in self.stats.keys():
            self.stats['nox_emission'] = sum(nox_emissions)
        else:
            self.stats['nox_emission'] += sum(nox_emissions)

        if 'pmx_emission' not in self.stats.keys():
            self.stats['pmx_emission'] = sum(pmx_emissions)
        else:
            self.stats['pmx_emission'] += sum(pmx_emissions)

        if 'fuel_consumption' not in self.stats.keys():
            self.stats['fuel_comsumption'] = sum(fuel_consumptions)
        else:
            self.stats['fuel_comsumption'] += sum(fuel_consumptions)


        edges = traci.edge.getIDList()
        if 'total_waiting_time' not in self.stats.keys():
            self.stats['total_waiting_time'] = 0
        for edge_id in edges:
            self.stats['total_waiting_time'] += traci.edge.getWaitingTime(edge_id)
        
        if len(speeds) != 0:
            mean_speed = np.mean(np.array(speeds))
        else:
            mean_speed = 0
        if 'total_speed' not in self.stats.keys():
            self.stats['total_speed'] = mean_speed
        else:
            self.stats['total_speed'] += mean_speed
        if 'avg_speed' not in self.stats.keys():
            self.stats['avg_speed'] = mean_speed
        else:
            self.stats['avg_speed'] = (self.stats['total_speed'] + mean_speed) / self.step

    def save_stats_to_file(self, filepath: str) -> None:
        with open(filepath, 'w') as file:
            json.dump(self.stats, file, indent=2)

    def simulation_loop(self) -> None:
        total_steps = self.configuration_manager.get_component_value('optimizer_simulation_steps')        
        self.logger.info(f'Simulating scene: {os.path.basename(self.scene_path)}...')
        for _ in range(total_steps):
            self.load_stats()
            traci.simulationStep()
            self.step += 1
        stats_file = self.configuration_manager.get_component_value('stats_file_path')  
        self.save_stats_to_file(os.path.join(self.scene_path, stats_file))      

    def get_graph(self) -> Graph:
        return self.scene_manager.get_graph(self.scene_path)
        

         
    


