import numpy as np
import pytest
from cxregions import Circle

@pytest.fixture
def circle_thru_origin():
    return Circle(1 - 1j, np.sqrt(2))

def test_arclength(circle_thru_origin):
    c = circle_thru_origin
    assert abs(c.arclength() - 2 * np.sqrt(2) * np.pi) < 1e-7

def test_distance(circle_thru_origin):
    c = circle_thru_origin
    assert abs(c.dist(-1 + 1j) - np.sqrt(2)) < 1e-7

def test_closest_point(circle_thru_origin):
    c = circle_thru_origin
    closest = c.closest(1 + 4j)
    assert abs(closest.real - 1) < 1e-7
    assert abs(closest.imag - (np.sqrt(2) - 1)) < 1e-7

def test_inside_outside(circle_thru_origin):
    c = circle_thru_origin
    # assert c.isinside(1.5 - 1j)
    # assert c.isoutside(3/2 + 1j)

def test_reflect(circle_thru_origin):
    c = circle_thru_origin
    reflected = c.reflect(-1 + 2j)
    reflected_twice = c.reflect(reflected)
    assert abs(reflected_twice.real - (-1)) < 1e-7
    assert abs(reflected_twice.imag - 2) < 1e-7

def test_tangent(circle_thru_origin):
    tangent = circle_thru_origin.tangent(0.125)
    assert abs(tangent) - 2 * np.pi * np.sqrt(2) < 1e-7

def test_unittangent(circle_thru_origin):
    unittangent = circle_thru_origin.unittangent(0.25)
    assert abs(unittangent) - 1.0 < 1e-7

def test_circle_add(circle_thru_origin):
    l1 = circle_thru_origin
    l2 = l1 + 2j
    assert l2.dist(l1.point(0.5) + 2j) < 1e-7
    l2 = 4 - 1j + l1
    assert l2.dist(l1.point(0.5) + (4 - 1j)) < 1e-7

def test_circle_sub(circle_thru_origin):
    l1 = circle_thru_origin
    l2 = l1 - 2j
    assert l2.dist(l1.point(0.5) - 2j) < 1e-7
    l2 = 4 - 1j - l1
    assert l2.dist(-l1.point(0.5) + (4 - 1j)) < 1e-7

def test_circle_mul(circle_thru_origin):
    l1 = circle_thru_origin
    l2 = l1 * 2j
    assert l2.dist(l1.point(0.5) * 2j) < 1e-7
    l2 = (4 - 1j) * l1
    assert l2.dist(l1.point(0.5) * (4 - 1j)) < 1e-7

def test_circle_div(circle_thru_origin):
    l1 = circle_thru_origin
    l2 = l1 / 2j
    assert l2.dist(l1.point(0.5) / 2j) < 1e-7

def test_repr(circle_thru_origin):
    repr_str = repr(circle_thru_origin)
    assert "Circle centered at" in repr_str
    assert "with radius" in repr_str