"""Single-frequency array of complex amplitudes detector."""

import logging

import numpy as np

from finesse.components.node import Node, NodeType
from finesse.detectors.general import Detector
from finesse.parameter import float_parameter
from finesse.detectors.workspace import DetectorWorkspace

LOGGER = logging.getLogger(__name__)


class FDWorkspace(DetectorWorkspace):
    def __init__(self, owner, sim):
        needs_carrier = False
        needs_signal = False
        self.lower_audio = False
        self.is_f_changing = owner.f.is_changing
        if owner.f.eval() is None:
            raise ValueError(
                f"{owner.f}: frequency value is `None`, check values have been set correctly."
            )
        fval = float(owner.f)
        fs = []

        if sim.carrier:
            f = sim.carrier.get_frequency_object(fval, owner.node)
            if f is not None:
                needs_carrier = True
                fs.append((f, sim.carrier))

        if sim.signal:
            f = sim.signal.get_frequency_object(fval, owner.node)
            if f is not None:
                needs_signal = True
                self.lower_audio = f.audio_order < 0
                fs.append((f, sim.signal))

        if len(fs) == 0:
            raise Exception(
                f"Error in field detector {owner.name}:\n"
                f"    Could not find a frequency bin at {owner.f}"
            )
        elif len(fs) > 1:
            raise Exception(
                f"Error in field detector {owner.name}:\n"
                f"    Found multiple frequency bins at {owner.f}"
            )

        super().__init__(
            owner, sim, needs_carrier=needs_carrier, needs_signal=needs_signal
        )
        freq, self.mtx = fs[0]
        self.fidx = freq.index
        self.node_idx = int(self.mtx.node_id(owner.node))
        self.set_output_fn(self.__output)

    @staticmethod
    def __output(ws):
        z = np.asarray(ws.mtx.node_field_vector(ws.node_idx, ws.fidx)) / np.sqrt(2)

        if ws.lower_audio:
            return z.conj()
        else:
            return z


@float_parameter("f", "Frequency", units="Hz")
# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class FieldDetector(Detector):
    """Outputs an array of the higher order modes amplitudes at a particular node and
    frequency. The mode ordering is given by `Model.homs`. Plane wave models will output
    a single element array.

    This detector can only be used on optical nodes.

    Parameters
    ----------
    name : str
        Name of newly created detector.

    node : :class:`.Node`
        Node to read output from.

    f : float
        Frequency of light to detect (in Hz).

    Examples
    --------
    >>> import finesse
    >>> model = finesse.Model()
    >>> model.parse('''
        laser l1
        gauss g1 l1.p1.o w0=1m z=0
        m m1 R=1 T=0 xbeta=1e-9 ybeta=3e-8
        link(l1, m1)
        modes(maxtem=1)
        fd fd1 m1.p1.o 0
    ''')
    >>> out = model.run('noxaxis()')
    >>> print(out['fd1'])
    array([
        0.99999998+0.00000000e+00j,
        0+1.77157478e-04j,
        0+5.90524926e-06j
    ])
    """

    def __init__(self, name, node: Node, f):
        if node.type is not NodeType.OPTICAL:
            raise Exception(f"Must be an optical node used for FieldDetector {name}")
        Detector.__init__(self, name, node, dtype=np.complex128, label="HOM Amplitudes")
        self.f = f

    def _get_workspace(self, sim):
        # Need to update the shape of this output depending on how many HOMs
        # there are, 1 if plane wave
        self._update_dtype_shape((sim.model_settings.num_HOMs,))
        return FDWorkspace(self, sim)
