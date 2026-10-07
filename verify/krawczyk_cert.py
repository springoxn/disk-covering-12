"""Independent Krawczyk certification of the symmetric KKT root.

If  K(X) := x0 - Y F(x0) + (I - Y J(X)) (X - x0)  satisfies  K(X) c int(X)
then F has a root in X; if in addition ||I - Y J(X)||_inf < 1 the root is unique
in X.

All interval work uses exact rational arithmetic (verify/interval.py); no
floating point enters the certificate.

Usage:  python verify/krawczyk_cert.py [rho_digits]
"""
from __future__ import annotations
import json
import os
import sys
import time
from fractions import Fraction

import mpmath as mp
import sympy as sp

sys.path.insert(0, r'E:\study\ADB\tools')
sys.path.insert(0, r'E:\study\ADB\verify')
from kkt_system import NAMES, system  # noqa: E402
from interval import Iv, iv_eval  # noqa: E402

OUT = r'E:\study\ADB\verify\out\krawczyk.json'
os.makedirs(os.path.dirname(OUT), exist_ok=True)
T0 = time.time()


def log(*a):
    print(f'[{time.time()-T0:7.1f}s]', *a, flush=True)


def main():
    rho_digits = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    rec = json.load(open(r'E:\study\ADB\runtime\hp_root_1000.json', encoding='utf-8'))
    D = 900
    Q = 10 ** D
    mp.mp.dps = D + 60
    x0 = [Fraction(int(mp.floor(mp.mpf(rec[n]) * Q) + mp.mpf('0.5')), Q) for n in NAMES]
    log('centre rationalised with', D, 'decimals')

    X, f = system()
    J = sp.Matrix(f).jacobian(X)
    log('system and Jacobian built')

    x0v = [mp.mpf(v.numerator) / v.denominator for v in x0]
    Jl = sp.lambdify(X, J, modules='mpmath')
    fl = sp.lambdify(X, f, modules='mpmath')
    Jnum = mp.matrix(Jl(*x0v))
    fnum = mp.matrix(fl(*x0v))
    log('numeric |F(x0)|_inf =', mp.nstr(max(abs(v) for v in fnum), 5))
    Ynum = Jnum ** -1
    resid = mp.matrix(14, 14)
    for i in range(14):
        for j in range(14):
            resid[i, j] = (1 if i == j else 0) - sum(Ynum[i, k] * Jnum[k, j] for k in range(14))
    log('numeric ||I - Y J(x0)||_inf =',
        mp.nstr(max(abs(resid[i, j]) for i in range(14) for j in range(14)), 5))

    Yq = 10 ** (D)
    Y = [[Fraction(int(mp.floor(Ynum[i, j] * Yq + mp.mpf('0.5'))), Yq) for j in range(14)]
         for i in range(14)]
    log('Y rationalised')

    rho = Fraction(1, 10 ** rho_digits)
    Xiv = [Iv.box(x0[i], rho) for i in range(14)]
    sub = {s: Xiv[i] for i, s in enumerate(X)}

    # ---- F(x0) exactly (rational)
    xsub = {s: x0[i] for i, s in enumerate(X)}
    fx0 = []
    for e in f:
        t = sp.together(e.subs(xsub))
        fx0.append(Fraction(int(sp.numer(t)), int(sp.denom(t))))
    log('F(x0) exact, max |F| =', float(max(abs(v) for v in fx0)))

    # ---- interval Jacobian over X
    Jiv = [[iv_eval(J[i, j], sub) for j in range(14)] for i in range(14)]
    log('interval Jacobian over X computed')

    YF = [sum((Y[i][k] * fx0[k] for k in range(14)), Fraction(0)) for i in range(14)]
    E = [[Iv(0, 0) for _ in range(14)] for _ in range(14)]
    for i in range(14):
        for j in range(14):
            s = Iv(0, 0)
            for k in range(14):
                s = s + Iv.point(Y[i][k]) * Jiv[k][j]
            E[i][j] = Iv.point(1 if i == j else 0) - s
    dx = [Iv(-rho, rho) for _ in range(14)]
    K = []
    for i in range(14):
        s = Iv.point(x0[i] - YF[i])
        for j in range(14):
            s = s + E[i][j] * dx[j]
        K.append(s)
    ok = all(K[i].inside_strict(Xiv[i]) for i in range(14))
    enorm = max(max(abs(E[i][j].lo), abs(E[i][j].hi)) for i in range(14) for j in range(14))
    log('K(X) subset of int(X):', ok)
    log('||I - Y J(X)||_inf <=', float(enorm), ' (<1:', enorm < 1, ')')
    log('max |K_i - x0_i| <=', float(max(max(abs(K[i].lo - x0[i]), abs(K[i].hi - x0[i])) for i in range(14))))

    out = {
        'rho_digits': rho_digits,
        'rationalisation_digits': D,
        'krawczyk_containment': bool(ok),
        'contraction_inf_norm_upper': str(enorm),
        'contraction_lt_one': bool(enorm < 1),
        'unique_root_in_box': bool(ok and enorm < 1),
        'x_center': [str(v) for v in x0],
        'rho': str(rho),
        'variable_order': NAMES,
        'box': [[str(Xiv[i].lo), str(Xiv[i].hi)] for i in range(14)],
    }
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1)
    log('written', OUT)
    if not (ok and enorm < 1):
        raise SystemExit('Krawczyk certificate FAILED')


if __name__ == '__main__':
    main()
