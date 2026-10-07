"""Try to reproduce the published standard fingerprint from plausible
canonicalisations of this project's answer.

Target: 35d604a5ea1b1fe5c52c30337743c1a8142b69827023284f9597e1ca9cb8f947
"""
from __future__ import annotations
import hashlib
import itertools
import json
import os
import sys

import sympy as sp

sys.set_int_max_str_digits(400000)
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
TARGET = '35d604a5ea1b1fe5c52c30337741c1a8142b69827023284f9597e1ca9cb8f947'
TARGET = '35d604a5ea1b1fe5c52c30337741c1a8142b69827023284f9597e1ca9cb8f947'.replace('41c1', '43c1')
ROOT = r'E:\study\ADB'

cand = json.load(open(os.path.join(ROOT, 'runtime', 'minpoly_candidate.json'), encoding='utf-8'))
coeffs = [int(x) for x in cand['P_coeffs_desc']]          # a37 ... a0
t = sp.symbols('t')
P = sp.Poly(sum(c * t ** i for i, c in enumerate(reversed(coeffs))), t)

rec = json.load(open(os.path.join(ROOT, 'runtime', 'hp_root_1000.json'), encoding='utf-8'))
r_str = rec['r']
checks = json.load(open(os.path.join(ROOT, 'verify', 'out', 'minpoly_checks.json'), encoding='utf-8'))
a_frac, b_frac = checks['a'], checks['b']

cands = {}


def add(name, s):
    if isinstance(s, str):
        cands[name] = s.encode()


# --- coefficient sequences
add('coeffs_comma', ','.join(map(str, coeffs)))
add('coeffs_comma_nl', ','.join(map(str, coeffs)) + '\n')
add('coeffs_space', ' '.join(map(str, coeffs)))
add('coeffs_nl', '\n'.join(map(str, coeffs)))
add('coeffs_nl_nl', '\n'.join(map(str, coeffs)) + '\n')
add('coeffs_semicolon', ';'.join(map(str, coeffs)))
add('coeffs_rev_comma', ','.join(map(str, reversed(coeffs))))
add('coeffs_brackets', '[' + ', '.join(map(str, coeffs)) + ']')
add('coeffs_brackets_nospace', '[' + ','.join(map(str, coeffs)) + ']')
add('coeffs_py_tuple', str(tuple(coeffs)))
add('coeffs_py_list', str(coeffs))

# --- polynomial strings
add('poly_str', str(P.as_expr()))
add('poly_srepr', sp.srepr(P.as_expr()))
add('poly_latex', sp.latex(P.as_expr()))
add('poly_str_nl', str(P.as_expr()) + '\n')
add('poly_factored_deg', f'degree {P.degree()} coeffs ' + ','.join(map(str, coeffs)))

# --- root values
for nd in (17, 20, 30, 36, 50, 60, 90, 100):
    try:
        add(f'r_{nd}', sp.N(sp.Float(0) + sp.sympify(r_str[:2 + nd]), nd).__str__())
    except Exception:
        pass
add('r_raw', r_str)
add('r_raw_nl', r_str + '\n')
add('r_trim100', r_str[:102])
add('t_sq', str(sp.N(sp.sympify(r_str[:80]) ** 2, 60)))

# --- isolating interval
add('a_frac', a_frac)
add('b_frac', b_frac)
add('ab_comma', a_frac + ',' + b_frac)
add('ab_pair', a_frac + ' ' + b_frac)

# --- project answer files (exact bytes)
for rel in ('verify/out/FINAL_ANSWER.json', 'runtime/minpoly_candidate.json',
            'docs/RESULT.md', 'verify/SHA256SUMS'):
    p = os.path.join(ROOT, rel.replace('/', os.sep))
    if os.path.isfile(p):
        add('file:' + rel, open(p, 'rb').read().decode('utf-8', 'replace'))

# --- canonical json structures
add('json_answer_min', json.dumps({
    'degree': P.degree(),
    'coefficients_high_to_low': coeffs,
    'a': a_frac, 'b': b_frac,
}, sort_keys=True, separators=(',', ':')))
add('json_answer_min2', json.dumps({
    'degree': P.degree(),
    'coefficients_high_to_low': coeffs,
    'a': a_frac, 'b': b_frac,
}, indent=1))

hits = []
print(f'{"name":34s} sha256')
print('-' * 100)
for name, b in cands.items():
    h = hashlib.sha256(b).hexdigest()
    flag = '  <<< MATCH' if h == TARGET else ''
    if flag:
        hits.append(name)
    print(f'{name:34s} {h}{flag}')
print()
print('TARGET  ', TARGET)
print('matches:', hits if hits else 'NONE')
