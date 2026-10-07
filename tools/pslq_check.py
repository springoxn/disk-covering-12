"""Targeted PSLQ confirmation that 37 is the minimal degree.

P has height ~3e11, so a relation of degree 37 needs only ~37*11.5 ~ 430 correct
digits; 600 dps is ample and much faster than 1200 dps.
"""
import json
import sys
import time

import mpmath as mp
import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
rec = json.load(open(r'E:\study\ADB\runtime\hp_root_1000.json', encoding='utf-8'))
mp.mp.dps = 600
r = mp.mpf(rec['r'])
t = sp.symbols('t')
cand = json.load(open(r'E:\study\ADB\runtime\minpoly_candidate.json', encoding='utf-8'))
P = sp.Poly(sum(sp.Integer(c) * t ** i for i, c in enumerate(reversed(cand['P_coeffs_desc']))), t)

for deg in (36, 37, 38):
    x = [mp.mpf(1)] + [r ** k for k in range(1, deg + 1)]
    t0 = time.time()
    rel = mp.pslq(x, tol=mp.mpf(10) ** (-520), maxcoeff=10 ** 15, maxsteps=30000)
    dt = time.time() - t0
    if rel is None:
        print(f'degree {deg}: no relation ({dt:.0f}s)', flush=True)
    else:
        Q = sp.Poly(sum(int(c) * t ** i for i, c in enumerate(rel)), t)
        same = sp.simplify(Q.as_expr() * sp.Rational(1, int(Q.all_coeffs()[0]))
                           - P.as_expr() * sp.Rational(1, int(P.all_coeffs()[0]))) == 0
        print(f'degree {deg}: FOUND  deg={Q.degree()} height='
              f'{max(abs(int(c)) for c in Q.all_coeffs())}  proportional to candidate: {same}  ({dt:.0f}s)')
        print('   ', Q.as_expr(), flush=True)
        break
