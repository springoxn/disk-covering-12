"""High-precision numeric root of the 14-variable symmetric KKT system (1).

Independent of the VonEquinox bundle: we re-solve the system ourselves with
Newton iteration in mpmath arithmetic, starting from a low-precision seed that
we obtain from a coarse mpmath solve (seed only fixes the branch).

Usage:
    python tools/hp_root.py [dps] [outfile]
"""
from __future__ import annotations
import json
import os
import sys
import time

import mpmath as mp
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kkt_system import NAMES, system  # noqa: E402

SEED = {  # low precision branch selector (from the literature bundle, 17 digits)
    'r': '0.36110296374450862', 'u': '0.87734826325923987', 'v': '0.76916901916340508',
    'w': '0.27824166087442792', 'c': '0.93426105303324747', 's': '0.35658979904816057',
    'z': '1.7320508075688772', 'P': '0.042221980449500977', 'Q': '0.032453298593944031',
    'S': '0.024989338586798665', 'A': '0.011674392369520666', 'B': '0.011659921920093427',
    'C': '0.042257621388831254', 'D': '0.028368885012439986',
}


def build():
    X, f = system()
    J = sp.Matrix(f).jacobian(X)
    fl = sp.lambdify(X, f, modules='mpmath')
    Jl = sp.lambdify(X, J, modules='mpmath')
    return X, f, J, fl, Jl


def newton(fl, Jl, x, dps, iters=60, verbose=False):
    mp.mp.dps = dps
    X = mp.matrix(x)
    for it in range(iters):
        F = mp.matrix(fl(*X))
        Jm = mp.matrix(Jl(*X))
        try:
            dx = mp.lu_solve(Jm, -F)
        except Exception as e:  # singular at low precision
            raise RuntimeError(f'LU failed at iter {it}: {e}')
        X = X + dx
        nrm = max(abs(v) for v in dx)
        if verbose:
            print(f'  it {it:3d} step {mp.nstr(nrm, 5)}')
        if nrm < mp.mpf(10) ** (-(dps - 8)):
            break
    return X


def main():
    dps = int(sys.argv[1]) if len(sys.argv) > 1 else 250
    out = sys.argv[2] if len(sys.argv) > 2 else r'E:\study\ADB\runtime\hp_root.json'
    X, f, J, fl, Jl = build()
    t0 = time.time()
    # coarse stage
    mp.mp.dps = 40
    x0 = [mp.mpf(SEED[n]) for n in NAMES]
    x = newton(fl, Jl, x0, 60, iters=40)
    print('coarse residuals:', [mp.nstr(abs(v), 5) for v in mp.matrix(fl(*x))])
    # refine progressively
    for d in (120, dps):
        x = newton(fl, Jl, x, d, iters=40)
    res = [abs(v) for v in mp.matrix(fl(*x))]
    print('max |f| at dps', dps, ':', mp.nstr(max(res), 5))
    rec = {n: mp.nstr(v, dps - 5) for n, v in zip(NAMES, x)}
    rec['_dps'] = dps
    rec['_max_residual'] = mp.nstr(max(res), 10)
    rec['_seconds'] = time.time() - t0
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump(rec, fh, indent=1)
    print('r =', mp.nstr(x[0], 100))
    print('r^2 =', mp.nstr(x[0] ** 2, 100))
    print('written', out)


if __name__ == '__main__':
    main()
