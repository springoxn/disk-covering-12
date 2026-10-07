"""Diagnostics: the z-split components at the root, and alternative elements of
the elimination ideal in Q[c,r] that can replace G in the resultant.

Elements of I = <system> intersected with Q[c,r] used here:
    S2  = a1^2 - 3 b1^2                     (norm of R1 w.r.t. z^2=3)
    V   = a2^2 - 3 b2^2                     (norm of R2)
    S1  = a1 b2 - b1 a2                     (cross term)
    U   = a1 a2 + 3 b1 b2                   (constant part of R1*R2)
    W   = a1 a2 - 3 b1 b2
where R1 = a1 + b1 z, R2 = a2 + b2 z are the two z-linear consequences of the
s-elimination.  Each of S2, V, U, W is in the ideal, hence vanishes at the root.
"""
from __future__ import annotations
import json
import pickle
import sys
import time

import mpmath as mp
import sympy as sp

sys.path.insert(0, r'E:\study\ADB\tools')

c, r = sp.symbols('c r')
rec = json.load(open(r'E:\study\ADB\runtime\hp_root.json', encoding='utf-8'))
mp.mp.dps = 100
CV, RV = mp.mpf(rec['c']), mp.mpf(rec['r'])


def ev(e, subs=('c', 'r'), vals=(CV, RV)):
    f = sp.lambdify(subs, e, modules='mpmath')
    try:
        return abs(f(*vals))
    except Exception:
        return None


d = pickle.load(open(r'E:\study\ADB\runtime\elim\stage_S_rat.pkl', 'rb'))
S1 = sp.sympify(d['S1'], evaluate=False)
S2 = sp.sympify(d['S2'], evaluate=False)

# recover R1, R2 (z-linear) from the stored stage by rebuilding them
from elim_full import build_S  # noqa: E402  (rebuilds and returns S1,S2 only)

# instead: reuse the saved FG factors and reconstruct nothing else; we recompute
# the z-split directly from S1,S2 is impossible, so we rebuild the chain quickly.
import kkt_system  # noqa: E402
from kkt_system import SYM, geometry_system  # noqa: E402

r_, u, v, w, c_, s, z, P, Q, S, A, B, C, D = SYM
_, geomsys, mat, stresses = geometry_system()
F6 = sp.expand((2 * mat).det())
Pc_ = c ** 2 - s ** 2 + 2 * z * c * s
wsub = u ** 2 - r ** 2 - r
Q5 = sp.expand(2 * r + wsub)
R5 = sp.expand(wsub * (wsub + r))
A1 = sp.expand(Q5 - Pc_)
A0 = sp.expand(R5 - 1 + r ** 2)
E3 = sp.expand(A0 ** 2 - A0 * A1 * Pc_ + (1 - r ** 2) * A1 ** 2)


def rem_u(e):
    return sp.expand(sp.rem(sp.Poly(e, u, v, c, s, z, r), sp.Poly(u ** 2 - 2 * c * u + 1 - r ** 2, u, v, c, s, z, r), u).as_expr())


R3 = rem_u(E3)
a1 = sp.expand(R3.coeff(u)); b1 = sp.expand(R3 - a1 * u)
dv = sp.Poly(sp.expand(F6.subs(w, wsub)), v, c, s, z, r)
k = dv.degree(); dve = dv.as_expr()
DET = sp.expand(sum(sp.expand(dve.coeff(v, i)) * A0 ** i * A1 ** (k - i) for i in range(k + 1)))
R6 = rem_u(DET)
a2 = sp.expand(R6.coeff(u)); b2 = sp.expand(R6 - a2 * u)


def red_s(e):
    return sp.expand(sp.rem(sp.Poly(e, s, c, z, r), sp.Poly(s ** 2 + c ** 2 - 1, s, c, z, r), s).as_expr())


def red_z(e):
    return sp.expand(sp.rem(sp.Poly(e, z, c, r), sp.Poly(z ** 2 - 3, z, c, r), z).as_expr())


gams = [red_s(sp.expand(b ** 2 + 2 * c * a * b + a ** 2 * (1 - r ** 2))) for a, b in ((a1, b1), (a2, b2))]
AB = [(sp.expand(g).coeff(s, 0), sp.expand(g).coeff(s, 1)) for g in gams]
(A1c, B1c), (A2c, B2c) = AB
R1 = red_z(sp.expand(A1c * B2c - B1c * A2c))
R2 = red_z(sp.expand(A1c ** 2 - B1c ** 2 * (1 - c ** 2)))
print('R1 == S1 ?', sp.expand(R1 - S1) == 0)
print('R2 == S2 ?', sp.expand(R2 - S2) == 0)
al1 = sp.expand(R1).coeff(z, 0); be1 = sp.expand(R1).coeff(z, 1)
al2 = sp.expand(R2).coeff(z, 0); be2 = sp.expand(R2).coeff(z, 1)
for nm, e in [('al1', al1), ('be1', be1), ('al2', al2), ('be2', be2)]:
    print(f'  {nm}(c*,r*) = {mp.nstr(ev(e), 8)}')

elems = {
    'S1 = al1 be2 - be1 al2': sp.expand(al1 * be2 - be1 * al2),
    'S2 = al1^2 - 3 be1^2': sp.expand(al1 ** 2 - 3 * be1 ** 2),
    'V  = al2^2 - 3 be2^2': sp.expand(al2 ** 2 - 3 * be2 ** 2),
    'U  = al1 al2 + 3 be1 be2': sp.expand(al1 * al2 + 3 * be1 * be2),
    'W  = al1 al2 - 3 be1 be2': sp.expand(al1 * al2 - 3 * be1 * be2),
    'al1^2': sp.expand(al1 ** 2),
    'be1^2': sp.expand(be1 ** 2),
    'al2^2': sp.expand(al2 ** 2),
    'be2^2': sp.expand(be2 ** 2),
    'al1 be1': sp.expand(al1 * be1),
}
out = {}
for nm, e in elems.items():
    print(f'--- {nm}: deg_c {sp.degree(sp.Poly(e, c))} deg_r {sp.degree(sp.Poly(e, r))} |e(c*,r*)|={mp.nstr(ev(e), 5)}')
    fl = sp.factor_list(e, c, r)
    rel = []
    for f, m in fl[1]:
        val = ev(f)
        if val is not None and val < mp.mpf('1e-40'):
            rel.append((f, m, val))
            print(f'      RELEVANT deg_c={sp.degree(f, c)} deg_r={sp.degree(f, r)} mult={m} |f|={mp.nstr(val,4)}')
    out[nm] = [(sp.srepr(f), m) for f, m, _ in rel]

with open(r'E:\study\ADB\runtime\elim\ideal_elems.json', 'w', encoding='utf-8') as fh:
    json.dump(out, fh, indent=1)
print('saved')
