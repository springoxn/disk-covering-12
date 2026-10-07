import json
import sys
import time

import mpmath as mp
import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
d = json.load(open(r'E:\study\ADB\runtime\hp_root_1000.json', encoding='utf-8'))
mp.mp.dps = 1200
r = mp.mpf(d['r'])
t = sp.symbols('t')
cand = json.load(open(r'E:\study\ADB\runtime\minpoly_candidate.json', encoding='utf-8'))
Pc = sp.Poly(sum(sp.Integer(c) * t ** i for i, c in enumerate(reversed(cand['P_coeffs_desc']))), t)
print('candidate P:', Pc.as_expr())
print('deg', Pc.degree(), 'height', max(abs(int(x)) for x in Pc.all_coeffs()))
mp.mp.dps = 1200
val = mp.mpf(0)
for i, cf in enumerate(Pc.all_coeffs()):
    val += mp.mpf(int(cf)) * r ** (Pc.degree() - i)
print('P(r_1000) =', mp.nstr(val, 20))

for tol_digits in (600, 700, 800, 900, 1000):
    for deg in (36, 37, 38):
        x = [mp.mpf(1)] + [r ** k for k in range(1, deg + 1)]
        t0 = time.time()
        rel = mp.pslq(x, tol=mp.mpf(10) ** (-tol_digits), maxcoeff=10 ** 40, maxsteps=20000)
        print(f'deg={deg} tol=1e-{tol_digits} -> {"None" if rel is None else len(rel)} ({time.time()-t0:.0f}s)', flush=True)
        if rel is not None:
            Q = sp.Poly(sum(int(c) * t ** i for i, c in enumerate(rel)), t)
            print('   found poly deg', Q.degree(), 'height',
                  max(abs(int(x)) for x in Q.all_coeffs()), flush=True)
            print('   ', Q.as_expr(), flush=True)
            print('   equals candidate?', sp.simplify(Q.as_expr() * sp.Rational(1, int(Q.all_coeffs()[0])) -
                                                      Pc.as_expr() * sp.Rational(1, int(Pc.all_coeffs()[0]))) == 0, flush=True)
            sys.exit(0)
