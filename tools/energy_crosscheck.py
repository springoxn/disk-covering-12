"""Cross-check: my leaf lower bound vs the third-party bound, and a Monte-Carlo
validity test of my bound on a real leaf."""
from __future__ import annotations
import json
import random
import sys
from fractions import Fraction

sys.path.insert(0, r'E:\study\ADB\lit\DiskCoveringSolve\cover12\proof_bundle')
sys.path.insert(0, r'E:\study\ADB\verify')

# third-party kernel (for comparison only)
import exact_core as XC            # noqa: E402
from fixed_trig import line_minorant as their_line   # noqa: E402

# my kernel
import energy_independent as EI    # noqa: E402

ROOT = r'E:\study\ADB\lit\DiskCoveringSolve\cover12\proof_bundle'
cert = json.load(open(ROOT + r'\residual_energy_cert_safe.json', encoding='utf-8'))
TARGET = Fraction(814971, 6250000)

z = [t for t in cert['topologies'] if (t['B'], t['I'], t['idx']) == (10, 2, 9875)][0]
B, I = z['B'], z['I']
faces = [tuple(f) for f in z['faces']]
pairs = [(i, j) for i in range(B) for j in range(i + 1, B)]
rec = z['records'][0]
nums = list(map(int, rec['wnum']))
stored = list(map(int, rec['dnum']))
D = EI.kron_conductances(B, I, faces, nums)
print('conductance check (stored <= exact):', all(Fraction(n, EI.QD) <= q for n, q in zip(stored, D)))
print('exact D values (first 6):', [str(q) for q in D[:6]])
print('stored/QD      (first 6):', [str(Fraction(n, EI.QD)) for n in stored[:6]])

boxes, leaves = EI.parse_box(z['nodes'], B)
print('leaves:', len(leaves))
worst_mine = None
for i in leaves:
    ri = int(z['nodes'][i]['leaf'])
    vm = EI.leaf_bound(*boxes[i], pairs, [stored][ri])
    vt = XC.F(0) if False else None
    # third-party bound
    lo, hi = boxes[i]
    lo2, hi2 = XC.tighten_sum_box(lo, hi)
    lines = [their_line(l, u, XC.PI_L, XC.PI_U) for l, u in XC.pair_intervals(lo2, hi2, pairs)]
    c = [XC.F(0)] * len(lo2)
    b = XC.F(0)
    for n, (i2, j2), (a2, b2) in zip(stored, pairs, lines):
        q = XC.F(int(n), EI.QD)
        b += q * b2
        for k in range(i2, j2):
            c[k] += q * a2
    vt = b + XC.linear_min(c, lo2, hi2)
    mar = vm - TARGET
    if worst_mine is None or mar < worst_mine[0]:
        worst_mine = (mar, i, vm, vt, boxes[i])
mar, i, vm, vt, box = worst_mine
print(f'worst leaf #{i}: my bound   {float(vm):.12f}  margin {float(vm-TARGET):.3e}')
print(f'                 their bound {float(vt):.12f}  margin {float(vt-TARGET):.3e}')
print(f'                 difference  {float(vm-vt):.6e}')
print('box lo:', [str(x) for x in box[0]][:3], '...')
print('box hi:', [str(x) for x in box[1]][:3], '...')

# ---- Monte-Carlo validity test of MY bound on this leaf
lo, hi = box
lo2, hi2 = EI.tighten(lo, hi)
print('after tighten, feasible:', lo2 is not None)
random.seed(1)
worst_energy = None
for trial in range(4000):
    g = [Fraction(random.random()) * (hi2[k] - lo2[k]) + lo2[k] for k in range(B)]
    s = sum(g)
    # rescale to sum = 2*pi (use a rational approximation inside [2piL,2piU])
    target = (EI.TWO_PI_L + EI.TWO_PI_U) / 2
    g = [x * target / s for x in g]
    g = [min(max(x, lo2[k]), hi2[k]) for k, x in enumerate(g)]
    if not (EI.TWO_PI_L <= sum(g) <= EI.TWO_PI_U):
        continue
    E = sum(Fraction(stored[p], EI.QD) * (1 - EI.sincos_bounds(g[j] - g[i])[3] if False else 0)
            for p, (i, j) in enumerate(pairs))
    # exact-ish energy using high-precision cos
    import mpmath as mp
    mp.mp.dps = 40
    E = mp.mpf(0)
    for p, (i2, j2) in enumerate(pairs):
        E += mp.mpf(stored[p]) / mp.mpf(EI.QD) * (1 - mp.cos(mp.mpf(g[j2].numerator) / g[j2].denominator
                                                             - mp.mpf(g[i2].numerator) / g[i2].denominator))
    E = float(E)
    if worst_energy is None or E < worst_energy:
        worst_energy = E
print(f'Monte-Carlo min energy on this leaf: {worst_energy:.12f}')
print(f'my bound                            : {float(vm):.12f}   valid: {worst_energy >= float(vm)}')
print(f'their bound                         : {float(vt):.12f}   valid: {worst_energy >= float(vt)}')
