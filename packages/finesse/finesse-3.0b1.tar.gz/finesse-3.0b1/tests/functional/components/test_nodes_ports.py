import finesse


def test_is_connected():
    model = finesse.script.parse(
        """
                              l l1
                              m m1
                              readout_dc PD
                              link(l1, m1, PD, PD.DC, l1.amp)
                              l l2
                              """
    )

    assert model.l1.p1.is_connected
    assert model.m1.p1.is_connected
    assert model.m1.p2.is_connected
    assert not model.l2.p1.is_connected
    assert not model.l1.phs.is_connected
    assert not model.l1.frq.is_connected
    assert not model.m1.mech.is_connected
    assert model.l1.amp.is_connected
    assert model.PD.DC.is_connected


def test_attached_to():
    model = finesse.script.parse(
        """
                                l l1
                                m m1
                                readout_dc PD
                                link(l1, m1, PD, PD.DC, l1.amp)
                                l l2
                                """
    )

    assert model.l1.p1.attached_to is model.spaces.l1_p1__m1_p1
    assert model.m1.p1.attached_to is model.spaces.l1_p1__m1_p1
    assert model.m1.p2.attached_to is model.spaces.m1_p2__PD_p1
    assert len(model.l1.mech.attached_to) == 0
    assert len(model.m1.mech.attached_to) == 0
    assert model.wires.PD_DC__l1_amp in model.l1.amp.attached_to
    assert model.wires.PD_DC__l1_amp in model.PD.DC.attached_to
