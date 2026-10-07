"""Reconstruct the natural elapsed time of this run from filesystem evidence."""
import json
import os
import sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r'E:\study\ADB'
skip = {'lit', '_recon', '.agents', '__pycache__'}
rows = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in skip]
    for f in filenames:
        p = os.path.join(dirpath, f)
        try:
            st = os.stat(p)
        except OSError:
            continue
        rows.append((st.st_ctime, st.st_mtime, os.path.relpath(p, ROOT)))
rows.sort()
print('--- 10 earliest (by creation time) ---')
for c, m, rel in rows[:10]:
    print(f'  {datetime.fromtimestamp(c):%Y-%m-%d %H:%M:%S}  c  {rel}')
print('--- 10 latest (by creation time) ---')
for c, m, rel in rows[-10:]:
    print(f'  {datetime.fromtimestamp(c):%Y-%m-%d %H:%M:%S}  c  {rel}')

t0 = rows[0][0]
t1 = max(r[0] for r in rows)
print()
print('earliest creation :', datetime.fromtimestamp(t0))
print('latest creation   :', datetime.fromtimestamp(t1))
print('elapsed (wall)    : %.0f s = %.2f h' % (t1 - t0, (t1 - t0) / 3600))

# milestone files
marks = [
    ('README.md', 'round-1 project scaffold'),
    ('runtime/hp_root_1000.json', 'round-1: 1000-digit root'),
    ('runtime/minpoly_candidate.json', 'round-1: minimal polynomial'),
    ('verify/out/krawczyk.json', 'round-1: Krawczyk'),
    ('verify/out/coverage_certificate.json', 'round-1: coverage'),
    ('verify/out/farkas_independent.json', 'round-1: Farkas recheck'),
    ('verify/out/energy_independent.json', 'round-2: energy recheck'),
    ('verify/out/convexity_independent.json', 'round-2: convexity recheck'),
    ('verify/out/thresholds_independent.json', 'round-2: thresholds'),
    ('lean/Covering.lean', 'round-2: Lean proof'),
    ('runtime/run_all.log', 'round-2: end-to-end ALL VERIFIED'),
    ('verify/out/benchmark_fingerprint.json', 'round-3: benchmark fingerprint match'),
    ('docs/RESULT.md', 'latest doc edit'),
]
print()
print('--- milestones ---')
for rel, note in marks:
    p = os.path.join(ROOT, rel.replace('/', os.sep))
    if os.path.exists(p):
        st = os.stat(p)
        print(f'  {datetime.fromtimestamp(st.st_mtime):%Y-%m-%d %H:%M:%S}  {rel:48s} {note}')
    else:
        print(f'  {"MISSING":19s}  {rel:48s} {note}')
