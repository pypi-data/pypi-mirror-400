import pytest
import numpy as np
from cxregions import Segment

@pytest.fixture

def segment_fixture():
    return Segment(1, 3 + 5j)

def test_segment_isfinite(segment_fixture):
    assert segment_fixture.isfinite()

def test_segment_isleft(segment_fixture):
    assert segment_fixture.isleft(-1)
    assert not segment_fixture.isleft(2)

def test_segment_point(segment_fixture):
    z = 2 + 5j / 2
    assert np.isclose(segment_fixture.point(0.5), z)
    assert np.isclose(segment_fixture.first, 1)
    assert np.isclose(segment_fixture.last, 3 + 5j)

def test_segment_dist(segment_fixture):
    assert np.isclose(segment_fixture.dist(-1), 2)

def test_segment_tangent(segment_fixture):
    theta = np.angle(segment_fixture.last - segment_fixture.first)
    assert np.isclose(np.angle(segment_fixture.tangent(2 / 3)), theta)

def test_segment_reverse(segment_fixture):
    theta = np.angle(segment_fixture.last - segment_fixture.first)
    t = segment_fixture.reverse().tangent(0.3)
    assert np.isclose(np.angle(t) + np.pi, theta)

def test_segment_isright(segment_fixture):
    assert segment_fixture.isright(3 + 3j)

def test_segment_closest(segment_fixture):
    s = segment_fixture
    z = s.point(7/10) + 1j * np.sign(s.point(9/10) - s.point(7/10))
    assert np.isclose(s.closest(z), s.point(7/10))

def test_segment_reflect(segment_fixture):
    s = segment_fixture
    p7 = s.point(7/10)
    z = p7 + 1j * np.sign(s.point(9/10) - p7)
    assert np.isclose(s.reflect(z), p7 - (z - p7))

def test_segment_arg(segment_fixture):
    assert np.isclose(segment_fixture.arg(segment_fixture.point(0.3)), 0.3)

def test_segment_add(segment_fixture):
    l1 = segment_fixture
    l2 = l1 + 2j
    assert l2.dist(l1.point(0.5) + 2j) < 1e-7
    l2 = 4 - 1j + l1
    assert l2.dist(l1.point(0.5) + (4 - 1j)) < 1e-7

def test_segment_sub(segment_fixture):
    l1 = segment_fixture
    l2 = l1 - 2j
    assert l2.dist(l1.point(0.5) - 2j) < 1e-7
    l2 = 4 - 1j - l1
    assert l2.dist(-l1.point(0.5) + (4 - 1j)) < 1e-7

def test_segment_mul(segment_fixture):
    l1 = segment_fixture
    l2 = l1 * 2j
    assert l2.dist(l1.point(0.5) * 2j) < 1e-7
    l2 = (4 - 1j) * l1
    assert l2.dist(l1.point(0.5) * (4 - 1j)) < 1e-7

def test_segment_div(segment_fixture):
    l1 = segment_fixture
    l2 = l1 / 2j
    assert l2.dist(l1.point(0.5) / 2j) < 1e-7

def test_segment_repr(segment_fixture):
    repr_str = repr(segment_fixture)
    assert "Segment from" in repr_str