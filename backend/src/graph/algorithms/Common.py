from src.graph.obj.Graph import Graph, Vertex, Edge


def get_dikjstra_path(graph: Graph, v_f: Vertex) -> list:
    path = []
    d_edge = v_f.dijkstra_edge

    while d_edge is not None:
        path.append(d_edge)
        d_vertex = graph.edges[d_edge].origin_vertex
        d_edge = graph.vertices[d_vertex].dijkstra_edge

    path.reverse()
    return path