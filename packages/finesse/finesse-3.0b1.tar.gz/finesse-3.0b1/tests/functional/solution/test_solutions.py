import finesse
import numpy as np


def test_nested_array_solutions():
    model = finesse.script.parse(
        """
                                    l l1
                                    pd P l1.p1.o
                                    """
    )

    sol = model.run("xaxis(l1.P, lin, 0, 1, 10, post_step=noxaxis())")

    assert np.allclose(sol["P"], sol.x[0]), "Didn't return pd P result"
    assert len(sol["post_step"].children) == 11, "Didn't return 11 post_step values"
    assert isinstance(
        sol["post_step"].children[0], finesse.solutions.ArraySolution
    ), "Didn't return ArraySolution"


def test_selection():
    model = finesse.script.parse(
        """
        l l1
        pd P l1.p1.o
        pd A l1.p1.o
        """
    )

    sol = model.run('noxaxis(name="A")')
    assert isinstance(sol["A"], float), "Didn't return pd A result"

    model = finesse.script.parse(
        """
        l l1
        pd P l1.p1.o
        """
    )

    sol = model.run('noxaxis(name="A")')
    assert isinstance(
        sol["A"], finesse.solutions.ArraySolution
    ), "Didn't return A solution"
    assert isinstance(
        sol[["A"]], finesse.solutions.ArraySolution
    ), "Didn't return A solution using a list of names"

    model = finesse.script.parse(
        """
        l l1
        pd P l1.p1.o
        pd A l1.p1.o
        """
    )

    sol = model.run('series(noxaxis(name="A"), noxaxis(name="B"))')
    assert isinstance(
        sol["A"], finesse.solutions.ArraySolution
    ), "Didn't return A solution"
