from typing import Tuple
from abc import ABC, abstractmethod
from mivp_agent.tunable.dimensions import Dimension

NOT_SET = 'NOT_SET'


class Tunable(ABC):
    def _set_vars(self):
        '''
        The following function and associated `_namespace` and `_feasible_space` properties allow for initialization of a single copy of the feasible space from the concrete implementation of `feasible_space()`. An alternative to the current pattern was to use `__init__(namespace, feasible_space)` however this requires that all implementors of Tunable and their subclasses to remember to call `super().__init__()`. I find requirements to call `__init__()` as not very intuitive to first time users. Thus, the following pattern.
        '''
        self.__namespace, self.__feasible_space = self.feasible_space()

        assert isinstance(self.__namespace, str), "Namespaces must be strings"

        assert isinstance(self.__feasible_space, dict), "Feasible space returned non dictionary type"
        for value in self.__feasible_space.values():
            assert isinstance(value, Dimension), f'Found non-dimension "{value}" inside of feasible space'

    @property
    def _feasible_space(self):
        try:
            return self.__feasible_space
        except AttributeError:
            self._set_vars()
        
        return self.__feasible_space
    
    @property
    def _namespace(self):
        try:
            return self.__namespace
        except AttributeError:
            self._set_vars()
        return self.__namespace
    
    def reset_values(self):
        self.__values = {}
        for key in self._feasible_space:
            self.__values[key] = NOT_SET

    @property
    def _values(self):
        try:
            return self.__values
        except AttributeError:
            self.reset_values()
        return self.__values

    @abstractmethod
    def feasible_space(self) -> Tuple[str, dict]:
        '''
        This method should be implemented to return a namespace for this tunable to use, along with the definition of the feasible space.
        
        Example:
        ```
            space = {
                'use_ec2': BooleanSpace(),
            }
            return 'my-namespace', space
        ```
        '''
        pass

    def from_config(self, config: dict, reset=False):
        '''
        Takes key pairs specified by the config dictionary and runs them through `set_value(...)`.

        If kwarg `reset` is set to `True` all existing values will be reset before being loaded from the config
        '''
        if reset:
            self.reset_values()

        assert self._namespace in config, f'Provided config does not contain the "{self._namespace}" namespace associated with this tunable'
        assert isinstance(config[self._namespace], dict), f'Value occupying the "{self._namespace}" position in the config is not a dictionary'

        for key, value in config[self._namespace].items():
            self.set_value(key, value)

    def set_value(self, key, value):
        assert key in self._feasible_space, f'key "{key}" not found in feasible space.'

        # Get the definition of the dimension and validate the value
        dim = self._feasible_space[key]
        assert dim.validate(value), f'Value "{value}" is not a valid point on the "{key}" Dimension'

        self._values[key] = value
    
    def get_value(self, key):
        return self._values[key]

    def unspecified_dimensions(self) -> dict:
        '''
        This method will return a dictionary of all dimensions which are currently unspecified in the feasible space along with the definition of that dimension.
        '''
        unspecified = {}
        for key, value in self._value.items():
            if value == NOT_SET:
                unspecified[key] = self._feasible_space[key]

        return unspecified

    def is_concrete(self) -> bool:
        '''
        This method will check if all locations on dimensions all dimensions have been specified.
        '''
        for key, value in self._value.items():
            if value == NOT_SET:
                return False
        return True
