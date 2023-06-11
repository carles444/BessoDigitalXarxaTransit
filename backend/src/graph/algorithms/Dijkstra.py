from src.graph.obj.Graph import Graph, Vertex, Edge
from src.configuration.ConfigurationManager import ConfigurationManager
import heapq
from src.simulator.SUMOSimulator import SUMOSimulator
from src.logging.Logger import Logger

INF = ConfigurationManager.get_instance().get_component_value('infinite')
logger = Logger.get_instance()


def get_aditional_cost(edge_id, stat_name, alpha=1) -> float:
    stats = SUMOSimulator.get_instance().stats
    if stat_name not in stats.keys():
        return 0
    if edge_id not in stats[stat_name].keys():
        return 0
    return alpha * stats[stat_name][edge_id]
    
def no_additional_cost(edge_id, alpha=1) -> float:
    return 0

def Dikstra(graph : Graph, initVertex : Vertex, add_cst_stat : str='none') -> None:
    for v in graph.vertices.values():
        v.dijkstra_dist = INF
        v.dijkstra_visited = False
        v.dijkstra_edge = None
    initVertex.dijkstra_dist = 0

    heap = [initVertex]
    heapq.heapify(heap)

    while len(heap) > 0:
        curr_vertex = heapq.heappop(heap)
        for edge_id in curr_vertex.out_edges:
            edge = graph.edges[edge_id]
            dst_vertex = graph.vertices[edge.dst_vertex]
            additional_cost = get_aditional_cost(edge_id, add_cst_stat)

            if dst_vertex.dijkstra_dist < curr_vertex.dijkstra_dist + edge.weight + additional_cost:
                continue

            dst_vertex.dijkstra_dist = curr_vertex.dijkstra_dist + edge.weight + additional_cost
            dst_vertex.dijkstra_edge = edge_id

            if not dst_vertex.dijkstra_visited:
                heapq.heappush(heap, dst_vertex)

        curr_vertex.dijkstra_visited |= True


def get_shortest_path(graph : Graph, v_i : Vertex, v_f : Vertex) -> list:
    shortest_path = []
    Dikstra(graph, v_i)
    d_edge = v_f.dijkstra_edge
    print(d_edge)

    while d_edge is not None:
        shortest_path.append(d_edge)
        d_vertex = graph.edges[d_edge].origin_vertex
        d_edge = graph.vertices[d_vertex].dijkstra_edge

    shortest_path.reverse()
    return shortest_path




