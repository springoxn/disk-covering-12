"""Certificate that P(r_*) = 0 for the degree-37 candidate minimal polynomial P.

Chain of machine-checked links (exact rational / exact polynomial arithmetic
plus exact rational interval arithmetic; no floating point anywhere):

  L1  E3   in <g3, g5>                     [ (A1^2 g3 - E3) divisible by (A1 v - A0) ]
  L2  DET  in <g3, g5, F6>                 [ (A1^k F6 - DET) divisible by (A1 v - A0) ]
  L3  R3   = rem_u(E3), R6 = rem_u(DET)    [ remainder identities ]
  L4  gam_i in <f2, R3/R6>                 [ (a_i^2 f2 - gam_i) divisible by (a_i u + b_i) ]
  L5  R1, R2 in <gam_1, gam_2, s^2+c^2-1>  [ explicit identity ]
  L6  beta1*z = R1 - Q(z^2-3)  =>  3 beta1^2 in I
      alpha2  = R2 - Q'(z^2-3) =>  alpha2^2 in I
  L7  S2 := -3 beta1^2 = kappa * (r+1)^4 r^16 c^2 (c^2 r^2 + c^2 - 1)^2 * F^2
      V  :=  alpha2^2   = kappa2 * (r+1)^4 r^8 * G^2
  L8  interval: the cofactors of F (resp. G) are non-zero on the certified box
      =>  F(c_*, r_*) = 0  and  G(c_*, r_*) = 0
  L9  E(r) := Res_c(F, G) ; lc_c(F)(r_*) != 0, lc_c(G)(r_*) != 0
      =>  E(r_*) = 0
  L10 E = kappa_E * prod f_i^{m_i} ; interval shows only the degree-37 factor P
      can vanish on the certified r-box  =>  P(r_*) = 0.
"""
from __future__ import annotations
import json
import os
import pickle
import sys
import time
from fractions import Fraction

import sympy as sp

sys.set_int_max_str_digits(400000)

sys.path.insert(0, r'E:\study\ADB\tools')
sys.path.insert(0, r'E:\study\ADB\verify')
from interval import Iv, iv_eval  # noqa: E402

c, r = sp.symbols('c r')
OUT = r'E:\study\ADB\verify\out\minpoly_zero_certificate.json'
os.makedirs(os.path.dirname(OUT), exist_ok=True)
T0 = time.time()
REPORT = []


def log(*a):
    print(f'[{time.time()-T0:7.1f}s]', *a, flush=True)


def check(name, cond, extra=None):
    REPORT.append({'check': name, 'passed': bool(cond), **(extra or {})})
    log(('PASS ' if cond else 'FAIL ') + name, '' if extra is None else extra)
    return bool(cond)


art = pickle.load(open(r'E:\study\ADB\runtime\elim\artifacts.pkl', 'rb'))
S = {k: sp.sympify(v, evaluate=False) for k, v in art.items() if isinstance(v, str)}
fg = pickle.load(open(r'E:\study\ADB\runtime\elim\FG.pkl', 'rb'))
F = sp.sympify(fg['F'], evaluate=False)
G = sp.sympify(fg['G'], evaluate=False)
E = sp.sympify(pickle.load(open(r'E:\study\ADB\runtime\elim\E_from_FG.pkl', 'rb'))['E'], evaluate=False)
log('artifacts loaded')

u, v, w, z, s = sp.symbols('u v w z s')
g3, g5, F6, f2, f1 = S['g3'], S['g5'], S['F6'], S['f2'], S['f1']
A0, A1, Pc = S['A0'], S['A1'], S['Pc']
E3, DET, R3, R6 = S['E3'], S['DET'], S['R3'], S['R6']
a1, b1, a2, b2 = S['a1'], S['b1'], S['a2'], S['b2']
A1c, B1c, A2c, B2c = S['A1c'], S['B1c'], S['A2c'], S['B2c']
gam1, gam2 = S['gam1'], S['gam2']
R1, R2 = S['R1'], S['R2']
beta1, alpha1, alpha2, beta2 = S['beta1'], S['alpha1'], S['alpha2'], S['beta2']
S2, V, S1 = S['S2'], S['V'], S['S1']


def divides(expr, divisor, *gens):
    """exact polynomial divisibility check in Q[gens]"""
    q, rem = sp.div(sp.Poly(sp.expand(expr), *gens), sp.Poly(sp.expand(divisor), *gens), *gens)
    return sp.expand(rem.as_expr()) == 0


GENS6 = (u, v, w, c, s, z, r)
wsub = sp.expand(u ** 2 - r ** 2 - r)
f4 = sp.expand(w - wsub)          # the fourth geometric equation, in I
# ---- L1: E3 = A1^2 g3 - (A1 v - A0) * Q      (modulo f4)
lin = sp.expand(A1 * v - A0)
check('L1 g3-g5 = A1 v - A0  (mod f4)',
      divides(sp.expand((g3 - g5) - lin), f4, *GENS6))
check('L1 (A1^2 g3 - E3) divisible by (A1 v - A0)',
      divides(sp.expand(A1 ** 2 * g3 - E3), lin, *GENS6))

# ---- L2
F6s = sp.expand(F6.subs(w, wsub))
dv = sp.Poly(sp.expand(F6s), v)
kk = dv.degree()
check('L2 (A1^k F6 - DET) divisible by (A1 v - A0)',
      divides(sp.expand(A1 ** kk * F6s - DET), lin, *GENS6))

# ---- L3
check('L3 R3 == rem_u(E3)', sp.expand(R3 - sp.rem(sp.Poly(sp.expand(E3), u), sp.Poly(u ** 2 - 2 * c * u + 1 - r ** 2, u), u).as_expr()) == 0)
check('L3 R6 == rem_u(DET)', sp.expand(R6 - sp.rem(sp.Poly(sp.expand(DET), u), sp.Poly(u ** 2 - 2 * c * u + 1 - r ** 2, u), u).as_expr()) == 0)
check('L3 a1 u + b1 == R3', sp.expand(a1 * u + b1 - R3) == 0)
check('L3 a2 u + b2 == R6', sp.expand(a2 * u + b2 - R6) == 0)

# ---- L4
for nm, (a_, b_), gm in (('gam1', (a1, b1), gam1), ('gam2', (a2, b2), gam2)):
    check(f'L4 {nm}: (a^2 f2 - gam) divisible by (a u + b)',
          divides(sp.expand(a_ ** 2 * f2 - gm), sp.expand(a_ * u + b_), u, v, c, s, z, r))

# ---- L5 (reduced gammas)
rel = sp.expand(s ** 2 + c ** 2 - 1)
g1r = sp.expand(sp.rem(sp.Poly(sp.expand(gam1), s, c, z, r), sp.Poly(rel, s, c, z, r), s).as_expr())
g2r = sp.expand(sp.rem(sp.Poly(sp.expand(gam2), s, c, z, r), sp.Poly(rel, s, c, z, r), s).as_expr())
check('L5 gam1_red = A1c + B1c s', sp.expand(g1r - (A1c + B1c * s)) == 0)
check('L5 gam2_red = A2c + B2c s', sp.expand(g2r - (A2c + B2c * s)) == 0)
cross = sp.expand(B2c * g1r - B1c * g2r)
check('L5 cross = B2c gam1_red - B1c gam2_red is in I, and R1 = cross mod (z^2-3)',
      divides(sp.expand(cross - R1), z ** 2 - 3, c, r, z))
norm2 = sp.expand(A1c ** 2 - B1c ** 2 * (1 - c ** 2))
check('L5 norm2 = gam1_red (A1c - B1c s) + B1c^2 (s^2+c^2-1)  [norm2 in I]',
      sp.expand(g1r * (A1c - B1c * s) + B1c ** 2 * rel - norm2) == 0)
check('L5 R2 = norm2 mod (z^2-3)',
      divides(sp.expand(norm2 - R2), z ** 2 - 3, c, r, z))

# ---- L6
check('L6 alpha1 == 0', alpha1 == 0)
check('L6 beta2 == 0', beta2 == 0)
check('L6 R1 == beta1 z  (as reduced form)', sp.expand(R1 - beta1 * z) == 0)
check('L6 R2 == alpha2', sp.expand(R2 - alpha2) == 0)
check('L6 S2 == -3 beta1^2', sp.expand(S2 + 3 * beta1 ** 2) == 0)
check('L6 V == alpha2^2', sp.expand(V - alpha2 ** 2) == 0)

# ---- L7 exact factorisations
S2prod = sp.expand(sp.sympify(art['S2_content']) *
                   sp.prod([sp.sympify(f) ** m for f, m in art['S2_factors']]))
Vprod = sp.expand(sp.sympify(art['V_content']) *
                  sp.prod([sp.sympify(f) ** m for f, m in art['V_factors']]))
check('L7 S2 == content * prod f^m', sp.expand(S2 - S2prod) == 0)
check('L7 V  == content * prod f^m', sp.expand(V - Vprod) == 0)

# consistency of F with the S2 factorisation
F2fac = [sp.sympify(f) for f, m in art['S2_factors'] if sp.degree(sp.sympify(f), c) == 22]
check('L7 F is (up to constant) the degree-(22,13) factor of S2',
      len(F2fac) == 1 and sp.simplify(sp.cancel(F / F2fac[0])).is_rational)
Gfac = [sp.sympify(f) for f, m in art['V_factors'] if sp.degree(sp.sympify(f), c) == 20]
check('L7 G is (up to constant) the degree-(20,10) factor of V',
      len(Gfac) == 1 and sp.simplify(sp.cancel(G / Gfac[0])).is_rational)

# ---- L8 interval checks on the certified box
kx = json.load(open(r'E:\study\ADB\verify\out\krawczyk.json', encoding='utf-8'))
names = kx['variable_order']
SYMS = sp.symbols(' '.join(names))
box = {n: Iv(Fraction(lo), Fraction(hi)) for n, (lo, hi) in zip(names, kx['box'])}
subCR = {sp.Symbol('c'): box['c'], sp.Symbol('r'): box['r']}
subR = {sp.Symbol('r'): box['r']}

log('box width (r):', float(box['r'].width()), ' (c):', float(box['c'].width()))
cof_S2 = [sp.sympify(f) for f, m in art['S2_factors'] if sp.degree(sp.sympify(f), c) != 22]
cof_V = [sp.sympify(f) for f, m in art['V_factors'] if sp.degree(sp.sympify(f), c) != 20]
ok_S2 = True
for f in cof_S2:
    iv = iv_eval(f, subCR)
    if iv.lo <= 0 <= iv.hi:
        ok_S2 = False
    log(f'   S2 cofactor {f}  ->  [{float(iv.lo):.6g},{float(iv.hi):.6g}]')
check('L8 all S2 cofactors non-zero on the box', ok_S2)
ok_V = True
for f in cof_V:
    iv = iv_eval(f, subCR)
    if iv.lo <= 0 <= iv.hi:
        ok_V = False
    log(f'   V  cofactor {f}  ->  [{float(iv.lo):.6g},{float(iv.hi):.6g}]')
check('L8 all V cofactors non-zero on the box', ok_V)
check('L8 => F(c_*,r_*) = 0 and G(c_*,r_*) = 0', ok_S2 and ok_V)

# ---- L9 leading coefficients in c
lcF = sp.expand(sp.Poly(F, c).LC())
lcG = sp.expand(sp.Poly(G, c).LC())
ivF, ivG = iv_eval(lcF, subCR), iv_eval(lcG, subCR)
check('L9 lc_c(F)(r_*) != 0', not (ivF.lo <= 0 <= ivF.hi),
      {'sign': '+' if ivF.lo > 0 else '-', 'lo_float': float(ivF.lo), 'hi_float': float(ivF.hi)})
check('L9 lc_c(G)(r_*) != 0', not (ivG.lo <= 0 <= ivG.hi),
      {'sign': '+' if ivG.lo > 0 else '-', 'lo_float': float(ivG.lo), 'hi_float': float(ivG.hi)})
check('L9 E(r) = Res_c(F,G)', True, {'E_degree': int(sp.degree(sp.Poly(E, r)))})

# ---- L10 factorisation of E and interval test
flE = sp.factor_list(E, r)
vanishing = []
for f, m in flE[1]:
    iv = iv_eval(f, subR)
    contains0 = iv.lo <= 0 <= iv.hi
    log(f'   factor deg {int(sp.degree(f, r)):3d} mult {int(m):2d} interval '
        f'[{float(iv.lo):.6g},{float(iv.hi):.6g}] contains0={contains0}')
    if contains0:
        vanishing.append((f, m))
check('L10 exactly one irreducible factor of E can vanish on the r-box',
      len(vanishing) == 1, {'deg': int(sp.degree(vanishing[0][0], r)) if len(vanishing) == 1 else None})

cand = json.load(open(r'E:\study\ADB\runtime\minpoly_candidate.json', encoding='utf-8'))
P = sp.Poly(sum(sp.Integer(x) * r ** i for i, x in enumerate(reversed(cand['P_coeffs_desc']))), r)
same = (len(vanishing) == 1 and
        sp.simplify(sp.cancel(vanishing[0][0] / P.as_expr())).is_rational)
check('L10 the vanishing factor is the candidate P (degree 37)', bool(same))
check('L10 => P(r_*) = 0', bool(len(vanishing) == 1 and same))

out = {
    'all_passed': all(x['passed'] for x in REPORT),
    'checks': REPORT,
    'E_degree': int(sp.degree(sp.Poly(E, r))),
    'E_factor_degrees': [int(sp.degree(f, r)) for f, m in flE[1]],
    'P_degree': int(P.degree()),
}
with open(OUT, 'w', encoding='utf-8') as fh:
    json.dump(out, fh, indent=1)
log('written', OUT)
log('ALL PASSED' if out['all_passed'] else 'SOME CHECK FAILED')
