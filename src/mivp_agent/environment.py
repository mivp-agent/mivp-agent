from abc import ABC, abstractmethod

class Environment(ABC):
    def __enter__(self):
        self.setup()
        return self
    
    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def teardown(self):
        pass
    
    def __exit__(self):
        self.teardown()
        return