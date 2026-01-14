import pytest

from finesse import Model
from finesse.env import has_pygraphviz
from finesse.plotting import tools as plotting_tools


@pytest.fixture
def simple_model():
    IFO = Model()
    IFO.parse(
        """
    l L0 P=1
    s s0 L0.p1 ITM.p1

    m ITM R=0.9 T=0.1 Rc=-2
    """
    )

    return IFO


@pytest.mark.parametrize("format", ["svg", "png"])
@pytest.mark.parametrize("path", [None, True])
@pytest.mark.parametrize("graphviz", [False, True])
@pytest.mark.parametrize("in_ipython", [True, False])
def test_filepath(
    format, simple_model, tmp_path, path, graphviz, in_ipython, monkeypatch
):
    if not has_pygraphviz() and graphviz:
        pytest.skip(reason="graphviz is not available")
    if in_ipython:
        monkeypatch.setattr(plotting_tools, "MOCK_IN_IPYTHON", True)
    if path:
        path = (tmp_path / "graph").with_suffix(f".{format}")
    simple_model.plot_graph(
        root="L0", path=path, graphviz=graphviz, format=format, show=False
    )

    if path:
        assert path.exists()
        assert path.is_file()


@pytest.mark.parametrize("in_ipython", [True, False])
def test_mocking(monkeypatch, in_ipython):
    if in_ipython:
        monkeypatch.setattr(plotting_tools, "MOCK_IN_IPYTHON", True)
    assert plotting_tools._in_ipython() is in_ipython
