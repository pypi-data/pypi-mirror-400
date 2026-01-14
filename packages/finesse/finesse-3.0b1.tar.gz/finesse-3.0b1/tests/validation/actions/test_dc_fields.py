import pytest
import finesse
import numpy as np
import finesse.analysis.actions as fa


@pytest.fixture
def model_solution():
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    l l2 P=1 f=10M
    m m1 L=0 T=0
    link(l1, m1, l2)

    gauss g1 l1.p1.o w0=0.05 z=0
    modes(maxtem=2)
    """
    )
    model.l2.tem(0, 0, 0)
    model.l2.tem(0, 2, 1)
    return model, model.run("dc_fields(name='DC')")


def test_solution_name(model_solution):
    assert (
        model_solution[1]["DC"] is model_solution[1]
    ), "Didn't return the solution itself"


def test_get_node_name(model_solution):
    model, solution = model_solution
    _ = solution[("l1.p1.i", "l1.p1.o"), :, :]
    with pytest.raises(KeyError):
        _ = solution["l1.p1."]
    with pytest.raises(TypeError):
        _ = solution(["l1.p1.i", "l1.p1.o"])
    with pytest.raises(TypeError):
        _ = solution([model.l1.p1.i, model.l1.p1.o])


def test_values(model_solution):
    model, solution = model_solution
    # all nodes in 0Hz not in 00 == 0
    np.testing.assert_allclose(solution[:, 0, 1:], 0)
    np.testing.assert_allclose(solution[("l1.p1.o", "m1.p1.i"), 0, 0], 1)
    np.testing.assert_allclose(solution[(model.l1.p1.o, model.m1.p1.i), 0, 0], 1)
    # all nodes in 10MHz not in 02 == 0
    index = np.array([_ == [0, 2] for _ in solution.homs])
    np.testing.assert_allclose(solution[:, 1, ~index], 0)
    np.testing.assert_allclose(solution[("l2.p1.o", "m1.p2.i"), 1, index], 1)
    np.testing.assert_allclose(solution[(model.l2.p1.o, model.m1.p2.i), 1, index], 1)


def test_shapes(model_solution):
    model, sol = model_solution
    n_nodes = len(sol.nodes)
    n_freqs = 2
    n_homs = 6
    assert sol.fields.shape == (n_nodes, n_freqs, n_homs)
    assert sol["l2.p1.i"].shape == (1, n_freqs, n_homs)
    assert sol["l2.p1.i", :, 0].shape == (1, n_freqs)
    assert sol[("l2.p1.i", "m1.p1.o")].shape == (2, n_freqs, n_homs)
    assert sol[:, :, sol.homs.index([0, 1])].shape == (n_nodes, n_freqs)
    assert sol[5].shape == (n_freqs, n_homs)
    assert sol[1:3].shape == (2, n_freqs, n_homs)
    assert sol[1:3, 0].shape == (2, n_homs)
    assert sol[np.array([1, 3, 5, 7])].shape == (4, n_freqs, n_homs)
    idx = np.array([node.split(".")[-1] == "o" for node in sol.nodes])
    assert sol[idx].shape == (np.count_nonzero(idx), n_freqs, n_homs)


def test_node_string_section_equivalent(model_solution):
    model, sol = model_solution
    assert np.all(sol[model.l2.p1.i] == sol["l2.p1.i"])
    assert np.all(sol[model.l2.p1.i, :, 0] == sol["l2.p1.i", :, 0])
    assert np.all(sol[(model.l2.p1.i, model.m1.p1.o)] == sol[("l2.p1.i", "m1.p1.o")])


def test_change_param(model_solution):
    model, _ = model_solution
    Pnew = 100
    act0 = fa.Change({"l1.P": Pnew})
    act1 = fa.DCFields(name="DC")
    with model.temporary_parameters():
        model.l1.P = Pnew
        sol1 = model.run(act1)
    with model.temporary_parameters():
        sol2 = model.run(fa.Series(act0, act1))
    np.testing.assert_allclose(sol1.fields, sol2.fields)
