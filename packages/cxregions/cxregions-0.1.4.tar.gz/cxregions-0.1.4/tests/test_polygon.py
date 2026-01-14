import pytest
import numpy as np
from cxregions import *

@pytest.fixture
def segment():
    return Segment(2, 2j)

@pytest.fixture
def polygon():
    return Polygon([4, 4 + 3j, 3j, -2j, 6 - 2j, 6])

@pytest.fixture
def circpoly():
    return CircularPolygon([
        Arc(1, 2 + 1j, 1j), 
        Segment(1j, -1), 
        Arc(-1, -0.5j, -1j), 
        Segment(-1j, 1)])

def cispi(t):
    return np.cos(np.pi * t) + 1j * np.sin(np.pi * t)

def test_polygon_arclength(segment):
    s = segment
    p = Polygon([s, 1j * s, -s, -1j * s])
    assert np.isclose(p.arclength(), 4 * s.arclength())
    assert np.all([p.side(k).isapprox(p.sides()[k]) for k in range(4)])

def test_polygon_angles(polygon):
    angles = polygon.angles()
    expected_angles = np.pi * np.array([3/2, 1/2, 1/2, 1/2, 1/2, 1/2])
    assert np.allclose(angles, expected_angles)

def test_polygon_winding(polygon):
    assert polygon.winding(5 - 1j) == 1
    assert polygon.winding(-1) == 0
    q = polygon.reverse()
    assert q.winding(5 - 1j) == -1
    assert q.winding(-1) == 0

def test_polygon_arithmetic(polygon):
    p1 = polygon
    p2 = p1 + 2j
    assert p2.dist(p1.point(0.5) + 2j) < 1e-7
    p2 = 4 - 1j + p1
    assert p2.dist(p1.point(0.5) + (4 - 1j)) < 1e-7

    p2 = p1 - 2j
    assert p2.dist(p1.point(0.5) - 2j) < 1e-7
    p2 = 4 - 1j - p1
    assert p2.dist(-p1.point(0.5) + (4 - 1j)) < 1e-7

    p2 = p1 * 2j
    assert p2.dist(p1.point(0.5) * 2j) < 1e-7
    p2 = (4 - 1j) * p1
    assert p2.dist((4 - 1j) * p1.point(0.5)) < 1e-7

def test_circularpolygon_arclength(circpoly):
    cp = circpoly
    total_length = sum([s.arclength() for s in cp.sides()])
    assert np.isclose(cp.arclength(), total_length)

def test_circularpolygon_winding(circpoly):
    z = [1 + 0.5j, 1.7 + 1j, 0, -1 + 0.05 * cispi(1/5), -1j + 0.05 * cispi(0.3)]
    assert np.all([circpoly.winding(x) == 1 for x in z])
    z = [-0.999j, 0.001 - 1j, -0.999, -1.001, 1.001, 1.999j, 1000j]
    assert np.all([circpoly.winding(x) == 0 for x in z])

def test_circularpolygon_inv(circpoly):
    cp = circpoly
    inv_cp = cp.inv()
    for (s, t) in zip(cp.sides(), inv_cp.sides()):
        assert t.isapprox(s.inv())