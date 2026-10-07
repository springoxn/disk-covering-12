"""Exact elimination of the symmetric KKT system down to a univariate poly in r.

Chain (every step is ideal-theoretically valid; no branch assumptions):

  f1 = c^2+s^2-1,  f2 = u^2-2cu+1-r^2,  f4 : w = u^2-r^2-r
  g3 = v^2 - v*Pc + 1-r^2                     (f3)
  g5 = v^2 - Q5*v + R5                        (f5, w substituted)
  F6 = det(2*stress matrix)                   (integer coefficients; w substituted)
  f7 = z^2-3

  A1 = Q5 - Pc,  A0 = R5 - (1-r^2)            g3 - g5 = A1 v + A0
  E3  = A1^2 * g3(v=-A0/A1)  = A0^2 - A0*A1*Pc + (1-r^2)*A1^2   in <g3,g5>
  DET = A1^k * F6(v=-A0/A1)                    in <g3,g5,F6>

  E3, DET reduced modulo f2 -> a_i u + b_i
  gam_i = Res_u(a_i u + b_i, f2) = b_i^2 + 2 c a_i b_i + a_i^2 (1-r^2)
  gam_i = A_i + B_i s   (mod s^2 = 1-c^2)
      R1 = A1 B2 - B1 A2,   R2 = A1^2 - B1^2 (1-c^2)
  R_i = al_i + be_i z   (mod z^2 = 3)
      S1 = al1 be2 - be1 al2,  S2 = al1^2 - 3 be1^2
  E(r) = Res_c(S1, S2)

All of R1,R2,S1,S2,E lie in the elimination ideal, hence vanish at the (unique)
certified root r_*.

Usage:
    python tools/elim_full.py                 # exact rational arithmetic
    python tools/elim_full.py --mod 2147483647
    python tools/elim_full.py --save-stage    # dump S1,S2 for reuse
"""
from __future__ import annotations
import os
import pickle
import sys
import time

import sympy as sp

sys.path.insert(0, r'E:\study\ADB\tools')
from kkt_system import SYM, geometry_system  # noqa: E402

r, u, v, w, c, s, z, P, Q, S, A, B, C, D = SYM
MOD = None
for _i, _a in enumerate(sys.argv):
    if _a == '--mod':
        MOD = int(sys.argv[_i + 1])
SAVE_STAGE = '--save-stage' in sys.argv
T0 = time.time()


def log(*a):
    print(f'[{time.time()-T0:8.1f}s]', *a, flush=True)


def P_(e, *g):
    return sp.Poly(sp.expand(e), *g)


def red(e):
    """expand, and reduce coefficients mod MOD when a modulus is in force."""
    e = sp.expand(e)
    if MOD is None:
        return e
    return sp.Poly(e, u, v, c, s, z, r, modulus=MOD).as_expr()


def rem_u(e):
    return red(sp.rem(P_(red(e), u, v, c, s, z, r),
                      P_(u ** 2 - 2 * c * u + 1 - r ** 2, u, v, c, s, z, r), u).as_expr())


def red_s(e):
    return red(sp.rem(P_(red(e), s, c, z, r), P_(s ** 2 + c ** 2 - 1, s, c, z, r), s).as_expr())


def red_z(e):
    return red(sp.rem(P_(red(e), z, c, r), P_(z ** 2 - 3, z, c, r), z).as_expr())


def build_S():
    """Return (S1, S2) as expressions in (c, r), plus diagnostics."""
    _, geomsys, mat, stresses = geometry_system()
    g3, g5 = geomsys[2], geomsys[4]
    F6 = sp.expand((2 * mat).det())          # = 2^7 det(mat); same zero set
    Pc = c ** 2 - s ** 2 + 2 * z * c * s
    wsub = u ** 2 - r ** 2 - r
    Q5 = red(2 * r + wsub)
    R5 = red(wsub * (wsub + r))
    A1 = red(Q5 - Pc)
    A0 = red(R5 - 1 + r ** 2)

    E3 = red(A0 ** 2 - A0 * A1 * Pc + (1 - r ** 2) * A1 ** 2)
    log('E3 built', sp.count_ops(E3))
    R3 = rem_u(E3)
    a1 = sp.expand(R3.coeff(u)); b1 = red(R3 - a1 * u)
    log('a1/b1', sp.count_ops(a1), sp.count_ops(b1))

    dv = P_(red(F6.subs(w, wsub)), v, c, s, z, r)
    k = dv.degree()
    dve = dv.as_expr()
    DET = red(sum(sp.expand(dve.coeff(v, i)) * A0 ** i * A1 ** (k - i)
                  for i in range(k + 1)))
    log('DET built (v-deg %d)' % k, sp.count_ops(DET))
    R6 = rem_u(DET)
    a2 = sp.expand(R6.coeff(u)); b2 = red(R6 - a2 * u)
    log('a2/b2', sp.count_ops(a2), sp.count_ops(b2))

    gam = [red(b ** 2 + 2 * c * a * b + a ** 2 * (1 - r ** 2)) for (a, b) in ((a1, b1), (a2, b2))]
    log('gamma', [sp.count_ops(g) for g in gam])

    ab = []
    for g in gam:
        g = red_s(g)
        ge = sp.expand(g)
        ab.append((red(ge.coeff(s, 0)), red(ge.coeff(s, 1))))
    (A1c, B1c), (A2c, B2c) = ab
    R1 = red_z(red(A1c * B2c - B1c * A2c))
    R2 = red_z(red(A1c ** 2 - B1c ** 2 * (1 - c ** 2)))
    log('R1,R2', sp.count_ops(R1), sp.count_ops(R2))

    p1e, p2e = sp.expand(R1), sp.expand(R2)
    al1, be1 = red(p1e.coeff(z, 0)), red(p1e.coeff(z, 1))
    al2, be2 = red(p2e.coeff(z, 0)), red(p2e.coeff(z, 1))
    S1 = red(al1 * be2 - be1 * al2)
    S2 = red(al1 ** 2 - 3 * be1 ** 2)
    log('S1,S2  c-deg', P_(S1, c, r).degree(c), 'r-deg', P_(S1, c, r).degree(r),
        '|', P_(S2, c, r).degree(c), P_(S2, c, r).degree(r))
    return S1, S2


def main():
    S1, S2 = build_S()
    os.makedirs(r'E:\study\ADB\runtime\elim', exist_ok=True)
    tag0 = 'rat' if MOD is None else f'm{MOD}'
    with open(rf'E:\study\ADB\runtime\elim\stage_S_{tag0}.pkl', 'wb') as fh:
        pickle.dump({'S1': sp.srepr(S1), 'S2': sp.srepr(S2), 'mod': MOD}, fh)
    log('stage saved')
    if '--stage-only' in sys.argv:
        return
    log('resultant in c ...')
    if MOD is None:
        E = sp.resultant(P_(S1, c, r), P_(S2, c, r), c)
    else:
        E = sp.resultant(P_(S1, c, r, ), P_(S2, c, r), c)
        E = sp.Poly(E, r, modulus=MOD).as_expr()
    E = sp.expand(E)
    tag = 'rat' if MOD is None else f'm{MOD}'
    with open(rf'E:\study\ADB\runtime\elim\E_{tag}.pkl', 'wb') as fh:
        pickle.dump({'E': sp.srepr(E), 'mod': MOD}, fh)
    log('E(r) degree', sp.Poly(E, r).degree(), 'ops', sp.count_ops(E), '->', tag)


if __name__ == '__main__':
    main()
