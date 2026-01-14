"""KatScript specification.

This defines supported KatScript syntax and maps it to Finesse Python classes via
:class:`.ItemAdapter` objects.
"""

from __future__ import annotations

import logging
from collections import ChainMap

from .. import components, detectors, frequency, locks, symbols
from ..analysis import actions, noise
from ..components import electronics, mechanical
from ..config import config_instance
from ..model import Model
from .adapter import (
    AnalysisDocumenter,
    AnalysisDumper,
    AnalysisFactory,
    AnalysisSetter,
    Argument,
    ArgumentDump,
    ArgumentType,
    CommandDump,
    CommandMethodDocumenter,
    CommandMethodSetter,
    CommandPropertyDocumenter,
    CommandPropertyDumper,
    CommandPropertySetter,
    ElementDocumenter,
    ElementDump,
    ElementDumper,
    ElementFactory,
    ElementSetter,
    ItemAdapter,
    ItemDumper,
    ItemSetter,
    SignatureArgumentMixin,
)

LOGGER = logging.getLogger(__name__)


def add_name_to_other_names(name: str, kwargs: dict) -> dict:
    """For 'make_element' and 'make_analysis', adds the name of the python class to the
    list of 'other_names', which get added in 'ItemAdapter' to the list of aliases.
    Allows 'Xaxis' to be recognized as 'xaxis' and 'Beamsplitter' as 'beamsplitter'.

    Parameters
    ----------
    cls_name : str
        Name of the class
    kwargs : dict
        kwargs meant to be passed to ItemAdapter

    Returns
    -------
    dict
        kwargs with 'other_names' modified to include the class name.
    """
    other_names = kwargs.setdefault("other_names", [])
    other_names.append(name)
    return kwargs


def make_element(element_type, full_name, build_last=False, ref_args=None, **kwargs):
    """Create a standard element adapter.

    Use this for elements that follow the normal behaviour: they are of type
    :class:`.ModelElement`, their constructor signature defines their attributes, and
    the attributes are available with the same name in the object.
    """
    kwargs = add_name_to_other_names(element_type.__name__, kwargs)
    return ItemAdapter(
        full_name,
        getter=ElementDumper(item_type=element_type, ref_args=ref_args),
        factory=ElementFactory(item_type=element_type, last=build_last),
        setter=ElementSetter(item_type=element_type),
        documenter=ElementDocumenter(item_type=element_type),
        **kwargs,
    )


def make_analysis(analysis_type, full_name, ref_args=None, **kwargs):
    """Create a standard analysis adapter.

    Use this for analyses that follow the normal behaviour: they are of type
    :class:`.Action`, their constructor signature defines their attributes, and the
    attributes are available with the same name in the object.
    """
    kwargs = add_name_to_other_names(analysis_type.__name__, kwargs)
    return ItemAdapter(
        full_name,
        getter=AnalysisDumper(item_type=analysis_type, ref_args=ref_args),
        factory=AnalysisFactory(item_type=analysis_type),
        setter=AnalysisSetter(item_type=analysis_type),
        documenter=AnalysisDocumenter(item_type=analysis_type),
        singular=True,
        **kwargs,
    )


class GaussDumper(ItemDumper):
    """Dumper for the :class:`.Gauss` component.

    Gauss components accept many different forms of argument to define the beam
    parameter but only store these internally as q parameters. This dumper therefore
    tries to figure out how the parameters were defined by the user (either via Python
    or KatScript) and generates parameters based on that.
    """

    def __init__(self):
        super().__init__(item_type=components.Gauss)

    def __call__(self, adapter, model):
        for gauss in model.get_elements_of_type(self.item_type):
            parameters = {
                "node": ArgumentDump("node", value=gauss.node, kind=ArgumentType.ANY),
                "priority": ArgumentDump(
                    "priorty", value=gauss.priority, default=0, kind=ArgumentType.ANY
                ),
            }

            # Map of available gauss call parameters to attributes.
            # FIXME: move these to Gauss itself.
            gauss_attr_map = {
                "w0": gauss.qx.w0,
                "w0x": gauss.qx.w0,
                "w0y": gauss.qy.w0,
                "z": gauss.qx.z,
                "zx": gauss.qx.z,
                "zy": gauss.qy.z,
                "zr": gauss.qx.zr,
                "zrx": gauss.qx.zr,
                "zry": gauss.qy.zr,
                "w": gauss.qx.w,
                "wx": gauss.qx.w,
                "wy": gauss.qy.w,
                "Rc": gauss.qx.Rc,
                "Rcx": gauss.qx.Rc,
                "Rcy": gauss.qy.Rc,
                "S": gauss.qx.S,
                "Sx": gauss.qx.S,
                "Sy": gauss.qy.S,
                "q": gauss.qx.q,
                "qx": gauss.qx.q,
                "qy": gauss.qy.q,
            }

            # Add additional parameters specified by the user.
            for param in gauss._specified_params:
                value = gauss_attr_map[param]
                parameters[param] = ArgumentDump(
                    param,
                    value=value,
                    default=None,
                    kind=ArgumentType.KEYWORD_ONLY,
                )

            yield ElementDump(
                element=gauss,
                adapter=adapter,
                parameters=parameters,
                is_default=all(param.is_default for param in parameters.values()),
            )


class VariableDumper(ItemDumper):
    """Variable for :class:`finesse.components.general.Variable`."""

    def __init__(self):
        super().__init__(item_type=components.Variable)

    def __call__(self, adapter, model):
        for variable in model.parameters:
            parameters = {
                "value": ArgumentDump(
                    "value", value=variable.value, kind=ArgumentType.POS_ONLY
                ),
                "units": ArgumentDump(
                    "units",
                    value=variable.units,
                    kind=ArgumentType.KEYWORD_ONLY,
                    default="",
                ),
                "description": ArgumentDump(
                    "description",
                    value=variable.description,
                    kind=ArgumentType.KEYWORD_ONLY,
                    default=None,
                ),
                # Not sure how to handle dtype
                # "dtype": ArgumentDump("dtype", value=variable.datatype, kind=ArgumentType.KEYWORD_ONLY),
                "is_geometric": ArgumentDump(
                    "is_geometric",
                    value=variable.is_geometric,
                    kind=ArgumentType.KEYWORD_ONLY,
                    default=False,
                ),
                "changeable_during_simulation": ArgumentDump(
                    "changeable_during_simulation",
                    value=variable.changeable_during_simulation,
                    kind=ArgumentType.KEYWORD_ONLY,
                    default=True,
                ),
            }

            yield ElementDump(
                element=variable,
                adapter=adapter,
                parameters=parameters,
                is_default=False,
            )


class FsigArgumentsMixin:
    def arguments(self, **kwargs):
        # FIXME: these would ideally come from Fsig's constructor, but we can't inspect
        # Cython types.
        return {"f": Argument("f", ArgumentType.ANY)}


class FsigDumper(ItemDumper):
    def __init__(self):
        super().__init__(item_type=frequency.Fsig)

    def __call__(self, adapter, model):
        # FIXME: these would ideally come from Fsig's constructor, but we can't inspect
        # Cython types.
        default = None
        is_default = model.fsig.f.value == default
        parameters = {"f": ArgumentDump("f", value=model.fsig.f, default=default)}

        yield CommandDump(adapter=adapter, parameters=parameters, is_default=is_default)


class FsigSetter(FsigArgumentsMixin, ItemSetter):
    def __init__(self):
        super().__init__(item_type=frequency.Fsig)

    def __call__(self, model, argskwargs):
        args, kwargs = argskwargs
        allargs = list(args) + list(kwargs.values())
        assert len(allargs) == 1
        model.fsig.f = allargs[0]


class FsigDocumenter(FsigArgumentsMixin, CommandMethodDocumenter):
    def __init__(self):
        super().__init__(item_type=frequency.Fsig)

    def argument_descriptions(self):
        descriptions = super().argument_descriptions()
        # The KatScript call to fsig doesn't use the name.
        descriptions.pop("name")

        return descriptions


class ModesDumper(SignatureArgumentMixin, ItemDumper):
    def __init__(self):
        super().__init__(item_type=Model.modes)

    def __call__(self, adapter, model):
        # Grab the values from :meth:`.Model.modes_setting` but grab the defaults from
        # the :meth:`.Model.modes` signature.
        sigparams = self.arguments()
        parameters = {
            key: ArgumentDump(
                key,
                value=value,
                default=sigparams[key].default,
                kind=sigparams[key].kind,
            )
            for key, value in model.modes_setting.items()
        }

        # Ensure the "modes" parameter exists so that, if "default valued" commands are
        # requested, a modes command with an "off" parameter is dumped.
        modes_other_defaults = [sigparams["modes"].default]
        if modes := parameters.get("modes"):
            # The `modes` parameter accepts "off" via KatScript as the same meaning as
            # the Python default (`None`).
            modes.default = "off"
            modes.other_defaults = modes_other_defaults
        else:
            # Ensure there is at least an "off".
            parameters["modes"] = ArgumentDump(
                "modes",
                value="off",
                default="off",
                other_defaults=modes_other_defaults,
                kind=sigparams["modes"].kind,
            )

        yield CommandDump(
            adapter=adapter,
            parameters=parameters,
            is_default=all(param.is_default for param in parameters.values()),
        )


class TEMDumper(SignatureArgumentMixin, ItemDumper):
    def __init__(self):
        super().__init__(item_type=components.Laser.tem)

    def __call__(self, adapter, model):
        """(args, kwargs) tuples for each defined TEM mode."""
        sigparams = self.arguments()

        for laser in model.get_elements_of_type(components.Laser):
            for (n, m), (factor, phase) in laser.power_coeffs.items():
                otherkv = {"n": n, "m": m, "factor": factor, "phase": phase}
                other_parameters = {
                    key: ArgumentDump(
                        key,
                        value=value,
                        default=sigparams[key].default,
                        kind=sigparams[key].kind,
                    )
                    for key, value in otherkv.items()
                }

                parameters = {
                    "laser": ArgumentDump("laser", value=laser),
                    **other_parameters,
                }

                current = {(n, m): (factor, phase)}
                yield CommandDump(
                    adapter=adapter,
                    parameters=parameters,
                    is_default=current.items() <= laser.DEFAULT_POWER_COEFFS.items(),
                )


class TEMSetter(CommandMethodSetter):
    def __init__(self):
        super().__init__(item_type=components.Laser.tem)

    def __call__(self, _, argskwargs):
        args, kwargs = argskwargs

        if "laser" in kwargs:
            laser = kwargs.pop("laser")
        else:
            laser, *args = args

        self.item_type(laser, *args, **kwargs)


class TEMDocumenter(CommandMethodDocumenter):
    def __init__(self):
        super().__init__(item_type=components.Laser.tem)

    ##
    # Override some inherited methods to add the laser argument, which is not part of
    # :meth:`.Laser.tem` (well, technically it's `self`, but we want to call it
    # "laser").

    def arguments(self):
        return {
            "laser": Argument(name="laser", kind=ArgumentType.ANY),
            **super().arguments(),
        }

    def argument_descriptions(self):
        return {
            "laser": (":class:`.Laser`", "The laser to set mode power for."),
            **super().argument_descriptions(),
        }


class PhaseConfigDumper(SignatureArgumentMixin, ItemDumper):
    def __init__(self):
        super().__init__(item_type=Model.phase_config)

    def __call__(self, adapter, model):
        # Grab the values from the model private settings (Cython) object but grab the
        # defaults from the :meth:`.Model.phase_config` signature.
        settings = {
            "zero_k00": model._settings.phase_config.zero_k00,
            "zero_tem00_gouy": model._settings.phase_config.zero_tem00_gouy,
        }
        sigparams = self.arguments()
        parameters = {
            key: ArgumentDump(
                key,
                value=value,
                default=sigparams[key].default,
                kind=sigparams[key].kind,
            )
            for key, value in settings.items()
        }

        yield CommandDump(
            adapter=adapter,
            parameters=parameters,
            is_default=all(param.is_default for param in parameters.values()),
        )


class KatSpec:
    """KatScript language specification.

    This defines the available KatScript elements, commands, and analyses that the
    parser recognises. These directives are mapped by this object to adapter classes to
    convert between KatScript and Finesse objects.

    Additional directives can be registered at runtime using :meth:`.register_element`,
    :meth:`.register_command`, and :meth:`.register_analysis`. These adapters will
    remain for the rest of the lifetime of the object.

    Supported KatScript keywords, constants, operators, and functions are not modifiable
    by users.

    This class should not normally be instantiated by user code; the shared instance in
    :data:`.KATSPEC` should instead be used.
    """

    # Fixed language constructs. These are not modifiable by the user.
    keywords = {
        # None.
        "none",
        # HOM collections.
        "even",
        "odd",
        "x",
        "y",
        "off",
        # Axis scales.
        "lin",
        "log",
        # Modulator types.
        "am",
        "pm",
        # Filter types.
        "lowpass",
        "highpass",
        "bandpass",
        "bandstop",
        "single",
        "xsplit",
        "ysplit",
        # Beam properties (see :class:`.BeamProperty`).
        *detectors.bpdetector.BP_KEYWORDS.keys(),
        # Cavity properties (see :class:`.CavityProperty`).
        *detectors.cavity_detector.CP_KEYWORDS.keys(),
        "both",
    }
    constants = symbols.CONSTANTS
    unary_operators = {
        "+": symbols.FUNCTIONS["pos"],
        "-": symbols.FUNCTIONS["neg"],
    }
    binary_operators = {
        "+": symbols.OPERATORS["__add__"],
        "-": symbols.OPERATORS["__sub__"],
        "*": symbols.OPERATORS["__mul__"],
        "**": symbols.OPERATORS["__pow__"],
        "/": symbols.OPERATORS["__truediv__"],
        "//": symbols.OPERATORS["__floordiv__"],
    }
    expression_functions = symbols.FUNCTIONS

    def __init__(self):
        # Modifiable specifications. These are dynamically supported by the parser.
        self.elements = {}
        self.commands = {}
        self.analyses = {}
        self._register_constructs()

    def _register_constructs(self):
        ### Register default language constructs.

        ## Components.
        self.register_element(make_element(electronics.Amplifier, "amplifier"))
        self.register_element(
            make_element(components.Beamsplitter, "beamsplitter", short_name="bs")
        )
        # The cavity factory's `last` flag is set because cavities implicitly depend on
        # any nodes that appear in paths from their start ports back to themselves, so
        # their dependencies cannot be determined by the time the first set of elements
        # are built into the model. It is moved to the second build pass by this flag.
        self.register_element(
            make_element(components.Cavity, "cavity", short_name="cav", build_last=True)
        )
        self.register_element(
            make_element(
                components.DegreeOfFreedom, "degree_of_freedom", short_name="dof"
            )
        )
        self.register_element(
            make_element(
                components.DirectionalBeamsplitter,
                "directional_beamsplitter",
                short_name="dbs",
            )
        )
        self.register_element(
            make_element(electronics.TestPoint, "test_point", short_name="test")
        )
        self.register_element(
            make_element(electronics.ZPKFilter, "filter_zpk", short_name="zpk")
        )
        self.register_element(
            make_element(electronics.ButterFilter, "filter_butter", short_name="butter")
        )
        self.register_element(
            make_element(electronics.Cheby1Filter, "filter_cheby1", short_name="cheby1")
        )
        self.register_element(
            make_element(components.Isolator, "isolator", short_name="isol")
        )
        self.register_element(make_element(components.Laser, "laser", short_name="l"))
        self.register_element(make_element(components.Lens, "lens"))
        self.register_element(make_element(components.AstigmaticLens, "alens"))
        self.register_element(make_element(components.Mirror, "mirror", short_name="m"))
        self.register_element(make_element(components.FrequencyLoss, "floss"))
        self.register_element(
            make_element(components.Modulator, "modulator", short_name="mod")
        )
        self.register_element(
            make_element(
                components.optical_bandpass.OpticalBandpassFilter,
                "optical_bandpass",
                short_name="obp",
            )
        )
        self.register_element(
            make_element(components.Squeezer, "squeezer", short_name="sq")
        )
        self.register_element(make_element(components.ReadoutDC, "readout_dc"))
        self.register_element(make_element(components.ReadoutRF, "readout_rf"))
        self.register_element(
            make_element(
                components.SignalGenerator, "signal_generator", short_name="sgen"
            )
        )
        self.register_element(
            make_element(components.Telescope, "telescope", short_name="tel")
        )

        ## Detectors.
        self.register_element(
            make_element(
                detectors.AmplitudeDetector, "amplitude_detector", short_name="ad"
            )
        )
        self.register_element(
            make_element(detectors.FieldDetector, "field_detector", short_name="fd")
        )
        self.register_element(make_element(detectors.AstigmatismDetector, "astigd"))
        self.register_element(
            make_element(
                detectors.BeamPropertyDetector,
                "beam_property_detector",
                short_name="bp",
            )
        )
        self.register_element(
            make_element(detectors.OptimalQ, "optimal_q_detector", short_name="optbp")
        )
        self.register_element(make_element(detectors.CCD, "ccd"))
        self.register_element(make_element(detectors.CCDScanLine, "ccdline"))
        self.register_element(make_element(detectors.CCDPixel, "ccdpx"))
        self.register_element(
            make_element(
                detectors.CavityPropertyDetector,
                "cavity_property_detector",
                short_name="cp",
            )
        )
        self.register_element(make_element(detectors.FieldCamera, "fcam"))
        self.register_element(make_element(detectors.FieldScanLine, "fline"))
        self.register_element(make_element(detectors.FieldPixel, "fpx"))
        # The gouy detector factory's `last` flag is set it implicitly depends on any
        # nodes that appear in the path from its start port back to itself, so its
        # dependencies cannot be determined by the time the first set of elements are
        # built into the model. It is moved to the second build pass by this flag.
        self.register_element(make_element(detectors.Gouy, "gouy", build_last=True))
        self.register_element(make_element(detectors.KnmDetector, "knmd"))
        self.register_element(make_element(detectors.ModeMismatchDetector, "mmd"))
        self.register_element(
            make_element(detectors.MathDetector, "math_detector", short_name="mathd")
        )
        self.register_element(
            make_element(detectors.MotionDetector, "motion_detector", short_name="xd")
        )
        self.register_element(
            make_element(detectors.PowerDetector, "power_detector_dc", short_name="pd")
        )
        self.register_element(
            make_element(
                detectors.PowerDetectorDemod1,
                "power_detector_demod_1",
                short_name="pd1",
            )
        )
        self.register_element(
            make_element(
                detectors.PowerDetectorDemod2,
                "power_detector_demod_2",
                short_name="pd2",
            )
        )
        self.register_element(
            make_element(
                detectors.QuantumNoiseDetector,
                "quantum_noise_detector",
                short_name="qnoised",
            )
        )
        self.register_element(
            make_element(
                detectors.QuantumNoiseDetectorDemod1,
                "quantum_noise_detector_demod_1",
                short_name="qnoised1",
            )
        )
        self.register_element(
            make_element(
                detectors.QuantumNoiseDetectorDemod2,
                "quantum_noise_detector_demod_2",
                short_name="qnoised2",
            )
        )
        self.register_element(
            make_element(
                detectors.QuantumShotNoiseDetector,
                "quantum_shot_noise_detector",
                short_name="qshot",
            )
        )
        self.register_element(
            make_element(
                detectors.QuantumShotNoiseDetectorDemod1,
                "quantum_shot_noise_detector_demod_1",
                short_name="qshot1",
            )
        )
        self.register_element(
            make_element(
                detectors.QuantumShotNoiseDetectorDemod2,
                "quantum_shot_noise_detector_demod_2",
                short_name="qshot2",
            )
        )

        ## Connectors.
        self.register_element(make_element(components.Space, "space", short_name="s"))
        self.register_element(make_element(components.Wire, "wire", short_name="w"))
        self.register_element(make_element(components.Nothing, "nothing"))

        ## Mechanics.
        self.register_element(make_element(mechanical.FreeMass, "free_mass"))
        self.register_element(make_element(mechanical.Pendulum, "pendulum"))
        self.register_element(
            make_element(
                mechanical.SuspensionZPK, "suspension_zpk", short_name="sus_zpk"
            )
        )

        ## Lock.
        self.register_element(make_element(locks.Lock, "lock", ref_args=("feedback",)))

        ## Noise.
        self.register_element(make_element(noise.ClassicalNoise, "noise"))

        ## Gauss.
        self.register_element(
            ItemAdapter(
                full_name="gauss",
                getter=GaussDumper(),
                factory=ElementFactory(item_type=components.Gauss),
                setter=ElementSetter(item_type=components.Gauss),
                documenter=ElementDocumenter(item_type=components.Gauss),
            )
        )

        ## Variable.
        self.register_element(
            ItemAdapter(
                full_name="variable",
                getter=VariableDumper(),  # ElementDumper(item_type=components.Variable),
                factory=ElementFactory(item_type=components.Variable),
                setter=ElementSetter(item_type=components.Variable),
                documenter=ElementDocumenter(item_type=components.Variable),
                short_name="var",
            )
        )

        ## Commands
        self.register_command(
            ItemAdapter(
                full_name="fsig",
                getter=FsigDumper(),
                setter=FsigSetter(),
                documenter=FsigDocumenter(),
                singular=True,
            )
        )
        self.register_command(
            ItemAdapter(
                full_name="lambda",
                getter=CommandPropertyDumper(
                    item_type=Model.lambda0,
                    default=config_instance()["constants"].getfloat("lambda0"),
                ),
                setter=CommandPropertySetter(item_type=Model.lambda0),
                documenter=CommandPropertyDocumenter(item_type=Model.lambda0),
                singular=True,
            )
        )
        self.register_command(
            ItemAdapter(
                full_name="modes",
                getter=ModesDumper(),
                setter=CommandMethodSetter(item_type=Model.modes),
                documenter=CommandMethodDocumenter(item_type=Model.modes),
                singular=True,
            )
        )
        # self.register_command(
        #     ItemAdapter(
        #         full_name="add_parameter",
        #         getter=CommandMethodSetter(item_type=Model.add_parameter),
        #         setter=CommandMethodSetter(item_type=Model.add_parameter),
        #         documenter=CommandMethodDocumenter(item_type=Model.add_parameter),
        #     )
        # )
        self.register_command(
            ItemAdapter(
                full_name="link",
                setter=CommandMethodSetter(item_type=Model.link),
                documenter=CommandMethodDocumenter(item_type=Model.link),
            )
        )
        self.register_command(
            ItemAdapter(
                full_name="tem",
                getter=TEMDumper(),
                setter=TEMSetter(),
                documenter=TEMDocumenter(),
            )
        )
        self.register_command(
            ItemAdapter(
                full_name="phase_config",
                getter=PhaseConfigDumper(),
                setter=CommandMethodSetter(item_type=Model.phase_config),
                documenter=CommandMethodDocumenter(item_type=Model.phase_config),
            )
        )

        ## Group actions.
        self.register_analysis(make_analysis(actions.Parallel, "parallel"))
        self.register_analysis(make_analysis(actions.Series, "series"))
        self.register_analysis(make_analysis(actions.For, "for"))
        ## Axes.
        self.register_analysis(make_analysis(actions.Noxaxis, "noxaxis"))
        self.register_analysis(
            make_analysis(actions.Xaxis, "xaxis", ref_args=("parameter",))
        )
        self.register_analysis(
            make_analysis(
                actions.X2axis, "x2axis", ref_args=("parameter1", "parameter2")
            )
        )
        self.register_analysis(
            make_analysis(
                actions.X3axis,
                "x3axis",
                ref_args=("parameter1", "parameter2", "parameter3"),
            )
        )
        self.register_analysis(
            make_analysis(actions.Sweep, "sweep", ref_args=("*args",))
        )
        self.register_analysis(make_analysis(actions.Change, "change"))
        self.register_analysis(make_analysis(actions.UpdateMaps, "update_maps"))
        self.register_analysis(
            make_analysis(
                actions.FrequencyResponse, "frequency_response", short_name="freqresp"
            )
        )
        self.register_analysis(
            make_analysis(
                actions.FrequencyResponse2,
                "frequency_response2",
                short_name="freqresp2",
            )
        )
        self.register_analysis(
            make_analysis(
                actions.FrequencyResponse3,
                "frequency_response3",
                short_name="freqresp3",
            )
        )
        self.register_analysis(
            make_analysis(
                actions.FrequencyResponse4,
                "frequency_response4",
                short_name="freqresp4",
            )
        )
        self.register_analysis(
            make_analysis(actions.OptimiseRFReadoutPhaseDC, "opt_rf_readout_phase")
        )
        self.register_analysis(
            make_analysis(actions.SensingMatrixDC, "sensing_matrix_dc")
        )
        self.register_analysis(make_analysis(actions.SetLockGains, "set_lock_gains"))
        self.register_analysis(
            make_analysis(actions.GetErrorSignals, "get_error_signals")
        )
        ## Model physics.
        self.register_analysis(make_analysis(actions.Eigenmodes, "eigenmodes"))
        self.register_analysis(make_analysis(actions.Operator, "operator"))
        self.register_analysis(make_analysis(actions.ABCD, "abcd"))
        self.register_analysis(make_analysis(actions.BeamTrace, "beam_trace"))
        self.register_analysis(make_analysis(actions.PropagateBeam, "propagate_beam"))
        self.register_analysis(
            make_analysis(actions.PropagateAstigmaticBeam, "propagate_beam_astig")
        )
        self.register_analysis(make_analysis(actions.AntiSqueezing, "antisqueezing"))
        ## Utilities.
        self.register_analysis(make_analysis(actions.Debug, "debug"))
        self.register_analysis(make_analysis(actions.debug.SaveMatrix, "save_matrix"))
        self.register_analysis(make_analysis(actions.Plot, "plot"))
        self.register_analysis(make_analysis(actions.Printer, "print"))
        self.register_analysis(make_analysis(actions.RunLocks, "run_locks"))
        self.register_analysis(
            make_analysis(actions.PseudoLockCavity, "pseudo_lock_cavity")
        )
        self.register_analysis(
            make_analysis(actions.PseudoLockDRFPMI, "pseudo_lock_drfpmi")
        )
        self.register_analysis(
            make_analysis(actions.NoiseProjection, "noise_projection")
        )
        self.register_analysis(make_analysis(actions.PrintModel, "print_model"))
        self.register_analysis(
            make_analysis(actions.PrintModelAttr, "print_model_attr")
        )
        self.register_analysis(make_analysis(actions.Minimize, "minimize"))
        self.register_analysis(make_analysis(actions.Maximize, "maximize"))
        self.register_analysis(make_analysis(actions.DCFields, "dc_fields"))

    @property
    def directives(self):
        """All top level parser directives.

        :`getter`: Returns a mapping of top level parser directive aliases to
                   :class:`adapters <.ItemAdapter>`.
        :`type`: :class:`~collections.ChainMap`
        """
        # ChainMap yields in LIFO order so key order becomes elements, then commands,
        # then analyses. This order is relied upon by :func:`.syntax`.
        return ChainMap(self.analyses, self.commands, self.elements)

    @property
    def function_directives(self):
        """All top level function-style parser directives.

        :`getter`: Returns a mapping of top level function parser directive aliases to
                   :class:`adapters <.ItemAdapter>`.
        :`type`: :class:`~collections.ChainMap`
        """
        return ChainMap(self.analyses, self.commands)

    @property
    def reserved_names(self):
        """All reserved names.

        This is primarily useful for tests.

        :`getter`: Returns the names reserved in the parser as special production types.
        :`type`: :class:`list`
        """
        return list(self.keywords) + list(self.constants)

    def _register_adapter(self, mapping, adapter, overwrite=False):
        for alias in adapter.aliases:
            if alias in mapping:
                if overwrite:
                    LOGGER.info(
                        f"overwriting existing {repr(alias)} with {repr(adapter)}"
                    )
                else:
                    raise KeyError(
                        f"{repr(alias)} from {repr(adapter)} already exists (provided "
                        f"by {mapping[alias]}). If you intend to overwrite the "
                        f"existing definition, set overwrite=True."
                    )

            mapping[alias] = adapter

    def register_element(self, adapter, **kwargs):
        """Add parser and generator support for a model element such as a component or
        detector.

        Parameters
        ----------
        adapter : :class:`.ItemAdapter`
            The element adapter.

        Other Parameters
        ----------------
        overwrite : bool, optional
            Overwrite elements with the same aliases, if present. If `False` and one of
            `adapter`'s aliases already exists, a :class:`KeyError` is raised.
            Defaults to `False`.
        """
        self._register_adapter(self.elements, adapter, **kwargs)

    def register_command(self, adapter, **kwargs):
        """Add parser and generator support for a command.

        Parameters
        ----------
        adapter : :class:`.ItemAdapter`
            The command adapter.

        Other Parameters
        ----------------
        overwrite : bool, optional
            Overwrite commands with the same aliases, if present. If `False` and one of
            `adapter`'s aliases already exists, a :class:`KeyError` is raised.
            Defaults to `False`.
        """
        self._register_adapter(self.commands, adapter, **kwargs)

    def register_analysis(self, adapter, **kwargs):
        """Add parser and generator support for an analysis.

        Parameters
        ----------
        adapter : :class:`.ItemAdapter`
            The analysis adapter.

        Other Parameters
        ----------------
        overwrite : bool, optional
            Overwrite analyses with the same aliases, if present. If `False` and one of
            `adapter`'s aliases already exists, a :class:`KeyError` is raised.
            Defaults to `False`.
        """
        self._register_adapter(self.analyses, adapter, **kwargs)

    def type_descriptor(self, _type, default=None):
        """Get a descriptor for a type that's suitable for use in user feedback.

        This allows something other than Python class names to be displayed to the user
        inside error messages.

        Supports the same parameters as :meth:`dict.get`.
        """
        # This function is typically only needed by error handling code, so import
        # required types on first call.
        from ..components.node import Node, Port

        descriptors = {
            str: "string",
            int: "integer",
            float: "floating point",
            complex: "complex",
            Node: "node",
            Port: "port",
        }

        return descriptors.get(_type, default)

    def get_element_class(self, name: str) -> type:
        """Get the corresponding python class for a katscript model element.

        Parameters
        ----------
        name : str
            name of a katscript element

        Returns
        -------
        type
            Python class for this element

        Raises
        ------
        ValueError
            When the element can not be found
        """
        try:
            return self.elements[name].factory.item_type
        except KeyError:
            raise ValueError(f"'{name}' does not represent an element in KatScript")


# Shared KatSpec instance.
KATSPEC = KatSpec()
