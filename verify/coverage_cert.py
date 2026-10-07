"""Rigorous coverage certificate:  D  ⊆  U_i  B(c_i, r_*).

Decomposition (a triangulation of the anchor nonagon plus nine circular caps):

  vertices   C0..C11  the twelve centres      (indices 0..11)
             Q0..Q8   the nine boundary anchors (indices 12..20, = Q[0..8])
  core       13 triangles with vertices among the centres
  type A     (Q[i-1], Q[i], C[i])          9 triangles -- inside B(C[i], r_*)
  type B     (Q[i], C[i], C[i+1])          9 triangles -- two-circle switch lemma
  caps       9 arcs between consecutive anchors + their chords -- inside B(C[i], r_*)

Elementary lemmas used (all proved in docs/proof.md):

  T (triangle lemma)  if a triangle has circumradius <= r then it is covered by
                      the three disks centred at its vertices;
  C (convexity)       a disk is convex, so a triangle whose three vertices lie
                      in B(c,r) lies in B(c,r);
  S (switch lemma)    q in B(a,r) n B(b,r)  =>  conv{a,b,q} c B(a,r) u B(b,r);
  A (arc lemma)       a disk containing the two endpoints of a circular arc of
                      angular width < pi and whose centre direction lies between
                      them contains the whole arc, and (by convexity) the cap
                      between the arc and its chord.

Symbolic part (exact polynomial identities reduced modulo the KKT equations):
  S1   |Q[i] - C[i]|^2   = r^2   for i = 0..8
  S2   |Q[i] - C[i+1]|^2 = r^2   for i = 0..8
  S3   the six active core faces have a circumcentre U with |U - V|^2 = r^2 for
       all three vertices V (U given explicitly)

Interval part (exact rational interval arithmetic on the certified root box):
  I1   the 31 faces form a strictly positively oriented triangulation of the
       nonagon (Euler characteristic 1, boundary = the nine nonagon edges)
  I2   the nonagon is strictly convex
  I3   the seven inactive core faces have circumradius^2 < r_lo^2
  I4   for every gap the owning centre direction lies strictly inside the gap
       (so the arc lemma applies)
"""
from __future__ import annotations
import json
import os
import sys
import time
from fractions import Fraction

import sympy as sp

C_DIR = r'E:\study\ADB\verify'
sys.path.insert(0, r'E:\study\ADB\tools')
sys.path.insert(0, C_DIR)
from interval import Iv, iv_eval  # noqa: E402

sys.set_int_max_str_digits(400000)

r, u, v, w, c, s, z = sp.symbols('r u v w c s z')
OUT = r'E:\study\ADB\verify\out\coverage_certificate.json'
os.makedirs(os.path.dirname(OUT), exist_ok=True)
T0 = time.time()
REPORT = []


def log(*a):
    print(f'[{time.time()-T0:7.1f}s]', *a, flush=True)


def check(name, cond, extra=None):
    REPORT.append({'check': name, 'passed': bool(cond), **(extra or {})})
    log(('PASS ' if cond else 'FAIL ') + name, '' if extra is None else extra)
    return bool(cond)


# ----------------------------------------------------------------------------
# symbolic reduction modulo the KKT equations
# ----------------------------------------------------------------------------
E2 = u ** 2 - 2 * u * c + 1 - r ** 2
E3 = v ** 2 - v * (c ** 2 - s ** 2 + 2 * z * c * s) + 1 - r ** 2
E4 = w - u ** 2 + r ** 2 + r
E5 = v ** 2 - (2 * r + w) * v + w * (w + r)
F1 = c ** 2 + s ** 2 - 1
Z3 = z ** 2 - 3


def reduce_expr(e, use_e3=False):
    """Repeatedly rewrite using the system equations; return the normal form.

    z^2 = 3 and s^2 = 1 - c^2 are applied as *polynomial remainders* (a plain
    `.subs(z**2, 3)` would miss the factor z^2 inside z^3).
    """
    e = sp.expand(e)
    for _ in range(40):
        e0 = e
        e = sp.expand(e.subs(w, u ** 2 - r ** 2 - r))            # E4
        e = sp.rem(sp.Poly(e, z), sp.Poly(z ** 2 - 3, z), z).as_expr()      # Z3
        e = sp.rem(sp.Poly(sp.expand(e), s), sp.Poly(s ** 2 + c ** 2 - 1, s), s).as_expr()  # F1
        pu = sp.Poly(sp.expand(e), u)
        if pu.degree() >= 2:                                       # E2
            e = sp.rem(pu, sp.Poly(u ** 2 - 2 * u * c + 1 - r ** 2, u), u).as_expr()
        pv = sp.Poly(sp.expand(e), v)
        if pv.degree() >= 2:                                       # E5 or E3
            e = sp.rem(pv, sp.Poly(E3 if use_e3 else E5, v), v).as_expr()
        e = sp.expand(e)
        if e == e0:
            break
    return sp.expand(e)


def zero_mod(e, use_e3=False):
    return reduce_expr(e, use_e3) == 0


# ----------------------------------------------------------------------------
# symbolic geometry (rotations by 120/240 degrees, reflection in the 60 deg axis)
# ----------------------------------------------------------------------------
def R120(p):
    return sp.expand((-(p[0] + z * p[1]) / 2), deep=True), sp.expand((z * p[0] - p[1]) / 2, deep=True)


def R240(p):
    return sp.expand((-(p[0] - z * p[1]) / 2), deep=True), sp.expand((-(z * p[0] + p[1])) / 2, deep=True)


def refl60(p):
    return sp.expand((-p[0] + z * p[1]) / 2, deep=True), sp.expand((z * p[0] + p[1]) / 2, deep=True)


gp = (u * c, u * s)
gm = (u * c, -u * s)
rawC = [gp, gm, R120(gp), R120(gm), R240(gp), R240(gm),
        (-v, sp.Integer(0)), R120((-v, sp.Integer(0))), R240((-v, sp.Integer(0))),
        (w, sp.Integer(0)), R120((w, sp.Integer(0))), R240((w, sp.Integer(0)))]
CS = [rawC[i] for i in [6, 5, 4, 7, 1, 0, 8, 3, 2, 9, 10, 11]]
q0 = (sp.Integer(1), sp.Integer(0))
q1 = (c ** 2 - s ** 2, 2 * c * s)
q2 = refl60(q1)
rawQ = [q0, q1, q2, R120(q0), R120(q1), R120(q2), R240(q0), R240(q1), R240(q2)]
QS = [rawQ[i] for i in [5, 6, 7, 8, 0, 1, 2, 3, 4]]


def dist2(A, B):
    return sp.expand((A[0] - B[0]) ** 2 + (A[1] - B[1]) ** 2)


# ---- S1, S2
ok1 = ok2 = True
for i in range(9):
    d1 = sp.expand(dist2(QS[i], CS[i]) - r ** 2)
    d2 = sp.expand(dist2(QS[i], CS[(i + 1) % 9]) - r ** 2)
    z1 = zero_mod(d1) or zero_mod(d1, use_e3=True)
    z2 = zero_mod(d2) or zero_mod(d2, use_e3=True)
    if not z1:
        log(f'   S1 failed for i={i}')
    if not z2:
        log(f'   S2 failed for i={i}')
    ok1 &= z1
    ok2 &= z2
check('S1 |Q[i]-C[i]|^2 = r^2 for all i (mod KKT)', ok1)
check('S2 |Q[i]-C[i+1]|^2 = r^2 for all i (mod KKT)', ok2)

# ---- S3 active faces and their circumcentres
WR = lambda: (w + r, sp.Integer(0))
active_faces = [
    ((4, 5, 9), (w + r, sp.Integer(0))),
    ((7, 8, 10), R120((w + r, sp.Integer(0)))),
    ((1, 2, 11), R240((w + r, sp.Integer(0)))),
    ((0, 10, 11), (-(v - r), sp.Integer(0))),
    ((3, 9, 11), ((v - r) / 2, -z * (v - r) / 2)),
    ((6, 9, 10), ((v - r) / 2, z * (v - r) / 2)),
]
ok3 = True
for face, U in active_faces:
    for j in face:
        d = sp.expand(dist2(U, CS[j]) - r ** 2)
        good = zero_mod(d) or zero_mod(d, use_e3=True)
        if not good:
            ok3 = False
            log(f'   S3 failed face {face} vertex {j}')
check('S3 six active faces have circumradius r (explicit circumcentres)', ok3)

# ----------------------------------------------------------------------------
# interval part
# ----------------------------------------------------------------------------
kx = json.load(open(r'E:\study\ADB\verify\out\krawczyk.json', encoding='utf-8'))
names = kx['variable_order']
box = {n: Iv(Fraction(lo), Fraction(hi)) for n, (lo, hi) in zip(names, kx['box'])}
rH = box['r']
sub = {sp.Symbol(k): box[k] for k in ('r', 'u', 'v', 'w', 'c', 's', 'z')}
HALF = Iv(Fraction(1, 2))


def IvR120(p):
    return (-(p[0] + sub[sp.Symbol('z')] * p[1]) * HALF, (sub[sp.Symbol('z')] * p[0] - p[1]) * HALF)


def IvR240(p):
    return (-(p[0] - sub[sp.Symbol('z')] * p[1]) * HALF, (-(sub[sp.Symbol('z')] * p[0] + p[1])) * HALF)


def IvR(p):
    return (((-p[0] + sub[sp.Symbol('z')] * p[1]) * HALF), ((sub[sp.Symbol('z')] * p[0] + p[1]) * HALF))


def ivx(e):
    return iv_eval(e, sub)


U_ = ivx(sp.Symbol('u')); V_ = ivx(sp.Symbol('v')); W_ = ivx(sp.Symbol('w'))
Cc = box['c']; Ss = box['s']
gpI = (U_ * Cc, U_ * Ss)
gmI = (U_ * Cc, -(U_ * Ss))
rawCI = [gpI, gmI, IvR120(gpI), IvR120(gmI), IvR240(gpI), IvR240(gmI),
         (-V_, Iv(0)), IvR120((-V_, Iv(0))), IvR240((-V_, Iv(0))),
         (W_, Iv(0)), IvR120((W_, Iv(0))), IvR240((W_, Iv(0)))]
CI = [rawCI[i] for i in [6, 5, 4, 7, 1, 0, 8, 3, 2, 9, 10, 11]]
q0I = (Iv(1), Iv(0))
q1I = (Cc * Cc - Ss * Ss, Iv(2) * Cc * Ss)
q2I = IvR(q1I)
rawQI = [q0I, q1I, q2I, IvR120(q0I), IvR120(q1I), IvR120(q2I), IvR240(q0I), IvR240(q1I), IvR240(q2I)]
QI = [rawQI[i] for i in [5, 6, 7, 8, 0, 1, 2, 3, 4]]
PI = CI + QI
log('interval geometry built')

# sanity: interval point coordinates must be tight (width ~ 1e-59)
log('  width of C[0].x =', float(CI[0][0].width()), ' Q[0].x =', float(QI[0][0].width()))


def orientI(a, b, cc):
    return (b[0] - a[0]) * (cc[1] - a[1]) - (b[1] - a[1]) * (cc[0] - a[0])


core = [(0, 1, 11), (0, 10, 8), (0, 11, 10), (1, 2, 11), (2, 3, 11), (3, 4, 9), (3, 9, 11),
        (4, 5, 9), (5, 6, 9), (6, 7, 10), (6, 10, 9), (7, 8, 10), (9, 10, 11)]
facesA = [((i - 1) % 9 + 12, i + 12, i) for i in range(9)]
facesB = [(i + 12, i, (i + 1) % 9) for i in range(9)]
allf = []
for f in core + facesA + facesB:
    if orientI(PI[f[0]], PI[f[1]], PI[f[2]]).hi < 0:
        f = (f[0], f[2], f[1])
    allf.append(f)

# I1 triangulation
directed, undirected = {}, {}
for f in allf:
    assert len(set(f)) == 3
    for a, b in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
        directed[(a, b)] = directed.get((a, b), 0) + 1
        e = tuple(sorted((a, b)))
        undirected[e] = undirected.get(e, 0) + 1
bnd = {e for e, n in undirected.items() if n == 1}
internal_ok = all(directed.get(e, 0) == 1 and directed.get((e[1], e[0]), 0) == 1
                  for e, n in undirected.items() if n == 2)
expected_bnd = {tuple(sorted((12 + i, 12 + (i + 1) % 9))) for i in range(9)}
area_ok = all(orientI(PI[f[0]], PI[f[1]], PI[f[2]]).lo > 0 for f in allf)
check('I1 21/51/31 triangulation, Euler=1', len(undirected) == 51 and 21 - len(undirected) + 31 == 1)
check('I1 boundary = the nine nonagon edges', bnd == expected_bnd)
check('I1 internal edges traversed once in each direction', internal_ok)
check('I1 all 31 faces strictly positively oriented', area_ok,
      {'min_area_lo': float(min(orientI(PI[f[0]], PI[f[1]], PI[f[2]]).lo for f in allf))})

# I2 nonagon strictly convex
conv = [orientI(QI[i], QI[(i + 1) % 9], QI[(i + 2) % 9]) for i in range(9)]
check('I2 nonagon strictly convex', all(a.lo > 0 for a in conv),
      {'min_convexity_lo': float(min(a.lo for a in conv))})

# I3 inactive faces (active ones identified as index sets)
ACTIVE_SETS = [frozenset(f) for f, _ in active_faces]
inactive = [f for f in core if frozenset(f) not in ACTIVE_SETS]
check('I3 face count: 6 active + 7 inactive core faces',
      len(inactive) == 7 and len(ACTIVE_SETS) == 6, {'inactive': [list(f) for f in inactive]})
margins = []


def circum2_I(A, B, Cc_):
    ba = (B[0] - A[0], B[1] - A[1])
    ca = (Cc_[0] - A[0], Cc_[1] - A[1])
    db = (B[0] * B[0] + B[1] * B[1]) - (A[0] * A[0] + A[1] * A[1])
    dc = (Cc_[0] * Cc_[0] + Cc_[1] * Cc_[1]) - (A[0] * A[0] + A[1] * A[1])
    den = Iv(2) * (ba[0] * ca[1] - ba[1] * ca[0])
    ux = (db * ca[1] - dc * ba[1]) / den
    uy = (ba[0] * dc - ca[0] * db) / den
    dx = ux - A[0]
    dy = uy - A[1]
    return dx * dx + dy * dy


okI3 = True
for f in inactive:
    A, B, Cc_ = (PI[j] for j in f)
    R2 = circum2_I(A, B, Cc_)
    m = rH.lo * rH.lo - R2.hi
    margins.append(float(m))
    if not (m > 0):
        okI3 = False
        log(f'   I3 failed face {f}')
check('I3 seven inactive core faces: circumradius^2 < r_lo^2', okI3,
      {'min_r2_margin': min(margins)})

# I4 centre direction strictly inside its gap
#     cross(Q[i-1], C[i]) > 0  and  cross(C[i], Q[i]) > 0
def crossI(a, b):
    return a[0] * b[1] - a[1] * b[0]


okI4 = True
worst = None
for i in range(9):
    qa, qb, cc_ = QI[(i - 1) % 9], QI[i], CI[i]
    o1 = crossI(qa, cc_)
    o2 = crossI(cc_, qb)
    good = o1.lo > 0 and o2.lo > 0
    if not good:
        okI4 = False
        log(f'   I4 failed gap {i}')
    v_ = min(float(o1.lo), float(o2.lo))
    worst = v_ if worst is None else min(worst, v_)
check('I4 owning centre direction strictly inside each gap', okI4, {'min_cross': worst})

out = {
    'all_passed': all(x['passed'] for x in REPORT),
    'checks': REPORT,
    'faces': len(allf),
    'vertices': 21,
    'edges': len(undirected),
    'active_faces': [list(f) for f, _ in active_faces],
    'inactive_r2_margins': margins,
    'r_box': [str(rH.lo), str(rH.hi)],
}
with open(OUT, 'w', encoding='utf-8') as fh:
    json.dump(out, fh, indent=1)
log('written', OUT)
log('ALL PASSED' if out['all_passed'] else 'SOME CHECK FAILED')
