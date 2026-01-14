import finesse


def test_make_micro_resonator():
    """Tests that the micro resonator example still builds and runs no physics checks
    here."""
    import numpy as np
    from finesse.components.workspace import ConnectorWorkspace
    from finesse.parameter import float_parameter
    from finesse.components import Connector, NodeType

    class MicroResonatorWorkspace(ConnectorWorkspace):
        pass

    @float_parameter("mass", "Mass", units="kg")
    @float_parameter("f", "Frequency", units="Hz")
    @float_parameter("Q", "Q-factor")
    class MicroResonator(Connector):
        """A micro resonator mechanical object.

        This mechanics element introduces three mechanical frequencies, one at the signal
        frequency and another at the resonance frequency +- the signal frequency.

        This element is meant to represent a micro resonantor whos resonance
        frequency matches the frequency separation between two carriers incident upon it.

        The object being suspended must have a mechanical port with
        node `z` and force `F_z`.
        """

        def __init__(self, name, mech_port, *, f=1e6, mass=1e-6, Q=1e4):
            super().__init__(name)
            self.mass = mass
            self.f = f
            self.Q = Q

            # Add motion and force nodes to mech port.
            # Here we duplicate the already created mechanical
            # nodes in some other connector element
            self._add_port("mech", NodeType.MECHANICAL)
            self.mech._add_node("z", None, mech_port.z)
            self.mech._add_node("F_z", None, mech_port.F_z)
            self._register_node_coupling("F_2_Z", self.mech.F_z, self.mech.z)

        def _on_add(self, model):
            self.mech.z.frequencies = self.frequencies
            self.mech.F_z.frequencies = self.frequencies

        def _get_workspace(self, sim):
            if sim.carrier.any_frequencies_changing:
                # ddb - This case probably needs some more thought on what beatings change
                raise NotImplementedError(
                    "Changing carrier frequencies whilst using a MicroResonant not supported yet."
                )

            if sim.signal:
                refill = (
                    sim.model.fsig.f.is_changing
                    or self.mass.is_changing
                    or self.f.is_changing
                    or self.Q.is_changing
                )
                ws = MicroResonatorWorkspace(self, sim)
                ws.signal.add_fill_function(self.fill, refill)
                ws.Fz_frequencies = sim.signal.signal_frequencies[self.mech.F_z]
                ws.z_frequencies = sim.signal.signal_frequencies[self.mech.z]
                return ws

            return None

        def _couples_frequency(self, ws, connection, frequency_in, frequency_out):
            return True

        @property
        def frequencies(self):
            """Mechanical frequencies this microresonant should model."""
            return (
                self._model.fsig.f.ref,
                self.f.ref + self._model.fsig.f.ref,
                self.f.ref - self._model.fsig.f.ref,
            )

        def fill(self, ws):
            wm = 2 * np.pi * ws.values.f

            Hz = lambda w: 1 / (
                self.mass.value * (wm**2 - w**2 + 1j * w * wm / ws.values.Q)
            )

            for fi in ws.Fz_frequencies.frequencies:
                for fo in ws.z_frequencies.frequencies:
                    if fi.f == fo.f:
                        with ws.sim.signal.component_edge_fill3(
                            ws.owner_id,
                            ws.signal.connections.F_2_Z_idx,
                            fi.index,
                            fo.index,
                        ) as mat:
                            mat[:] = Hz(2 * np.pi * fo.f)

    kat = finesse.Model()
    kat.parse(
        """
    l l1 P=1
    s sa l1.p1 bs1.p1
    l l2 P=1e3 f=1e6
    s sb l2.p1 bs1.p4
    bs bs1 R=0.5 T=0.5
    s s1 bs1.p3 m1.p1
    m m1 R=1 T=0

    fsig(1)
    sgen sg1 l2.amp.i 1 0

    # ad z m1.mech.z fsig
    ad probe_l m1.p1.o l1.f-fsig
    ad probe_u m1.p1.o l1.f+fsig
    ad pump_l m1.p1.o l2.f-fsig
    ad pump_u m1.p1.o l2.f+fsig
    """
    )
    kat.add(MicroResonator("ures", kat.m1.mech))
    kat.run()
