import pytest
import numpy.testing as npt
import numpy as np
from np_vmd.misc import convert_harmonic_to_cos, convert_harmonic_to_sin
from np_vmd.misc import HarmonicMotion
# create a fixture for the time vector
@pytest.fixture
def times():
    return np.linspace(0, 10, 1000)

# define the parameterized test for convert_harmonic_to_cos
@pytest.mark.parametrize("A, B", [(1, 2), (3, 4), (5, 6), (1,0),(1,1)])
def test_convert_harmonic_to_cos(A, B, times):
    """
    Test the conversion of a harmonic function to a cosine function.

    Parameters:
    - A: float
        Amplitude of the cosine function.
    - B: float
        Amplitude of the sine function.
    - times: array-like
        The time values at which to evaluate the functions.

    Returns:
    None
    """
    w = 1
    xcos, pc = convert_harmonic_to_cos(A, B)

    h1 = A * np.cos(w * times) + B * np.sin(w * times)
    hcos = xcos * np.cos(w * times + pc)
    npt.assert_allclose(h1, hcos)

# define the parameterized test for convert_harmonic_to_sin
@pytest.mark.parametrize("A, B", [(1, 2), (3, 4), (5, 6)])
def test_convert_harmonic_to_sin(A, B, times):
    """
    Test the conversion of a harmonic function to a sine function.

    Parameters:
    - A: float
        Amplitude of the cosine function.
    - B: float
        Amplitude of the sine function.
    - times: array-like
        The time values at which to evaluate the functions.

    Returns:
    None
    """
    w = 1
    xsin, psin = convert_harmonic_to_sin(A, B)
    h1 = A * np.cos(w * times) + B * np.sin(w * times)
    hsin = xsin * np.sin(w * times + psin)
    npt.assert_allclose(h1, hsin)

# define the test for HarmonicMotion class
def test_harmonic_motion():
    """
    Test the HarmonicMotion class.

    Parameters:
    None

    Returns:
    None
    """
    A = 1
    B = 2
    motion = HarmonicMotion(A=1, B=2)
    Xc, pcos = motion.to_X_cos_phi()
    Xs, psin = motion.to_X_sin_phi()
    assert Xc == Xs
    hm_cos = HarmonicMotion.from_X_cos_phi(Xc, pcos)
    hm_sin = HarmonicMotion.from_X_sin_phi(Xs, psin)
    assert hm_cos.A == pytest.approx(hm_sin.A, rel=1e-6)
    assert hm_cos.B == pytest.approx(hm_sin.B, rel=1e-6)
    assert hm_cos.A == pytest.approx(A, rel=1e-6)
    assert hm_cos.B == pytest.approx(B, rel=1e-6)
    

    



