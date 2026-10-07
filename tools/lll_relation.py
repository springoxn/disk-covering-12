"""LLL-based integer-relation cross-check for the minimal polynomial of r_*.

mpmath's `pslq` cannot recover relations whose coefficients exceed ~10^6 (see
tools/pslq_capability.py), so the cross-check uses an exact LLL reduction of

    rows i = (e_i, round(N * rho^i))       i = 0..d ,   rho = 2 r_*

and then *evaluates* sum b_i rho^i in high precision for every reduced basis
vector: a genuine relation has |sum| ~ 1e-950 while a merely short lattice
vector has |sum| = O(1).
"""
from __future__ import annotations
import json
import sys
import time

import mpmath as mp
import sympy as sp
from sympy import Matrix

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
rec = json.load(open(r'E:\study\ADB\runtime\hp_root_1000.json', encoding='utf-8'))
DIG = 700
mp.mp.dps = 900
r = mp.mpf(rec['r'])
rho = 2 * r
N = mp.mpf(10) ** DIG
t = sp.symbols('t')
cand = json.load(open(r'E:\study\ADB\runtime\minpoly_candidate.json', encoding='utf-8'))
P = sp.Poly(sum(sp.Integer(c) * t ** i for i, c in enumerate(reversed(cand['P_coeffs_desc']))), t)
TOL = mp.mpf(10) ** (-800)

for d in (37, 36):
    rows = []
    for i in range(d + 1):
        row = [0] * (d + 2)
        row[i] = 1
        row[d + 1] = int(mp.nint(N * rho ** i))
        rows.append(row)
    t0 = time.time()
    R = Matrix(rows).lll(delta=sp.Rational(99, 100))
    dt = time.time() - t0
    found = None
    stats = []
    for i in range(R.rows):
        b = [int(x) for x in R.row(i)][:-1]
        S = mp.fsum(mp.mpf(b[k]) * rho ** k for k in range(len(b)))
        stats.append((abs(S), max(abs(x) for x in b)))
    stats.sort(key=lambda z: z[0])
    print(f'd={d}: LLL {dt:.0f}s; smallest |sum b_i rho^i| over the {len(stats)} reduced rows: '
          f'{mp.nstr(stats[0][0], 6)} (max|b| = {stats[0][1]:.3g}); '
          f'next: {mp.nstr(stats[1][0], 6)}', flush=True)
    if stats[0][0] < TOL:
        # identify which row
        for i in range(R.rows):
            b = [int(x) for x in R.row(i)][:-1]
            S = mp.fsum(mp.mpf(b[k]) * rho ** k for k in range(len(b)))
            if abs(S) < TOL:
                print(f'   RELATION FOUND in row {i}, max|b| = {max(abs(x) for x in b)}', flush=True)
                Rr = sp.Poly(sum(sp.Integer(b[k]) * 2 ** k * t ** k for k in range(len(b))), t)
                quo, rem = sp.div(Rr, P, t)
                print(f'   as polynomial in r: degree {Rr.degree()}; remainder mod P = '
                      f'{sp.expand(rem.as_expr())}', flush=True)
                found = (d, b)
                break
    if found:
        break
