from src.graph.obj.Graph import Graph, Vertex, Edge
from src.configuration.ConfigurationManager import ConfigurationManager
from src.graph.algorithms.Dijkstra import get_shortest_path, Dikstra
from src.graph.algorithms.Common import get_dikjstra_path

def shortest_dijkstra_dist(vertices: list) -> int:
    return vertices.index(min(vertices, key=lambda x : x.dijkstra_dist))

def get_greedy_track(graph: Graph, visits: list) -> list:
    if len(visits) <= 0:
        return []
    
    track = []
    current_v = visits[0]
    final_v = visits[-1]

    visits = visits[1:-1]

    if len(visits) == 0:
        return get_shortest_path(graph, current_v, final_v)

    while len(visits) > 0:
        Dikstra(graph, current_v)
        next_vertex_i = shortest_dijkstra_dist(visits)
        track += get_dikjstra_path(graph, visits[next_vertex_i])
        current_v = visits.pop(next_vertex_i)
    
    # path to final vertex
    Dikstra(graph, current_v)
    track += get_dikjstra_path(graph, final_v)
    
    return track