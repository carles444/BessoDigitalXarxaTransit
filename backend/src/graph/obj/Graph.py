from src.graph.obj.Vertex import Vertex
from src.graph.obj.Edge import Edge
import math
import json
import copy
from src.configuration.ConfigurationManager import ConfigurationManager

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
        
        for in_edge_id in self.vertices[id].in_edges:
            in_edge = self.edges[in_edge_id]
            from_v = self.vertices[in_edge.origin_vertex]
            from_v.out_edges.remove(in_edge_id)
            self.edges.pop(in_edge_id)
        
        for out_edge_id in self.vertices[id].out_edges:
            out_edge = self.edges[out_edge_id]
            to_v = self.vertices[out_edge.dst_vertex]
            to_v.in_edges.remove(out_edge_id)
            self.edges.pop(out_edge_id)

        new_connections = [conn for conn in self.connections if id not in conn]
        self.connections.clear()
        self.connections = new_connections

        self.vertices.pop(id)
        return True
    
    def add_edge(self, edge : Edge, allow_intersection=False) -> bool:
        if edge.id in self.edges.keys():
            return False
        
        if [edge.origin_vertex, edge.dst_vertex] in self.connections:
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
        if id in self.vertices[edge.origin_vertex].out_edges:
            self.vertices[edge.origin_vertex].out_edges.remove(id)
        if id in self.vertices[edge.dst_vertex].in_edges:
            self.vertices[edge.dst_vertex].in_edges.remove(id)

        new_connections = [conn for conn in self.connections 
                           if not (conn[0] == edge.origin_vertex and conn[1] == edge.dst_vertex)]
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
            if edge.origin_vertex not in self.vertices.keys() or edge.dst_vertex in self.vertices.keys():
                edge.weight = ConfigurationManager.get_instance().get_component_value('infinite')
                continue
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
    
    def get_max_coords(self) -> tuple:
        max_coords = [0, 0]
        for vertex in self.vertices.values():
            max_coords[0] = max(max_coords[0], vertex.position[0])
            max_coords[1] = max(max_coords[1], vertex.position[1])
        return max_coords



