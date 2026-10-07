"""Independent verification of the numeric thresholds used by the reduction.

These are the inequalities that make the *combinatorial reduction* of the lower
bound work (third-party proof, sections 3.3 and 5):

  (T1)  r_* < 1/2                      -- the origin's Voronoi cell cannot touch
                                          the unit circle, hence I >= 1
  (T2)  t_* = r_*^2 < T := 814971/6250000
  (T3)  8*Delta < 2*pi                 -- so B >= 9 for any radius-rho < r_* cover
  (T4)  4*Delta < pi                   -- the path used in the metric bound is
                                          the minor arc
  (T5)  T < sin^2(Delta/2)
  (T6)  4*sin^2(alpha_d/2) > d^2 * T   for d = 2,3,4,5,
        alpha = (0.73891, 1.14482, 1.61399, 2.25230)

with Delta = 73891/100000.  All inequalities are checked with my own rational
Machin-series bounds for pi and my own rational Taylor bounds for sin; r_* comes
from the certified Krawczyk box.  No floating point enters any decision.
"""
from __future__ import annotations
import json
import os
import sys
from fractions import Fraction
from math import factorial

OUT = r'E:\study\ADB\verify\out\thresholds_independent.json'
T0 = 0
REPORT = []


def log(*a):
    print(*a, flush=True)


def check(name, cond, extra=None):
    REPORT.append({'check': name, 'passed': bool(cond), **(extra or {})})
    log(('PASS ' if cond else 'FAIL ') + name, '' if extra is None else extra)
    return bool(cond)


# ---- my own pi bounds (Machin) and sin bounds (Taylor) -------------------
def atan_inv_bounds(q, terms=90):
    s, x, x2, p = Fraction(0), Fraction(1, q), Fraction(1, q * q), Fraction(1, q)
    for k in range(terms):
        s += p / (2 * k + 1) if k % 2 == 0 else -p / (2 * k + 1)
        p *= x2
    nxt = p / (2 * terms + 1)
    return (s - nxt, s) if terms % 2 else (s, s + nxt)


_a5l, _a5u = atan_inv_bounds(5)
_a239l, _a239u = atan_inv_bounds(239, 30)
PI_L = 16 * _a5l - 4 * _a239u
PI_U = 16 * _a5u - 4 * _a239l


def sin_bounds(x, n=24):
    x = Fraction(x)
    s, term = Fraction(0), x
    for k in range(n + 1):
        if k:
            term *= -x * x / ((2 * k) * (2 * k + 1))
        s += term
    r = abs(x) ** (2 * n + 2) / factorial(2 * n + 2)
    return s - r, s + r


T = Fraction(814971, 6250000)
DELTA = Fraction(73891, 100000)
ALPHA = {2: Fraction(73891, 100000), 3: Fraction(57241, 50000),
         4: Fraction(161399, 100000), 5: Fraction(22523, 10000)}

kx = json.load(open(r'E:\study\ADB\verify\out\krawczyk.json', encoding='utf-8'))
box = {n: (Fraction(lo), Fraction(hi)) for n, (lo, hi) in zip(kx['variable_order'], kx['box'])}
rlo, rhi = box['r']

check('T1  r_* < 1/2', rhi < Fraction(1, 2), {'r_upper': float(rhi)})
check('T2  t_* = r_*^2 < T', rhi * rhi < T,
      {'t_upper': float(rhi * rhi), 'T': float(T)})
check('T3  8*Delta < 2*pi', 8 * DELTA < 2 * PI_L, {'8Delta': float(8 * DELTA), '2pi_lower': float(2 * PI_L)})
check('T4  4*Delta < pi', 4 * DELTA < PI_L, {'4Delta': float(4 * DELTA), 'pi_lower': float(PI_L)})

sl, su = sin_bounds(DELTA / 2)
check('T5  T < sin^2(Delta/2)', T < sl * sl, {'sin_lower': float(sl), 'T': float(T)})

ok = True
det = {}
for d, a in ALPHA.items():
    x = a / 2
    sl, su = sin_bounds(x)
    lhs = 4 * sl * sl
    rhs = Fraction(d * d) * T
    det[str(d)] = {'alpha': str(a), '4sin2_lower': float(lhs), 'd2T': float(rhs),
                   'margin': float(lhs - rhs)}
    if not (lhs > rhs):
        ok = False
        log(f'   T6 failed for d={d}: {float(lhs)} <= {float(rhs)}')
check('T6  4 sin^2(alpha_d/2) > d^2 T for d=2,3,4,5', ok, det)

out = {'verified': all(x['passed'] for x in REPORT), 'checks': REPORT,
       'pi_lower': str(PI_L), 'pi_upper': str(PI_U)}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(out, open(OUT, 'w', encoding='utf-8'), indent=1)
log('written', OUT)
log('ALL PASSED' if out['verified'] else 'SOME CHECK FAILED')
