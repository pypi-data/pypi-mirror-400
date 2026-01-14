"""Legacy parser 1:n attribute mappings."""

import finesse


def test_g_attr():
    """Test that using `g` correctly maps to `user_gouy_x` and `user_gouy_y`."""
    model = finesse.Model()
    model.parse_legacy(
        """
        l l1 1 0 n0
        s s1 1 n0 n1
        attr s1 g 90
        """
    )

    assert model.s1.user_gouy_x == 90
    assert model.s1.user_gouy_y == 90


def test_gx_attr():
    """Test that using `gx` correctly maps to `user_gouy_x`."""
    model = finesse.Model()
    model.parse_legacy(
        """
        l l1 1 0 n0
        s s1 1 n0 n1
        attr s1 gx 90
        """
    )

    assert model.s1.user_gouy_x == 90


def test_gy_attr():
    """Test that using `gy` correctly maps to `user_gouy_y`."""
    model = finesse.Model()
    model.parse_legacy(
        """
        l l1 1 0 n0
        s s1 1 n0 n1
        attr s1 gy 90
        """
    )

    assert model.s1.user_gouy_y == 90
