import pytest
import numpy as np
from cxregions import *

@pytest.fixture
def circfun():
    return lambda t: np.exp(2j * np.pi * t)

@pytest.fixture
def circtanfun():
    return lambda t: 1j * 2 * np.pi * np.exp(2j * np.pi * t)

def test_curve_point(circfun, circtanfun):
    c = Curve(circfun, circtanfun, (0, 0.5))
    assert np.isclose(c.point(0.5), 1j)
    assert np.isclose(c.point(1), -1)
    c = ClosedCurve(circfun, circtanfun)
    assert np.isclose(c.point(0.25), 1j)
    assert np.isclose(c.point(0.5), -1)

def test_curve_tangent(circfun, circtanfun):
    c = Curve(circfun, circtanfun, (0, 1))
    t0 = c.tangent(0)
    t25 = c.tangent(0.25)
    assert np.isclose(t0, 1j * 2 * np.pi)
    assert np.isclose(t25, -2 * np.pi)
    c = ClosedCurve(circfun, circtanfun)
    t50 = c.tangent(0.5)
    assert np.isclose(t50, -1j * 2 * np.pi)

def test_curve_arclength(circfun, circtanfun):
    c = Curve(circfun, circtanfun, (0.5, 1))
    assert np.isclose(c.arclength(), np.pi)
    c = ClosedCurve(circfun, circtanfun)
    assert np.isclose(c.arclength(), 2 * np.pi)

def test_curve_inv(circfun, circtanfun):
    c = Curve(circfun, circtanfun, (0, 0.4))
    cinv = c.inv()
    assert np.isclose(cinv.point(0.3), 1 / c.point(0.3))
    c = ClosedCurve(circfun, circtanfun)
    cinv = c.inv()
    assert np.isclose(cinv.point(0.3), 1 / c.point(0.3))

def test_curve_conj(circfun, circtanfun):
    c = Curve(circfun, circtanfun, (0, 0.5))
    cconj = c.conj()
    assert np.isclose(cconj.point(0.25), np.conj(c.point(0.25)))
    c = ClosedCurve(circfun, circtanfun)
    cconj = c.conj()
    assert np.isclose(cconj.point(0.75), np.conj(c.point(0.75)))

def test_curve_winding(circfun, circtanfun):
    c = ClosedCurve(circfun, circtanfun)
    assert c.winding(0) == 1
    assert c.winding(2) == 0
    assert c.winding(-0.8j) == 1

def test_curve_arithmetic(circfun, circtanfun):
    l1 = Curve(circfun, circtanfun, (0, 1))
    l2 = l1 + 2j
    assert np.isclose(l2.point(0.5), l1.point(0.5) + 2j)
    l2 = 4 - 1j + l1
    assert np.isclose(l2.point(0.5), l1.point(0.5) + (4 - 1j))
    l2 = l1 - 2j
    assert np.isclose(l2.point(0.5), l1.point(0.5) - 2j)
    l2 = 4 - 1j - l1
    assert np.isclose(l2.point(0.5), -l1.point(0.5) + (4 - 1j))
    l2 = l1 * 2j
    assert np.isclose(l2.point(0.5), l1.point(0.5) * 2j)
    l2 = (4 - 1j) * l1
    assert np.isclose(l2.point(0.5), l1.point(0.5) * (4 - 1j))
    l2 = l1 / 2j
    assert np.isclose(l2.point(0.5), l1.point(0.5) / 2j)

def test_curve_repr(circfun, circtanfun):
    c = Curve(circfun, circtanfun, (0, 1))
    repr_str = repr(c)
    assert "Curve" in repr_str
    c = ClosedCurve(circfun, circtanfun)
    repr_str = repr(c)
    assert "Closed curve" in repr_str

# not possible without some autodiff capability
# def test_curve_notangent(circfun):
#     c = Curve(circfun, domain=(0, 1))
#     t0 = c.tangent(0)
#     t25 = c.tangent(0.25)
#     assert np.isclose(t0, 1j * 2 * np.pi)
#     assert np.isclose(t25, -2 * np.pi)
#     c = ClosedCurve(circfun)
#     t50 = c.tangent(0.5)
#     assert np.isclose(t50, -1j * 2 * np.pi)
