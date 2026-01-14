import pytest
import numpy as np
from cxregions import (
    Circle, Line, Rectangle, Segment, unitcircle,
    Exterior1CRegion, Interior1CRegion, ExteriorRegion, InteriorConnectedRegion, Annulus,
    between, interior, exterior, disk, quad, halfplane, upperhalfplane, lowerhalfplane,
    lefthalfplane, righthalfplane
)


@pytest.fixture
def unit_circle():
    """Unit circle centered at origin."""
    return Circle(0, 1)


@pytest.fixture
def small_circle():
    """Small circle for testing annulus."""
    return Circle(0, 0.5)


@pytest.fixture
def large_circle():
    """Large circle for testing annulus."""
    return Circle(0, 2)


@pytest.fixture
def horizontal_line():
    """Horizontal line through origin."""
    return Line(0, direction=1)


class TestExteriorRegion:
    def test_exterior_region_from_boundaries(self, unit_circle, small_circle):
        """Test creating exterior region from multiple boundaries."""
        region = ExteriorRegion([unit_circle, small_circle])
        assert isinstance(region, ExteriorRegion)
        
        # Test that it's infinite
        assert not region.isfinite()

    def test_exterior_region_1c(self, unit_circle):
        """Test string representation."""
        region = Exterior1CRegion(unit_circle)
        assert isinstance(region, Exterior1CRegion)
        repr_str = repr(region)
        assert "Exterior simply connected region" in repr_str

    def test_exterior_region_repr(self, unit_circle):
        """Test string representation."""
        region = ExteriorRegion([unit_circle])
        repr_str = repr(region)
        assert "Exterior region with" in repr_str
        assert "inner boundaries" in repr_str

    def test_exterior_region_containment(self, unit_circle):
        """Test containment for exterior region."""
        region = ExteriorRegion([unit_circle])
        
        # Point outside should be contained
        assert region.contains(2)
        
        # Point inside should not be contained
        assert not region.contains(0)


class TestAnnulus:
    def test_annulus_from_circles(self, small_circle, large_circle):
        """Test creating annulus from two circles."""
        annulus = Annulus(large_circle, small_circle)
        assert isinstance(annulus, Annulus)
        assert annulus.isfinite()
        
    def test_annulus_from_radii(self):
        """Test creating annulus from radii."""
        annulus = Annulus(2, 1, center=0)  # outer=2, inner=1
        assert isinstance(annulus, Annulus)
        assert annulus.isfinite()
        
    def test_annulus_containment(self, small_circle, large_circle):
        """Test point containment in annulus."""
        annulus = Annulus(large_circle, small_circle)
        
        # Point in annulus (between circles)
        assert annulus.contains(1)
        
        # Point inside inner circle
        assert not annulus.contains(0.25)
        
        # Point outside outer circle
        assert not annulus.contains(3)
        
    def test_annulus_modulus(self):
        # Create annulus with known radii
        inner = Circle(0, 1)
        outer = Circle(0, 2)
        annulus = Annulus(outer, inner)
        mod = annulus.modulus()
        assert np.isclose(mod, 0.5)
        
    def test_annulus_repr(self, small_circle, large_circle):
        annulus = Annulus(large_circle, small_circle)
        repr_str = repr(annulus)
        assert "Annulus centered at" in repr_str
        assert "with radii" in repr_str


class TestRegionBoundaries:
    def test_annulus_boundaries(self, small_circle, large_circle):
        """Test boundary methods for annulus."""
        annulus = Annulus(large_circle, small_circle)
        
        # Test boundaries
        outer = annulus.outerboundary()
        inner = annulus.innerboundary()
        assert outer is not None
        assert inner is not None


class TestEdgeCases:
    def test_valid_annulus_construction(self):
        """Test valid annulus construction."""
        # Outer radius larger than inner radius (correct order)
        annulus = Annulus(2, 1, center=0)  # outer=2, inner=1
        assert isinstance(annulus, Annulus)
        assert annulus.isfinite()
        
    def test_rectangle_construction(self):
        """Test rectangle construction with proper parameters."""
        # Rectangle needs complex center and numpy array for radii
        rect = Rectangle(0.0+0.0j, np.array([1.0, 0.5]))  # center=0+0j, radii=[1, 0.5]
        assert isinstance(rect, Rectangle)


class TestNumericalAccuracy:
    def test_annulus_boundary_points(self):
        """Test annulus containment near boundaries."""
        annulus = Annulus(2, 1, center=0)  # outer=2, inner=1
        
        # Points near boundaries
        assert not annulus.contains(0.99)  # just inside inner circle
        assert annulus.contains(1.01)     # just outside inner circle
        assert annulus.contains(1.99)     # just inside outer circle
        assert not annulus.contains(2.01) # just outside outer circle


class TestSpecialCases:
    def test_simple_annulus(self):
        """Test simple annulus creation."""
        inner = Circle(0, 1)
        outer = Circle(0, 2)
        annulus = Annulus(outer, inner)
        
        assert annulus.contains(1.5)  # between circles
        assert not annulus.contains(0.5)  # inside inner
        assert not annulus.contains(2.5)  # outside outer

    def test_exterior_region_multiple_boundaries(self):
        """Test exterior region with multiple inner boundaries."""
        circle1 = Circle(0, 1)
        circle2 = Circle(3, 0.5)
        region = ExteriorRegion([circle1, circle2])
        
        assert isinstance(region, ExteriorRegion)
        assert not region.isfinite()
        
        # Test containment
        assert region.contains(10)  # far outside
        assert not region.contains(0)  # inside first circle
        assert not region.contains(3)  # inside second circle

class TestRegionBuilders:
    def test_disk_builder(self):
        d = disk(1j, 2)
        assert isinstance(d, Interior1CRegion)
        assert d.contains(0.5)
        assert not d.contains(-1.5j)
        
    def test_quad_builder(self):
        r = Rectangle(-1-2j, 3.)
        q = quad(r)
        assert isinstance(q, Interior1CRegion)
        assert q.contains(0.5 - 0.5j)
        assert not q.contains(1.5 + 0.5j)

    def test_between_builder(self, small_circle, large_circle):
        b = between(large_circle, small_circle)
        assert isinstance(b, InteriorConnectedRegion)
        assert b.contains(1)
        assert not b.contains(0.25)
        assert not b.contains(3)

    def test_interior_builder(self, unit_circle):
        i = interior(unit_circle)
        assert isinstance(i, Interior1CRegion)
        assert i.contains(0)
        assert not i.contains(2)

    def test_exterior_builder(self, unit_circle):
        e = exterior(unit_circle)
        assert isinstance(e, Exterior1CRegion)
        assert e.contains(2)
        assert not e.contains(0)

class TestRegionOperations:
    def test_exterior_region_union(self):
        """Test union of exterior regions."""
        region1 = ExteriorRegion([Circle(0, 1)])
        region2 = ExteriorRegion([Circle(2, 0.5)])
        
        union_region = region1.union(region2)
        # Should return a JuliaRegion base type
        assert hasattr(union_region, 'julia')
        
    def test_exterior_region_intersection(self):
        """Test intersection of exterior regions."""
        region1 = ExteriorRegion([Circle(0, 1)])
        region2 = ExteriorRegion([Circle(0, 2)])
        
        intersection_region = region1.intersect(region2)
        # Should return a JuliaRegion base type
        assert hasattr(intersection_region, 'julia')

class TestHalfplanes:
    def test_halfplane_construction(self, horizontal_line):
        """Test halfplane construction from line."""
        hp = halfplane(horizontal_line)
        assert isinstance(hp, Interior1CRegion)
        assert not hp.isfinite()
        
    def test_halfplane_containment(self, horizontal_line):
        """Test point containment in halfplane."""
        hp = halfplane(horizontal_line)
        # Point above line should be contained
        assert hp.contains(1 + 1j)
        # Point below line should not be contained
        assert not hp.contains(1 - 1j)

    def test_builtin_halfplanes(self):
        """Test built-in halfplane regions."""
        assert lowerhalfplane.contains(-1j)
        assert not lowerhalfplane.contains(1j)
        assert lefthalfplane.contains(-1)
        assert not lefthalfplane.contains(1)
        assert righthalfplane.contains(1)
        assert not righthalfplane.contains(-1)
        assert upperhalfplane.contains(1j)
        assert not upperhalfplane.contains(-1j)

if __name__ == "__main__":
    pytest.main([__file__])