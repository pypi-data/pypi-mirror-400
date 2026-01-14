import pytest
import numpy as np
from cxregions import *

@pytest.fixture
def segment():
    return Segment(1, 1j)

@pytest.fixture
def arc():
    return Arc(1j, -1 + 0.5j, -1)

def test_path_points(segment, arc):
    P = Path([segment, arc, -segment])
    assert isinstance(P, Path)
    for (t,z) in [(0, segment.point(0)), 
                  (1, segment.point(1)),
                  (1.5, arc.point(0.5)),
                  (2.5, -segment.point(0.5)),
                  (3, -segment.point(1))]:
        assert np.isclose(P.point(t), z)

def test_path_curve_access(segment, arc):
    P = Path([segment, arc])
    curves = P.curves()
    assert len(curves) == 2
    assert isinstance(curves[0], Segment)
    assert isinstance(curves[1], Arc)

def test_path_angles():
    z = (2 + 2j) / 5
    p = Path([Arc(-1, -z, -1j), Arc(-1j, np.conj(z), 1), Arc(1, z, 1j)])
    theta = p.angles()
    assert np.isclose(theta[1], 0.78121408739537)
    assert np.isclose(theta[1], theta[2])

def test_path_vertices(segment, arc):
    P = Path([segment, 1j * segment, -segment])
    v = P.vertices()
    assert len(v) == 4
    assert np.isclose(v[2], -1)
    assert np.isclose(P.vertex(3), -1)

def test_path_arclength(segment, arc):
    P = Path([segment, arc, -segment])
    L = segment.arclength() + arc.arclength() + segment.arclength()
    assert np.isclose(P.arclength(), L)

def test_path_reverse(segment, arc):
    P = Path([segment, arc])
    Pr = P.reverse()
    assert np.isclose(Pr.point(0), P.point(2))
    assert np.isclose(Pr.point(0.5), P.point(1.5))
    assert np.isclose(Pr.point(2), P.point(0))

def test_path_tangent(segment, arc):
    P = Path([segment, 1j * segment, -segment])
    t1 = P.unittangent(1.5)
    assert np.isclose(t1, 1j * segment.unittangent(0.5))

def test_path_inverse(segment, arc):
    P = Path([segment, 1j * segment, -segment])
    Pinv = P.inv()
    assert np.isclose(Pinv.point(0), 1 / P.point(0))
    assert np.isclose(Pinv.point(1.5), 1 / P.point(1.5))
    assert np.isclose(Pinv.point(3), 1 / P.point(3))

def test_path_closest(segment, arc):
    P = Path([segment, arc, -segment])
    z = P.closest(2 + 2j)
    assert np.isclose(z, segment.closest(2 + 2j))

def test_path_winding(segment, arc):
    P = ClosedPath([segment, 1j * segment, -segment, -1j * segment])
    assert P.winding(-1/3 - 1j/2) == 1
    assert P.winding(2 + 2j) == 0
    assert P.isinside(-1/3 - 1j/2)