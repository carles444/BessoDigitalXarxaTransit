from src.graph.obj.Vertex import Vertex
from src.graph.obj.Edge import Edge
import math
import json

def euclidean_distance(point1 : tuple, point2 : tuple) -> float:
    x_distance = point2[0] - point1[0]
    y_distance = point2[1] - point1[1]
    return math.sqrt((x_distance**2) + (y_distance**2))

class Graph:
    def __init__(self):
        self.vertices = {}
        self.edges = {}
        self.connections = []

    def add_vertex(self, vertex : Vertex) -> bool:
        if vertex.id in self.vertices.keys():
            return False
        self.vertices[vertex.id] = vertex
        return True
    
    def remove_vertex(self, id : str) -> bool:
        if not id in self.vertices.keys():
            return False
        for in_edge, out_edge in zip(self.vertices[id].in_edges, self.vertices[id].out_edges):
            self.edges.pop(in_edge)
            self.edges.pop(out_edge)
        
        new_connections = [conn for conn in self.connections if id not in conn]
        self.connections.clear()
        self.connections = new_connections

        self.vertices.pop(id)
        return True
    
    def add_edge(self, edge : Edge) -> bool:
        if edge.id in self.edges.keys():
            return False
        
        vertices = self.vertices.keys()
        if edge.dst_vertex not in vertices or edge.origin_vertex not in vertices:
            return False
        self.edges[edge.id] = edge
        self.vertices[edge.origin_vertex].out_edges.append(edge.id)
        self.vertices[edge.dst_vertex].in_edges.append(edge.id)
        self.connections.append([edge.origin_vertex, edge.dst_vertex])
        return True
    
    def remove_edge(self, id : str) -> bool:
        if not id in self.edges.keys():
            return False
        edge = self.edges[id]
        self.vertices[edge.origin_vertex].out_edges.remove(id)
        self.vertices[edge.dst_vertex].in_edges.remove(id)


        new_connections = [conn for conn in self.connections 
                           if conn[0] != edge.origin_vertex or conn[1] != edge.dst_vertex]
        self.connections.clear()
        self.connections = new_connections

    def get_distance(self, edge : Edge, type : str) -> float:
        point1 = self.verices[edge.origin_vertex].position
        point2 = self.verices[edge.dst_vertex].position

        x_distance = point2[0] - point1[0]
        y_distance = point2[1] - point1[1]
        if type == 'euclidean':
            return math.sqrt((x_distance**2) + (y_distance**2))

    def get_distance(self, vertex1 : Vertex, vertex2 : Vertex, type : str) -> float:
        point1 = vertex1.position
        point2 = vertex2.position

        if type == 'euclidean':
            return euclidean_distance(point1, point2)
        
    def init_distance_edge_weights(self, distance_type = 'euclidean'):
        for edge in self.edges.values():
            v1 = self.vertices[edge.origin_vertex]
            v2 = self.vertices[edge.dst_vertex]
            edge.weight = self.get_distance(v1, v2, distance_type)

    def __json__(self) -> str: 
        vertices = []
        edges = []
        for v in self.vertices.values():
            vertices.append(v.__json__())
        for e in self.edges.values():
            edges.append(e.__json__())

        return {
            "vertices": vertices,
            "edges": edges
        }




