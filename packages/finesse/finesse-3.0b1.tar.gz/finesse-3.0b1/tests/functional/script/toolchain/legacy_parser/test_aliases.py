"""Legacy parser aliases tests."""


def test_mirror_alias(parser):
    """Test that using `mirror` in place of `m` does not throw error.

    See #537.
    """
    parser.parse(
        """
        l l1 1 0 n0
        s s1 1 n0 n1
        mirror m1 0.7 0.3 0 n1 n2
        """
    )


def test_space_alias(parser):
    """Test that using `space` in place of `s` does not throw error.

    See #536.
    """
    parser.parse(
        """
        l l1 1 0 n0
        space s1 1 n0 n1
        pd pd1 n1
        """
    )
