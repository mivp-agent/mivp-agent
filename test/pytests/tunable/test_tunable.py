import pytest
from typing import Tuple
from mivp_agent.tunable import Tunable, BooleanDim, generate_config
from mivp_agent.tunable.configs import only_set

from fake.tunables import DummyTunable1, DummyTunable2


def test_space_validation():
    with pytest.raises(TypeError):
        Tunable()

    class BadSpace(Tunable):
        def feasible_space(self) -> Tuple[str, dict]:
            return 'blah', {'blea', 'blah'}
    
    test = BadSpace()
    with pytest.raises(AssertionError):
        test._feasible_space
    
    class GoodSpace(Tunable):
        def feasible_space(self) -> Tuple[str, dict]:
            return 'blah', {
                'blah': BooleanDim()
            }
    
    GoodSpace()._feasible_space


def test_value_validation():
    tunable = DummyTunable1()

    with pytest.raises(AssertionError):
        tunable.set_value('bool', 'not bool')
    tunable.set_value('bool', True)
    tunable.set_value('bool', False)

    with pytest.raises(AssertionError):
        tunable.set_value('nums', 'NaN')
    with pytest.raises(AssertionError):
        tunable.set_value('nums', 6)
    tunable.set_value('nums', 3)


def test_from_config():
    tunable = DummyTunable1()
    tunable.from_config({
        'tunable1': {
            'bool': True,
            'nums': 3
        }
    })
    
    assert tunable.get_value('bool')
    assert tunable.get_value('nums') == 3


def test_to_config():
    tunable1 = DummyTunable1()
    tunable2 = DummyTunable2()

    config = {
        'tunable1': {
            'bool': True,
            'nums': 3
        },
        'tunable2': {
            'bool':  False,
            'nums': 8
        }
    }

    tunable1.from_config(config)
    tunable2.from_config(config)

    assert generate_config(tunable1, tunable2) == config

    # Test filtering
    tunable1.reset_values()
    tunable1.set_value('nums', 4)

    assert generate_config(tunable1, rule=only_set) == {
        'tunable1': {
            'nums': 4
        }
    }
