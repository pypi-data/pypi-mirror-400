import pytest

import numpy as np

from finesse import Model
from finesse.detectors import PowerDetector
from finesse.analysis.actions import Xaxis
from finesse.components import Gauss


@pytest.fixture
def forward_model():
    model = Model()
    model.parse(
        """
        l l1 P=1
        s s1 l1.p1 FI.p1
        isolator FI S=0
        """
    )
    model.add(PowerDetector("FI_p1", model.FI.p1.i))
    model.add(PowerDetector("FI_p2", model.FI.p2.o))
    return model


@pytest.fixture
def backward_model():
    model = Model()
    model.parse(
        """
        l l1 P=1
        s s1 l1.p1 FI.p2
        isolator FI S=0
        """
    )
    model.add(PowerDetector("FI_p1", model.FI.p1.o))
    model.add(PowerDetector("FI_p2", model.FI.p2.i))
    return model


@pytest.mark.parametrize("homs", (True, False))
class TestIsolator:

    def handle_homs(self, model, homs):
        if homs:
            model.add(Gauss("g1", model.l1.p1.o, w0=1e-3, z=0))
            model.modes(maxtem=1)
        return model

    def test_forward_complete_transmission(self, forward_model, homs):
        forward_model = self.handle_homs(forward_model, homs)
        sol = forward_model.run(Xaxis(forward_model.l1.P, "lin", 1, 10, 10))
        for det in ["FI_p1", "FI_p2"]:
            np.testing.assert_allclose(sol[det], np.linspace(1, 10, 11))

    def test_backward_complete_transmission(self, backward_model, homs):
        backward_model = self.handle_homs(backward_model, homs)
        sol = backward_model.run(Xaxis(backward_model.l1.P, "lin", 1, 10, 10))
        for det in ["FI_p1", "FI_p2"]:
            np.testing.assert_allclose(sol[det], np.linspace(1, 10, 11))

    def test_forward_suppression(self, forward_model, homs):
        forward_model = self.handle_homs(forward_model, homs)
        # should not be suppressing in the forward direction
        sol = forward_model.run(Xaxis(forward_model.FI.S, "lin", 1, 20, 10))
        for det in ["FI_p1", "FI_p2"]:
            np.testing.assert_allclose(sol[det], np.ones(11))

    def test_backward_suppression(self, backward_model, homs):
        backward_model = self.handle_homs(backward_model, homs)
        sol = backward_model.run(Xaxis(backward_model.FI.S, "lin", 1, 20, 10))
        np.testing.assert_allclose(sol["FI_p2"], np.ones(11))
        np.testing.assert_allclose(
            sol["FI_p1"], np.power(10 ** (-np.linspace(1, 20, 11) / 20), 2)
        )
