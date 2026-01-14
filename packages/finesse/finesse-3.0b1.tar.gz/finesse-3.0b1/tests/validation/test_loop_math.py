import numpy as np
import finesse
from finesse.components.electronics import ZPKFilter
from finesse.analysis.actions import FrequencyResponse


def test_AB_feedback_D_C():
    def run(*args, **kwargs):
        model = finesse.Model()
        model.parse("l l1")
        model.fsig.f = 1
        A = model.add(ZPKFilter("A", [1], [2], 1))
        B = model.add(ZPKFilter("B", [0.01], [1, 4], 3))
        C = model.add(ZPKFilter("C", [5], [10, 10], -2))
        D = model.add(ZPKFilter("D", [], [10 + 0.1j, 10 - 0.1j], 10000))
        model.link(A, B, C)
        model.link(B.p2, D, B.p1)
        sol = model.run(
            FrequencyResponse(
                np.geomspace(0.001, 100, 100),
                *args,
                **kwargs,
            )
        )
        _A = A.eval(sol.f)
        _B = B.eval(sol.f)
        _C = C.eval(sol.f)
        _D = D.eval(sol.f)

        return sol, _A, _B, _C, _D

    sol, _A, _B, _C, _D = run("B.p1", "B.p2", open_loop=False)
    assert np.allclose(sol.out[:, 0, 0], _B / (1 - _B * _D))
    sol, _A, _B, _C, _D = run("B.p1", "B.p2", open_loop=True)
    assert np.allclose(sol.out[:, 0, 0], _B)

    sol, _A, _B, _C, _D = run("D.p1", "D.p2", open_loop=False)
    assert np.allclose(sol.out[:, 0, 0], _D / (1 - _D * _B))
    sol, _A, _B, _C, _D = run("D.p1", "D.p2", open_loop=True)
    assert np.allclose(sol.out[:, 0, 0], _D)

    sol, _A, _B, _C, _D = run("B.p1", "D.p2", open_loop=True)
    assert np.allclose(sol.out[:, 0, 0], _B * _D)

    sol, _A, _B, _C, _D = run("B.p1", "D.p2", open_loop=False)
    assert np.allclose(sol.out[:, 0, 0], _B * _D / (1 - _D * _B))

    for open_loop in (True, False):
        sol, _A, _B, _C, _D = run("A.p1", "A.p2", open_loop=open_loop)
        assert np.allclose(sol.out[:, 0, 0], _A)
        sol, _A, _B, _C, _D = run("C.p1", "C.p2", open_loop=open_loop)
        assert np.allclose(sol.out[:, 0, 0], _C)
        sol, _A, _B, _C, _D = run("A.p1", "B.p2", open_loop=open_loop)
        assert np.allclose(sol.out[:, 0, 0], _A * _B / (1 - _B * _D))
        sol, _A, _B, _C, _D = run("A.p1", "C.p2", open_loop=open_loop)
        assert np.allclose(sol.out[:, 0, 0], _C * _A * _B / (1 - _B * _D))


def test_A_fC_fBD():
    def run(*args, **kwargs):
        model = finesse.Model()
        model.parse("l l1")
        model.fsig.f = 1
        A = model.add(ZPKFilter("A", [1], [2], 1))
        B = model.add(ZPKFilter("B", [0.01], [1, 4], 3))
        C = model.add(ZPKFilter("C", [5], [10, 10], -2))
        D = model.add(ZPKFilter("D", [], [10 + 0.1j, 10 - 0.1j], 10000))
        model.link(A.p2, C, A.p1)
        model.link(A.p2, B, D, A.p1)
        sol = model.run(
            FrequencyResponse(
                np.geomspace(0.001, 100, 100),
                *args,
                **kwargs,
            )
        )
        _A = A.eval(sol.f)
        _B = B.eval(sol.f)
        _C = C.eval(sol.f)
        _D = D.eval(sol.f)

        return sol, _A, _B, _C, _D

    sol, _A, _B, _C, _D = run("A.p1", "A.p2", open_loop=True)
    assert np.allclose(sol.out[:, 0, 0], _A)
    sol, _A, _B, _C, _D = run("A.p1", "A.p2", open_loop=False)
    assert np.allclose(sol.out[:, 0, 0], _A / (1 - _C * _A - _A * _B * _D))
