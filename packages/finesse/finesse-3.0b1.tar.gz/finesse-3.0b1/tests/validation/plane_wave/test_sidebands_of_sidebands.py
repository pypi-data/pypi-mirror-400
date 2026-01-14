import finesse
import numpy as np


def test_sos_cancellation():
    """Https://dcc.ligo.org/LIGO-T1300986/public"""

    base = finesse.Model()
    base.parse(
        """
    l L1 P=1.0                          # Laser : 1 W
    s s0 L1.p1 EOM1.p1 L=0
    mod EOM1 f=5M midx=0.05             # EOM1 : Omega_1 = 2 pi *5 MHz , m_1 = 0.05
    s S1 EOM1.p2 EOM2.p1 L=0            # Zero space
    mod EOM2 f=1M midx=0.01             # EOM2 : Omega_2 = 2 pi *1 MHz , m_2 = 0.01
    s S2 EOM2.p2 n0.p1
    nothing n0
    pd1 PD n0.p1.i 6M 0                 # PD : omega_x = 2 pi *6 MHz
    xaxis(EOM1.phase, lin, 0, 360, 100) # Tuning the modulation phase of EOM1
    """
    )

    base.add_frequency(-6e6)
    base.add_frequency(-4e6)
    base.add_frequency(4e6)
    base.add_frequency(6e6)

    sol = base.run()

    assert np.allclose(sol["PD"], 0)
