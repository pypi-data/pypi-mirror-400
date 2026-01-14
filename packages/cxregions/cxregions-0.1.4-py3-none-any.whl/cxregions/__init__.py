import juliacall
import numpy as np
jl = juliacall.newmodule("PyCR")
jl.seval('import Pkg')
installed = False
for v in jl.Pkg.dependencies().values():
    if v.name == "ComplexRegions":
        installed = True
        break
if not installed:
    jl.seval('Pkg.add("ComplexRegions")')
    
jl.seval("using ComplexRegions, PythonCall")

__all__ = ["jl", "Curve", "ClosedCurve", "Line", "Segment", "Circle", "Ray", "Arc", 
           "Path", "ClosedPath", "CircularPolygon", "Polygon", "Rectangle", "n_gon", "unitcircle",
           "Exterior1CRegion", "Interior1CRegion", "ExteriorRegion", "InteriorConnectedRegion",
           "between", "interior", "exterior", "disk", "quad", "Annulus",
           "halfplane", "upperhalfplane",  "lowerhalfplane", "lefthalfplane", "righthalfplane"]

JLCR = jl.ComplexRegions

def wrap_jl_curve(jul):
    if not isinstance(jul, juliacall.AnyValue):  # type: ignore
        raise ValueError("Argument to wrap_jl_curve is not a Julia object")
    if jl.isa(jul, JLCR.AbstractCurve):
        if jl.isa(jul, JLCR.Circle):
            return Circle(jul)
        elif jl.isa(jul, JLCR.Arc):
            return Arc(jul)
        elif jl.isa(jul, JLCR.Line):
            return Line(jul)
        elif jl.isa(jul, JLCR.Segment):
            return Segment(jul)
        elif jl.isa(jul, JLCR.Ray):
            return Ray(jul)
        elif jl.isa(jul, JLCR.AbstractClosedCurve):
            return ClosedCurve(jul)
        else:
            return Curve(jul)
    else:
        raise ValueError(f"Julia type {jl.typeof(jul)} not recognized for wrapping")

# classes named "Julia.*" wrap Julia objects and give native methods to access the object's methods, plus a get method to get fields
# classes derived from these take their properties from the embedded Julia object, presenting them in a native type

class JuliaCurve:
    def __init__(self, julia_obj):
        if isinstance(julia_obj, juliacall.AnyValue):  # type: ignore
            if jl.isa(julia_obj, JLCR.AbstractCurve):
                self.julia = julia_obj
        else:
            raise ValueError("Invalid argument to Curve constructor")

    def get(self, field):
        return jl.getproperty(self.julia, jl.Symbol(field))

    def point(self, t):
        p = JLCR.point(self.julia, t)
        return np.complex128(p)

    def arclength(self):
        return JLCR.arclength(self.julia)

    def tangent(self, t=0.):
        p = JLCR.tangent(self.julia, t)
        return np.complex128(p)

    def unittangent(self, t=0.):
        p = JLCR.unittangent(self.julia, t)
        return np.complex128(p)
    
    def normal(self, t):
        p = JLCR.normal(self.julia, t)
        return np.complex128(p)

    def arg(self, z):
        return JLCR.arg(self.julia, z)

    def conj(self):
        c = JLCR.conj(self.julia)
        return type(self)(c)

    def reverse(self):
        c = JLCR.reverse(self.julia)
        return type(self)(c)
    
    def isfinite(self):
        return JLCR.isfinite(self.julia)
    
    def ispositive(self):
        return JLCR.ispositive(self.julia)

    def isreal(self):
        return JLCR.isreal(self.julia)

    def isapprox(self, other):
        return JLCR.isapprox(self.julia, other.julia)

    def inv(self):
        # can't know the return type in general, so this must be wrapped by inheritors
        c = JLCR.inv(self.julia)
        return c

    def isleft(self, z):
        return JLCR.isleft(z, self.julia)

    def isright(self, z):
        return JLCR.isright(z, self.julia)
    
    def reflect(self, z):
        return JLCR.reflect(z, self.julia)

    def closest(self, z):
        return JLCR.closest(z, self.julia)

    def dist(self, z):
        return JLCR.dist(z, self.julia)
    
    def __add__(self, other):
        julia_add = getattr(jl, "+")
        t = julia_add(self.julia, other)
        return type(self)(t)

    def __radd__(self, other):
        julia_add = getattr(jl, "+")
        t = julia_add(other, self.julia)
        return type(self)(t)

    def __neg__(self):
        julia_neg = getattr(jl, "-")
        t = julia_neg(self.julia)
        return type(self)(t)

    def __sub__(self, other):
        julia_sub = getattr(jl, "-")
        t = julia_sub(self.julia, other)
        return type(self)(t)

    def __rsub__(self, other):
        julia_sub = getattr(jl, "-")
        t = julia_sub(other, self.julia)
        return type(self)(t)
    
    def __mul__(self, other):
        julia_mul = getattr(jl, "*")
        t = julia_mul(self.julia, other)
        return type(self)(t)

    def __rmul__(self, other):
        julia_mul = getattr(jl, "*")
        t = julia_mul(other, self.julia)
        return type(self)(t)

    def __truediv__(self, other):
        julia_div = getattr(jl, "/")
        t = julia_div(self.julia, other)
        return type(self)(t)

    def intersect(self, other):
        z = JLCR.intersect(self.julia, other.julia)
        if isinstance(z, juliacall.VectorValue):  # type: ignore
            if len(z) == 0:
                return np.array([])
            else:
                return np.array(z)
        elif jl.isa(z, JLCR.AbstractCurve):
            return wrap_jl_curve(z)
        else:
            return z

class Curve(JuliaCurve):
    def __init__(self, point, tangent=None, domain=(0.0, 1.0)):
        if isinstance(point, juliacall.AnyValue):  # type: ignore
            if jl.isa(point, JLCR.Curve):
                self.julia = point
            else:
                raise ValueError("Invalid argument to Curve constructor")
        else:
            self.julia = JLCR.Curve(point, tangent, domain[0], domain[1])

    def inv(self):
        c = JuliaCurve.inv(self)
        return type(self)(c)

    def __repr__(self):
        return str("Curve")

class ClosedCurve(Curve):
    def __init__(self, point, tangent=None, domain=(0.0, 1.0)):
        if isinstance(point, juliacall.AnyValue):  # type: ignore
            if jl.isa(point, JLCR.AbstractClosedCurve):
                self.julia = point
            else:
                raise ValueError("Invalid argument to ClosedCurve constructor")
        else:
            self.julia = JLCR.ClosedCurve(point, tangent, domain[0], domain[1])

    def winding(self, z):
        return JLCR.winding(self.julia, z)

    def __repr__(self):
        return str("Closed curve")

class Line(Curve):
    def __init__(self, a, b=None, direction=None):
        if isinstance(a, juliacall.AnyValue): # type: ignore
            if jl.isa(a, JLCR.Line):
                self.julia = a
            else:
                raise ValueError("Invalid argument to Line constructor")
        elif b is not None:
            self.julia = JLCR.Line(a, b)
        else:
            self.julia = JLCR.Line(a, direction=direction)
        self.base = JuliaCurve.get(self, "base")
        self.direction = JuliaCurve.get(self, "direction")

    def arclength(self):
        return np.inf

    def ispositive(self):
        return True

    def isfinite(self):
        return False

    def inv(self):
        c = JuliaCurve.inv(self)
        if jl.isa(c, JLCR.Circle):
            return Circle(c)
        else:
            return Line(c)

    def slope(self):
        return JLCR.slope(self.julia)

    def angle(self):
        return JLCR.angle(self.julia)
    
    def __repr__(self):
        return f"Line through {self.point(0.5)} at angle {self.angle() / np.pi} * pi"

class Circle(ClosedCurve):
    def __init__(self, a, b=None, c=None, ccw=True):
        if b is None:
            if isinstance(a, juliacall.AnyValue): # type: ignore
                if jl.isa(a, JLCR.Circle):
                    self.julia = a
            else:
                raise ValueError("Invalid argument to Circle constructor")
        elif c is None:
            self.julia = JLCR.Circle(a, b, ccw)
        else:
            self.julia = JLCR.Circle(a, b, c)
        
        self.radius = JuliaCurve.get(self, "radius")
        self.center = JuliaCurve.get(self, "center")
        self.ccw = JuliaCurve.get(self, "ccw")

    def ispositive(self):
        return self.ccw()

    def isfinite(self):
        return True

    def inv(self):
        c = JuliaCurve.inv(self)
        if jl.isa(c, JLCR.Circle):
            return Circle(c)
        else:
            return Line(c)

    def __repr__(self):
        return f"Circle centered at {self.center} with radius {self.radius}"
 
class Segment(Curve):
    def __init__(self, a, b=None):
        if isinstance(a, juliacall.AnyValue):  # type: ignore
            if jl.isa(a, JLCR.Segment):
                self.julia = a
            else:
                raise ValueError("Invalid argument to Segment constructor")
        else:
            self.julia = JLCR.Segment(a, b)
        
        self.first = JuliaCurve.get(self, "za")
        self.last = JuliaCurve.get(self, "zb")

    def inv(self):
        c = JuliaCurve.inv(self)
        if jl.isa(c, JLCR.Arc):
            return Arc(c)
        elif jl.isa(c, JLCR.Ray):
            return Ray(c)
        else:
            return Segment(c)

    def __repr__(self):
        return f"Segment from {self.first} to {self.last}"

class Ray(Curve):
    def __init__(self, base, angle=None):
        if isinstance(base, juliacall.AnyValue):  # type: ignore
            if jl.isa(base, JLCR.Ray):
                self.julia = base
            else:
                raise ValueError("Invalid argument to Ray constructor")
        else:
            self.julia = JLCR.Ray(base, angle)
        self.base = JuliaCurve.get(self, "base")
        self.angle = JuliaCurve.get(self, "angle")

    def __repr__(self):
        return f"Ray from {self.base} at angle {self.angle / np.pi} * pi"

class Arc(Curve):
    def __init__(self, a, b=None, c=None):
        if isinstance(a, juliacall.AnyValue):  # type: ignore
            if jl.isa(a, JLCR.Arc):
                self.julia = a
            elif jl.isa(a, JLCR.Circle):
                self.julia = JLCR.Arc(a, b, c)
            else:
                raise ValueError("Invalid argument to Arc constructor")
        else:
            self.julia = JLCR.Arc(a, b, c)
        
        circ = JuliaCurve.get(self, "circle")
        try:
            self.circle = Circle(circ)
        except Exception:
            self.circle = Segment(circ)
        self.start = JuliaCurve.get(self, "start")
        self.delta = JuliaCurve.get(self, "delta")

    def inv(self):
        c = JuliaCurve.inv(self)
        if jl.isa(c, JLCR.Arc):
            return Arc(c)
        elif jl.isa(c, JLCR.Ray):
            return Ray(c)
        else:
            return Segment(c)

    def __repr__(self):
        return f"Arc: fraction {self.delta} of {self.circle} from {self.start}"

def wrap_jl_path(jul):
    if not isinstance(jul, juliacall.AnyValue):  # type: ignore
        raise ValueError("Argument to wrap_jl_path is not a Julia object")
    if jl.isa(jul, JLCR.AbstractPath):
        if jl.isa(jul, JLCR.CircularPolygon):
            return CircularPolygon(jul)
        elif jl.isa(jul, JLCR.Polygon):
            return Polygon(jul)
        elif jl.isa(jul, JLCR.Rectangle):
            return Rectangle(jul)
        elif jl.isa(jul, JLCR.AbstractClosedPath):
            return ClosedPath(jul)
        else:
            return Path(jul)
    else:
        raise ValueError(f"Julia type {jl.typeof(jul)} not recognized for wrapping")


class JuliaPath:
    def __init__(self, julia_obj):
        if isinstance(julia_obj, juliacall.AnyValue):  # type: ignore
            if jl.isa(julia_obj, JLCR.AbstractPath):
                self.julia = julia_obj
        else:
            raise ValueError("Invalid argument to Path constructor")

    def get(self, field):
        return jl.getproperty(self.julia, jl.Symbol(field))

    def length(self):
        return JLCR.length(self.julia)
    
    def curves(self):
        curves = []
        for j in JLCR.curves(self.julia):
            if jl.isa(j, jl.Circle):
                curves.append(Circle(j))
            elif jl.isa(j, jl.Arc):
                curves.append(Arc(j))
            elif jl.isa(j, jl.Line):
                curves.append(Line(j))
            elif jl.isa(j, jl.Segment):
                curves.append(Segment(j))
            elif jl.isa(j, jl.Ray):
                curves.append(Ray(j))
            else:
                curves.append(JuliaCurve(j))
        return curves
    
    def curve(self, k):
        return self.curves()[k]

    def __getitem__(self, index):
        return self.curve(index)

    def point(self, t):
        p = JLCR.point(self.julia, t)
        return np.complex128(p)

    def arclength(self):
        return JLCR.arclength(self.julia)

    def tangent(self, t=0.):
        p = JLCR.tangent(self.julia, t)
        return np.complex128(p)

    def unittangent(self, t=0.):
        p = JLCR.unittangent(self.julia, t)
        return np.complex128(p)
    
    def normal(self, t=0.):
        p = JLCR.normal(self.julia, t)
        return np.complex128(p)

    def angles(self):
        return np.array(JLCR.angles(self.julia))

    def vertices(self):
        return np.array(JLCR.vertices(self.julia))
    
    def vertex(self, k):
        p = JLCR.vertex(self.julia, k)
        return np.complex128(p)

    def arg(self, z):
        return JLCR.arg(self.julia, z)

    def conj(self):
        p = JLCR.conj(self.julia)
        return type(self)(p)

    def reverse(self):
        p = JLCR.reverse(self.julia)
        return type(self)(p)
    
    def isfinite(self):
        return JLCR.isfinite(self.julia)
    
    def ispositive(self):
        return JLCR.ispositive(self.julia)

    def isreal(self):
        return JLCR.isreal(self.julia)

    def isapprox(self, other):
        return JLCR.isapprox(self.julia, other.julia)

    def inv(self):
        p = JLCR.inv(self.julia)
        return type(self)(p)

    def reflect(self, z):
        return JLCR.reflect(z, self.julia)

    def closest(self, z):
        return JLCR.closest(z, self.julia)

    def dist(self, z):
        return JLCR.dist(z, self.julia)
    
    def __add__(self, other):
        julia_add = getattr(jl, "+")
        t = julia_add(self.julia, other)
        return type(self)(t)

    def __radd__(self, other):
        julia_add = getattr(jl, "+")
        t = julia_add(other, self.julia)
        return type(self)(t)

    def __neg__(self):
        julia_neg = getattr(jl, "-")
        t = julia_neg(self.julia)
        return type(self)(t)

    def __sub__(self, other):
        julia_sub = getattr(jl, "-")
        t = julia_sub(self.julia, other)
        return type(self)(t)

    def __rsub__(self, other):
        julia_sub = getattr(jl, "-")
        t = julia_sub(other, self.julia)
        return type(self)(t)
    
    def __mul__(self, other):
        julia_mul = getattr(jl, "*")
        t = julia_mul(self.julia, other)
        return type(self)(t)

    def __rmul__(self, other):
        julia_mul = getattr(jl, "*")
        t = julia_mul(other, self.julia)
        return type(self)(t)

    def __truediv__(self, other):
        julia_div = getattr(jl, "/")
        t = julia_div(self.julia, other)
        return type(self)(t)

    def intersect(self, other):
        z = JLCR.intersect(self.julia, other.julia)
        return z

class Path(JuliaPath):
    def __init__(self, curves):
        if isinstance(curves, juliacall.AnyValue):  # type: ignore
            if jl.isa(curves, JLCR.AbstractPath):
                self.julia = curves
            else:
                raise ValueError("Invalid argument to Path constructor")
        else:
            self.julia = JLCR.Path([c.julia for c in np.atleast_1d(curves)])
        
        # self.curve = self.get("curve")
        
    def __repr__(self):
        N = len(self.curves())
        return f"Path with {N} curves"

class ClosedPath(Path):
    def __init__(self, curves):
        if isinstance(curves, juliacall.AnyValue):  # type: ignore
            if jl.isa(curves, JLCR.AbstractClosedPath):
                self.julia = curves
            else:
                raise ValueError("Invalid argument to ClosedPath constructor")
        elif isinstance(curves, Path):
            self.julia = JLCR.ClosedPath(curves.julia)
        else:
            self.julia = JLCR.ClosedPath([c.julia for c in np.atleast_1d(curves)])
        
        # self.curve = self.get("curve")

    def winding(self, z):
        return JLCR.winding(self.julia, z)
            
    def isinside(self, z):
        return JLCR.isinside(z, self.julia)

    def __repr__(self):
        N = len(self.curves())
        return f"Closed path with {N} curves"

def Jordan(c):
    """Construct a Jordan curve from a ClosedPath object."""
    if isinstance(c, ClosedPath) or isinstance(c, ClosedCurve):
        return c
    elif isinstance(c, juliacall.AnyValue):  # type: ignore
        if jl.isa(c, JLCR.AbstractClosedPath):
            return wrap_jl_path(c)
        elif jl.isa(c, JLCR.AbstractClosedCurve):
            return wrap_jl_curve(c)
        else:
            raise ValueError("Julia argument to Jordan not recognized")
    else:
        raise ValueError("Argument to Jordan not recognized")

def get_julia(p):
    if isinstance(p, JuliaCurve) or isinstance(p, JuliaPath):
        return p.julia
    else:
        return p

class CircularPolygon(ClosedPath):
    def __init__(self, arg):
        if isinstance(arg, juliacall.AnyValue):  # type: ignore
            if jl.isa(arg, JLCR.CircularPolygon):
                self.julia = arg
        else:
            vec = juliacall.convert(jl.Vector,[get_julia(a) for a in arg])
            self.julia = JLCR.CircularPolygon(vec)
        
        self.path = ClosedPath(JuliaPath.get(self, "path"))
    
    def sides(self):
        return self.curves()
    
    def side(self, k):
        return self.curve(k)

    def __repr__(self):
        N = len(self.sides())
        return f"Circular polygon with {N} sides"

class Polygon(ClosedPath):
    def __init__(self, arg):
        if isinstance(arg, juliacall.AnyValue):  # type: ignore
            if jl.isa(arg, JLCR.Polygon):
                self.julia = arg
        else:
            vec = juliacall.convert(jl.Vector,[get_julia(a) for a in arg])
            self.julia = JLCR.Polygon(vec)

        self.path = ClosedPath(JuliaPath.get(self, "path"))
    
    def sides(self):
        return self.curves()
    
    def side(self, k):
        return self.curve(k)
    
    def __repr__(self):
        N = len(self.sides())
        return f"Polygon with {N} sides"
    
class Rectangle(Polygon):
    def __init__(self, a, b=None):
        if isinstance(a, juliacall.AnyValue):  # type: ignore
            if jl.isa(a, JLCR.Rectangle):
                self.julia = a
            else:
                raise ValueError("Invalid argument to Rectangle constructor")
        else:
            if b is None:
                # hopefully, a vector of vertices was given
                self.julia = JLCR.rectangle(a)
            else:
                if np.ndim(a) == 0 and np.ndim(b) > 0:
                    # center and radii were given; use constructor
                    self.julia = JLCR.Rectangle(a, b)
                else:
                    # opposite corners were given; use rectangle function
                    self.julia = JLCR.rectangle(a, b)
        
        self.center = JuliaPath.get(self, "center")
        self.radii = JuliaPath.get(self, "radii")
        self.rotation = JuliaPath.get(self, "rotation")
        self.polygon = Polygon(JuliaPath.get(self, "polygon"))

##
unitcircle = Circle(0, 1)
def n_gon(n):
    """Construct a regular n-gon as a Polygon object."""
    return Polygon(JLCR.n_gon(n))

def wrap_jl_region(jul):
    if not isinstance(jul, juliacall.AnyValue):  # type: ignore
        raise ValueError("Argument to wrap_jl_region is not a Julia object")
    if jl.isa(jul, JLCR.AbstractRegion):
        if jl.isa(jul, JLCR.Annulus):
            return Annulus(jul)
        elif jl.isa(jul, JLCR.ExteriorSimplyConnectedRegion):
            return Exterior1CRegion(jul)
        elif jl.isa(jul, JLCR.InteriorSimplyConnectedRegion):
            return Interior1CRegion(jul)
        elif jl.isa(jul, JLCR.ExteriorRegion):
            return ExteriorRegion(jul)
        elif jl.isa(jul, JLCR.InteriorConnectedRegion):
            return InteriorConnectedRegion(jul)
        else:
            raise ValueError(f"Julia type {jl.typeof(jul)} not recognized for wrapping")
    else:
        raise ValueError(f"Julia type {jl.typeof(jul)} not recognized for wrapping")

class JuliaRegion:
    def __init__(self, julia_obj):
        if isinstance(julia_obj, juliacall.AnyValue):  # type: ignore
            if jl.isa(julia_obj, JLCR.AbstractRegion):
                self.julia = julia_obj
        else:
            raise ValueError("Invalid argument to Region constructor")
        
    def get(self, field):
        return jl.getproperty(self.julia, jl.Symbol(field))

    def contains(self, z=None):
        if z is not None:
            return getattr(JLCR, "in")(z, self.julia)
        else:
            getattr(JLCR, "in")(self.julia)

    def innerboundary(self):
        b = JLCR.innerboundary(self.julia)
        if isinstance(b, juliacall.VectorValue):  # type: ignore
            return [JuliaPath(j) for j in b]
        else:
            return JuliaPath(b)

    def outerboundary(self):
        b = JLCR.outerboundary(self.julia)
        if isinstance(b, juliacall.VectorValue):  # type: ignore
            paths = []
            for j in b:
                paths.append(JuliaPath(j))
            return paths
        else:
            return JuliaPath(b)

    def union(self, other):
        r = JLCR.union(self.julia, other.julia)
        return JuliaRegion(r)
    
    def intersect(self, other):
        r = JLCR.intersect(self.julia, other.julia)
        return JuliaRegion(r)
    
class Exterior1CRegion(JuliaRegion):
    def __init__(self, boundary):
        if isinstance(boundary, juliacall.AnyValue):  # type: ignore
            if jl.isa(boundary, JLCR.ExteriorSimplyConnectedRegion) :
                self.julia = boundary
            else:
                raise ValueError("Invalid argument to Exterior1CRegion constructor")
        else:
            self.julia = JLCR.ExteriorSimplyConnectedRegion(boundary.julia)

        self.boundary = Jordan(JuliaRegion.get(self, "boundary"))

    def isfinite(self):
        return self.boundary.isfinite()
    
    def __repr__(self):
        return str(f"Exterior simply connected region")

class ExteriorRegion(JuliaRegion):
    def __init__(self, inner):
        if isinstance(inner, juliacall.AnyValue):  # type: ignore
            if jl.isa(inner, JLCR.ExteriorRegion):
                self.julia = inner
            else:
                raise ValueError("Invalid argument to ExteriorRegion constructor")
        else:
            innerb = juliacall.convert(jl.Vector, [get_julia(b) for b in inner])
            self.julia = JLCR.ExteriorRegion(innerb)

        b = JuliaRegion.get(self, "inner")
        self.inner = [Jordan(j) for j in b]

    def isfinite(self):
        return False
    
    def __repr__(self):
        return f"Exterior region with {len(self.inner)} inner boundaries"
    
class Interior1CRegion(JuliaRegion):
    def __init__(self, boundary):
        if isinstance(boundary, juliacall.AnyValue):  # type: ignore
            if jl.isa(boundary, JLCR.InteriorSimplyConnectedRegion) :
                self.julia = boundary
            else:
                raise ValueError("Invalid argument to InteriorConnectedRegion constructor")
        else:
            self.julia = JLCR.InteriorSimplyConnectedRegion(boundary.julia)

        self.boundary = Jordan(JuliaRegion.get(self, "boundary"))

    def isfinite(self):
        return self.boundary.isfinite()
    
    def __repr__(self):
        return str(f"Interior simply connected region")

class InteriorConnectedRegion(JuliaRegion):
    def __init__(self, outer, inner=[]):
        if isinstance(outer, juliacall.AnyValue):  # type: ignore
            if jl.isa(outer, JLCR.InteriorConnectedRegion) :
                self.julia = outer
            else:
                raise ValueError("Invalid argument to InteriorConnectedRegion constructor")
        else:
            innerb = juliacall.convert(jl.Vector, [get_julia(b) for b in inner])
            self.julia = JLCR.InteriorRegion(outer.julia, innerb)

        b = JuliaRegion.get(self, "inner")
        self.inner = [Jordan(j) for j in b]
        self.outer = JuliaRegion.get(self, "outer")

    def isfinite(self):
        return self.outer.isfinite() & all([b.isfinite() for b in self.inner])
    
    def __repr__(self):
        N = len(self.inner)
        return f"Interior {N+1}-connnected region"
        
def between(curve1, curve2):
    """Construct the region between two closed curves."""
    r = JLCR.between(curve1.julia, curve2.julia)
    return InteriorConnectedRegion(r)

def interior(curve):
    """Construct the interior region of a closed curve."""
    r = JLCR.interior(curve.julia)
    return Interior1CRegion(r)

def exterior(curve):
    """Construct the exterior region of a closed curve."""
    r = JLCR.exterior(curve.julia)
    return Exterior1CRegion(r)

def disk(center, radius):
    """Construct a disk as an InteriorRegion."""
    r = JLCR.disk(center, radius)
    return Interior1CRegion(r)

def quad(rect:Rectangle):
    """Construct a quadrilateral region from a Rectangle."""
    r = JLCR.quad(rect.julia)
    return Interior1CRegion(r)

def halfplane(l:Line):
    """Construct a half-plane as an InteriorRegion from a Line."""
    r = JLCR.halfplane(l.julia)
    return Interior1CRegion(r)

upperhalfplane = halfplane(Line(0.0, direction=1.0))
lowerhalfplane = halfplane(Line(0.0, direction=-1.0))
lefthalfplane = halfplane(Line(0.0, direction=1.0j))
righthalfplane = halfplane(Line(0.0, direction=-1.0j))

class Annulus(InteriorConnectedRegion):
    def __init__(self, outer, inner=None, center=0j):
        if isinstance(outer, juliacall.AnyValue):  # type: ignore
            if jl.isa(outer, JLCR.Annulus):
                self.julia = outer
            elif jl.isa(outer, JLCR.Circle) and jl.isa(inner, JLCR.Circle):
                self.julia = JLCR.Annulus(outer, inner)
            else:
                raise ValueError("Invalid argument to Annulus constructor")
        elif isinstance(inner, Circle) and isinstance(outer, Circle):
            self.julia = JLCR.Annulus(outer.julia, inner.julia)
        else:
            self.julia = JLCR.Annulus(outer, inner, center)

        self.inner = Circle(JuliaRegion.get(self, "inner"))
        self.outer = Circle(JuliaRegion.get(self, "outer"))

    def modulus(self):
        return JLCR.modulus(self.julia)
    
    def isfinite(self):
        return True

    def __repr__(self):
        return f"Annulus centered at {self.inner.center} with radii {self.inner.radius} and {self.outer.radius}"