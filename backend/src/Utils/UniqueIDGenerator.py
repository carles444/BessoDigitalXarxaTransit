import uuid

class UniqueIDGenerator:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.current_id = 0
        return cls.__instance

    def generate_id(self):
        self.current_id += 1
        return str(uuid.uuid4()) + "_" + str(self.current_id)