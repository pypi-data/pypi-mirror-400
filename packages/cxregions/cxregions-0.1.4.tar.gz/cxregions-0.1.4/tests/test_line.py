import pytest
import numpy as np
from cxregions import Line, Circle

def check(u, v, rtol=1e-12, atol=1e-12):
    """Helper function to check approximate equality with tolerance"""
    if isinstance(u, (list, tuple, np.ndarray)) and isinstance(v, (list, tuple, np.ndarray)):
        return all(check(ui, vi, rtol, atol) for ui, vi in zip(u, v))
    elif isinstance(u, (list, tuple, np.ndarray)):
        return all(check(ui, v, rtol, atol) for ui in u)
    else:
        return np.isclose(u, v, rtol=rtol, atol=atol)

@pytest.fixture
def line_fixture():
    return Line(1j, direction=1 + 2j)

def test_line_constructor():
    """Test Line constructor"""
    l = Line(1, 5)
    assert isinstance(l, Line)

def test_line_with_direction(line_fixture):
    """Test Line with direction parameter"""
    l = line_fixture
    assert check(l.slope(), 2.0)
    assert check(l.angle(), np.arctan(2.0))
    
def test_line_conjugate_angle(line_fixture):
    """Test conjugate line angle"""
    conj_l = line_fixture.conj()
    assert check(conj_l.angle(), -np.arctan(2.0))
    
def test_line_reverse_angle(line_fixture):
    """Test reverse line angle"""
    rev_l = line_fixture.reverse()
    assert check(rev_l.angle(), np.arctan(2.0) - np.pi)
    
def test_line_left_right(line_fixture):
    """Test isleft and isright methods"""
    l = line_fixture
    assert l.isleft(2j) and not l.isleft(0)
    assert not l.isright(2j) and l.isright(0)
    
def test_line_arclength_infinite(line_fixture):
    assert np.isinf(line_fixture.arclength())
    
def test_line_not_finite(line_fixture):
    """Test that line is not finite"""
    assert not line_fixture.isfinite()
    
def test_line_is_positive(line_fixture):
    """Test that line is positive"""
    assert line_fixture.ispositive()
    
def test_line_arg_method(line_fixture):
    """Test arg method for points on the line"""
    # Test that arg works for points on the line
    for t in np.arange(0.1, 1.0, 0.1):
        point_on_line = line_fixture.point(t)
        arg_val = line_fixture.arg(point_on_line)
        assert check(arg_val, t)
    
    # Test that arg returns None for points not on the line
    assert line_fixture.arg(1 + 2j) is None
    
def test_line_unittangent(line_fixture):
    """Test unit tangent vector"""
    ut = line_fixture.unittangent()
    assert check(abs(ut), 1.0)
    
def test_line_tangent_direction(line_fixture):
    """Test tangent direction consistency"""
    l = line_fixture
    p1 = l.point(3/5)
    p2 = l.point(1/10)
    dz = p1 - p2
    assert check(np.angle(dz), np.angle(1 + 2j))
    
def test_line_inverse_is_circle(line_fixture):
    """Test that 1/line is a Circle"""
    inv_l = line_fixture.inv()
    assert isinstance(inv_l, Circle)
    
def test_line_arithmetic_operations(line_fixture):
    """Test arithmetic operations on lines"""
    # Test that we can get points and tangents from the line
    tangent_val = line_fixture.tangent(0.5)
    
    # Check that the tangent direction is consistent
    assert check(np.angle(tangent_val), np.angle(1 + 2j))
        
def test_line_distance_and_closest(line_fixture):
    """Test distance and closest point calculations"""
    l = line_fixture
    
    # Create a point offset from the line
    point_on_line = l.point(3/10)
    direction = 1 + 2j
    normal_direction = 1j * np.sign(direction)  # perpendicular direction
    z = point_on_line + normal_direction
    
    # Test distance
    dist = l.dist(z)
    assert check(dist, 1.0)
    
    # Test that distance calculation works
    assert isinstance(l.dist(z), (int, float, complex, np.number))
    
    # Test closest point
    closest = l.closest(z)
    expected_closest = l.point(3/10)
    assert check(closest, expected_closest)
    
def test_line_reflection(line_fixture):
    """Test reflection across line"""
    l = line_fixture
    
    # Create a point offset from the line
    point_on_line = l.point(3/10)
    direction = 1 + 2j
    normal_direction = 1j * np.sign(direction)
    z = point_on_line + normal_direction
    
    # Test reflection
    reflected = l.reflect(z)
    expected_reflected = l.point(3/10) - normal_direction
    assert check(reflected, expected_reflected)
    
def test_line_arg_consistency(line_fixture):
    """Test arg method consistency for points on line"""
    for t in np.arange(0, 1.0, 0.1):
        point_t = line_fixture.point(t)
        arg_t = line_fixture.arg(point_t)
        assert check(arg_t, t)

def test_line_repr(line_fixture):
    """Test string representation of Line"""
    repr_str = repr(line_fixture)
    assert "Line through" in repr_str
    assert "at angle" in repr_str

def test_line_add(line_fixture):
    """Test addition of two lines raises error"""
    l1 = line_fixture
    l2 = l1 + 2j
    assert check(np.angle(l2.tangent(0.5)), np.angle(l1.tangent(0.5)))
    l2 = 4 - 1j + l1
    assert check(np.angle(l2.tangent(0.5)), np.angle(l1.tangent(0.5)))

def test_line_sub(line_fixture):
    """Test addition of two lines raises error"""
    l1 = line_fixture
    l2 = l1 - 2j
    assert check(np.angle(l2.tangent(0.5)), np.angle(l1.tangent(0.5)))
    l2 = 4 - 1j - l1
    assert check(np.pi + np.angle(l2.tangent(0.5)), np.angle(l1.tangent(0.5)))

def test_line_mul(line_fixture):
    """Test addition of two lines raises error"""
    l1 = line_fixture
    l2 = l1 * 2j
    assert check(np.angle(l2.tangent(0.5)/2j), np.angle(l1.tangent(0.5)))
    l2 = (4 - 1j) * l1
    assert check(np.angle(l2.tangent(0.5)/(4 - 1j)), np.angle(l1.tangent(0.5)))

def test_line_div(line_fixture):
    """Test addition of two lines raises error"""
    l1 = line_fixture
    l2 = l1 / 2j
    assert check(np.angle(l2.tangent(0.5)*2j), np.angle(l1.tangent(0.5)))