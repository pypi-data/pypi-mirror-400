import pytest
from finesse.knm.maps import Map
from finesse.exceptions import FinesseException
import numpy as np


@pytest.fixture
def mock_data():
    x = np.random.rand(3)
    y = np.random.rand(3)
    z = np.random.rand(3, 3)
    return x, y, z


@pytest.mark.parametrize("amp_or_opd", ("amplitude", "opd"))
def test_nans_raise_error(mock_data, amp_or_opd):
    x, y, z = mock_data
    z[1][1] = np.nan
    with pytest.raises(FinesseException):
        Map(x, y, **{amp_or_opd: z})


@pytest.mark.parametrize("amp_or_opd", ("amplitude", "opd"))
def test_wrong_shape(mock_data, amp_or_opd):
    x, y, z = mock_data
    x = np.random.rand(4)
    with pytest.raises(FinesseException):
        Map(x, y, **{amp_or_opd: z})


@pytest.mark.parametrize(
    "auto_kwarg",
    ("auto_remove_tilts", "auto_remove_curvatures", "auto_remove_astigmatism"),
)
def test_auto_args(mock_data, auto_kwarg):
    x, y, z = mock_data
    with pytest.raises(FinesseException):
        Map(x, y, z, **{auto_kwarg: True})
