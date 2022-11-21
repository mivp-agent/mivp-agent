from abc import ABC, abstractmethod
from typing import Any

from readerwriterlock.rwlock import RWLockFair


class Model(ABC):
    def __new__(cls, *args, **kwargs):
        instance = super(Model, cls).__new__(cls, *args, **kwargs)
        instance._rwlock = RWLockFair()

        return instance

    @abstractmethod
    def inference(self, state: Any) -> Any:
        pass

    def rlock(self):
        return self._rwlock.gen_rlock()
    
    def wlock(self):
        return self._rwlock.gen_wlock()
