"""Factor the exact stage polynomials S1, S2 in (c,r) and select the factors that
vanish at the numerical root (c_*, r_*)."""
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
mp.mp.dps = 60
CV, RV = mp.mpf(rec['c']), mp.mpf(rec['r'])


def ev(e):
    f = sp.lambdify((c, r), e, modules='mpmath')
    try:
        return abs(f(CV, RV))
    except Exception as ex:
        return None


for name in ('S1', 'S2'):
    d = pickle.load(open(rf'E:\study\ADB\runtime\elim\stage_S_rat.pkl', 'rb'))
    e = sp.sympify(d[name], evaluate=False)
    t0 = time.time()
    fl = sp.factor_list(e, c, r)
    print(f'--- {name}: content={fl[0]}  factors={len(fl[1])}  ({time.time()-t0:.1f}s)')
    for f, m in fl[1]:
        pc = sp.Poly(f, c, r)
        print(f'   deg(c)={pc.degree(c):3d} deg(r)={pc.degree(r):3d} mult={m} '
              f'ops={sp.count_ops(f):6d} |f(c*,r*)|={mp.nstr(ev(f), 5)}')
        print(f'      f = {f}')
    print()
