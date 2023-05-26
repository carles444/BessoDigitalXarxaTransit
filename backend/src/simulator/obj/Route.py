from src.Utils.UniqueIDGenerator import UniqueIDGenerator

class Route:
    def __init__(self,  path: list, id: str = ''):
        if id == '':
            id_generator = UniqueIDGenerator()
            id = id_generator.generate_id()
        self.id = id
        self.path = path