"""Exact rational interval arithmetic (outward rounding) — no floats anywhere.

Supports +, -, *, /, integer powers, and recursive evaluation of sympy
polynomial expressions.  Designed for certified enclosures of polynomial
systems in Q[x1..xn].
"""
from __future__ import annotations
from fractions import Fraction

import sympy as sp


class Iv:
    __slots__ = ('lo', 'hi')

    def __init__(self, lo, hi=None):
        lo = Fraction(lo)
        hi = lo if hi is None else Fraction(hi)
        if lo > hi:
            raise ValueError('empty interval')
        self.lo, self.hi = lo, hi

    # ---- constructors
    @staticmethod
    def point(v):
        return Iv(v, v)

    @staticmethod
    def box(center, radius):
        c, rad = Fraction(center), Fraction(radius)
        return Iv(c - rad, c + rad)

    # ---- arithmetic
    def __add__(self, o):
        o = o if isinstance(o, Iv) else Iv.point(o)
        return Iv(self.lo + o.lo, self.hi + o.hi)

    __radd__ = __add__

    def __sub__(self, o):
        o = o if isinstance(o, Iv) else Iv.point(o)
        return Iv(self.lo - o.hi, self.hi - o.lo)

    def __rsub__(self, o):
        return Iv.point(o) - self

    def __neg__(self):
        return Iv(-self.hi, -self.lo)

    def __mul__(self, o):
        o = o if isinstance(o, Iv) else Iv.point(o)
        p = (self.lo * o.lo, self.lo * o.hi, self.hi * o.lo, self.hi * o.hi)
        return Iv(min(p), max(p))

    __rmul__ = __mul__

    def __truediv__(self, o):
        o = o if isinstance(o, Iv) else Iv.point(o)
        if o.lo <= 0 <= o.hi:
            raise ZeroDivisionError('interval division by interval containing 0')
        p = (self.lo / o.lo, self.lo / o.hi, self.hi / o.lo, self.hi / o.hi)
        return Iv(min(p), max(p))

    def __rtruediv__(self, o):
        return Iv.point(o) / self

    def __pow__(self, n):
        if not isinstance(n, int) or n < 0:
            raise ValueError('only non-negative integer powers')
        if n == 0:
            return Iv(1, 1)
        r = Iv(1, 1)
        for _ in range(n):
            r = r * self
        return r

    # ---- predicates
    def __contains__(self, x):
        x = Fraction(x)
        return self.lo <= x <= self.hi

    def inside_strict(self, other):
        return other.lo < self.lo and self.hi < other.hi

    def width(self):
        return self.hi - self.lo

    def __repr__(self):
        return f'Iv({self.lo}, {self.hi})'

    def __str__(self):
        return f'[{float(self.lo):.18g}, {float(self.hi):.18g}]'


def iv_eval(expr, sub):
    """Recursively evaluate a sympy expression built from +,-,*,**,integer over Iv."""
    e = sp.sympify(expr)
    if e.is_Number:
        return Iv(Fraction(int(sp.numer(e)), int(sp.denom(e))))
    if e.is_Symbol:
        try:
            return sub[e]
        except KeyError:
            raise KeyError(f'no interval bound for {e}')
    if e.is_Add:
        r = Iv(0, 0)
        for a in e.args:
            r = r + iv_eval(a, sub)
        return r
    if e.is_Mul:
        r = Iv(1, 1)
        for a in e.args:
            r = r * iv_eval(a, sub)
        return r
    if e.is_Pow:
        b, ex = e.args
        if ex.is_Integer and int(ex) >= 0:
            return iv_eval(b, sub) ** int(ex)
        raise ValueError(f'unsupported power {e}')
    raise ValueError(f'unsupported node {e} ({sp.srepr(e)[:80]})')


def iv_dot(A, B):
    """Interval matrix product A (list of rows of Iv) times B."""
    n = len(A); m = len(B[0]); k = len(B)
    out = []
    for i in range(n):
        row = []
        for j in range(m):
            s = Iv(0, 0)
            for l in range(k):
                s = s + A[i][l] * B[l][j]
            row.append(s)
        out.append(row)
    return out
