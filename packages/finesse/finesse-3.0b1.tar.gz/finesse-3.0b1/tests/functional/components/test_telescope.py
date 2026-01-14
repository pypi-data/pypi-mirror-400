import numpy as np
import pytest

import finesse
import finesse.components

from finesse.detectors import FieldDetector
from finesse.exceptions import BeamTraceException


@pytest.fixture
def telescope_model():
    model = finesse.Model()
    laser1 = model.add(finesse.components.Laser("laser1"))
    telescope = model.add(finesse.components.Telescope("telescope"))
    laser2 = model.add(finesse.components.Laser("laser2"))
    model.link(laser1, telescope, laser2)
    model.modes("even", maxtem=2)
    return model


def test_telescope_fields(telescope_model):
    # ensure fields transmit with a mode-mismatch unperturbed
    telescope_model.laser1.p1.o.q = finesse.BeamParam(w0=0.1, z=0.1)
    telescope_model.laser2.p1.o.q = finesse.BeamParam(w0=0.2, z=0.2)
    telescope_model.laser2.set_output_field([0, 1, 0], telescope_model.homs)

    telescope_model.add(FieldDetector("E1", telescope_model.telescope.p1.o, 0))
    telescope_model.add(FieldDetector("E2", telescope_model.telescope.p2.o, 0))
    out = telescope_model.run()

    assert np.allclose(out["E2"], [1, 0, 0])
    assert np.allclose(abs(out["E1"]), [0, 1, 0])


def test_telescope_detect_mismatches(telescope_model):
    telescope_model.laser1.p1.o.q = finesse.BeamParam(w0=0.1, z=0.1)
    telescope_model.laser2.p1.o.q = finesse.BeamParam(w0=0.2, z=0.2)
    assert len(telescope_model.detect_mismatches()) == 0


def test_telescope_trace_error(telescope_model):
    telescope_model.laser1.p1.o.q = finesse.BeamParam(w0=0.1, z=0.1)

    with pytest.raises(BeamTraceException):
        # missing beam parameters on laser2 side
        telescope_model.beam_trace()
