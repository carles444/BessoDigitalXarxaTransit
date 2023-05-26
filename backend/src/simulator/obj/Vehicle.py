from src.Utils.UniqueIDGenerator import UniqueIDGenerator


class Vehicle:
    def __init__(self, route_id: str, id: str = ''):
        if id == '':
            id_generator = UniqueIDGenerator()
            id = id_generator.generate_id()
        self.id = id
        self.route_id = route_id
