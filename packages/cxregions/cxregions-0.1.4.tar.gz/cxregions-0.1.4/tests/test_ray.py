import pytest
import numpy as np
from cxregions import Ray

@pytest.fixture

def ray_fixture():
    return Ray(2, angle=np.pi / 2)

def test_ray_isfinite(ray_fixture):
    assert not ray_fixture.isfinite()

def test_ray_isleft(ray_fixture):
    assert ray_fixture.isleft(-1j)
    assert not ray_fixture.isleft(4 + 1j)

def test_ray_point(ray_fixture):
    assert np.isclose(ray_fixture.point(23 / 100).real, 2)
    z1 = ray_fixture.point(0.9)
    z2 = ray_fixture.point(0.7)
    assert z1.imag > z2.imag

def test_ray_tangent(ray_fixture):
    assert np.isclose(np.angle(ray_fixture.tangent(1 / 10)), np.pi / 2)

def test_ray_reverse(ray_fixture):
    t = ray_fixture.reverse().tangent(0.3)
    assert np.isclose(np.angle(t), -np.pi / 2)

def test_ray_conj(ray_fixture):
    assert np.isclose(np.angle(ray_fixture.conj().tangent(0.3)), -np.pi / 2)
    
def test_ray_isright(ray_fixture):
    assert ray_fixture.isright(3 + 3j)

def test_ray_closest(ray_fixture):
    assert np.isclose(ray_fixture.closest(5j), 2 + 5j)

def test_ray_arg(ray_fixture):
    assert np.isclose(ray_fixture.arg(ray_fixture.point(0.5)), 0.5)

def test_ray_add(ray_fixture):
    l1 = ray_fixture
    l2 = l1 + 2j
    assert l2.dist(l1.point(0.5) + 2j) < 1e-7
    l2 = 4 - 1j + l1
    assert l2.dist(l1.point(0.5) + (4 - 1j)) < 1e-7

def test_ray_sub(ray_fixture):
    l1 = ray_fixture
    l2 = l1 - 2j
    assert l2.dist(l1.point(0.5) - 2j) < 1e-7
    l2 = 4 - 1j - l1
    assert l2.dist(-l1.point(0.5) + (4 - 1j)) < 1e-7

def test_ray_mul(ray_fixture):
    l1 = ray_fixture
    l2 = l1 * 2j
    assert l2.dist(l1.point(0.5) * 2j) < 1e-7
    l2 = (4 - 1j) * l1
    assert l2.dist(l1.point(0.5) * (4 - 1j)) < 1e-7

def test_ray_div(ray_fixture):
    l1 = ray_fixture
    l2 = l1 / 2j
    assert l2.dist(l1.point(0.5) / 2j) < 1e-7

def test_ray_repr(ray_fixture):
    repr_str = repr(ray_fixture)
    assert "Ray from" in repr_str
    assert "at angle" in repr_str