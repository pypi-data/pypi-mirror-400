import pytest
import numpy as np
from cxregions import Line, Segment, Arc, Circle, Ray

def test_intersect_circles():
    u = 1/5 + 1j/2
    c = Circle(0, 1)
    z = c.intersect(Circle(u, 3/2))
    assert isinstance(z, np.ndarray)
    assert len(z) == 2
    assert np.allclose(np.abs(z - 0), 1)
    assert np.allclose(np.abs(z - u), 3/2)
    z = c.intersect(Circle(u, 0.1))
    assert isinstance(z, np.ndarray) and len(z) == 0

def test_intersect_ray_ray():
    r1 = Ray(1, np.pi)
    r2 = Ray(1j, -np.pi/2)
    z = r1.intersect(r2)
    assert isinstance(z, np.ndarray)
    assert len(z) == 1
    assert np.allclose(z[0], 0j)
    r3 = Ray(-2.0, 0)
    z = r1.intersect(r3)
    #assert isinstance(z, Segment)   # TODO wrong in Julia
# TODO more tests for intersections

def test_intersect_line_line():
    l1 = Line(0, 1)
    l2 = Line(1+1j, -1-1j)
    z = l1.intersect(l2)
    assert isinstance(z, np.ndarray)
    assert len(z) == 1
    assert np.allclose(z[0], 0j)

def test_intersect_segment_segment():
    s1 = Segment(1j, 2+1j)
    s2 = Segment(1+2j, 1-2j)
    z = s1.intersect(s2)
    assert isinstance(z, np.ndarray)
    assert len(z) == 1
    assert np.allclose(z[0], 1+1j)
    s3 = Segment(-1+1j, 1+1j)
    z = s1.intersect(s3)
    assert isinstance(z, Segment)
    assert np.isclose(z.arclength(), 1.0)