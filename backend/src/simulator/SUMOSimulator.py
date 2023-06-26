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
import json


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
        self.scene_manager = SceneManager(self.scene_path)
        self.traci_running = False
        self.to_add_routes = [] # touples list
        self.running_vehicles = []
        self.stats = {}
        self.vehicle_stats = {}
        self.step = 0
        self.logger = Logger.get_instance()
        self.traci_vehicle_stats = [
            traci.constants.VAR_LANE_INDEX,
            traci.constants.VAR_SPEED,
            traci.constants.VAR_WAITING_TIME,
            traci.constants.VAR_DISTANCE
        ]

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
            self.traci_running ^= self.traci_running

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
        self.stats['edges_fuel_consumption'] = {}
        self.stats['edges_avg_speed'] = {}
        self.stats['edges_waiting_time']['total_waiting_time'] = 0
        for edge_id in edges:
            self.stats['edges_waiting_time']['total_waiting_time'] += traci.edge.getWaitingTime(edge_id)
            self.stats['edges_waiting_time'][edge_id] = traci.edge.getWaitingTime(edge_id)
            self.stats['edges_avg_speed'][edge_id] = traci.edge.getLastStepMeanSpeed(edge_id)
            self.stats['edges_fuel_consumption'][edge_id] = traci.edge.getFuelConsumption(edge_id)



    def handle_vehicle_end(self, vehicle_id : str):
        depart_step = self.vehicle_stats[vehicle_id]['depart_step']
        self.logger.info(f'Vehicle with Id: {vehicle_id} in {self.step - depart_step} steps')

    def load_vehicle_data(self, vehicle_id : str) -> None:
        data = traci.vehicle.getSubscriptionResults(vehicle_id) 
        self.vehicle_stats[vehicle_id]['subscription_stats'] = data

    def check_routes(self) -> None:
        if not self.traci_running:
            return
        
        ended_vehicles = []
        for v_id in self.running_vehicles:
            if v_id not in traci.vehicle.getIDList() and v_id in self.vehicle_stats.keys():
                self.handle_vehicle_end(v_id)
                ended_vehicles.append(v_id)
                continue
            depart_time = traci.vehicle.getDeparture(v_id)
            if not depart_time > 0:
                continue
            elif v_id not in self.vehicle_stats.keys():
                self.vehicle_stats[v_id] = {}
            if 'depart_step' not in self.vehicle_stats[v_id].keys():
                self.vehicle_stats[v_id]['depart_step'] = depart_time
            self.load_vehicle_data(v_id)

        for v_id in ended_vehicles:
            self.running_vehicles.remove(v_id)
        
        for route_vehicle in self.to_add_routes:
            route = route_vehicle[0]
            vehicle = route_vehicle[1]
            traci.route.add(route.id, route.path)
            traci.vehicle.add(vehicle.id, vehicle.route_id)
            traci.vehicle.subscribe(vehicle.id, self.traci_vehicle_stats)
            self.running_vehicles.append(vehicle.id)
        self.to_add_routes = []

    def simulation_loop(self) -> None:
        total_steps = self.configuration_manager.get_component_value('simulation_steps')        
        junctions = traci.junction.getIDList()
        edges = traci.edge.getIDList()
        
        for _ in range(total_steps):
            # self.logger.info(f'Step: {self.step}')
            self.check_routes()
            if self.step % 1 == 0:
                self.load_stats()
            vehicles = traci.vehicle.getIDList()
            stopped_vehicles = 0
            for v_id in vehicles:
                if traci.vehicle.getSpeed(v_id) == 0:
                    stopped_vehicles += 1
            # print(f'Step: {self.stats["avg_speed"]}')
            traci.simulationStep()
            self.step += 1
        stats_file = self.configuration_manager.get_component_value('stats_file_path')  
        self.save_stats_to_file(os.path.join(self.scene_path, stats_file))   

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
    
    def get_avg_speed(self, edges: list) -> float:
        stat_key = 'edges_avg_speed'
        avg_speed = 0
        total_edges = 0
        total_avg_speed = 0
        if stat_key not in self.stats.keys():
         return avg_speed
        for edge_id in edges:
            if not edge_id in self.stats[stat_key].keys():
                continue
            total_edges += 1
            total_avg_speed += self.stats[stat_key][edge_id]
        
        return total_avg_speed / total_edges
    
    def get_fuel_consumption(self, edges: list, stat_key) -> float:
        avg_fuel_cons = 0
        total_edges = 0
        total_avg_fuel_cons = 0
        if stat_key not in self.stats.keys():
            return avg_fuel_cons
        for edge_id in edges:
            if not edge_id in self.stats[stat_key].keys():
                continue
            total_edges += 1
            total_avg_fuel_cons += self.stats[stat_key][edge_id]
        return total_avg_fuel_cons / total_edges
    
    def save_stats_to_file(self, filepath: str) -> None:
        with open(filepath, 'w') as file:
            json.dump(self.stats, file, indent=2)

    def get_graph(self) -> Graph:
        return self.scene_manager.get_graph(self.scene_path)
        

         
    


