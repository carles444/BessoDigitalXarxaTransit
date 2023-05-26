

class Vertex:
    def __init__(self, id : str, position : tuple):
        self.id = id
        self.position = position
        self.out_edges = []
        self.in_edges = []

        # Dijkstra parameters
        self.dijkstra_dist = 0
        self.dijkstra_visited = False
        self.dijkstra_edge = None

    def __json__(self):
        return {
            "id": self.id,
            "position": self.position,
            "out_edges": self.out_edges,
            "in_edges": self.in_edges
        }
    
    def __lt__(self, v):
        return self.dijkstra_dist < v.dijkstra_dist