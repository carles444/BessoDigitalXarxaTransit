from src.graph.obj.Graph import Graph, Vertex, Edge
from src.configuration.ConfigurationManager import ConfigurationManager
from src.graph.algorithms.Dijkstra import get_shortest_path, Dikstra
from src.graph.algorithms.Common import get_dikjstra_path
from src.simulator.SUMOSimulator import SUMOSimulator
from copy import deepcopy
import numpy as np
import heapq
from abc import ABC, abstractclassmethod
from enum import Enum
import traci



INF = ConfigurationManager.get_instance().get_component_value('infinite')

class TrackComparisonStrategy(ABC):
    @abstractclassmethod
    def compare(self, track1, track2):
        pass


class ShortestPathEstimation(TrackComparisonStrategy):
    def __init__(self):
        self.simulation_stat = 'none'
    def compare(self, track1, track2):
        return (track1.cost + track1.estimation) < (track2.cost + track2.estimation)

class TrafficEstimationStrategy(TrackComparisonStrategy):
    def __init__(self) -> None:
        self.simulation_stat = 'edges_waiting_time'

    def compare(self, track1, track2):
        simulator = SUMOSimulator.get_instance()
        use_gui = ConfigurationManager.get_instance().get_component_value("use_gui")
        simulator.init_traci(use_gui=use_gui)

        alpha = 2
        w_time1 = simulator.get_waiting_time(track1.estimation_path) * alpha
        w_time2 = simulator.get_waiting_time(track2.estimation_path) * alpha

        estimation1 = track1.cost + track1.estimation + w_time1
        estimation2 = track2.cost + track2.estimation + w_time2
        return estimation1 < estimation2
    
class AvgSpeedStrategy(TrackComparisonStrategy):
    def __init__(self) -> None:
        self.simulation_stat = 'edges_avg_speed'
    
    def compare(self, track1, track2):
        simulator = SUMOSimulator.get_instance()
        use_gui = ConfigurationManager.get_instance().get_component_value("use_gui")
        simulator.init_traci(use_gui=use_gui)

        alpha = 3
        avg_speed1 = simulator.get_avg_speed(track1.estimation_path) * alpha
        avg_speed2 = simulator.get_avg_speed(track2.estimation_path) * alpha

        estimation1 = track1.cost + track1.estimation - avg_speed1
        estimation2 = track2.cost + track2.estimation - avg_speed2
        return estimation1 < estimation2
    
class FuelConsumptionStrategy(TrackComparisonStrategy):
    def __init__(self) -> None:
        self.simulation_stat = 'edges_fuel_consumption'
    
    def compare(self, track1, track2):
        simulator = SUMOSimulator.get_instance()
        use_gui = ConfigurationManager.get_instance().get_component_value("use_gui")
        simulator.init_traci(use_gui=use_gui)

        alpha = 3
        avg_speed1 = simulator.get_fuel_consumption(track1.estimation_path, self.simulation_stat) * alpha
        avg_speed2 = simulator.get_fuel_consumption(track2.estimation_path, self.simulation_stat) * alpha

        estimation1 = track1.cost + track1.estimation + avg_speed1
        estimation2 = track2.cost + track2.estimation + avg_speed2
        return estimation1 < estimation2

    
class Strategy(Enum):
    TRAFFIC = TrafficEstimationStrategy()
    SHORTEST_PATH = ShortestPathEstimation()
    FUEL_CONSUMPTION = FuelConsumptionStrategy()

class Track:
    def __init__(self, visited: list, path_order: list, estimation: float = INF, cost: float = 0) -> None:
        self.estimation = estimation
        self.visited = visited
        self.path_order = path_order
        self.cost = cost
        self.comparison_strategy = Strategy.SHORTEST_PATH
        self.estimation_path = []

    def set_comparison_strategy(self, strategy : TrackComparisonStrategy):
        self.comparison_strategy = strategy

    def __lt__(self, other):
        return self.comparison_strategy.value.compare(self, other)



class AStar:
    def __init__(self, graph: Graph, visits: list, estimation_strategy: str) -> None:
        self.cost_table = []
        self.path_table = []
        self.graph = graph
        self.visits = visits
        self.estimation_strategy = estimation_strategy
        # self.start_v = visits[0]
        # self.final_v = visits[-1]
        self.lower_bound = 0
        self.upper_bound = 0
        self.heap_queue = []
        heapq.heapify(self.heap_queue)

    def init_tables(self) -> tuple:
        for visit in self.visits:
            path_row, cost_row = [], []
            Dikstra(self.graph, visit, self.estimation_strategy.value.simulation_stat)
            for to_candidate in self.visits:
                path_row.append(get_dikjstra_path(self.graph, to_candidate))
                cost_row.append(to_candidate.dijkstra_dist)
            self.path_table.append(path_row)
            self.cost_table.append(cost_row)

    def calculate_estimation(self, track : Track, last_cost) -> None:
        if len(track.path_order) == 1:
            track.cost = 0
        else:
            track.cost = last_cost + self.cost_table[track.path_order[-2]][track.path_order[-1]]
        track.estimation = self.cost_table[track.path_order[-1]][len(self.visits)-1]
        track.estimation_path = self.path_table[track.path_order[-1]][len(self.visits)-1]

    def expand(self, track: Track) -> None:
        for i in range(1, len(self.visits)):
            if track.visited[i]:
                # el node ja ha estat visitat
                continue
            if len(track.path_order) != len(self.visits) - 1 and i == len(self.visits) - 1:
                # no s'han recorregut les altres parades abans de visitar l'ultim node
                continue
            child_track = Track(track.visited.copy(), track.path_order.copy(), i)
            child_track.visited[i] = True
            child_track.path_order.append(i)
            child_track.set_comparison_strategy(self.estimation_strategy)
            self.calculate_estimation(child_track, track.cost)
            heapq.heappush(self.heap_queue, child_track)

    def is_solution(self, track: Track) -> bool:
        return len(track.path_order) == len(self.visits)
    
    def build_final_path(self, track: Track) -> list:
        path = []
        for i in range(len(track.path_order)-1):
            path += self.path_table[track.path_order[i]][track.path_order[i + 1]]

        return path

    def __call__(self) -> list:
        self.init_tables()
        init_track = Track([False for _ in self.visits], [0], 0, 0)
        init_track.set_comparison_strategy(self.estimation_strategy)
        init_track.visited[0] = True
        heapq.heappush(self.heap_queue, init_track)

        while len(self.heap_queue) > 0:
            track = heapq.heappop(self.heap_queue)
            if self.is_solution(track):
                return self.build_final_path(track)
            self.expand(track)

        return []
    

def get_optimal_path(graph: Graph, visits: list, estimation_strategy: Strategy=Strategy.SHORTEST_PATH) -> list:
    astar = AStar(graph, visits, estimation_strategy)
    return astar()