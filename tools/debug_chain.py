"""Numerically debug the elimination chain at the certified root."""
from __future__ import annotations
import json
import pickle
import sys

import mpmath as mp
import sympy as sp

sys.path.insert(0, r'E:\study\ADB\tools')
from kkt_system import SYM, geometry_system  # noqa: E402

r, u, v, w, c, s, z, P, Q, S, A, B, C, D = SYM
rec = json.load(open(r'E:\study\ADB\runtime\hp_root.json', encoding='utf-8'))
mp.mp.dps = 80
VAL = {n: mp.mpf(rec[n]) for n in ('r', 'u', 'v', 'w', 'c', 's', 'z', 'P', 'Q', 'S', 'A', 'B', 'C', 'D')}


def ev(e):
    f = sp.lambdify(SYM, e, modules='mpmath')
    return f(*[VAL[n] for n in ('r', 'u', 'v', 'w', 'c', 's', 'z', 'P', 'Q', 'S', 'A', 'B', 'C', 'D')])


def show(name, e):
    try:
        print(f'  {name:12s} {mp.nstr(ev(e), 8)}')
    except Exception as ex:
        print(f'  {name:12s} ERR {ex}')


_, geomsys, mat, stresses = geometry_system()
g3, g5 = geomsys[2], geomsys[4]
F6 = sp.expand((2 * mat).det())
Pc = c ** 2 - s ** 2 + 2 * z * c * s
wsub = u ** 2 - r ** 2 - r
Q5 = sp.expand(2 * r + wsub)
R5 = sp.expand(wsub * (wsub + r))
A1 = sp.expand(Q5 - Pc)
A0 = sp.expand(R5 - 1 + r ** 2)
print('point values:')
for nm, e in [('g1', geomsys[0]), ('g2', geomsys[1]), ('g3', g3), ('g5', g5), ('F6', F6),
              ('z2-3', z ** 2 - 3)]:
    show(nm, e)
print('  g3-g5 vs A1*v+A0:', mp.nstr(ev(g3 - g5), 6), mp.nstr(ev(A1 * v + A0), 6))

E3 = sp.expand(A0 ** 2 - A0 * A1 * Pc + (1 - r ** 2) * A1 ** 2)
show('E3', E3)
R3 = sp.rem(sp.Poly(E3, u, v, c, s, z, r), sp.Poly(u ** 2 - 2 * c * u + 1 - r ** 2, u, v, c, s, z, r), u).as_expr()
show('R3', R3)
a1 = sp.expand(R3.coeff(u)); b1 = sp.expand(R3 - a1 * u)
show('a1', a1); show('b1', b1)
gam1 = sp.expand(b1 ** 2 + 2 * c * a1 * b1 + a1 ** 2 * (1 - r ** 2))
show('gam1', gam1)

dv = sp.Poly(sp.expand(F6.subs(w, wsub)), v, c, s, z, r)
k = dv.degree(); dve = dv.as_expr()
DET = sp.expand(sum(sp.expand(dve.coeff(v, i)) * A0 ** i * A1 ** (k - i) for i in range(k + 1)))
show('DET', DET)
R6 = sp.rem(sp.Poly(DET, u, v, c, s, z, r), sp.Poly(u ** 2 - 2 * c * u + 1 - r ** 2, u, v, c, s, z, r), u).as_expr()
show('R6', R6)
a2 = sp.expand(R6.coeff(u)); b2 = sp.expand(R6 - a2 * u)
show('a2', a2); show('b2', b2)
gam2 = sp.expand(b2 ** 2 + 2 * c * a2 * b2 + a2 ** 2 * (1 - r ** 2))
show('gam2', gam2)

print('s-degree of gammas:', sp.degree(sp.Poly(gam1, s)), sp.degree(sp.Poly(gam2, s)))

for tag, g in (('g1', gam1), ('g2', gam2)):
    gr = sp.rem(sp.Poly(g, s, c, z, r), sp.Poly(s ** 2 + c ** 2 - 1, s, c, z, r), s).as_expr()
    show('red_s ' + tag, gr)
    ge = sp.expand(gr)
    print(f'  {tag}: s-degree after red {sp.degree(sp.Poly(gr, s))}')
    AA, BB = ge.coeff(s, 0), ge.coeff(s, 1)
    show('A ' + tag, AA); show('B ' + tag, BB)
    globals()['A_' + tag] = AA; globals()['B_' + tag] = BB

A1c, B1c, A2c, B2c = A_g1, B_g1, A_g2, B_g2
R1 = sp.expand(A1c * B2c - B1c * A2c)
R2 = sp.expand(A1c ** 2 - B1c ** 2 * (1 - c ** 2))
show('R1', R1); show('R2', R2)
print('z-degree R1,R2:', sp.degree(sp.Poly(R1, z)), sp.degree(sp.Poly(R2, z)))
R1z = sp.rem(sp.Poly(R1, z, c, r), sp.Poly(z ** 2 - 3, z, c, r), z).as_expr()
R2z = sp.rem(sp.Poly(R2, z, c, r), sp.Poly(z ** 2 - 3, z, c, r), z).as_expr()
show('R1z', R1z); show('R2z', R2z)
print('z-degree after red:', sp.degree(sp.Poly(R1z, z)), sp.degree(sp.Poly(R2z, z)))
for tag, Rz in (('1', R1z), ('2', R2z)):
    e = sp.expand(Rz)
    globals()['al' + tag] = e.coeff(z, 0)
    globals()['be' + tag] = e.coeff(z, 1)
    show('al' + tag, globals()['al' + tag]); show('be' + tag, globals()['be' + tag])
S1 = sp.expand(al1 * be2 - be1 * al2)
S2 = sp.expand(al1 ** 2 - 3 * be1 ** 2)
show('S1', S1); show('S2', S2)
show('S2 alt (al2^2-3be2^2)', sp.expand(al2 ** 2 - 3 * be2 ** 2))
print('S2 via (al1-be1 z)*R1z :', mp.nstr(ev(R1z) * ev(sp.expand(al1 - be1 * z)), 8))
