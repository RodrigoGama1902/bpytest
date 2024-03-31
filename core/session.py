import random


class Session:
    _instance = None

    def __init__(self):
        if self._instance is None:
            self.id = random.randint(0, 1000000)
            self._instance = self
        else:
            self.id = self._instance.id


session = Session()
