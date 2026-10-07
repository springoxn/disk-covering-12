"""Numerical check of the covering triangulation used in the coverage proof.

Triangulation of the anchor nonagon, 21 vertices / 31 faces:
  C0..C11  the twelve centres           (vertices 0..11)
  Q0..Q8   the nine boundary anchors    (vertices 12..20)

  core   (13 triangles, vertices among the centres)
  A_i = (Q[i-1], Q[i], C[i])   i=0..8   -- single disk B(C[i],r) by convexity
  B_i = (Q[i], C[i], C[i+1])   i=0..8   -- two-circle switch lemma
"""
from __future__ import annotations
import json
import sys

import mpmath as mp

mp.mp.dps = 50
rec = json.load(open(r'E:\study\ADB\runtime\hp_root_1000.json', encoding='utf-8'))
V = {k: mp.mpf(rec[k]) for k in ('r', 'u', 'v', 'w', 'c', 's', 'z')}
r, u, v, w, c, s, z = (V[k] for k in ('r', 'u', 'v', 'w', 'c', 's', 'z'))
h = mp.acos(c)


def R120(p):
    return (-(p[0] + z * p[1]) / 2, (z * p[0] - p[1]) / 2)


def R240(p):
    return (-(p[0] - z * p[1]) / 2, -(z * p[0] + p[1]) / 2)


def refl60(p):
    return ((-p[0] + z * p[1]) / 2, (z * p[0] + p[1]) / 2)


gp = (u * c, u * s)
gm = (u * c, -u * s)
rawC = [gp, gm, R120(gp), R120(gm), R240(gp), R240(gm),
        (-v, mp.mpf(0)), R120((-v, mp.mpf(0))), R240((-v, mp.mpf(0))),
        (w, mp.mpf(0)), R120((w, mp.mpf(0))), R240((w, mp.mpf(0)))]
C = [rawC[i] for i in [6, 5, 4, 7, 1, 0, 8, 3, 2, 9, 10, 11]]
q0 = (mp.mpf(1), mp.mpf(0))
q1 = (c * c - s * s, 2 * c * s)
q2 = refl60(q1)
rawQ = [q0, q1, q2, R120(q0), R120(q1), R120(q2), R240(q0), R240(q1), R240(q2)]
Q = [rawQ[i] for i in [5, 6, 7, 8, 0, 1, 2, 3, 4]]

P = C + Q
print('anchor angles (deg):', [mp.nstr(mp.degrees(mp.atan2(p[1], p[0])) % 360, 8) for p in Q])
print('centre angles (deg):', [mp.nstr(mp.degrees(mp.atan2(p[1], p[0])) % 360, 8) for p in C])
print()
print('anchor distances to centres (rows=anchor, entries < r+1e-9):')
for i, q in enumerate(Q):
    close = [(j, mp.sqrt((q[0] - P[j][0]) ** 2 + (q[1] - P[j][1]) ** 2)) for j in range(12)]
    close = [t for t in close if abs(t[1] - r) < mp.mpf('1e-12')]
    print(f'  Q[{i}] angle {mp.nstr(mp.degrees(mp.atan2(q[1], q[0])) % 360, 8):>10s} : '
          + ', '.join(f'C[{j}]' for j, _ in close))

core = [(0,1,11),(0,10,8),(0,11,10),(1,2,11),(2,3,11),(3,4,9),(3,9,11),(4,5,9),(5,6,9),
        (6,7,10),(6,10,9),(7,8,10),(9,10,11)]
facesA = [((i - 1) % 9 + 12, i + 12, i) for i in range(9)]
facesB = [(i + 12, i, (i + 1) % 9) for i in range(9)]
allf = core + facesA + facesB
print()
print('faces:', len(allf))


def orient(a, b, cc):
    return (b[0] - a[0]) * (cc[1] - a[1]) - (b[1] - a[1]) * (cc[0] - a[0])


# orient every face counter-clockwise
oriented = []
for f in allf:
    if orient(P[f[0]], P[f[1]], P[f[2]]) < 0:
        f = (f[0], f[2], f[1])
    oriented.append(f)
allf = oriented
areas = [orient(P[f[0]], P[f[1]], P[f[2]]) for f in allf]
print('all positive areas:', all(a > 0 for a in areas), ' min area', mp.nstr(min(areas), 6))

directed = {}
undirected = {}
for f in allf:
    for a, b in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
        directed[(a, b)] = directed.get((a, b), 0) + 1
        e = tuple(sorted((a, b)))
        undirected[e] = undirected.get(e, 0) + 1
print('edges:', len(undirected), 'Euler V-E+F =', 21 - len(undirected) + len(allf))
bnd = [e for e, n in undirected.items() if n == 1]
print('boundary edges:', sorted(bnd))
print('boundary is the 9 nonagon edges:',
      sorted(bnd) == sorted(tuple(sorted((12 + i, 12 + (i + 1) % 9))) for i in range(9)))
bad = [e for e, n in undirected.items() if n == 2 and not (directed.get(e, 0) == 1 and directed.get((e[1], e[0]), 0) == 1)]
print('internal edges traversed in opposite directions:', not bad)

print()
print('circumradius of core faces:')
active = {(1,2,11),(4,5,9),(7,8,10),(0,10,11),(3,9,11),(6,9,10)}
for f in core:
    A, B, Cc = (P[j] for j in f)
    ax, ay = A; bx, by = B; cx, cy = Cc
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) + (cx**2 + cy**2) * (ay - by)) / d
    uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) + (cx**2 + cy**2) * (bx - ax)) / d
    R = mp.sqrt((ux - ax)**2 + (uy - ay)**2)
    print(f'  {str(f):12s} {"ACTIVE" if f in active else "      "} R-r = {mp.nstr(R-r,6)}')
print()
print('nonagon convexity: min orient(Q_i,Q_i+1,Q_i+2) =',
      mp.nstr(min(orient(Q[i], Q[(i+1)%9], Q[(i+2)%9]) for i in range(9)), 6))
print('boundary half-gaps (deg): 2h/2 =', mp.nstr(mp.degrees(h), 8),
      ' (120-4h)/2 =', mp.nstr(mp.degrees(mp.pi/3 - 2*h), 8))
