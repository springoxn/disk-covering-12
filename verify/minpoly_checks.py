"""Rigorous checks on the candidate minimal polynomial P of r_*.

Checks performed (all exact / interval):
  A. P is primitive in Z[t], nonconstant, with positive leading coefficient.
  B. P(a) * P(b) != 0 for the isolating endpoints (exact rational evaluation).
  C. P has exactly one real root in (a,b) (Sturm sequence, exact).
  D. r_* lies in (a,b)  (using the certified rational enclosure of r_*).
  E. P is irreducible over Q:
       E1. exact factorisation over Z (sympy) -> single factor
       E2. degree-preserving irreducibility certificate modulo a prime p
           (P mod p irreducible and deg(P mod p) = deg P).
Output: verify/out/minpoly_checks.json
"""
from __future__ import annotations
import json
import os
import sys
import time
from fractions import Fraction

import sympy as sp

t = sp.symbols('t')
OUTDIR = r'E:\study\ADB\verify\out'
os.makedirs(OUTDIR, exist_ok=True)
cand = json.load(open(r'E:\study\ADB\runtime\minpoly_candidate.json', encoding='utf-8'))
coeffs_desc = [int(x) for x in cand['P_coeffs_desc']]
P = sp.Poly(sum(c * t ** i for i, c in enumerate(reversed(coeffs_desc))), t)
res = {}


def log(*a):
    print(*a, flush=True)


# ---------- A ----------
cont, prim = P.primitive()
res['degree'] = P.degree()
res['content'] = int(cont)
res['primitive'] = bool(cont == 1)
res['leading_coeff'] = int(P.all_coeffs()[0])
res['leading_positive'] = bool(P.all_coeffs()[0] > 0)
res['constant_term'] = int(P.all_coeffs()[-1])
res['height'] = max(abs(int(x)) for x in P.all_coeffs())
log('A: degree', res['degree'], 'primitive', res['primitive'],
    'lc', res['leading_coeff'], 'height', res['height'])

# ---------- D ----------
k = json.load(open(r'E:\study\ADB\lit\DiskCoveringSolve\cover12\proof_bundle'
                   r'\cover12_symmetric_kkt_cert.json', encoding='utf-8'))
rho_num, rho_den = int(k['rho_num']), int(k['rho_den'])
xnum = [int(v) for v in k['xnum']]
Qx = int(k['Qx'])
r_center = Fraction(xnum[0], Qx)
r_radius = Fraction(rho_num, rho_den)
res['certified_r_interval_bundle'] = [str(r_center - r_radius), str(r_center + r_radius)]

# ---------- isolating interval ----------
# take a tight rational box around the certified r_* enclosure
lo = r_center - r_radius
hi = r_center + r_radius
# widen to a "nice" rational interval with a short decimal representation
import math
scale = 10 ** 30
a = Fraction(math.floor(lo * scale) - 1, scale)
b = Fraction(math.ceil(hi * scale) + 1, scale)
res['a'] = str(a)
res['b'] = str(b)


def dec(fr: Fraction, nd: int = 45) -> str:
    s = '-' if fr < 0 else ''
    fr = abs(fr)
    q, rem = divmod(fr.numerator, fr.denominator)
    frac = ''
    for _ in range(nd):
        rem *= 10
        d, rem = divmod(rem, fr.denominator)
        frac += str(d)
    return f'{s}{q}.{frac}'


res['a_decimal'] = dec(a)
res['b_decimal'] = dec(b)


def evalf_rat(poly, x: Fraction):
    num = 0
    den = 1
    xn, xd = x.numerator, x.denominator
    # Horner with rationals
    acc = Fraction(0)
    for cf in poly.all_coeffs():
        acc = acc * x + Fraction(int(cf))
    return acc


Pa, Pb = evalf_rat(P, a), evalf_rat(P, b)
res['P(a)'] = str(Pa)
res['P(b)'] = str(Pb)
res['P(a)_nonzero'] = bool(Pa != 0)
res['P(b)_nonzero'] = bool(Pb != 0)
log('B: P(a)!=0', res['P(a)_nonzero'], ' P(b)!=0', res['P(b)_nonzero'])
log('   a =', res['a_decimal'], ' b =', res['b_decimal'])

# ---------- C: Sturm ----------
t0 = time.time()
n_ab = P.count_roots(a, b)
n_re = P.count_roots()
res['roots_in_ab'] = int(n_ab)
res['real_roots_total'] = int(n_re)
res['r_star_in_ab'] = bool(a <= lo and hi <= b)
log(f'C: roots in (a,b) = {n_ab}; total real roots = {n_re}  ({time.time()-t0:.1f}s)')
log('D: r_* enclosure inside (a,b):', res['r_star_in_ab'])

# ---------- E1 ----------
t0 = time.time()
fl = sp.factor_list(P.as_expr(), t)
res['factorization'] = [(sp.srepr(f), int(m)) for f, m in fl[1]]
res['factor_degrees'] = [int(sp.degree(f, t)) for f, m in fl[1]]
res['irreducible_over_Q_by_factor'] = bool(len(fl[1]) == 1 and fl[1][0][1] == 1)
log(f'E1: factorization degrees {res["factor_degrees"]} ({time.time()-t0:.1f}s)')

# ---------- E2: modular irreducibility certificate ----------
best = None
for p in list(sp.primerange(10 ** 9, 10 ** 9 + 4000)):
    if int(P.all_coeffs()[0]) % p == 0:
        continue
    Pp = sp.Poly(P.as_expr(), t, modulus=p)
    if Pp.degree() != P.degree():
        continue
    fp = sp.factor_list(P.as_expr(), t, modulus=p)
    if len(fp[1]) == 1 and fp[1][0][1] == 1:
        best = p
        break
res['modular_prime'] = int(best) if best else None
res['irreducible_mod_p'] = bool(best is not None)
log('E2: mod-p irreducibility certificate with p =', best,
    '=> P irreducible over Q:', res['irreducible_mod_p'])

with open(os.path.join(OUTDIR, 'minpoly_checks.json'), 'w', encoding='utf-8') as fh:
    json.dump(res, fh, indent=1)
log('written', os.path.join(OUTDIR, 'minpoly_checks.json'))
