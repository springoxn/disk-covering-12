"""Numerical exploration of the candidate covering geometry.

Reproduces the 12 centres and 9 boundary anchors of the D3 candidate, identifies
the active faces (circumradius = r) and inspects the circumcentres.
"""
from __future__ import annotations
import json
import sys

import mpmath as mp

mp.mp.dps = 60
rec = json.load(open(r'E:\study\ADB\runtime\hp_root_1000.json', encoding='utf-8'))
V = {k: mp.mpf(rec[k]) for k in ('r', 'u', 'v', 'w', 'c', 's', 'z', 'P', 'Q', 'S', 'A', 'B', 'C', 'D')}
r, u, v, w, c, s, z = (V[k] for k in ('r', 'u', 'v', 'w', 'c', 's', 'z'))


def rot(a, k):
    th = 2 * mp.pi * k / 3
    return (a[0] * mp.cos(th) - a[1] * mp.sin(th), a[0] * mp.sin(th) + a[1] * mp.cos(th))


gp = (u * c, u * s)
gm = (u * c, -u * s)
rawC = [gp, gm, rot(gp, 1), rot(gm, 1), rot(gp, 2), rot(gm, 2),
        (-v, mp.mpf(0)), rot((-v, mp.mpf(0)), 1), rot((-v, mp.mpf(0)), 2),
        (w, mp.mpf(0)), rot((w, mp.mpf(0)), 1), rot((w, mp.mpf(0)), 2)]
C = [rawC[i] for i in [6, 5, 4, 7, 1, 0, 8, 3, 2, 9, 10, 11]]
c2, s2 = c * c - s * s, 2 * c * s
q0 = (mp.mpf(1), mp.mpf(0))
q1 = (c2, s2)
# reflect q1 about the axis at angle pi/3
th = 2 * mp.pi / 3
q2 = (q1[0] * mp.cos(th) - q1[1] * mp.sin(th), q1[0] * mp.sin(th) + q1[1] * mp.cos(th))  # placeholder
rawQ = [q0, q1, q2, rot(q0, 1), rot(q1, 1), rot(q2, 1), rot(q0, 2), rot(q1, 2), rot(q2, 2)]
Qp = [rawQ[i] for i in [5, 6, 7, 8, 0, 1, 2, 3, 4]]

print('r =', mp.nstr(r, 20), ' u,v,w =', mp.nstr(u, 15), mp.nstr(v, 15), mp.nstr(w, 15))
print('h = arccos(c) =', mp.nstr(mp.acos(c), 15), 'deg', mp.nstr(mp.degrees(mp.acos(c)), 12))
print()
for i, p in enumerate(C):
    print(f'  C[{i:2d}] = ({mp.nstr(p[0],18)}, {mp.nstr(p[1],18)})   |C| = {mp.nstr(mp.sqrt(p[0]**2+p[1]**2),18)}')
print()
for i, p in enumerate(Qp):
    print(f'  Q[{i}] = ({mp.nstr(p[0],15)}, {mp.nstr(p[1],15)})  angle deg {mp.nstr(mp.degrees(mp.atan2(p[1],p[0])) % 360,12)}')
print()


def circum(A, B, Cc):
    ax, ay = A; bx, by = B; cx, cy = Cc
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) + (cx**2 + cy**2) * (ay - by)) / d
    uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) + (cx**2 + cy**2) * (bx - ax)) / d
    R = mp.sqrt((ux - ax)**2 + (uy - ay)**2)
    return (ux, uy), R


core = [(0,1,11),(0,10,8),(0,11,10),(1,2,11),(2,3,11),(3,4,9),(3,9,11),(4,5,9),(5,6,9),
        (6,7,10),(6,10,9),(7,8,10),(9,10,11)]
active = {(1,2,11),(4,5,9),(7,8,10),(0,10,11),(3,9,11),(6,9,10)}
print('core faces:')
for f in core:
    U, R = circum(C[f[0]], C[f[1]], C[f[2]])
    tag = 'ACTIVE' if f in active else '      '
    print(f'  {str(f):12s} {tag}  R = {mp.nstr(R,18)}  R-r = {mp.nstr(R-r,6)}'
          f'  U = ({mp.nstr(U[0],18)}, {mp.nstr(U[1],18)})  |U| = {mp.nstr(mp.sqrt(U[0]**2+U[1]**2),18)}')
print()
print('distances of active circumcentres to relevant centres:')
for f in core:
    if f not in active:
        continue
    U, R = circum(C[f[0]], C[f[1]], C[f[2]])
    ds = [(j, mp.sqrt((U[0]-C[j][0])**2 + (U[1]-C[j][1])**2)) for j in range(12)]
    ds.sort(key=lambda t: t[1])
    print(f'  {str(f):12s} nearest: ' + ', '.join(f'{j}:{mp.nstr(d,14)}' for j, d in ds[:5]))
print()
print('distance from origin of active circumcentres / inner centre radius w =', mp.nstr(w, 12))
