"""Independent re-verification of the first-layer Farkas exclusion certificates.

This is my own implementation (not a call into the third-party verifier).  It

  1. re-validates every stored triangulation orbit and recomputes orbit sizes,
     checking that they sum to Brown's closed-form count;
  2. rebuilds the auxiliary graph, the anchor-distance matrix D and the angle-gap
     constraint system from the definitions in docs/RESULT.md section 4.1;
  3. checks every stored Farkas multiplier exactly:
        sum_j lam_j * row_j[i] >= 1   for all i,
        cost = sum_j (lam_j/Q) * alpha_{d_j}  <  2*pi_L .
  4. checks that the residual set is exactly the set of orbits without a
     certificate.

All arithmetic is integer / Fraction; 2*pi is bounded below by the rational
PILOW (a truncated 15-digit value of 2*pi, hence certainly a lower bound).
"""
from __future__ import annotations
import itertools
import json
import math
import pickle
import sys
import time
from collections import defaultdict, deque
from fractions import Fraction

ROOT = r'E:\study\ADB\lit\DiskCoveringSolve\cover12\proof_bundle'
CERT = ROOT + r'\metric_exact_cert_safe.json'
CASES = [(9, 1), (9, 2), (9, 3), (10, 1), (10, 2), (11, 1)]
PILOW = Fraction(314159265358979, 10 ** 14)      # 3.14159265358979 < pi
TWOPILOW = 2 * PILOW
ALPHA = {2: Fraction(73891, 100000), 3: Fraction(57241, 50000),
         4: Fraction(161399, 100000), 5: Fraction(22523, 10000)}
DELTA = Fraction(73891, 100000)
Q = 10 ** 12
T0 = time.time()


def log(*a):
    print(f'[{time.time()-T0:7.1f}s]', *a, flush=True)


def canon_face(f):
    return tuple(sorted(map(int, f)))


def canon_state(fs):
    return tuple(sorted(canon_face(f) for f in fs))


def transform_state(s, B, I, shift, reflect, perm):
    def mp(x):
        return ((-x if reflect else x) + shift) % B if x < B else B + perm[x - B]
    return canon_state(tuple(mp(x) for x in f) for f in s)


def orbit_set(s, B, I):
    return {transform_state(s, B, I, sh, refl, p)
            for refl in (False, True) for sh in range(B)
            for p in (itertools.permutations(range(I)) if I else [()])}


def valid_disk_triangulation(s, B, I):
    """Own implementation of the 'simple disk triangulation' check."""
    s = canon_state(s)
    V, nf = B + I, B + 2 * I - 2
    ne = 2 * B + 3 * I - 3
    if len(s) != nf or len(set(s)) != len(s):
        return False
    if any(len(set(f)) < 3 or min(f) < 0 or max(f) >= V for f in s):
        return False
    if set(x for f in s for x in f) != set(range(V)):
        return False
    ec, ef = defaultdict(int), defaultdict(list)
    for fi, (a, b, c) in enumerate(s):
        for x, y in ((a, b), (a, c), (b, c)):
            e = tuple(sorted((x, y)))
            ec[e] += 1
            ef[e].append(fi)
    if len(ec) != ne:
        return False
    bnd = {tuple(sorted((i, (i + 1) % B))) for i in range(B)}
    for e, n in ec.items():
        if e in bnd:
            if n != 1:
                return False
        elif n != 2:
            return False
    if any(ec.get(e, 0) != 1 for e in bnd):
        return False
    adj = [set() for _ in s]
    for e, ff in ef.items():
        if len(ff) == 2:
            adj[ff[0]].add(ff[1])
            adj[ff[1]].add(ff[0])
    seen, stack = {0}, [0]
    while stack:
        q = stack.pop()
        for z in adj[q]:
            if z not in seen:
                seen.add(z)
                stack.append(z)
    if len(seen) != len(s):
        return False
    for x in range(V):
        ladj, ledges = defaultdict(set), set()
        for f in s:
            if x not in f:
                continue
            a, b = [q for q in f if q != x]
            e = tuple(sorted((a, b)))
            if e in ledges:
                return False
            ledges.add(e)
            ladj[a].add(b)
            ladj[b].add(a)
        if not ladj:
            return False
        root = next(iter(ladj))
        vis, st = {root}, [root]
        while st:
            q = st.pop()
            for z in ladj[q]:
                if z not in vis:
                    vis.add(z)
                    st.append(z)
        if len(vis) != len(ladj):
            return False
        deg = {q: len(z) for q, z in ladj.items()}
        if x < B:
            if {q for q, d in deg.items() if d == 1} != {(x - 1) % B, (x + 1) % B}:
                return False
            if any(d not in (1, 2) for d in deg.values()):
                return False
        elif any(d != 2 for d in deg.values()):
            return False
    return V - len(ec) + len(s) == 1


def brown_labeled(B, I):
    m, n = B - 3, I
    num = 2 * math.factorial(2 * m + 3) * math.factorial(4 * n + 2 * m + 1) * math.factorial(I)
    den = math.factorial(m + 2) * math.factorial(m) * math.factorial(n) * math.factorial(3 * n + 2 * m + 3)
    assert num % den == 0
    return num // den


def graph(B, I, faces):
    ncent = B + I
    n = B + ncent + len(faces)
    adj = [[] for _ in range(n)]

    def add(a, b):
        adj[a].append(b)
        adj[b].append(a)
    for i in range(B):
        add(i, B + i)
        add(i, B + (i + 1) % B)
    for k, f in enumerate(faces):
        p = B + ncent + k
        for vv in f:
            add(p, B + vv)
    return adj


def anchor_dist(B, I, faces):
    adj = graph(B, I, faces)
    out = []
    for src in range(B):
        dd = [99] * len(adj)
        dd[src] = 0
        q = deque([src])
        while q:
            uu = q.popleft()
            for vv2 in adj[uu]:
                if dd[vv2] > dd[uu] + 1:
                    dd[vv2] = dd[uu] + 1
                    q.append(vv2)
        out.append(tuple(dd[:B]))
    return tuple(out)


def keyD(D):
    return ','.join(''.join(str(x) for x in row) for row in D)


def constraints(D):
    B = len(D)
    rows, rhs = [], []
    for i in range(B):
        for j in range(i + 1, B):
            k = j - i
            if 2 * k == B:
                continue
            inds = list(range(i, j)) if 2 * k < B else list(range(j, B)) + list(range(i))
            if len(inds) * DELTA >= PILOW:      # path not certified to be the minor arc
                continue
            d = D[i][j]
            if d <= 5:
                row = [0] * B
                for h in inds:
                    row[h] = 1
                rows.append(row)
                rhs.append(ALPHA[d])
    return rows, rhs


def main():
    data = json.load(open(CERT, encoding='utf-8'))
    assert Fraction(*data['T']) == Fraction(13039536, 10 ** 8)
    total_orbits = total_res = 0
    allok = True
    for B, I in CASES:
        reps = pickle.load(open(rf'{ROOT}\triangulations_B{B}_I{I}_orbits.pkl', 'rb'))
        assert reps == sorted(set(reps)), 'reps not sorted/canonical list'
        seen = 0
        for s in reps:
            assert valid_disk_triangulation(s, B, I), f'invalid triangulation {s}'
            orb = orbit_set(s, B, I)
            assert min(orb) == s, 'representative is not the canonical minimum'
            seen += len(orb)
        blk = data['cases'][f'{B},{I}']
        assert blk['orbit_count'] == len(reps)
        res = set(map(int, blk['residual_indices']))
        excluded = 0
        minmar = None
        for idx, s in enumerate(reps):
            D = anchor_dist(B, I, s)
            k = keyD(D)
            rows, rhs = constraints(D)
            z = blk['certs'].get(k)
            if z is None:
                assert idx in res, f'orbit {idx} has no cert but is not residual'
                continue
            nums = [0] * len(rows)
            for j, n in z['lam']:
                nums[int(j)] = int(n)
            assert all(n >= 0 for n in nums)
            cov = [sum(nums[j] * rows[j][i] for j in range(len(rows))) for i in range(B)]
            assert min(cov) >= Q, f'coverage {min(cov)} < Q'
            cost = sum((Fraction(nums[j], Q) * rhs[j] for j in range(len(rows))), Fraction(0))
            assert cost == Fraction(*z['cost']), 'stored cost mismatch'
            mar = TWOPILOW - cost
            assert mar > 0, f'cost {float(cost)} >= 2pi'
            minmar = mar if minmar is None or mar < minmar else minmar
            excluded += 1
        assert excluded + len(res) == len(reps)
        assert seen == brown_labeled(B, I), f'Brown count mismatch {seen}'
        total_orbits += len(reps)
        total_res += len(res)
        log(f'({B},{I}): orbits {len(reps):>6d}  labeled {seen:>8d}  excluded {excluded:>6d}  '
            f'residual {len(res):>3d}  min margin {float(minmar):.6e}  OK')
    log(f'TOTAL orbits {total_orbits}  residual {total_res}  excluded {total_orbits-total_res}')
    out = {'verified': True, 'total_orbits': total_orbits, 'total_residual': total_res,
           'excluded': total_orbits - total_res, 'two_pi_lower_bound': str(TWOPILOW)}
    json.dump(out, open(r'E:\study\ADB\verify\out\farkas_independent.json', 'w'), indent=1)
    log('written verify/out/farkas_independent.json')


if __name__ == '__main__':
    main()
