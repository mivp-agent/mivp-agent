from abc import ABC, abstractmethod


class Dimension(ABC):
    def __init__(self):
        self._set = self.define_dim()

    @abstractmethod
    def define_dim(self) -> set:
        '''
        This method will be called directly after __init__ to define the possible values for dimension.

        It will be used to validate user input and define feasible spaces for searching.
        '''
        pass

    def validate(self, value) -> bool:
        return value in self._set
    
    def __str__(self) -> str:
        return f'{self._set}'


class BooleanDim(Dimension):
    boolean_space = set((True, False))

    def define_dim(self) -> set:
        return self.boolean_space


class IntDim(Dimension):
    def __init__(self, start, stop, step=1):
        '''
        This class defines a dimension of ints with specified `start` and `stop` and optional `step` kwarg.

        The underlying functionality uses Python's `range` function to generate a set defining the space / dimension.
        '''
        self.start = start
        self.stop = stop
        self.step = step

        super().__init__()

    def define_dim(self) -> set:
        return set(range(self.start, self.stop, self.step))