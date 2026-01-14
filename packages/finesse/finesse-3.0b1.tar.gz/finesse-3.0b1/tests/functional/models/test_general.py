import pytest

import finesse
from finesse.components import Mirror
from finesse.exceptions import ModelClassAttributeError, ModelMissingAttributeError
from finesse.utilities.collections import OrderedSet


@pytest.fixture
def model() -> finesse.Model:
    return finesse.Model()


def test_phase_level_change(model):
    # Issue 506
    model.phase_config(zero_k00=True, zero_tem00_gouy=False)
    assert model._settings.phase_config.zero_k00 is True
    assert model._settings.phase_config.zero_tem00_gouy is False
    model.phase_config(zero_k00=False, zero_tem00_gouy=True)
    assert model._settings.phase_config.zero_k00 is False
    assert model._settings.phase_config.zero_tem00_gouy is True
    model.phase_config(zero_k00=True, zero_tem00_gouy=True)
    assert model._settings.phase_config.zero_k00 is True
    assert model._settings.phase_config.zero_tem00_gouy is True


def test_get_string(model):
    model = finesse.Model()
    model.parse("m m1")
    model.parse("gauss g1 m1.p1.o w=1 Rc=1")
    model.beam_trace()

    assert model.m1 is model.get("m1")
    assert model.m1 is model.get_element("m1")

    assert model.m1.p1 is model.get("m1.p1")
    assert model.m1.p2 is model.get("m1.p2")

    assert model.m1.p2.i is model.get("m1.p2.i")
    assert model.m1.p2.o is model.get("m1.p2.o")

    assert model.m1.p2.i.qx is model.get("m1.p2.i.qx")
    assert model.m1.p2.i.qy is model.get("m1.p2.i.qy")
    assert model.m1.p2.o.qx is model.get("m1.p2.o.qx")
    assert model.m1.p2.o.qy is model.get("m1.p2.o.qy")

    assert model.m1.R is model.get("m1.R")
    assert model.m1.T is model.get("m1.T")


def test_get_other_model(model):
    model = finesse.Model()
    model.parse("m m1")

    model2 = finesse.Model()
    model2.parse("m m1")

    assert model.m1 is model.get(model2.m1)
    assert model.m1 is model.get_element(model2.m1)

    assert model.m1.p1 is model.get(model2.m1.p1)
    assert model.m1.p2 is model.get(model2.m1.p2)

    assert model.m1.p2.i is model.get(model2.m1.p2.i)
    assert model.m1.p2.o is model.get(model2.m1.p2.o)

    assert model.m1.R is model.get(model2.m1.R)
    assert model.m1.T is model.get(model2.m1.T)


def test_reduce_model_path(model):
    model.parse("l l1 P=5")
    assert model._reduce_model_path(["l1", "P"]) == 5


def test_reduce_model_path_namespaces(model):
    model.parse(
        """\
    m m1
    m m2
    link(m1, m2)"""
    )
    assert (
        model._reduce_model_path(["m1_p1__m2_p1"], check_namespaces=True)
        == model.spaces.m1_p1__m2_p1
    )


def test_reduce_model_path_namespaces_missing(model):
    model.parse(
        """\
    m m1
    m m2
    link(m1, m2)"""
    )
    with pytest.raises(ModelMissingAttributeError):
        model._reduce_model_path(["m1_p1__m2_p1"], check_namespaces=False)


def test_reduce_model_path_missing(model):
    model.parse("l l1 P=5")
    with pytest.raises(ModelMissingAttributeError):
        model._reduce_model_path(["l1", "__missing"])


def test_reduce_model_path_class_attr(model):
    model.parse("l l1 P=5")
    with pytest.raises(ModelClassAttributeError):
        model._reduce_model_path(["l1", "set_output_field"])


def test_get_namespace_paths_empty(model):
    assert model._get_namespace_paths() == OrderedSet()


def test_get_namespace_paths_with_elements(model):
    model.parse(
        """
    m m1
    m m2
    link(m1, m2)
    readout_dc r1
    readout_dc r2
    wire w1 r1.DC r2.DC
    noise n1 r1.DC 5.0
    """
    )
    assert model._get_namespace_paths() == {".spaces", ".wires", ".noises"}


def test_get_namespaces_empty(model):
    assert model._get_namespaces() == []


def test_get_namespaces_with_elements(model):
    model.parse(
        """
    m m1
    m m2
    link(m1, m2)
    readout_dc r1
    readout_dc r2
    wire w1 r1.DC r2.DC
    noise n1 r1.DC 5.0
    """
    )
    assert model._get_namespaces() == [model.noises, model.spaces, model.wires]


def test_get_elements_of_type(model):
    model.parse(
        """
    m m1
    m m2
    l l1
    """
    )
    assert model.get_elements_of_type("m") == (model.m1, model.m2)
    assert model.get_elements_of_type(Mirror) == (model.m1, model.m2)
    assert model.get_elements_of_type(Mirror, "Laser") == (model.m1, model.m2, model.l1)
