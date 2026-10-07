"""Cross-check via PSLQ on a scaled variable.

Powers of r_* ~ 0.361 decay to 1e-16 at k = 37, which upsets PSLQ's scaling.
Writing rho = 2 r_* keeps rho^k within [1e-6, 1], and P(r)=0 is equivalent to

    sum_k a_k 2^{37-k} rho^k = 0      (integer coefficients, <= 8e16)

so a relation of degree 37 in rho certifies a relation of degree 37 in r.
"""
import json
import sys
import time

import mpmath as mp
import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
t = sp.symbols('t')
rec = json.load(open(r'E:\study\ADB\runtime\hp_root_1000.json', encoding='utf-8'))
cand = json.load(open(r'E:\study\ADB\runtime\minpoly_candidate.json', encoding='utf-8'))
P = sp.Poly(sum(sp.Integer(c) * t ** i for i, c in enumerate(reversed(cand['P_coeffs_desc']))), t)
mp.mp.dps = 1000
r = mp.mpf(rec['r'])
rho = 2 * r
for deg in (35, 36, 37, 38):
    x = [mp.mpf(1)] + [rho ** k for k in range(1, deg + 1)]
    t0 = time.time()
    rel = mp.pslq(x, tol=mp.mpf(10) ** (-800), maxcoeff=10 ** 20, maxsteps=40000)
    dt = time.time() - t0
    if rel is None:
        print(f'degree {deg}: no relation ({dt:.0f}s)', flush=True)
        continue
    R = sp.Poly(sum(int(c) * t ** i for i, c in enumerate(rel)), t)
    ratio = sp.simplify(sp.cancel(R.as_expr() / P.as_expr()))
    print(f'degree {deg}: FOUND height {max(abs(int(c)) for c in R.all_coeffs())} '
          f'| R/P = {ratio}  (is polynomial: {sp.denom(sp.cancel(ratio)) == 1})  ({dt:.0f}s)', flush=True)
    break
