import finesse


def test_cyexpr_parse():
    """Simple test to see if cyexpr parses strings correctly after setting the user
    locale.

    These would fail if the tinyexpr locale patch was not present, i.e, if the user
    locale is set to `.,` and the patch is not applied the expression `1.2+3` would fail
    since `1,2+3` would be expected.
    """

    # set the user locale (this is done within finesse.__init__)
    # locale.setlocale(locale.LC_ALL, "")

    # should pass with any user locale
    # fails without `tinyexpr` locale patch
    assert finesse.cyexpr.test_expr(".1", 0.1)
    assert finesse.cyexpr.test_expr("1.1+1", 2.1)
    assert finesse.cyexpr.test_expr("1.0+0.1", 1.1)
    assert finesse.cyexpr.test_expr("1.0+.1", 1.1)

    # should not pass
    # TODO: this should be tested in different environments
    assert not finesse.cyexpr.test_expr(",1", 0.1)  # invalid
    assert not finesse.cyexpr.test_expr("1,1+1", 2.1)  # 2.0
    assert not finesse.cyexpr.test_expr("1,0+0,1", 1.1)  # 1.0
    assert not finesse.cyexpr.test_expr("1,0+,1", 1.1)  # invalid
