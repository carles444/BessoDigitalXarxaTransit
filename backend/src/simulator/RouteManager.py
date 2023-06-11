import xml.etree.ElementTree as ET
from src.configuration.ConfigurationManager import ConfigurationManager
from src.Utils.Utils import get_last_dir_path, prettify
from src.simulator.obj.Route import Route
from src.simulator.obj.Vehicle import Vehicle
import os
import subprocess
from src.simulator.SUMOSimulator import SUMOSimulator

class RouteManager:
    def __init__(self, routes_file_path=None) -> None:
        self.configuration_manager = ConfigurationManager.get_instance()
        if routes_file_path is None:
            self.base_path = self.configuration_manager.get_component_value('default_simulation_path')
        else:
            self.base_path = routes_file_path
        routes_file_path = os.path.join(self.base_path, f'{get_last_dir_path(self.base_path)}.rou.xml')
        self.net_file_path = os.path.join(self.base_path, f'{get_last_dir_path(self.base_path)}.net.xml')
        self.routes_file_path = routes_file_path
        self.tree = None

    def add_route(self, path : list) -> None:
        self.prepare_routes()
        root = self.tree.getroot()
        edges = " ".join(path)

        vType = ET.SubElement(root, 'vType', {
            'accel': '1.0',
            'decel': '5.0',
            'id': 'Car',
            'length': '2.0',
            'maxSpeed': '100',
            'sigma': '0.0'
        })

        route = ET.SubElement(root, 'route', {
            'id': 'route0',
            'edges': edges,
        })

        vehicle = ET.SubElement(root, 'vehicle', {
            'depart': '50',
            'id': 'veh0',
            'route': 'route0',
            'type': 'Car',
            'color': '0, 0, 255'
        })

        self.tree.write(self.routes_file_path)

    def add_route_simulation(self, path: list) -> None:
        simulator = SUMOSimulator.get_instance()
        route = Route(path)
        vehicle = Vehicle(route.id)
        simulator.add_route(route, vehicle)

    def clean_routes(self) -> None:
        self.create_new_file()

    def create_new_file(self) -> None:
        root = ET.Element('routes')
        self.tree = ET.ElementTree(root)
        self.tree.write(self.routes_file_path)
    
    def prepare_routes(self) -> None:
        """Creates .rou.xml file if does not exists and loads the tree
        """
        if not os.path.isfile(self.routes_file_path):
            self.create_new_file()

        with open(self.routes_file_path, 'r') as file:
            try:
                self.tree = ET.parse(file)
            except ET.ParseError:
                # no content xml
                self.create_new_file()

    def generate_random_trips(self, steps=1000, period='0.2', fringe_factor=10) -> None:
        self.create_new_file()
        try:
            output_path = self.base_path
            trips_path = os.path.join(output_path, f'{get_last_dir_path(output_path)}.trips.xml')
            SUMO_path = self.configuration_manager.get_component_value('SUMO_base_path')
            random_trips_path = os.path.join(SUMO_path, 'tools/randomTrips.py')

            command = f'python \"{random_trips_path}\" -n \"{self.net_file_path}\" -e {steps}' \
                        f' -o \"{self.routes_file_path}\"' \
                        f' --period {period}' \
                        f' --fringe-factor {fringe_factor}' \
                        f' --prefix \"random_trip_\"'

            # --fringe fa que sigui molt més probable que els viatges comencin des de les afores 
            subprocess.run(command, shell=True)
        except Exception:
            print('Could not generate randomTrips.py')
            
