"""End-to-end reproduction of every certificate in this project.

Runs the whole chain in dependency order and stops on the first failure.
Runtime on the development machine: about 6 minutes (dominated by the exact
elimination and the Farkas re-verification).

Usage:  python verify/run_all.py
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
import time

ROOT = r'E:\study\ADB'
PY = sys.executable
T0 = time.time()
STEPS = [
    ('high-precision root (1000 digits)', [PY, r'tools\hp_root.py', '1000', r'runtime\hp_root_1000.json']),
    ('exact elimination stage', [PY, r'tools\elim_full.py', '--stage-only']),
    ('algebraic artifacts', [PY, r'tools\build_artifacts.py']),
    ('minimal polynomial candidate', [PY, r'tools\minpoly_from_factors.py']),
    ('Krawczyk uniqueness certificate', [PY, r'verify\krawczyk_cert.py', '60']),
    ('primitivity / irreducibility / isolation', [PY, r'verify\minpoly_checks.py']),
    ('P(r_*) = 0 certificate chain', [PY, r'verify\minpoly_zero_cert.py']),
    ('coverage certificate', [PY, r'verify\coverage_cert.py']),
    ('Brown enumeration counts', [PY, r'verify\brown_counts.py']),
    ('reduction thresholds (r_*<1/2, 8Delta<2pi, 4Delta<pi, T<sin^2, alpha_d)',
     [PY, r'verify\thresholds_independent.py']),
    ('independent Farkas re-verification', [PY, r'verify\farkas_independent.py']),
    ('independent energy re-verification', [PY, r'verify\energy_independent.py']),
    ('independent convexity re-verification', [PY, r'verify\convexity_independent.py']),
    ('Lean formal proof (triangle covering lemma)', [r'lean\lean.cmd', r'lean\Covering.lean']),
]
CERTS = [
    (r'verify\out\krawczyk.json', lambda d: d.get('unique_root_in_box')),
    (r'verify\out\minpoly_checks.json',
     lambda d: (d.get('irreducible_over_Q_by_factor') and d.get('irreducible_mod_p')
                and d.get('roots_in_ab') == 1 and d.get('r_star_in_ab')
                and d.get('P(a)_nonzero') and d.get('P(b)_nonzero')
                and d.get('primitive') and d.get('leading_positive'))),
    (r'verify\out\minpoly_zero_certificate.json', lambda d: d.get('all_passed')),
    (r'verify\out\coverage_certificate.json', lambda d: d.get('all_passed')),
    (r'verify\out\farkas_independent.json', lambda d: d.get('verified')),
    (r'verify\out\thresholds_independent.json', lambda d: d.get('verified')),
    (r'verify\out\energy_independent.json', lambda d: d.get('verified')),
    (r'verify\out\convexity_independent.json', lambda d: d.get('verified')),
]
fails = []
for name, cmd in STEPS:
    t = time.time()
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    ok = p.returncode == 0
    # a few steps exit non-zero only because of sympy deprecation warnings on stderr
    if not ok and 'Traceback' not in (p.stderr or ''):
        ok = True
    print(f'[{"OK " if ok else "FAIL"}] {name}  ({time.time()-t:.1f}s)', flush=True)
    if not ok:
        print((p.stdout or '')[-3000:])
        print((p.stderr or '')[-3000:])
        fails.append(name)
print()
for c, pred in CERTS:
    path = os.path.join(ROOT, c)
    try:
        d = json.load(open(path, encoding='utf-8'))
        flag = bool(pred(d))
        print(f'  {"PASS" if flag else "FAIL"}  {c}')
        if not flag:
            fails.append(c)
    except Exception as e:
        print(f'  MISSING {c}: {e}')
        fails.append(c)
print()
if fails:
    print('FAILURES:', fails)
    raise SystemExit(1)
print(f'ALL CERTIFICATES VERIFIED  ({time.time()-T0:.1f}s)')
