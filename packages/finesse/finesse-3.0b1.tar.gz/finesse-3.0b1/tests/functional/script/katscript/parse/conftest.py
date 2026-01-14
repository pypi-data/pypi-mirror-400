from __future__ import annotations

import pytest
from finesse.script.compiler import KatCompiler
from finesse.script.spec import KatSpec
from finesse.script.adapter import ItemAdapter, ElementFactory, ElementSetter
from finesse.components.general import Connector
from finesse.components.node import NodeDirection, NodeType


def _resolve(value):
    if isinstance(value, list):
        for index, item in enumerate(value):
            value[index] = _resolve(item)
    else:
        try:
            value = value.eval()
        except AttributeError:
            pass

    return value


# Fixture for fuzzing tests. Hypothesis requires package scoped fixtures. Registers a
# special component that accepts a single argument of any type, which can be used to
# test parsing KatScript to Python objects.
@pytest.fixture(scope="package")
def fuzz_argument():
    class FuzzElement(Connector):
        """A fake element for fuzzing."""

        def __init__(self, name, value):
            super().__init__(name)
            self.value = value

            # Add some ports (required by the parent class).
            self._add_port("p1", NodeType.OPTICAL)
            self.p1._add_node("i", NodeDirection.INPUT)
            self.p1._add_node("o", NodeDirection.OUTPUT)

            self._add_port("p2", NodeType.OPTICAL)
            self.p2._add_node("i", NodeDirection.INPUT)
            self.p2._add_node("o", NodeDirection.OUTPUT)

    # Note: this breaks the "rule" not to modify the default KatSpec in the
    # /tests/script/katscript tree, but it's the simplest way to test parsing of
    # arbitrary arguments.
    spec = KatSpec()

    # Register fuzz element.
    spec.register_element(
        ItemAdapter(
            full_name="fuzz",
            factory=ElementFactory(item_type=FuzzElement),
            setter=ElementSetter(item_type=FuzzElement),
        )
    )

    compiler = KatCompiler(spec=spec)

    def _(argument_script):
        model = compiler.compile(f"fuzz el1 {argument_script}")
        value = model.el1.value

        return _resolve(value)

    return _


@pytest.fixture
def DIRECTIVES_REFERENCE() -> set[str]:
    return {
        "ABCD",
        "AstigmaticLens",
        "Amplifier",
        "AmplitudeDetector",
        "AntiSqueezing",
        "AstigmatismDetector",
        "BeamPropertyDetector",
        "BeamTrace",
        "Beamsplitter",
        "ButterFilter",
        "CCD",
        "CCDPixel",
        "CCDScanLine",
        "Cavity",
        "CavityPropertyDetector",
        "Change",
        "Cheby1Filter",
        "ClassicalNoise",
        "DCFields",
        "Debug",
        "DegreeOfFreedom",
        "DirectionalBeamsplitter",
        "Eigenmodes",
        "FieldCamera",
        "FieldDetector",
        "FieldPixel",
        "FieldScanLine",
        "For",
        "FreeMass",
        "FrequencyLoss",
        "FrequencyResponse",
        "FrequencyResponse2",
        "FrequencyResponse3",
        "FrequencyResponse4",
        "GetErrorSignals",
        "Gouy",
        "Isolator",
        "KnmDetector",
        "Laser",
        "Lens",
        "Lock",
        "MathDetector",
        "Maximize",
        "Minimize",
        "Mirror",
        "ModeMismatchDetector",
        "Modulator",
        "MotionDetector",
        "NoiseProjection",
        "Nothing",
        "Noxaxis",
        "Operator",
        "OpticalBandpassFilter",
        "OptimalQ",
        "OptimiseRFReadoutPhaseDC",
        "Parallel",
        "Pendulum",
        "Plot",
        "PowerDetector",
        "PowerDetectorDemod1",
        "PowerDetectorDemod2",
        "PrintModel",
        "PrintModelAttr",
        "Printer",
        "PropagateAstigmaticBeam",
        "PropagateBeam",
        "PseudoLockCavity",
        "PseudoLockDRFPMI",
        "QuantumNoiseDetector",
        "QuantumNoiseDetectorDemod1",
        "QuantumNoiseDetectorDemod2",
        "QuantumShotNoiseDetector",
        "QuantumShotNoiseDetectorDemod1",
        "QuantumShotNoiseDetectorDemod2",
        "ReadoutDC",
        "ReadoutRF",
        "RunLocks",
        "SaveMatrix",
        "SensingMatrixDC",
        "Series",
        "SetLockGains",
        "SignalGenerator",
        "Space",
        "Squeezer",
        "SuspensionZPK",
        "Sweep",
        "Telescope",
        "UpdateMaps",
        "Wire",
        "X2axis",
        "X3axis",
        "Xaxis",
        "ZPKFilter",
        "abcd",
        "ad",
        "amplifier",
        "amplitude_detector",
        "antisqueezing",
        "astigd",
        "beam_property_detector",
        "beam_trace",
        "beamsplitter",
        "bp",
        "bs",
        "butter",
        "cav",
        "cavity",
        "cavity_property_detector",
        "ccd",
        "ccdline",
        "ccdpx",
        "change",
        "cheby1",
        "cp",
        "dbs",
        "dc_fields",
        "debug",
        "degree_of_freedom",
        "directional_beamsplitter",
        "dof",
        "eigenmodes",
        "fcam",
        "fd",
        "field_detector",
        "filter_butter",
        "filter_cheby1",
        "filter_zpk",
        "fline",
        "floss",
        "for",
        "fpx",
        "free_mass",
        "freqresp",
        "frequency_response",
        "freqresp2",
        "frequency_response2",
        "freqresp3",
        "frequency_response3",
        "freqresp4",
        "frequency_response4",
        "fsig",
        "gauss",
        "get_error_signals",
        "gouy",
        "isol",
        "isolator",
        "knmd",
        "l",
        "lambda",
        "laser",
        "alens",
        "lens",
        "link",
        "lock",
        "m",
        "math_detector",
        "mathd",
        "maximize",
        "minimize",
        "mirror",
        "mmd",
        "mod",
        "modes",
        "modulator",
        "motion_detector",
        "noise",
        "noise_projection",
        "nothing",
        "noxaxis",
        "obp",
        "operator",
        "opt_rf_readout_phase",
        "optbp",
        "optical_bandpass",
        "optimal_q_detector",
        "parallel",
        "pd",
        "pd1",
        "pd2",
        "pendulum",
        "phase_config",
        "plot",
        "power_detector_dc",
        "power_detector_demod_1",
        "power_detector_demod_2",
        "print",
        "print_model",
        "print_model_attr",
        "propagate_beam",
        "propagate_beam_astig",
        "pseudo_lock_cavity",
        "pseudo_lock_drfpmi",
        "qnoised",
        "qnoised1",
        "qnoised2",
        "qshot",
        "qshot1",
        "qshot2",
        "quantum_noise_detector",
        "quantum_noise_detector_demod_1",
        "quantum_noise_detector_demod_2",
        "quantum_shot_noise_detector",
        "quantum_shot_noise_detector_demod_1",
        "quantum_shot_noise_detector_demod_2",
        "readout_dc",
        "readout_rf",
        "run_locks",
        "s",
        "save_matrix",
        "sensing_matrix_dc",
        "series",
        "set_lock_gains",
        "sgen",
        "signal_generator",
        "space",
        "sq",
        "squeezer",
        "sus_zpk",
        "suspension_zpk",
        "sweep",
        "tel",
        "telescope",
        "tem",
        "update_maps",
        "var",
        "variable",
        "w",
        "wire",
        "x2axis",
        "x3axis",
        "xaxis",
        "xd",
        "zpk",
        "TestPoint",
        "test_point",
        "test",
    }
