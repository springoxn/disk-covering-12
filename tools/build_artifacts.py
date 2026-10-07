"""Build and save every exact algebraic artifact needed for the certificate that
P(r_*) = 0, where P is the degree-37 minimal polynomial candidate.

Artifacts (all in Q[c,r] unless stated):
    beta1   : R1 = beta1 * z           (R1 = cross resultant of the s-elimination)
    alpha2  : R2 = alpha2              (R2 = norm-type resultant)
    S2 = -3 beta1^2  in I
    V  =    alpha2^2 in I
    S2 = kappa * (r+1)^4 r^16 c^2 (c^2 r^2 + c^2 - 1)^2 * F^2
    V  = kappa2 * cof2 * G^2
    F, G : the irreducible relevant factors
    E(r) = Res_c(F, G) with E(r_*) = 0
"""
from __future__ import annotations
import json
import os
import pickle
import sys
import time

import sympy as sp

sys.path.insert(0, r'E:\study\ADB\tools')
from kkt_system import SYM, geometry_system  # noqa: E402

r, u, v, w, c, s, z, P, Q, S, A, B, C, D = SYM
T0 = time.time()


def log(*a):
    print(f'[{time.time()-T0:7.1f}s]', *a, flush=True)


_, geomsys, mat, stresses = geometry_system()
g3, g5 = geomsys[2], geomsys[4]
F6 = sp.expand((2 * mat).det())
Pc = c ** 2 - s ** 2 + 2 * z * c * s
wsub = u ** 2 - r ** 2 - r
Q5 = sp.expand(2 * r + wsub)
R5 = sp.expand(wsub * (wsub + r))
A1 = sp.expand(Q5 - Pc)
A0 = sp.expand(R5 - 1 + r ** 2)
E3 = sp.expand(A0 ** 2 - A0 * A1 * Pc + (1 - r ** 2) * A1 ** 2)


def rem_u(e):
    return sp.expand(sp.rem(sp.Poly(e, u, v, c, s, z, r),
                            sp.Poly(u ** 2 - 2 * c * u + 1 - r ** 2, u, v, c, s, z, r), u).as_expr())


R3 = rem_u(E3)
a1 = sp.expand(R3.coeff(u)); b1 = sp.expand(R3 - a1 * u)
dv = sp.Poly(sp.expand(F6.subs(w, wsub)), v, c, s, z, r)
k = dv.degree(); dve = dv.as_expr()
DET = sp.expand(sum(sp.expand(dve.coeff(v, i)) * A0 ** i * A1 ** (k - i) for i in range(k + 1)))
R6 = rem_u(DET)
a2 = sp.expand(R6.coeff(u)); b2 = sp.expand(R6 - a2 * u)
gam = [sp.expand(b ** 2 + 2 * c * a * b + a ** 2 * (1 - r ** 2)) for a, b in ((a1, b1), (a2, b2))]
log('gammas built')


def red_s(e):
    return sp.expand(sp.rem(sp.Poly(e, s, c, z, r), sp.Poly(s ** 2 + c ** 2 - 1, s, c, z, r), s).as_expr())


def red_z(e):
    return sp.expand(sp.rem(sp.Poly(e, z, c, r), sp.Poly(z ** 2 - 3, z, c, r), z).as_expr())


AB = [(sp.expand(red_s(g)).coeff(s, 0), sp.expand(red_s(g)).coeff(s, 1)) for g in gam]
(A1c, B1c), (A2c, B2c) = AB
R1 = red_z(sp.expand(A1c * B2c - B1c * A2c))
R2 = red_z(sp.expand(A1c ** 2 - B1c ** 2 * (1 - c ** 2)))
log('R1,R2 built')

R1e = sp.expand(R1); R2e = sp.expand(R2)
beta1 = sp.expand(R1e.coeff(z, 1))
alpha1 = sp.expand(R1e.coeff(z, 0))
alpha2 = sp.expand(R2e.coeff(z, 0))
beta2 = sp.expand(R2e.coeff(z, 1))
log('alpha1 identically zero:', alpha1 == 0, '| beta2 identically zero:', beta2 == 0)

S2 = sp.expand(alpha1 ** 2 - 3 * beta1 ** 2)
V = sp.expand(alpha2 ** 2 - 3 * beta2 ** 2)
S1 = sp.expand(alpha1 * beta2 - beta1 * alpha2)
log('S1,S2,V built: deg_c', sp.degree(sp.Poly(S2, c)), 'deg_r', sp.degree(sp.Poly(S2, r)),
    '| V', sp.degree(sp.Poly(V, c)), sp.degree(sp.Poly(V, r)))

# ---- exact factorisations
flS2 = sp.factor_list(S2, c, r)
flV = sp.factor_list(V, c, r)
log('S2 factors:', [(int(sp.degree(f, c)), int(sp.degree(f, r)), int(m)) for f, m in flS2[1]])
log('V  factors:', [(int(sp.degree(f, c)), int(sp.degree(f, r)), int(m)) for f, m in flV[1]])

art = {
    'beta1': sp.srepr(beta1),
    'alpha1': sp.srepr(alpha1),
    'alpha2': sp.srepr(alpha2),
    'beta2': sp.srepr(beta2),
    'S1': sp.srepr(S1),
    'S2': sp.srepr(S2),
    'V': sp.srepr(V),
    'R1': sp.srepr(R1),
    'R2': sp.srepr(R2),
    'S2_content': sp.srepr(flS2[0]),
    'S2_factors': [[sp.srepr(f), int(m)] for f, m in flS2[1]],
    'V_content': sp.srepr(flV[0]),
    'V_factors': [[sp.srepr(f), int(m)] for f, m in flV[1]],
    # identity witnesses:  S2 = content * prod f^m  (checked by expansion)
    'E3': sp.srepr(E3), 'DET': sp.srepr(DET), 'R3': sp.srepr(R3), 'R6': sp.srepr(R6),
    'A0': sp.srepr(A0), 'A1': sp.srepr(A1), 'Pc': sp.srepr(Pc),
    'a1': sp.srepr(a1), 'b1': sp.srepr(b1), 'a2': sp.srepr(a2), 'b2': sp.srepr(b2),
    'A1c': sp.srepr(A1c), 'B1c': sp.srepr(B1c), 'A2c': sp.srepr(A2c), 'B2c': sp.srepr(B2c),
    'gam1': sp.srepr(gam[0]), 'gam2': sp.srepr(gam[1]),
    'F6': sp.srepr(F6), 'g3': sp.srepr(g3), 'g5': sp.srepr(g5),
    'f2': sp.srepr(geomsys[1]), 'f1': sp.srepr(geomsys[0]),
}
os.makedirs(r'E:\study\ADB\verify\out', exist_ok=True)
with open(r'E:\study\ADB\runtime\elim\artifacts.pkl', 'wb') as fh:
    pickle.dump(art, fh)
log('artifacts saved')
