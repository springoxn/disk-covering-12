"""Symbolic elimination: minimal polynomial candidate for r_*.

Strategy (avoids a 7-variable lex Groebner basis):
  1. f4 gives w = u^2 - r^2 - r;  f2 gives u^2 = 2uc - 1 + r^2.
     Reducing modulo these two relations makes w an explicit rational function
     and every polynomial at most linear in u.
  2. f3, f5 are quadratics in v with the same leading coefficient; f3-f5 is
     linear in v  =>  v = P/Q.  Substituting into (f3+f5) yields E1(c,s,z,r)=0.
  3. det(stress matrix) is linear in u => u = P2/Q2; substituting into
     (f3+f5) gives E2(c,s,z,r)=0.
  4. Eliminate s with s^2 = 1 - c^2, then eliminate c by resultant, then
     z with z^2 = 3, then take the Q-norm.
Final step: factor the resulting univariate polynomial in r over Q.
"""
from __future__ import annotations
import sys, time, json, os
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kkt_system import SYM, system, geometry_system  # noqa: E402

r, u, v, w, c, s, z, P, Q, S, A, B, C, D = SYM


def num(e):
    return sp.together(sp.expand(sp.numer(sp.together(e)))), sp.together(sp.denom(sp.together(e)))


def reduce_u(e):
    """Reduce a polynomial in u using u^2 = 2*u*c - 1 + r^2 (from f2)."""
    return sp.rem(sp.expand(sp.sympify(e)), sp.Poly(u ** 2 - 2 * u * c + 1 - r ** 2, u), u)


def main():
    t0 = time.time()
    _, f = system()
    _, geomsys, mat, stresses = geometry_system()
    det = sp.expand(mat.det())

    # w and u^2 substitutions
    wsub = u ** 2 - r ** 2 - r
    u2sub = 2 * u * c - 1 + r ** 2

    def red(e):
        e = sp.expand(e.subs(w, wsub))
        e = sp.expand(e)
        p = sp.Poly(e, u)
        q = sp.Poly(u ** 2 - u2sub, u)
        e = sp.rem(p, q, u).as_expr()
        # also cancel u^2 in coefficients repeatedly
        return sp.expand(sp.rem(sp.Poly(sp.expand(e), u), sp.Poly(sp.expand(u ** 2 - u2sub), u), u).as_expr())

    E3 = red(f[2])   # f3
    E5 = red(f[4])   # f5
    Edet = red(det)
    print('degrees: E3', sp.Poly(E3, u, v).total_degree(), 'E5', sp.Poly(E5, u, v).total_degree(),
          'Edet', sp.Poly(Edet, u).total_degree(), 'time', round(time.time() - t0, 2), flush=True)

    # Edet is linear in u  ->  solve for u
    u_sol = sp.solve(sp.Eq(Edet, 0), u)
    print('u solutions:', len(u_sol), [sp.count_ops(x) for x in u_sol], flush=True)
    uu = u_sol[0]
    A1 = sp.together(sp.expand(E3.subs(u, uu)))
    A2 = sp.together(sp.expand(E5.subs(u, uu)))
    # both are quadratics in v with same leading coefficient
    p1n, p1d = num(A1)
    p2n, p2d = num(A2)
    G1 = sp.Poly(sp.expand(p1n * p2d), v)
    G2 = sp.Poly(sp.expand(p2n * p1d), v)
    diff = sp.expand(G1.as_expr() - G2.as_expr())
    v_sol = sp.solve(sp.Eq(diff, 0), v)
    print('v solutions:', len(v_sol), [sp.count_ops(x) for x in v_sol], flush=True)
    vv = v_sol[0]
    E1 = sp.together(sp.expand(G1.as_expr().subs(v, vv)))
    n1, d1 = num(E1)
    print('E1 ops', sp.count_ops(n1), 'time', round(time.time() - t0, 2), flush=True)
    # E1 = 0  <=>  n1 = 0 , together with c^2+s^2=1 and z^2=3
    E1 = sp.expand(n1)

    # sanity: substitute known numeric root later.
    with open(r'E:\study\ADB\runtime\elim_stage.json', 'w') as fh:
        json.dump({'ops_E1': sp.count_ops(E1), 'deg_E1': sp.Poly(E1, c, s, z, r).total_degree()}, fh)

    # Eliminate s: s^2 = 1 - c^2.  E1 is even in s?  not necessarily; write E1 = A + B*s
    Pe = sp.Poly(E1, s)
    Acoef = Pe.coeff_monomial(1)
    Bcoef = Pe.coeff_monomial(s)
    assert Pe.degree() <= 2, Pe.degree()
    if Pe.degree() == 2:
        # handle s^2 -> 1-c^2
        E1 = sp.expand(E1.subs(s ** 2, 1 - c ** 2))
        Pe = sp.Poly(E1, s)
        Acoef = Pe.coeff_monomial(1)
        Bcoef = Pe.coeff_monomial(s)
    # (A + B s)=0 and s^2 = 1-c^2  =>  A^2 - B^2 (1-c^2) = 0
    F1 = sp.expand(Acoef ** 2 - Bcoef ** 2 * (1 - c ** 2))
    print('F1 ops', sp.count_ops(F1), 'deg_c', sp.degree(sp.Poly(F1, c)), 'time', round(time.time() - t0, 2), flush=True)

    # z: write F1 = A2 + B2*z ; z^2=3 => A2^2 - 3 B2^2 = 0
    Pz = sp.Poly(F1, z)
    Az = Pz.coeff_monomial(1)
    Bz = Pz.coeff_monomial(z)
    F2 = sp.expand(Az ** 2 - 3 * Bz ** 2)
    print('F2 ops', sp.count_ops(F2), 'deg_c', sp.degree(sp.Poly(F2, c)), 'time', round(time.time() - t0, 2), flush=True)

    F2p = sp.Poly(F2, c)
    Rr = sp.resultant(F2p, sp.Poly(c ** 2 - 1 + s ** 2, c), c)  # placeholder (s already gone)
    print('unused', sp.count_ops(Rr))
    # Now eliminate c between F2(c) and nothing else: F2 is a univariate poly in c
    # with coefficients in Q[r].  The minimal polynomial of r divides the
    # resultant of F2 and its derivative-free factors... use the "trace" trick:
    # r is a root iff F2 has a common root with ... we need the second equation
    # in c.  We have only F2 and c^2+s^2 (already used).  So the remaining
    # unknown c is determined by F2(c)=0 alone; then r is a root of Res_c(F2,
    # dF2/dc) is wrong.  Instead: the set of r for which F2(c)=0 has a solution
    # in c is the discriminant-free condition: F2 must have a root, which over
    # the algebraic closure always holds.  We therefore still need one more
    # independent equation -- see the direct Groebner route below.
    print('NOTE: fall back to groebner (see eliminate2.py)')
    print('total time', round(time.time() - t0, 2))


if __name__ == '__main__':
    main()
