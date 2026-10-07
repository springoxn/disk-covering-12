"""Build verify/SHA256SUMS: an integrity manifest of every deliverable."""
from __future__ import annotations
import hashlib
import json
import os

ROOT = r'E:\study\ADB'
targets = []
for d, exts in [('docs', ('.md',)), ('lean', ('.lean', '.cmd')), ('verify', ('.py',)),
                ('tools', ('.py',)), ('runtime', ('.json', '.md', '.txt')),
                ('submission', ('.json', '.txt')), ('', ('.md',))]:
    base = os.path.join(ROOT, d) if d else ROOT
    for f in sorted(os.listdir(base)):
        p = os.path.join(base, f)
        if os.path.isfile(p) and f.endswith(exts):
            targets.append(os.path.relpath(p, ROOT))
outdir = os.path.join(ROOT, 'verify', 'out')
targets += [os.path.join('verify', 'out', f) for f in sorted(os.listdir(outdir))]

lines = []
for rel in sorted(set(targets)):
    p = os.path.join(ROOT, rel)
    if not os.path.isfile(p):
        continue
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    lines.append(h + '  ' + rel.replace(os.sep, '/'))

manifest = os.path.join(ROOT, 'verify', 'SHA256SUMS')
with open(manifest, 'w', encoding='utf-8', newline='\n') as fh:
    fh.write('\n'.join(lines) + '\n')
print(f'{len(lines)} files hashed -> verify/SHA256SUMS')
print()

key = ['verify/out/FINAL_ANSWER.json', 'docs/RESULT.md', 'lean/Covering.lean',
       'verify/out/minpoly_checks.json', 'verify/out/minpoly_zero_certificate.json',
       'verify/out/krawczyk.json', 'verify/out/coverage_certificate.json',
       'verify/out/farkas_independent.json', 'verify/out/energy_independent.json',
       'verify/out/convexity_independent.json', 'verify/out/thresholds_independent.json',
       'verify/run_all.py', 'runtime/minpoly_candidate.json', 'verify/SHA256SUMS']
for k in key:
    for l in lines:
        if l.endswith('  ' + k):
            print(l)
            break

cand = json.load(open(os.path.join(ROOT, 'runtime', 'minpoly_candidate.json'), encoding='utf-8'))
s = ','.join(str(c) for c in cand['P_coeffs_desc'])
print()
print('sha256 of the coefficient string  a37,a36,...,a0 :')
print('  ' + hashlib.sha256(s.encode()).hexdigest())
