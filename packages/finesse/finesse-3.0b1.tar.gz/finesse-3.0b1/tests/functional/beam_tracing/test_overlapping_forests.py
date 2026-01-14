"""Tests for model trace forest structure when cavities which overlap are included."""

from itertools import permutations

import pytest
from finesse import Model
from finesse.tracing.tree import TraceTree
from testutils.diff import assert_trace_trees_equal


@pytest.fixture()
def aligo_model():
    IFO = Model()
    IFO.parse(
        """
    # modulators for core interferometer sensing - Advanced LIGO, CQG, 2015
    # http://iopscience.iop.org/article/10.1088/0264-9381/32/7/074001/meta#cqg507871s4-8
    # 9MHz (CARM, PRC, SRC loops)
    variable f1 9099471
    variable f2 5*f1
    variable nsilica 1.45
    variable Mloss 30u

    ###############################################################################
    ###   length definitions
    ###############################################################################
    variable Larm 3994
    variable LPR23 16.164  # distance between PR2 and PR3
    variable LSR23 15.443  # distance between SR2 and SR3
    variable LPR3BS 19.538 # distance between PR3 and BS
    variable LSR3BS 19.366 # distance between SR3 and BS
    variable lmich 5.342   # average length of MICH
    variable lschnupp 0.08
    variable lPRC (3+0.5)*c0/(2*f1) # T1000298 Eq2.1, N=3
    variable lSRC (17)*c0/(2*f2) # T1000298 Eq2.2, M=3

    ###############################################################################
    ###   laser
    ###############################################################################
    laser L0 P=125
    mod mod1 f=f1 midx=0.18 order=1 mod_type=pm
    mod mod2 f=f2 midx=0.18 order=1 mod_type=pm
    link(L0, mod1, mod2)

    ###############################################################################
    ###   PRC
    ###############################################################################
    s sPRCin mod2.p2 PRMAR.p1
    m PRMAR R=0 L=40u xbeta=PRM.xbeta ybeta=PRM.ybeta phi=PRM.phi
    s sPRMsub1 PRMAR.p2 PRM.p1 L=0.0737 nr=nsilica
    m PRM T=0.03 L=8.5u Rc=11.009
    s lp1 PRM.p2 PR2.p1 L=lPRC-LPR3BS-LPR23-lmich
    bs PR2 T=250u L=Mloss alpha=-0.79 Rc=-4.545
    s lp2 PR2.p2 PR3.p1 L=LPR23
    bs PR3 T=0 L=Mloss alpha=0.615 Rc=36.027
    s lp3 PR3.p2 BS.p1 L=LPR3BS

    ###############################################################################
    ###   BS
    ###############################################################################
    bs BS R=0.5 L=Mloss alpha=45
    s BSsub1 BS.p3 BSAR1.p1 L=0.0687 nr=nsilica
    s BSsub2 BS.p4 BSAR2.p2 L=0.0687 nr=nsilica
    bs BSAR1 L=50u R=0 alpha=-29.195
    bs BSAR2 L=50u R=0 alpha=29.195

    ###############################################################################
    ###   Yarm
    ###############################################################################
    # Distance from beam splitter to Y arm input mirror
    s ly1 BS.p2 ITMYlens.p1 L=lmich-lschnupp/2-ITMYsub.L*ITMXsub.nr
    lens ITMYlens f=34500
    s ly2 ITMYlens.p2 ITMYAR.p1
    m ITMYAR R=0 L=20u xbeta=ITMY.xbeta ybeta=ITMY.ybeta phi=ITMY.phi
    s ITMYsub ITMYAR.p2 ITMY.p1 L=0.2 nr=nsilica
    m ITMY T=0.014 L=Mloss Rc=-1934
    s LY ITMY.p2 ETMY.p1 L=Larm
    m ETMY T=5u L=Mloss Rc=2245
    s ETMYsub ETMY.p2 ETMYAR.p1 L=0.2 nr=nsilica
    m ETMYAR 0 500u xbeta=ETMY.xbeta ybeta=ETMY.ybeta phi=ETMY.phi
    cav cavYARM ETMY.p1.o

    ###############################################################################
    ###   Xarm
    ###############################################################################
    # Distance from beam splitter to X arm input mirror
    s lx1 BSAR1.p3 ITMXlens.p1 L=lmich+lschnupp/2-ITMXsub.L*ITMXsub.nr-BSsub1.L*BSsub1.nr
    lens ITMXlens f=34500
    s lx2 ITMXlens.p2 ITMXAR.p1
    m ITMXAR R=0 L=20u xbeta=ITMX.xbeta ybeta=ITMX.ybeta phi=ITMX.phi
    s ITMXsub ITMXAR.p2 ITMX.p1 L=0.2 nr=nsilica
    m ITMX T=0.014 L=Mloss Rc=-1934
    s LX ITMX.p2 ETMX.p1 L=Larm
    m ETMX T=5u L=Mloss Rc=2245
    s ETMXsub ETMX.p2 ETMXAR.p1 L=0.2 nr=nsilica
    m ETMXAR 0 500u xbeta=ETMX.xbeta ybeta=ETMX.ybeta phi=ETMX.phi
    cav cavXARM ETMX.p1.o

    ###############################################################################
    ###   SRC
    ###############################################################################
    s ls3 BSAR2.p4 SR3.p1 L=LSR3BS
    bs SR3 T=0 L=Mloss alpha=0.785 Rc=35.972841
    s ls2 SR3.p2 SR2.p1 L=LSR23
    bs SR2 T=0 L=Mloss alpha=-0.87 Rc=-6.406
    s ls1 SR2.p2 SRM.p1 L=lSRC-LSR3BS-LSR23-BSsub2.L*BSsub2.nr-lmich
    m SRM T=0.2 L=8.7u Rc=-5.6938
    s SRMsub SRM.p2 SRMAR.p1 L=0.0749 nr=nsilica
    m SRMAR R=0 L=50n

    ###############################################################################
    ###   Output path
    ###############################################################################
    # Here we just use some simple filter to approximate an OMC for filtering
    # out RF fields, this doesn't filter HOMs!
    dbs OFI
    sq sqz db=6 angle=90.0
    link(sqz, OFI.p2)

    # (as built parameters: D1300507-v1)
    s sSRM_OFI SRMAR.p2 OFI.p1 L=0.7278
    s sOFI_OM1 OFI.p3 OM1.p1 L=2.9339

    bs OM1 T=800u L=0 alpha=2.251 Rc=[4.6, 4.6]
    s sOM1_OM2 OM1.p2 OM2.p1 L=1.395
    bs OM2 T=0 L=0 alpha=4.399 Rc=[1.7058, 1.7058]
    s sOM2_OM3 OM2.p2 OM3.p1 L=0.631
    bs OM3 T=0 L=0 alpha=30.037
    s sOM3_OMC OM3.p2 OMC_IC.p1 L=0.2034

    ###############################################################################
    ###   OMC
    ###############################################################################
    # obp OMC fc=0 bandwidth=1M filter_hom=[0,0]
    # link(SRMAR.p2, OFI.p1)
    # link(OFI.p3, OMC)

    cav cavOMC OMC_IC.p3.o
    bs OMC_IC T=0.0076 L=10u alpha=2.7609
    s lIC_OC OMC_IC.p3 OMC_OC.p1 L=0.2815
    bs OMC_OC T=0.0075 L=10u alpha=4.004
    s lOC_CM1 OMC_OC.p2 OMC_CM1.p1 L=0.2842
    bs OMC_CM1 T=36u L=10u alpha=4.004 Rc=[2.57321, 2.57321]
    s lCM1_CM2 OMC_CM1.p2 OMC_CM2.p1 L=0.2815
    bs OMC_CM2 T=35.9u L=10u alpha=4.004 Rc=[2.57369, 2.57369]
    s lCM2_IC OMC_CM2.p2 OMC_IC.p4 L=0.2842

    ###############################################################################
    ### Length sensing and control
    ###############################################################################
    dof XARM ETMX.dofs.z
    dof YARM ETMY.dofs.z
    dof CARM ETMX.dofs.z +1 ETMY.dofs.z +1
    dof DARM ETMX.dofs.z +1 ETMY.dofs.z -1
    dof PRCL PRM.dofs.z +1
    dof SRCL SRM.dofs.z +1 DC=90
    dof MICH BS.dofs.z +1
    dof MICH2 ITMY.dofs.z +1 ETMY.dofs.z +1 ITMX.dofs.z -1 ETMX.dofs.z -1
    dof STRAIN LX.dofs.h +1 LY.dofs.h -1
    dof FRQ L0.dofs.frq
    dof RIN L0.dofs.amp

    readout_rf REFL9 PRMAR.p1.o f=f1
    readout_rf REFL18 PRMAR.p1.o f=3*f1
    readout_rf REFL45 PRMAR.p1.o f=5*f1
    readout_rf POP9  PR2.p3.o   f=f1
    readout_rf POP45 PR2.p3.o   f=f2
    readout_rf AS45  SRMAR.p2.o f=f2
    readout_dc AS    OMC_OC.p3.o

    lock CARM_lock REFL9.outputs.I CARM.DC -0.1 1e-6
    lock MICH_lock POP45.outputs.Q MICH.DC -15 1e-6
    lock PRCL_lock POP9.outputs.I PRCL.DC 2.8 1e-6
    lock SRCL_lock POP45.outputs.I SRCL.DC 42 1e-6
    lock DARM_rf_lock AS45.outputs.I DARM.DC -0.003 1e-6
    lock DARM_dc_lock AS.outputs.DC DARM.DC -0.003 1e-6 offset=20m enabled=False

    ###############################################################################
    ### DC power measurements
    ###############################################################################
    pd Px ETMX.p1.i
    pd Py ETMX.p1.i
    pd Pprc PRM.p2.o
    pd Psrc SRM.p1.i
    pd Prefl ETMX.p1.i
    pd Pas OMC_OC.p3.o
    """
    )
    return IFO


@pytest.mark.parametrize("order", list(permutations(["PRX", "PRY"])))
def test_overlapping_prx_pry_forest(aligo_model: Model, order):
    """Test that overlapping power recycling cavities in X and Y arms are structured
    correctly in the model trace forest."""
    IFO = aligo_model

    IFO.parse(
        """
    cav PRX PRM.p2 ITMX.p1.i
    cav PRY PRM.p2 ITMY.p1.i
    """
    )
    IFO.remove("cavOMC")
    IFO.beam_trace(order=order)

    expect = [TraceTree.from_cavity(getattr(IFO, cav)) for cav in order]
    expect.reverse()

    # Arm cavities don't overlap with anything so will constitute
    # the first block of internal trace trees
    expect.insert(0, TraceTree.from_cavity(IFO.cavXARM))
    expect.insert(1, TraceTree.from_cavity(IFO.cavYARM))

    # Only really care about the internal trace trees, other
    # tests cover external forest structures
    for i in range(len(expect)):
        assert_trace_trees_equal(IFO.trace_forest.forest[i], expect[i])


@pytest.mark.parametrize("order", list(permutations(["SRX", "SRY"])))
def test_overlapping_srx_sry_forest(aligo_model: Model, order):
    """Test that overlapping signal recycling cavities in X and Y arms are structured
    correctly in the model trace forest."""
    IFO = aligo_model

    IFO.remove("cavOMC")
    IFO.parse(
        """
    cav SRX SRM.p1 ITMX.p1.i
    cav SRY SRM.p1 ITMY.p1.i
    """
    )

    IFO.beam_trace(order=order)

    expect = [TraceTree.from_cavity(getattr(IFO, cav)) for cav in order]
    expect.reverse()

    # Arm cavities don't overlap with anything so will constitute
    # the first block of internal trace trees
    expect.insert(0, TraceTree.from_cavity(IFO.cavXARM))
    expect.insert(1, TraceTree.from_cavity(IFO.cavYARM))

    # Only really care about the internal trace trees, other
    # tests cover external forest structures
    for i in range(len(expect)):
        assert_trace_trees_equal(IFO.trace_forest.forest[i], expect[i])


@pytest.mark.parametrize("order", list(permutations(["SRX", "SRY", "PRX", "PRY"])))
def test_overlapping_all_recycling_cavs_forest(aligo_model: Model, order):
    """Test that overlapping both recycling cavities in X and Y arms are structured
    correctly in the model trace forest."""
    IFO = aligo_model

    IFO.parse(
        """
    cav SRX SRM.p1 ITMX.p1.i
    cav SRY SRM.p1 ITMY.p1.i
    cav PRX PRM.p2 ITMX.p1.i
    cav PRY PRM.p2 ITMY.p1.i
    """
    )
    IFO.remove("cavOMC")
    IFO.remove("cavXARM")
    IFO.remove("cavYARM")

    IFO.beam_trace(order=order)

    expect = [TraceTree.from_cavity(getattr(IFO, cav)) for cav in order]
    expect.reverse()

    # Only really care about the internal trace trees, other
    # tests cover external forest structures
    for i in range(len(expect)):
        assert_trace_trees_equal(IFO.trace_forest.forest[i], expect[i])
