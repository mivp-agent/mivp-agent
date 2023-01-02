from typing import Tuple
from mivp_agent.tunable import Tunable, BooleanDim, IntDim


class DummyTunable1(Tunable):
    def feasible_space(self) -> Tuple[str, dict]:
        return 'tunable1', {
            'bool': BooleanDim(),
            'nums': IntDim(0, 6)
        }


class DummyTunable2(Tunable):
    def feasible_space(self) -> Tuple[str, dict]:
        return 'tunable2', {
            'bool': BooleanDim(),
            'nums': IntDim(6, 10, step=2)
        }