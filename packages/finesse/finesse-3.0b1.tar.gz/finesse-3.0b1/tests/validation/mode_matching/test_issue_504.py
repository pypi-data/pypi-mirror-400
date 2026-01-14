"""Issues 504 turned out to be an error because setting a Gauss fixes the q parameters
and marks certain connections as not changing.

There fore there is a difference in changing geometric parameters inside and outside of
actions.
"""

import finesse
from finesse.analysis.actions import Series, Noxaxis, Change


def test_in_and_out_of_action_Rc_change():
    script = """
    laser i1 P=20.0
    mod eom8 f=(1.3333333333333333*6270777) midx=0.15
    link(i1, eom8, PR.p1)
    m PR R=0.95162 T=0.04835 L=30u Rc=-1435.88
    s s_prc PR.p2 ITM.p1 L=11.95196615985547
    m ITM R=0.986203 T=0.013769999999999949 L=27u Rc=-1425.0
    pd1 prc_err_I PR.p1.o f=eom8.f phase=2.4697678827455953

    dof PR_z PR.dofs.z 1 DC=90

    cav cavPR PR.p2.o via=ITM.p1.i priority=1
    """

    ifo = finesse.Model()
    ifo.parse(script)
    ifo.parse("gauss g1 PR.p1.i w0=0.010013251224726306 z=-1365.8318213619111")
    ifo.modes("even", maxtem=2)

    out1 = ifo.run(
        Series(
            Change({"PR.Rcx": ifo.PR.Rcx + 2, "PR.Rcy": ifo.PR.Rcy + 2}),
            Noxaxis(name="noxaxis"),
        )
    )

    out2 = ifo.run(Noxaxis())
    # These should be numerically identical
    assert out1["prc_err_I"] == out2["prc_err_I"]
