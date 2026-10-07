"""Exact definition of the 14-variable symmetric KKT system for the n=12 disk cover.

Reference: lit/DiskCoveringSolve/cover12/docs/cover12_proof_zh.md, system (1).

Variables (ordered):
    (r, u, v, w, c, s, z, P, Q, S, A, B, C, D)

Geometric meaning:
    z = sqrt(3)
    c = cos(h), s = sin(h)   for the odd boundary orbit angle h
    u: radius of the 6-point orbit {R^k(+-u c, +-u s)}
    v: radius of the 3-point orbit {R^k(-v, 0)}
    w: radius of the 3-point orbit {R^k( w, 0)} (inner disks)

This module contains no floating point: sympy expressions only.
"""
from __future__ import annotations

import sympy as sp

NAMES = ['r', 'u', 'v', 'w', 'c', 's', 'z', 'P', 'Q', 'S', 'A', 'B', 'C', 'D']
SYM = sp.symbols('r u v w c s z P Q S A B C D')


def system():
    """Return (vars, [f1..f14]) as sympy expressions, exactly as in proof (1)."""
    r, u, v, w, c, s, z, P, Q, S, A, B, C, D = SYM
    L = (c ** 2 - s ** 2) / 2 + z * c * s
    M = z * (c ** 2 - s ** 2) / 2 - c * s
    f = [
        c ** 2 + s ** 2 - 1,
        u ** 2 - 2 * u * c + 1 - r ** 2,
        v ** 2 - v * (c ** 2 - s ** 2 + 2 * z * c * s) + 1 - r ** 2,
        w - u ** 2 + r ** 2 + r,
        v ** 2 - (2 * r + w) * v + w * (w + r),
        z ** 2 - 3,
        2 * A * (u * c - (w + r)) - B * r,
        C * r - 2 * D * (v - r - w / 2),
        2 * P * (L - v) - C * r,
        Q - S - A * (w + r),
        (S + Q) * (c - u) + A * ((w + r) * c - u),
        B * r - D * (2 * w - v + r),
        Q * u * s - P * v * M,
        6 * (P + Q + S + A + D) + 3 * (B + C) - 1,
    ]
    return SYM, f


def geometry_system():
    """Reduce to the 6 equations in (r,u,v,w,c,s) plus the stress-kernel condition.

    Equations (7)-(13) are 7 homogeneous linear equations in the 7 unknown
    stresses (P,Q,S,A,B,C,D); a nonzero solution exists iff the 7x7 matrix has
    zero determinant.  Equation (14) then fixes the (positive) scale.

    Returns (geovars, geomsys, mat, stresses).
    """
    r, u, v, w, c, s, z, P, Q, S, A, B, C, D = SYM
    L = (c ** 2 - s ** 2) / 2 + z * c * s
    M = z * (c ** 2 - s ** 2) / 2 - c * s
    stresses = [P, Q, S, A, B, C, D]
    eqs = [
        2 * A * (u * c - (w + r)) - B * r,
        C * r - 2 * D * (v - r - w / 2),
        2 * P * (L - v) - C * r,
        Q - S - A * (w + r),
        (S + Q) * (c - u) + A * ((w + r) * c - u),
        B * r - D * (2 * w - v + r),
        Q * u * s - P * v * M,
    ]
    mat = sp.Matrix([[sp.expand(sp.expand(e).coeff(t)) for t in stresses] for e in eqs])
    geovars = (r, u, v, w, c, s)
    geomsys = [
        c ** 2 + s ** 2 - 1,
        u ** 2 - 2 * u * c + 1 - r ** 2,
        v ** 2 - v * (c ** 2 - s ** 2 + 2 * z * c * s) + 1 - r ** 2,
        w - u ** 2 + r ** 2 + r,
        v ** 2 - (2 * r + w) * v + w * (w + r),
        sp.expand(mat.det()),
    ]
    return geovars, geomsys, mat, stresses


def centers(sol):
    """12 centers from a solution dict (u,v,w,c,s).  Returns list of (x, y).

    Orbits:  R^k(u c, u s), R^k(u c, -u s), R^k(-v, 0), R^k(w, 0), k=0,1,2
    with R the rotation by 2*pi/3 (order: as listed in the proof).
    """
    u, v, w, c, s = sol['u'], sol['v'], sol['w'], sol['c'], sol['s']
    base = [(u * c, u * s), (u * c, -u * s), (-v, 0), (w, 0)]
    out = []
    for (x0, y0) in base:
        for k in range(3):
            th = 2 * sp.pi * k / 3
            out.append((x0 * sp.cos(th) - y0 * sp.sin(th), x0 * sp.sin(th) + y0 * sp.cos(th)))
    return out


if __name__ == '__main__':
    SY, f = system()
    print('vars:', SY)
    for i, e in enumerate(f, 1):
        print(f'  f{i} = {sp.simplify(e)}')
    gv, gs, mat, st = geometry_system()
    print('\ngeometric reduction: vars', gv, ' eqs', len(gs))
    print('stress matrix shape', mat.shape, ' det degree',
          sp.Poly(mat.det(), *gv).total_degree() if mat.det() != 0 else None)
