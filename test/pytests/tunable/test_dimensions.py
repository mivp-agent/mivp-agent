import pytest
from mivp_agent.tunable import Dimension, BooleanDim, IntDim


def test_dimension_class():
    with pytest.raises(TypeError):
        Dimension()
    
    space = set(['a', 'b'])
    class DummyDim(Dimension): # noqa: E306
        def define_dim(self) -> set:
            return space
    
    inst = DummyDim()
    assert inst._set == space

    assert inst.validate('a') and inst.validate('b')
    assert not inst.validate('c')
    assert not inst.validate(15)

    # Ordering of sets is arbitrary... for some reason
    str_rpr = str(inst)
    assert str_rpr == "{'a', 'b'}" or str_rpr == "{'b', 'a'}"


def test_boolean_dim():
    dim = BooleanDim()
    assert dim._set == set((True, False))


def test_int_dim():
    dim1 = IntDim(0, 10)
    assert dim1._set == set((0, 1, 2, 3, 4, 5, 6, 7, 8, 9))