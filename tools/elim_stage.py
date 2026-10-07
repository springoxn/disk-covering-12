"""Staged exact elimination for the r-projection of the symmetric KKT system.

Only the *branch* containing the certified numerical root is followed, which is
enough for the final minimal polynomial:  an irreducible P in Z[t] with
P(r_*) = 0 is the minimal polynomial.

Stages
------
S0  g1 = c^2+s^2-1,  g2 = u^2-2cu+1-r^2,  g3, g5 (v-quadratics), g6 = det, g7 = z^2-3
S1  w = u^2-r^2-r ;  g3-g5 is linear in v  =>  v = A0/A1
S2  g3 with v substituted -> polynomial, reduce mod g2 -> linear in u: a1 u + b1
S3  g6 with v,w substituted -> polynomial, reduce mod g2 -> linear in u: a2 u + b2
S4  eliminate u against g2:  gamma = b^2 + 2 c a b + a^2 (1-r^2)
S5  eliminate s using s^2 = 1-c^2  ->  two polynomials in (c,z,r)
S6  eliminate c by resultant       ->  polynomial in (z,r)
S7  eliminate z using z^2 = 3      ->  polynomial in r
Then factor over Q.

Usage:  python tools/elim_stage.py [--dry]
"""
from __future__ import annotations
import sys, time
import sympy as sp

sys.path.insert(0, r'E:\study\ADB\tools')
from kkt_system import SYM, geometry_system  # noqa: E402

r, u, v, w, c, s, z, P, Q, S, A, B, C, D = SYM
DRY = '--dry' in sys.argv


def deg(e, *vs):
    try:
        return sp.Poly(sp.expand(e), *vs).total_degree()
    except Exception:
        return None


def reduce_mod_g2(e):
    """Reduce a polynomial in u modulo g2 = u^2 - 2cu + 1 - r^2 -> linear in u."""
    e = sp.expand(e)
    p = sp.Poly(e, u)
    q = sp.Poly(u ** 2 - 2 * c * u + 1 - r ** 2, u)
    return sp.expand(sp.rem(p, q, u).as_expr())


def main():
    t0 = time.time()
    _, geomsys, mat, stresses = geometry_system()
    g1, g2, g3, g5 = geomsys[0], geomsys[1], geomsys[2], geomsys[4]
    det = sp.expand(mat.det())
    g7 = z ** 2 - 3
    print('det: total deg', deg(det, u, v, c, s, z, r), 'op count', sp.count_ops(det), flush=True)

    wsub = u ** 2 - r ** 2 - r
    Pc = c ** 2 - s ** 2 + 2 * z * c * s
    Q5 = 2 * r + wsub
    R5 = sp.expand(wsub * (wsub + r))
    A1 = sp.expand(Q5 - Pc)
    A0 = sp.expand(R5 - 1 + r ** 2)
    print('A0 deg', deg(A0, u, c, s, z, r), 'ops', sp.count_ops(A0), flush=True)
    print('A1 deg', deg(A1, u, c, s, z, r), 'ops', sp.count_ops(A1), flush=True)

    # S2
    E3p = sp.expand(A0 ** 2 - A0 * A1 * Pc + (1 - r ** 2) * A1 ** 2)
    print('[S2] E3p ops', sp.count_ops(E3p), 'u-deg', sp.degree(sp.Poly(E3p, u)), flush=True)
    R3 = reduce_mod_g2(E3p)
    a1 = sp.expand(sp.Poly(R3, u).coeff_monomial(u))
    b1 = sp.expand(R3 - a1 * u)
    print('[S2] a1 ops', sp.count_ops(a1), 'c-deg', deg(a1, c, s), 'r-deg', deg(a1, r),
          'z-deg', deg(a1, z), flush=True)
    print('[S2] b1 ops', sp.count_ops(b1), 'c-deg', deg(b1, c, s), 'r-deg', deg(b1, r),
          'z-deg', deg(b1, z), flush=True)
    if DRY:
        return

    # S3: det with v = A0/A1
    dv = sp.Poly(det.subs(w, wsub), v)
    k = dv.degree()
    print('[S3] det v-degree', k, flush=True)
    det_sub = sp.expand(sum(sp.expand(dv.coeff_monomial(v ** i)) * A0 ** i * A1 ** (k - i)
                            for i in range(k + 1)))
    print('[S3] det_sub ops', sp.count_ops(det_sub), 'u-deg', sp.degree(sp.Poly(det_sub, u)), flush=True)
    R6 = reduce_mod_g2(det_sub)
    a2 = sp.expand(sp.Poly(R6, u).coeff_monomial(u))
    b2 = sp.expand(R6 - a2 * u)
    print('[S3] a2 ops', sp.count_ops(a2), 'c-deg', deg(a2, c, s), 'r-deg', deg(a2, r), flush=True)
    print('[S3] b2 ops', sp.count_ops(b2), 'c-deg', deg(b2, c, s), 'r-deg', deg(b2, r), flush=True)
    print('[time]', round(time.time() - t0, 1), flush=True)

    # S4
    g1_ = b1 ** 2 + 2 * c * a1 * b1 + a1 ** 2 * (1 - r ** 2)
    g2_ = b2 ** 2 + 2 * c * a2 * b2 + a2 ** 2 * (1 - r ** 2)
    g1_ = sp.expand(g1_); g2_ = sp.expand(g2_)
    print('[S4] gam1 ops', sp.count_ops(g1_), 'c-deg', deg(g1_, c, s), flush=True)
    print('[S4] gam2 ops', sp.count_ops(g2_), 'c-deg', deg(g2_, c, s), flush=True)
    print('[time]', round(time.time() - t0, 1), flush=True)

    # S5: eliminate s using s^2 = 1-c^2
    def split_s(e):
        e = sp.expand(e.subs(s ** 2, 1 - c ** 2))
        p = sp.Poly(e, s)
        e = sp.expand(e - p.coeff_monomial(s ** 2) * s ** 2) if p.degree() == 2 else e
        e = sp.expand(e)
        p = sp.Poly(e, s)
        assert p.degree() <= 1, p.degree()
        e0 = sp.expand(p.coeff_monomial(1))
        e1 = sp.expand(p.coeff_monomial(s))
        return e0, e1
    a_1, b_1 = split_s(g1_)
    a_2, b_2 = split_s(g2_)
    R1 = sp.expand(a_1 * b_2 - b_1 * a_2)
    R2 = sp.expand(a_1 ** 2 - b_1 ** 2 * (1 - c ** 2))
    print('[S5] R1 ops', sp.count_ops(R1), 'c-deg', sp.degree(sp.Poly(R1, c)), flush=True)
    print('[S5] R2 ops', sp.count_ops(R2), 'c-deg', sp.degree(sp.Poly(R2, c)), flush=True)
    print('[time]', round(time.time() - t0, 1), flush=True)
    sp.save(sp.symbols('x'), None) if False else None
    import pickle
    with open(r'E:\study\ADB\runtime\elim_stage2.pkl', 'wb') as fh:
        pickle.dump({'R1': sp.srepr(R1), 'R2': sp.srepr(R2), 'a1': sp.srepr(a1), 'b1': sp.srepr(b1),
                     'a2': sp.srepr(a2), 'b2': sp.srepr(b2)}, fh)
    print('saved stage data')


if __name__ == '__main__':
    main()
