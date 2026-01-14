import finesse
import pytest
import numpy as np


@pytest.mark.parametrize("z", [1 + 0j, 0 + 1j, 0.2 + 40j, 1e1 + 1e-14j])
def test_internals(z):
    assert np.allclose(
        finesse.cymath.complex._test_carg(z), np.angle(z), rtol=1e-13, atol=1e-13
    )
    assert np.allclose(
        finesse.cymath.complex._test_cabs(z), np.abs(z), rtol=1e-13, atol=1e-13
    )
    assert np.allclose(
        finesse.cymath.complex._test_creal(z), np.real(z), rtol=1e-13, atol=1e-13
    )
    assert np.allclose(
        finesse.cymath.complex._test_cimag(z), np.imag(z), rtol=1e-13, atol=1e-13
    )
    assert np.allclose(
        finesse.cymath.complex._test_cexp(z), np.exp(z), rtol=1e-13, atol=1e-13
    )
    assert np.allclose(
        finesse.cymath.complex._test_conj(z), np.conj(z), rtol=1e-13, atol=1e-13
    )


@pytest.mark.parametrize("z", [1 + 0j, 0 + 1j, 0.2 + 40j, 1e1 + 1e-14j])
@pytest.mark.parametrize("n", [0, 1, -1, 0.5, 2, 1.33])
def test_cpow_re(z, n):
    assert np.allclose(
        finesse.cymath.complex.cpow_re(z, n), np.power(z, n), rtol=1e-13, atol=1e-13
    )


@pytest.mark.parametrize("z1", [1 + 0j, 0 + 1j, 0.2 + 40j, 1e1 + 1e-14j])
@pytest.mark.parametrize("z2", [1 + 0j, 0 + 1j, 0.2 + 40j, 1e1 + 1e-14j])
def test_ceq(z1, z2):
    assert finesse.cymath.complex.ceq(z1, z2) == np.allclose(z1, z2, atol=1e-13)


@pytest.mark.parametrize("z", [1 + 0j, 0 + 1j, 0.2 + 40j, 1e1 + 1e-14j, 0, -0])
def test_czero(z):
    assert finesse.cymath.complex.czero(z) == (np.real(z) == 0 and np.imag(z) == 0)


@pytest.mark.parametrize("z", [1 + 0j, 0 + 1j, 0.2 + 40j, 1e1 + 1e-14j])
@pytest.mark.parametrize("phi", [0, np.pi, np.pi / 2, 0.33234453])
def test_crotate(z, phi):
    assert np.allclose(finesse.cymath.complex.crotate(z, phi), z * np.exp(1j * phi))


@pytest.mark.parametrize("z", [1 + 0j, 0 + 1j, 0.2 + 40j, 1e1 + 1e-14j, 0, -0])
def test_cnorm(z):
    assert finesse.cymath.complex.cnorm(z) == (np.real(z) ** 2 + np.imag(z) ** 2)


@pytest.mark.parametrize("z", [1 + 0j, 0 + 1j, 0.2 + 40j, 1e1 + 1e-14j])
def test_inverse(z):
    assert np.allclose(finesse.cymath.complex.inverse_unsafe(z), 1 / z)
