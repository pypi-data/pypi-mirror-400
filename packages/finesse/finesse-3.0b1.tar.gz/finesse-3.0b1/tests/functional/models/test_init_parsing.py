from pathlib import Path
import pytest

from finesse import Model


@pytest.fixture
def katscripts() -> list[str]:
    return ["l l1 P=1.1", "m m1 R=0.9 T=0.1", "s s1 l1.p1 m1.p1"]


@pytest.fixture
def basemodel(katscripts) -> Model:
    m = Model()
    m.parse("\n".join(katscripts))
    return m


@pytest.fixture
def basefile(katscripts, tmp_path) -> Path:
    (path := tmp_path / Path("basemodel")).write_text("\n".join(katscripts))
    return path


def test_parsing_katscripts(katscripts, basemodel):
    assert basemodel.unparse() == Model(*katscripts).unparse()


def test_loading_file(katscripts, basemodel, basefile):
    assert basemodel.unparse() == Model(loadfile=basefile).unparse()


def test_parse_and_load(katscripts, basemodel, basefile):
    model = Model("m m2 R=0.2 T=0.7", loadfile=basefile)
    assert basemodel.unparse() != model.unparse()
    assert model.m2.R == 0.2
