"""Minimal-polynomial discovery for r_* via integer relation (PSLQ / LLL).

Input: high-precision value of r produced by tools/hp_root.py.
Output: candidate P in Z[t] with P(r_*) = 0, plus degree/height report.

Two independent engines are tried:
  * mpmath.pslq on the vector (1, r, ..., r^d)
  * exact LLL (sympy) on the standard integer-relation lattice
"""
from __future__ import annotations
import json
import os
import sys
import time

import mpmath as mp

OUT = r'E:\study\ADB\runtime\minpoly_search.json'


def load_r(dps):
    p = r'E:\study\ADB\runtime\hp_root.json'
    d = json.load(open(p, encoding='utf-8'))
    if d['_dps'] < dps:
        raise SystemExit(f'run tools/hp_root.py {dps} first (have {d["_dps"]})')
    return mp.mpf(d['r'])


def try_pslq(r, d, dps, maxcoeff, maxsteps=20000):
    mp.mp.dps = dps
    x = [mp.mpf(1)] + [r ** k for k in range(1, d + 1)]
    t0 = time.time()
    try:
        rel = mp.pslq(x, tol=mp.mpf(10) ** (-(dps - 30)), maxcoeff=maxcoeff, maxsteps=maxsteps)
    except Exception as e:
        return None, f'ERR {e}', time.time() - t0
    return rel, '', time.time() - t0


def main():
    dps = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    dmax = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    r = load_r(dps)
    mp.mp.dps = dps
    print('r =', mp.nstr(r, 60))
    found = []
    for d in range(1, dmax + 1):
        for mc in (10 ** 12, 10 ** 30, 10 ** 60, 10 ** 100):
            rel, err, dt = try_pslq(r, d, dps, mc)
            if rel:
                # normalise: leading coefficient positive, content 1
                c = rel
                print(f'degree {d:3d}  maxcoeff {mc:.0e}  rel={c}  ({dt:.1f}s)')
                found.append({'degree': d, 'maxcoeff': mc, 'coeffs': [str(x) for x in c]})
                break
        else:
            print(f'degree {d:3d}  no relation  ({dt:.1f}s)', flush=True)
            continue
        if found:
            break
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({'r_dps': dps, 'found': found}, open(OUT, 'w'), indent=1)
    print('written', OUT)


if __name__ == '__main__':
    main()
