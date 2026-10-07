"""Independent re-verification of the 131 non-candidate graph-energy certificates.

This is my own implementation of the *definitions* given in
docs/RESULT.md section 4.1 (and in the third-party proof, sections 6-7); no
function from the third-party bundle is imported.

For every non-candidate residual topology stored in
    lit/DiskCoveringSolve/cover12/proof_bundle/residual_energy_cert_safe.json
it

  1. rebuilds the anchor/centre/face-witness graph from the triangulation and
     the edge weights `wnum` (sum = QW);
  2. performs the exact rational star-mesh (Kron) elimination itself and checks
     that every stored conductance `dnum` is a valid *lower* bound
     (dnum/QD <= D_ij);
  3. reconstructs the branch-and-bound box tree from `nodes`;
  4. for every leaf recomputes an exact rational lower bound of
        E_w(g) = sum_pairs 2 c_ij (1 - cos(theta_j - theta_i))
     using a *tangent-line* minorant of 1 - cos (valid by convexity on
     [0, Delta], Delta < pi/2) with my own rational Taylor bounds for sin/cos
     and my own Machin-series rational bounds for pi, and checks
        E_w(g) >= T = 814971/6250000  >  r_*^2
     for every g in the leaf box with sum(g) = 2 pi.

Everything is integer / Fraction arithmetic.
"""
from __future__ import annotations
import json
import os
import pickle
import sys
import time
from fractions import Fraction
from math import factorial

ROOT = r'E:\study\ADB\lit\DiskCoveringSolve\cover12\proof_bundle'
OUT = r'E:\study\ADB\verify\out\energy_independent.json'
T0 = time.time()
TARGET = Fraction(814971, 6250000)          # T = 0.13039536 > r_*^2
DELTA = Fraction(73891, 100000)
QW = 10 ** 15
QD = 10 ** 18
CANDIDATE = (9, 3, 21015)


def log(*a):
    print(f'[{time.time()-T0:7.1f}s]', *a, flush=True)


# --------------------------------------------------------------------------
# my own rational pi bounds (Machin) and sin/cos Taylor bounds
# --------------------------------------------------------------------------
def atan_inv_bounds(q: int, terms: int = 80):
    s = Fraction(0)
    x = Fraction(1, q)
    x2 = x * x
    p = x
    for k in range(terms):
        s += p / (2 * k + 1) if k % 2 == 0 else -p / (2 * k + 1)
        p *= x2
    nxt = p / (2 * terms + 1)
    if terms % 2 == 1:
        return s - nxt, s
    return s, s + nxt


_a5l, _a5u = atan_inv_bounds(5, 80)
_a239l, _a239u = atan_inv_bounds(239, 25)
PI_L = 16 * _a5l - 4 * _a239u
PI_U = 16 * _a5u - 4 * _a239l
TWO_PI_L, TWO_PI_U = 2 * PI_L, 2 * PI_U


def sincos_bounds(x: Fraction, n: int = 12):
    """Rigorous rational enclosure of (sin x, cos x) by Taylor + remainder.

    Boxes have |x| <= Delta = 0.73891 < pi/2, so n = 12 already gives a
    remainder below 1e-24 while keeping the rationals small.
    """
    x = Fraction(x)
    ax = abs(x)
    s = Fraction(0)
    term = x
    for k in range(n + 1):
        if k:
            term *= -x * x / ((2 * k) * (2 * k + 1))
        s += term
    rs = ax ** (2 * n + 2) / factorial(2 * n + 2)
    c = Fraction(0)
    term = Fraction(1)
    for k in range(n + 1):
        if k:
            term *= -x * x / ((2 * k - 1) * (2 * k))
        c += term
    rc = ax ** (2 * n + 1) / factorial(2 * n + 1)
    return (s - rs, s + rs, c - rc, c + rc)


_LM_CACHE = {}


def cos_lower_on(l: Fraction, u: Fraction):
    """Rigorous lower bound for min_{[l,u]} cos, using 0 <= l <= u <= 2*pi.

    cos decreases on [0,pi] and increases on [pi,2*pi]; my own rational bounds
    PI_L < pi < PI_U are used.
    """
    if u <= PI_L:
        return sincos_bounds(u)[2]
    if l >= PI_U:
        return sincos_bounds(l)[2]
    return Fraction(-1)


def line_minorant(l: Fraction, u: Fraction):
    """Affine L(x) = A x + B <= 1 - cos x for every x in [l, u].

    Taylor with the Lagrange remainder: for x = a + d, |d| <= h,
        1 - cos(a+d) = (1 - cos a) + sin(a) d + cos(xi) d^2 / 2 ,
    and with sin a in [sl,su], cos a <= cu, cos(xi) >= m this gives
        1 - cos x >= (1 - cu) + A d - eps h + min(0, m) h^2 / 2 =: A x + B ,
    A = (sl+su)/2, eps = (su-sl)/2.  Valid for *any* interval, including those
    crossing pi (where 1 - cos is not convex).
    """
    key = (l, u)
    v = _LM_CACHE.get(key)
    if v is not None:
        return v
    a = (l + u) / 2
    h = (u - l) / 2
    sl, su, cl, cu = sincos_bounds(a)
    A = (sl + su) / 2
    eps = (su - sl) / 2
    m = cos_lower_on(l, u)
    q = min(Fraction(0), m) * h * h / 2
    B = (1 - cu) - A * a - eps * h + q
    res = (A, B)
    if len(_LM_CACHE) < 400000:
        _LM_CACHE[key] = res
    return res


# --------------------------------------------------------------------------
# my own star-mesh (Kron) elimination
# --------------------------------------------------------------------------
def build_graph(B, I, faces):
    """Vertices: anchors 0..B-1, centres B..B+B+I-1, face witnesses after."""
    ncent = B + I
    n = B + ncent + len(faces)
    edges = []
    for i in range(B):
        edges.append((i, B + i))
        edges.append((i, B + (i + 1) % B))
    for k, f in enumerate(faces):
        p = B + ncent + k
        for v in f:
            edges.append((p, B + v))
    return n, edges


def kron_conductances(B, I, faces, wnum, den=QW):
    """Exact star-mesh elimination; returns D_ij for all anchor pairs i<j."""
    n, edges = build_graph(B, I, faces)
    assert len(wnum) == len(edges), (len(wnum), len(edges))
    assert min(wnum) >= 0 and sum(wnum) == den
    adj = {v: {} for v in range(n)}

    def add(a, b, w):
        if a == b or w == 0:
            return
        adj[a][b] = adj[a].get(b, Fraction(0)) + w
        adj[b][a] = adj[b].get(a, Fraction(0)) + w
    for (a, b), zz in zip(edges, wnum):
        add(a, b, Fraction(zz, den))
    # drop components without an anchor
    anchors = set(range(B))
    seen, keep = set(), set(anchors)
    for s in range(n):
        if s in seen:
            continue
        stack, comp, has = [s], [], False
        seen.add(s)
        while stack:
            vv = stack.pop()
            comp.append(vv)
            has |= vv in anchors
            for w2 in adj[vv]:
                if w2 not in seen:
                    seen.add(w2)
                    stack.append(w2)
        if has:
            keep.update(comp)
    for vv in list(adj):
        if vv not in keep:
            for w2 in list(adj[vv]):
                adj[w2].pop(vv, None)
            del adj[vv]
    # eliminate every non-anchor vertex
    for vv in range(B, n):
        if vv not in adj:
            continue
        nei = list(adj[vv].items())
        S = sum((w2 for _, w2 in nei), Fraction(0))
        if S == 0:
            del adj[vv]
            continue
        for x in range(len(nei)):
            a, wa = nei[x]
            for y in range(x + 1, len(nei)):
                b, wb = nei[y]
                add(a, b, wa * wb / S)
        for a, _ in nei:
            adj[a].pop(vv, None)
        del adj[vv]
    return [2 * adj[i].get(j, Fraction(0)) for i in range(B) for j in range(i + 1, B)]


# --------------------------------------------------------------------------
# box arithmetic and the LP lower bound
# --------------------------------------------------------------------------
def tighten(lo, hi, L=TWO_PI_L, U=TWO_PI_U):
    lo, hi = list(map(Fraction, lo)), list(map(Fraction, hi))
    for _ in range(64):
        sl, sh = sum(lo, Fraction(0)), sum(hi, Fraction(0))
        if sh < L or sl > U:
            return None
        ch = False
        for i in range(len(lo)):
            nl = L - (sh - hi[i])
            nh = U - (sl - lo[i])
            if nl > lo[i]:
                lo[i] = nl
                ch = True
            if nh < hi[i]:
                hi[i] = nh
                ch = True
            if lo[i] > hi[i]:
                return None
        if not ch:
            break
    return lo, hi


def pair_intervals(lo, hi, pairs, L=TWO_PI_L, U=TWO_PI_U):
    sl, sh = sum(lo, Fraction(0)), sum(hi, Fraction(0))
    out = []
    for i, j in pairs:
        ml0 = sum(lo[i:j], Fraction(0))
        mh0 = sum(hi[i:j], Fraction(0))
        ml = max(ml0, L - (sh - mh0))
        mh = min(mh0, U - (sl - ml0))
        assert ml <= mh
        out.append((ml, mh))
    return out


def linear_min(c, lo, hi, L=TWO_PI_L, U=TWO_PI_U):
    n = len(c)
    x = [hi[i] if c[i] < 0 else lo[i] for i in range(n)]
    v = sum((c[i] * x[i] for i in range(n)), Fraction(0))
    S = sum(x, Fraction(0))
    if S < L:
        need = L - S
        for i in sorted(range(n), key=lambda z: c[z]):
            d = min(hi[i] - x[i], need)
            v += c[i] * d
            x[i] += d
            need -= d
            if need == 0:
                break
        assert need == 0
    elif S > U:
        need = S - U
        for i in sorted(range(n), key=lambda z: c[z], reverse=True):
            d = min(x[i] - lo[i], need)
            v -= c[i] * d
            x[i] -= d
            need -= d
            if need == 0:
                break
        assert need == 0
    return v


def leaf_bound(lo, hi, pairs, row):
    z = tighten(lo, hi)
    if z is None:
        return None
    lo, hi = z
    lines = [line_minorant(l, u) for l, u in pair_intervals(lo, hi, pairs)]
    c = [Fraction(0)] * len(lo)
    b = Fraction(0)
    for n, (i, j), (A, B) in zip(row, pairs, lines):
        q = Fraction(int(n), QD)
        b += q * B
        for k in range(i, j):
            c[k] += q * A
    return b + linear_min(c, lo, hi)


def parse_box(nodes, B):
    boxes = [None] * len(nodes)
    boxes[0] = ((Fraction(0),) * B, (DELTA,) * B)
    leaves = []
    for i, nd in enumerate(nodes):
        assert boxes[i] is not None
        lo, hi = boxes[i]
        if 'split' in nd:
            k = int(nd['split'])
            m = (lo[k] + hi[k]) / 2
            for side, ch in enumerate(nd['child']):
                l, h = list(lo), list(hi)
                if side == 0:
                    h[k] = m
                else:
                    l[k] = m
                assert boxes[int(ch)] is None
                boxes[int(ch)] = (tuple(l), tuple(h))
        elif 'leaf' in nd:
            leaves.append(i)
        elif 'empty' in nd:
            pass
        else:
            raise AssertionError(nd)
    return boxes, leaves


def main():
    cert = json.load(open(ROOT + r'\residual_energy_cert_safe.json', encoding='utf-8'))
    assert Fraction(*cert['target']) == TARGET
    assert Fraction(*cert['delta']) == DELTA
    metric = json.load(open(ROOT + r'\metric_exact_cert_safe.json', encoding='utf-8'))
    expected = {}
    for key, blk in metric['cases'].items():
        B, I = map(int, key.split(','))
        reps = pickle.load(open(rf'{ROOT}\triangulations_B{B}_I{I}_orbits.pkl', 'rb'))
        for idx in blk['residual_indices']:
            if (B, I, int(idx)) != CANDIDATE:
                expected[(B, I, int(idx))] = [list(f) for f in reps[int(idx)]]
    actual = {(z['B'], z['I'], z['idx']): z['faces'] for z in cert['topologies']}
    log('topologies in certificate:', len(actual), ' expected 131 residual non-candidate:',
        len(expected), ' match:', actual == expected)
    assert actual == expected and len(actual) == 131

    min_margin = None
    tot_nodes = tot_leaves = 0
    for zi, z in enumerate(cert['topologies']):
        tz = time.time()
        B, I = z['B'], z['I']
        faces = [tuple(f) for f in z['faces']]
        pairs = [(i, j) for i in range(B) for j in range(i + 1, B)]
        assert z['qweight'] == QW and z['qcoef'] == QD
        rows = []
        for rec in z['records']:
            w = list(map(int, rec['wnum']))
            assert min(w) >= 0 and sum(w) == QW
            D = kron_conductances(B, I, faces, w)
            stored = list(map(int, rec['dnum']))
            assert len(stored) == len(D)
            for n, q in zip(stored, D):
                assert Fraction(n, QD) <= q, 'stored conductance is not a lower bound'
            rows.append(stored)
        boxes, leaves = parse_box(z['nodes'], B)
        # structural completeness: recursively splitting the root box
        # [0,Delta]^B means the leaves plus the empty nodes cover the whole cube,
        # hence the whole gap polytope {0 <= g <= Delta, sum g = 2 pi}.
        for i, nd in enumerate(z['nodes']):
            if 'split' in nd:
                ch = nd['child']
                assert len(ch) == 2 and all(c is not None for c in ch), 'split without two children'
                assert int(ch[0]) != int(ch[1]), 'split with identical children'
            elif 'leaf' in nd or 'empty' in nd:
                pass
            else:
                raise AssertionError(f'unknown node type {nd}')
        assert 'split' in z['nodes'][0] or 'leaf' in z['nodes'][0] or 'empty' in z['nodes'][0]
        cnt = 0
        for i in leaves:
            ri = int(z['nodes'][i]['leaf'])
            v = leaf_bound(*boxes[i], pairs, rows[ri])
            assert v is not None and v >= TARGET, (B, I, z['idx'], i, float(v - TARGET))
            mar = v - TARGET
            min_margin = mar if min_margin is None or mar < min_margin else min_margin
            cnt += 1
        for i, nd in enumerate(z['nodes']):
            if 'empty' in nd:
                assert tighten(*boxes[i]) is None, 'stored empty node is actually feasible'
        tot_nodes += len(z['nodes'])
        tot_leaves += len(leaves)
        log(f'  [{zi+1:3d}/131] (B,I)=({B},{I}) idx {z["idx"]:6d}: nodes {len(z["nodes"]):5d} '
            f'leaves {cnt:4d}  {time.time()-tz:.1f}s')
    log(f'ALL {len(cert["topologies"])} topologies verified: nodes {tot_nodes}, leaves {tot_leaves}')
    log('minimum exact margin over leaves:', float(min_margin))
    out = {'verified': True, 'topologies': len(cert['topologies']), 'nodes': tot_nodes,
           'leaves': tot_leaves, 'min_margin_float': float(min_margin),
           'tree_structure_checked': True,
           'target': str(TARGET), 'pi_lower_bound': str(PI_L), 'pi_upper_bound': str(PI_U)}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, 'w', encoding='utf-8'), indent=1)
    log('written', OUT)


if __name__ == '__main__':
    main()
