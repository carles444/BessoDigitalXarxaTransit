from src.graph.obj.Graph import Graph, Vertex, Edge
from src.configuration.ConfigurationManager import ConfigurationManager
import heapq

INF = ConfigurationManager.get_instance().get_component_value('infinite')


def Dikstra(graph : Graph, initVertex : Vertex) -> None:
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

            if dst_vertex.dijkstra_dist < curr_vertex.dijkstra_dist + edge.weight:
                continue

            dst_vertex.dijkstra_dist = curr_vertex.dijkstra_dist + edge.weight
            dst_vertex.dijkstra_edge = edge_id

            if not dst_vertex.dijkstra_visited:
                heapq.heappush(heap, dst_vertex)

        curr_vertex.dijkstra_visited |= True


def get_shortest_path(graph : Graph, v_i : Vertex, v_f : Vertex) -> list:
    shortest_path = []
    Dikstra(graph, v_i)
    d_edge = v_f.dijkstra_edge

    while d_edge is not None:
        shortest_path.append(d_edge)
        d_vertex = graph.edges[d_edge].origin_vertex
        d_edge = graph.vertices[d_vertex].dijkstra_edge

    shortest_path.reverse()
    return shortest_path




