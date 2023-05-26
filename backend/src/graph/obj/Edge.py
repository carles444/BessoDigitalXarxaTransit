

class Edge:
    def __init__(self, id : str, origin_vertex : str, dst_vertex : str, weight : int = 0):
        self.id = id
        self.weight = weight
        self.dst_vertex = dst_vertex
        self.origin_vertex = origin_vertex

    def __json__(self):
        return {
            "id": self.id,
            "weight": self.weight,
            "dst_vertex": self.dst_vertex,
            "origin_vertex": self.origin_vertex
        }