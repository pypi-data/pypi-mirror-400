import pytest
import numpy as np
from cxregions import Arc

@pytest.fixture
def arc_fixture_a():
    a = np.exp(1j * np.pi / 2) 
    b = np.exp(1j * np.pi / 5)
    return Arc(a, b, 1)

@pytest.fixture
def arc_fixture_b():
    return Arc(-1j, 1j, -1)

def test_arc_isfinite(arc_fixture_a):
    assert arc_fixture_a.isfinite()

def test_arc_point(arc_fixture_a, arc_fixture_b):
    z = (1 + 1j) / np.sqrt(2)
    assert np.isclose(arc_fixture_a.point(0.5), z)
    assert np.isclose(arc_fixture_b.point(2/3), 1j)

def test_arc_arg(arc_fixture_a):
    assert np.isclose(arc_fixture_a.arg(arc_fixture_a.point(0.3)), 0.3)

def test_arc_dist(arc_fixture_b):
    assert np.isclose(arc_fixture_b.dist(-2 - 4j), np.abs(-2 - 4j + 1j))

def test_arc_tangent(arc_fixture_a):
    assert np.isclose(np.angle(arc_fixture_a.tangent(0.5)), -np.pi / 4)

def test_arc_inv(arc_fixture_a):
    assert arc_fixture_a.isapprox(arc_fixture_a.inv().inv())

def test_arc_closest(arc_fixture_b):
    assert np.isclose(arc_fixture_b.closest(5j), 1j)

def test_arc_repr(arc_fixture_b):
    repr_str = repr(arc_fixture_b)
    assert "Arc" in repr_str

def test_arc_add(arc_fixture_a):
    l1 = arc_fixture_a
    l2 = l1 + 2j
    assert np.isclose(l2.point(0.5), l1.point(0.5) + 2j)
    l2 = 4 - 1j + l1
    assert np.isclose(l2.point(0.5), l1.point(0.5) + (4 - 1j))

def test_arc_sub(arc_fixture_a):
    l1 = arc_fixture_a
    l2 = l1 - 2j
    assert np.isclose(l2.point(0.5), l1.point(0.5) - 2j)
    l2 = 4 - 1j - l1
    assert np.isclose(l2.point(0.5), -l1.point(0.5) + (4 - 1j))

def test_arc_mul(arc_fixture_a):
    l1 = arc_fixture_a
    l2 = l1 * 2j
    assert np.isclose(l2.point(0.5), l1.point(0.5) * 2j)
    l2 = (4 - 1j) * l1
    assert np.isclose(l2.point(0.5), l1.point(0.5) * (4 - 1j))

def test_arc_div(arc_fixture_a):
    l1 = arc_fixture_a
    l2 = l1 / 2j
    assert np.isclose(l2.point(0.5) * 2j, l1.point(0.5))