import os, sys
from src.configuration.ConfigurationManager import ConfigurationManager
import traci

def configure_SUMO():
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        sys.exit("please declare environment variable 'SUMO_HOME'")

def get_last_dir_path(path):
    # return path[::-1][:path[::-1].find('/')][::-1]
    return os.path.basename(os.path.normpath(path))

class SUMODatasetGenerator:
    def __init__(self) -> None:
        self.configuration_manager = ConfigurationManager()
        self.scenes_path = self.configuration_manager.get_component_value('scenes_path')
        self.available_scenes = []

    def find_config_file(self, scene : str, extension : str = 'sumocfg') -> str:
        try:
            scene_path = os.path.join(self.scenes_path, scene)
            scene_files = os.listdir(scene_path)
            for file in scene_files:
                if file.endswith(extension):
                    return file
        except:
            raise Exception(f'Could not find the configuration for the scene {scene}')
        pass

    def configure_simulations(self, use_gui : bool = False) -> list:
        configure_SUMO()
        cmds = []
        if use_gui:
            sumo_binary = self.configuration_manager.get_component_value('SUMO_gui_path')
        else:
            sumo_binary = self.configuration_manager.get_component_value('SUMO_bin_path')
        for scene in self.available_scenes:
            sumo_config_file = self.find_config_file(scene)
            cmd = [sumo_binary, '-c', os.path.join(self.scenes_path, scene, sumo_config_file)]
            cmds.append(cmd)
        return cmds
    
    def generate_dataset(self, scenes : list = []) -> None:
        self.available_scenes = os.listdir(self.scenes_path)
        if len(scenes) > 0:
            self.available_scenes = [s for s in self.available_scenes if s in scenes]
        cmds = self.configure_simulations()

        for scene, cmd in zip(self.available_scenes, cmds):
            self.simulate(scene, cmd)

    def simulate(self, scene_path : str, cmd : list) -> None:
        out_path = self.configuration_manager.get_component_value('dataset_out_path')
        total_steps = self.configuration_manager.get_component_value('simulation_steps')
        out_path = os.path.join(out_path, scene_path)
        out_file = None
        
        try:
            out_file = open(out_path , 'w+') # opens the file and creates it if doesn't exist
        except:
            print('error: cannot open out file')
            exit(-1)

        traci.start(cmd)
        for step in range(total_steps):
            vehicles = traci.vehicle.getIDList()
            stopped_vehicles = 0
            for v_id in vehicles:
                if traci.vehicle.getSpeed(v_id) == 0:
                    stopped_vehicles += 1
            out_file.write(f'{stopped_vehicles}\n')
            traci.simulationStep()
            
        traci.close()
        out_file.close()
            

    


