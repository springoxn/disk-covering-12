"""Independent verification of the candidate global-convexity certificate.

Definitions (proof sections 1 and 8):

  * the candidate's active graph has the seven stress orbits (P,Q,S,A,B,C,D)
    distributed as
        anchors  i -> c_i      weight pat[i][0]
        anchors  i -> c_{i+1}  weight pat[i][1],   pat = [(P,Q),(S,S),(Q,P)]*3
        generic active faces (1,2,11),(4,5,9),(7,8,10):
            outer centre edge weight A, inner centre edge weight B
        axial active faces (0,10,11),(3,9,11),(6,9,10):
            outer centre edge weight C, inner centre edge weight D
  * star-mesh eliminating the six witnesses and the twelve centres gives
    conductances kappa_ij between anchors i<j;
  * the Hessian of the Dirichlet energy on the nine anchor angles is
        H = sum_{i<j} 2 kappa_ij cos(theta_j - theta_i) (e_i-e_j)(e_i-e_j)^T ,
    and on the gap polytope 0 <= g_i <= Delta, sum g_i = 2 pi the circular
    distance satisfies |theta_j - theta_i| <= d(i,j) Delta with
    d(i,j) = min(|i-j|, 9-|i-j|) <= 4, hence
        H >= H0 = sum_{i<j} 2 kappa_ij cos_lower(d(i,j) Delta) (e_i-e_j)(e_i-e_j)^T
    (using the upper end of the kappa interval when that cosine is negative).

The certificate is:  every LDL^T pivot of H0 with one coordinate deleted is
strictly positive, so the energy is strictly convex on the polytope and the
candidate gap vector is its unique minimiser.

This script recomputes everything with my own interval kernel, my own
star-mesh elimination, my own rational pi/sin/cos bounds and my own exact
rational LDL^T.
"""
from __future__ import annotations
import json
import os
import sys
import time
from fractions import Fraction
from math import factorial

sys.path.insert(0, r'E:\study\ADB\verify')
from interval import Iv  # noqa: E402

sys.set_int_max_str_digits(400000)

OUT = r'E:\study\ADB\verify\out\convexity_independent.json'
T0 = time.time()
DELTA = Fraction(73891, 100000)


def log(*a):
    print(f'[{time.time()-T0:7.1f}s]', *a, flush=True)


# ---- my own pi and cos lower bounds -------------------------------------
def atan_inv_bounds(q, terms=80):
    s, x, x2, p = Fraction(0), Fraction(1, q), Fraction(1, q * q), Fraction(1, q)
    for k in range(terms):
        s += p / (2 * k + 1) if k % 2 == 0 else -p / (2 * k + 1)
        p *= x2
    nxt = p / (2 * terms + 1)
    return (s - nxt, s) if terms % 2 else (s, s + nxt)


_a5l, _a5u = atan_inv_bounds(5)
_a239l, _a239u = atan_inv_bounds(239, 25)
PI_L = 16 * _a5l - 4 * _a239u
PI_U = 16 * _a5u - 4 * _a239l


def cos_bounds(x, n=16):
    x = Fraction(x)
    ax = abs(x)
    c, term = Fraction(0), Fraction(1)
    for k in range(n + 1):
        if k:
            term *= -x * x / ((2 * k - 1) * (2 * k))
        c += term
    r = ax ** (2 * n + 1) / factorial(2 * n + 1)
    return c - r, c + r


def cos_lower(x):
    """Lower bound of cos on [0,x] for 0 <= x <= 2pi."""
    x = Fraction(x)
    if x <= PI_L:
        return cos_bounds(x)[0]
    if x >= PI_U:
        return cos_bounds(x)[0]
    return Fraction(-1)


# ---- star-mesh elimination on the candidate active graph ----------------
def build_kron(W):
    A = [f'q{i}' for i in range(9)]
    Cc = [f'c{i}' for i in range(12)]
    Pp = [f'p{i}' for i in range(6)]
    adj = {v: {} for v in A + Cc + Pp}

    def add(a, b, w):
        if a == b:
            return
        adj[a][b] = adj[a].get(b, Iv(0)) + w
        adj[b][a] = adj[b].get(a, Iv(0)) + w

    pat = [('P', 'Q'), ('S', 'S'), ('Q', 'P')] * 3
    for i, (x, y) in enumerate(pat):
        add(f'q{i}', f'c{i}', W[x])
        add(f'q{i}', f'c{(i+1)%9}', W[y])
    faces = [(1, 2, 11), (4, 5, 9), (7, 8, 10), (0, 10, 11), (3, 9, 11), (6, 9, 10)]
    for k, fa in enumerate(faces):
        for cc in fa:
            typ = ('B' if cc >= 9 else 'A') if k < 3 else ('D' if cc >= 9 else 'C')
            add(f'p{k}', f'c{cc}', W[typ])
    for v in Pp + Cc:
        ne = list(adj[v].items())
        S = Iv(0)
        for _, z in ne:
            S = S + z
        assert S.lo > 0
        for i in range(len(ne)):
            a, x = ne[i]
            for j in range(i + 1, len(ne)):
                b, y = ne[j]
                add(a, b, x * y / S)
        for a, _ in ne:
            adj[a].pop(v, None)
        del adj[v]
    return {(i, j): adj[f'q{i}'].get(f'q{j}', Iv(0)) for i in range(9) for j in range(i + 1, 9)}


def ldl_pivots(M):
    """Exact rational LDL^T; returns the diagonal pivots (asserts positivity)."""
    n = len(M)
    L = [[Fraction(0)] * n for _ in range(n)]
    D = [Fraction(0)] * n
    for i in range(n):
        L[i][i] = Fraction(1)
        for j in range(i):
            L[i][j] = (M[i][j] - sum((L[i][k] * D[k] * L[j][k] for k in range(j)), Fraction(0))) / D[j]
        D[i] = M[i][i] - sum((L[i][k] * L[i][k] * D[k] for k in range(i)), Fraction(0))
        assert D[i] > 0, f'pivot {i} is not positive: {float(D[i])}'
    return D


def main():
    kx = json.load(open(r'E:\study\ADB\verify\out\krawczyk.json', encoding='utf-8'))
    names = kx['variable_order']
    # Outward-round the certified box to 10^-40 so that the exact rational
    # arithmetic stays tractable.  Widening an enclosure is always sound.
    Q = 10 ** 40
    box = {}
    for n, (lo, hi) in zip(names, kx['box']):
        a, b = Fraction(lo), Fraction(hi)
        box[n] = Iv(Fraction(a.numerator * Q // a.denominator, Q),
                    Fraction(-((-b.numerator * Q) // b.denominator), Q))
    W = {k: box[k] for k in ('P', 'Q', 'S', 'A', 'B', 'C', 'D')}
    log('box loaded (outward-rounded to 1e-40); weights:',
        {k: (float(W[k].lo), float(W[k].hi)) for k in W})

    K = build_kron(W)
    for k, v in K.items():
        assert v.lo >= 0, 'negative conductance'
    log('Kron conductances computed:', len(K), 'pairs; min lower',
        float(min(v.lo for v in K.values())))

    coslo = {d: cos_lower(d * DELTA) for d in range(1, 5)}
    log('cos lower bounds cos(d*Delta):', {d: float(c) for d, c in coslo.items()})
    assert coslo[1] > 0 and coslo[2] > 0 and coslo[3] < 0 and coslo[4] < 0

    H = [[Fraction(0)] * 9 for _ in range(9)]
    for (i, j), kap in K.items():
        d = min(j - i, 9 - j + i)
        cl = coslo[d]
        kapc = kap.lo if cl >= 0 else kap.hi
        a = 2 * kapc * cl
        H[i][i] += a
        H[j][j] += a
        H[i][j] -= a
        H[j][i] -= a
    # delete the first coordinate (removes the global rotation direction)
    M = [row[1:] for row in H[1:]]
    piv = ldl_pivots(M)
    log('LDL^T pivots (all must be positive):', [float(p) for p in piv])
    out = {
        'verified': True,
        'method': 'independent star-mesh + rational LDL^T',
        'delta': str(DELTA),
        'cos_lower_d1_d4': {str(d): str(c) for d, c in coslo.items()},
        'min_conductance_lower': float(min(v.lo for v in K.values())),
        'max_conductance_width': float(max(v.width() for v in K.values())),
        'ldl_pivots': [str(p) for p in piv],
        'min_ldl_pivot': float(min(piv)),
        'pi_lower': str(PI_L),
        'pi_upper': str(PI_U),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, 'w', encoding='utf-8'), indent=1)
    log('written', OUT)


if __name__ == '__main__':
    main()
