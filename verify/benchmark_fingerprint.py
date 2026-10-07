"""Run the benchmark's official fingerprint tool on THIS project's answer."""
import json
import os
import subprocess
import sys

sys.set_int_max_str_digits(400000)
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r'E:\study\ADB'
TOOL = os.path.join(ROOT, r'_recon\benchmark\diskcover_answer.py')
EXPECTED = '35d604a5ea1b1fe5c52c30337743c1a8142b69827023284f9597e1ca9cb8f947'

cand = json.load(open(os.path.join(ROOT, r'runtime\minpoly_candidate.json'), encoding='utf-8'))
desc = [int(x) for x in cand['P_coeffs_desc']]      # a_37 ... a_0
asc = list(reversed(desc))                          # constant term first
print('degree', len(asc) - 1)
print('a0 .. a3 =', asc[:4], '... a35 .. a37 =', asc[-3:])

coef_path = os.path.join(ROOT, r'runtime\coefficients_n12.json')
with open(coef_path, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(asc, fh)

# high precision radius text (from the 1000-digit solve)
r_str = json.load(open(os.path.join(ROOT, r'runtime\hp_root_1000.json'), encoding='utf-8'))['r']
print('radius (70 digits):', r_str[:72])
print()
cmd = [sys.executable, TOOL, '--n', '12', '--coefficients', coef_path,
       '--radius', r_str, '--expected-sha256', EXPECTED]
p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(p.stdout)
if p.stderr:
    print('STDERR:', p.stderr)
print('exit code:', p.returncode)

out = json.loads(p.stdout) if p.stdout.strip().startswith('{') else {}
print()
print('computed sha256 :', out.get('sha256'))
print('expected sha256 :', EXPECTED)
print('MATCH           :', out.get('matches_reference'))
json.dump({'computed': out.get('sha256'), 'expected': EXPECTED,
           'matches_reference': out.get('matches_reference'),
           'canonical_json': out.get('canonical_json'),
           'payload': out.get('answer')},
          open(os.path.join(ROOT, r'verify\out\benchmark_fingerprint.json'), 'w',
               encoding='utf-8'), indent=1)
