"""Compute the minimal polynomial of r_* from the exact stage polynomials.

Steps
-----
1. load exact S1, S2 in Q[c,r] (from tools/elim_full.py --stage-only)
2. factor them over Q; select the irreducible factors that vanish at the
   certified numeric point (c_*, r_*)
3. F := the relevant factor of S2, G := the other relevant factor of S1
4. E(r) := Res_c(F, G)   -> E(r_*) = 0
5. factor E over Q, pick the irreducible factor with r_* as a root  ==  minimal
   polynomial of r_*
"""
from __future__ import annotations
import json
import os
import pickle
import sys
import time

import mpmath as mp
import sympy as sp

sys.path.insert(0, r'E:\study\ADB\tools')

c, r = sp.symbols('c r')
rec = json.load(open(r'E:\study\ADB\runtime\hp_root.json', encoding='utf-8'))
mp.mp.dps = 80
CV, RV = mp.mpf(rec['c']), mp.mpf(rec['r'])
T0 = time.time()


def log(*a):
    print(f'[{time.time()-T0:7.1f}s]', *a, flush=True)


def ev(e, subs=('c', 'r'), vals=(CV, RV)):
    f = sp.lambdify(subs, e, modules='mpmath')
    return abs(f(*vals))


def relevant_factors(e):
    fl = sp.factor_list(e, c, r)
    out = []
    for f, m in fl[1]:
        v = ev(f)
        if v is not None and v < mp.mpf('1e-40'):
            out.append((f, m, v))
    return fl[0], out


def main():
    d = pickle.load(open(r'E:\study\ADB\runtime\elim\stage_S_rat.pkl', 'rb'))
    S1 = sp.sympify(d['S1'], evaluate=False)
    S2 = sp.sympify(d['S2'], evaluate=False)
    log('stage loaded')
    c1, rel1 = relevant_factors(S1)
    log('S1 relevant:', [(sp.degree(f, c), sp.degree(f, r), mp.nstr(v, 3)) for f, m, v in rel1])
    c2, rel2 = relevant_factors(S2)
    log('S2 relevant:', [(sp.degree(f, c), sp.degree(f, r), mp.nstr(v, 3)) for f, m, v in rel2])

    assert rel2, 'no relevant factor in S2'
    F, mF, vF = max(rel2, key=lambda t: sp.degree(t[0], c))
    log('F (from S2): deg_c', sp.degree(F, c), 'deg_r', sp.degree(F, r), 'mult', mF)
    others = [t for t in rel1 if sp.simplify(t[0] - F) != 0 and sp.expand(t[0] - F) != 0]
    assert others, 'no second relevant factor in S1'
    G, mG, vG = max(others, key=lambda t: sp.degree(t[0], c))
    log('G (from S1): deg_c', sp.degree(G, c), 'deg_r', sp.degree(G, r), 'mult', mG)

    with open(r'E:\study\ADB\runtime\elim\FG.pkl', 'wb') as fh:
        pickle.dump({'F': sp.srepr(F), 'G': sp.srepr(G)}, fh)

    log('resultant Res_c(F,G) ...')
    E = sp.resultant(sp.Poly(F, c, r), sp.Poly(G, c, r), c)
    E = sp.expand(E)
    log('E degree', sp.Poly(E, r).degree(), 'ops', sp.count_ops(E))
    with open(r'E:\study\ADB\runtime\elim\E_from_FG.pkl', 'wb') as fh:
        pickle.dump({'E': sp.srepr(E)}, fh)

    log('factoring E ...')
    fl = sp.factor_list(E, r)
    log('E = content * factors:', fl[0], [sp.degree(f, r) for f, m in fl[1]])
    cands = []
    for f, m in fl[1]:
        v = ev(f, ('r',), (RV,))
        log('   factor deg', sp.degree(f, r), 'mult', m, '|f(r_*)|', mp.nstr(v, 5))
        if v < mp.mpf('1e-40'):
            cands.append((f, m, v))
    assert len(cands) == 1, f'expected exactly one vanishing factor, got {len(cands)}'
    P0 = cands[0][0]
    # normalise: primitive, positive leading coefficient
    P = sp.Poly(P0, r)
    cont, prim = P.primitive()
    if sp.LC(prim) < 0:
        prim = -prim
    P = sp.Poly(prim, r)
    log('P(r) candidate: degree', P.degree(), 'height', max(abs(int(x)) for x in P.all_coeffs()))
    out = {
        'F': sp.srepr(F), 'G': sp.srepr(G),
        'E_degree': sp.Poly(E, r).degree(),
        'P_degree': P.degree(),
        'P_coeffs_desc': [int(x) for x in P.all_coeffs()],
        'P': sp.srepr(P.as_expr()),
        'P_tex': sp.latex(P.as_expr()),
    }
    os.makedirs(r'E:\study\ADB\runtime\elim', exist_ok=True)
    with open(r'E:\study\ADB\runtime\minpoly_candidate.json', 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1)
    log('saved runtime/minpoly_candidate.json')
    print('P(r) =', P.as_expr())


if __name__ == '__main__':
    main()
