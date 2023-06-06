from src.simulator.SUMOSimulator import SUMOSimulator
from src.graph.algorithms.Dijkstra import Dikstra, get_shortest_path
from src.simulator.RouteManager import RouteManager
import src.graph.algorithms.Greedy as Greedy
import src.graph.algorithms.AStar as Astar
import threading
import time
from src.optimizer.Optimizer import Optimizer
from src.configuration.ConfigurationManager import ConfigurationManager

def add_route_thread():
    time.sleep(5)
    ds_gen = SUMOSimulator.get_instance()
    # ds_gen.simulate(use_gui=False)
    graph = ds_gen.get_graph()
    # GREEDY
    visits = [
        graph.vertices['0'],
        graph.vertices['1'],
        graph.vertices['2'],
        graph.vertices['5'],
        graph.vertices['4'],
    ]
    visits = [
        graph.vertices['0'],
        graph.vertices['5'],
        graph.vertices['19'],
    ]
    
    greedy_path = Greedy.get_greedy_track(graph, visits)
    # AStar_path = Astar.get_optimal_path(graph, visits, Astar.Strategy.SHORTEST_PATH)
    AStar_path_tr = Astar.get_optimal_path(graph, visits, Astar.Strategy.TRAFFIC)

    #ds_gen.add_route(path)
    rm = RouteManager()

    rm.add_route_simulation(AStar_path_tr)
    rm.add_route_simulation(greedy_path)


def main() -> None:
    conf = ConfigurationManager.get_instance()
    default_path = conf.get_component_value('default_simulation_path')
    optimizer = Optimizer(default_path)
    optimizer.optimize_escene()
    exit(0)
    ds_gen = SUMOSimulator.get_instance()
    # ds_gen.simulate(use_gui=False)
    graph = ds_gen.get_graph()
    Dikstra(graph, graph.vertices['0'])
    path = get_shortest_path(graph, graph.vertices['0'], graph.vertices['15'])
    rm = RouteManager()
    rm.clean_routes()
    #rm.generate_random_trips()
    #rm.add_route(path)
    simulation_thread = threading.Thread(target=ds_gen.simulate)
    route_thread = threading.Thread(target=add_route_thread)

    simulation_thread.start()
    route_thread.start()

   
    route_thread.join()
    simulation_thread.join()
    a = 3


if __name__ == '__main__':
    main()