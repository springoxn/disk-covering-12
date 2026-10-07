"""Diagnostic: can mpmath.pslq find relations with large coefficients?

Builds a random monic-ish integer polynomial of degree d with coefficients of
size ~10^h, takes a real root to high precision, and asks pslq to recover the
relation from (1, a, ..., a^d).
"""
import random
import sys
import time

import mpmath as mp
import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
t = sp.symbols('t')
random.seed(7)

for d, h, dps in ((4, 17, 300), (8, 17, 400), (12, 17, 500), (20, 17, 700), (37, 17, 1000)):
    coeffs = [random.randint(0, 10 ** h) for _ in range(d)]
    P = sp.Poly(sum(c * t ** i for i, c in enumerate(coeffs)) + t ** d, t)
    roots = sp.Poly(P, t).nroots(n=40, maxsteps=200)
    real = [x for x in roots if abs(sp.im(x)) < sp.Rational(1, 10 ** 30)]
    if not real:
        print(f'd={d}: no real root, skipped')
        continue
    a_expr = real[0]
    mp.mp.dps = dps
    a = mp.mpf(str(sp.N(a_expr, dps - 20)))
    x = [mp.mpf(1)] + [a ** k for k in range(1, d + 1)]
    t0 = time.time()
    rel = mp.pslq(x, tol=mp.mpf(10) ** (-(dps - 100)), maxcoeff=10 ** (h + 2), maxsteps=40000)
    dt = time.time() - t0
    if rel is None:
        print(f'd={d} height~1e{h}: pslq FAILED to find the known relation ({dt:.0f}s, {dps} dps)')
    else:
        Q = sp.Poly(sum(int(c) * t ** i for i, c in enumerate(rel)), t)
        print(f'd={d} height~1e{h}: found, deg {Q.degree()}, '
              f'height {max(abs(int(c)) for c in Q.all_coeffs())} ({dt:.0f}s)', flush=True)
