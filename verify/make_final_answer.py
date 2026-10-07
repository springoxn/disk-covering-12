"""Assemble the compact final answer (submission object)."""
from __future__ import annotations
import json

import sympy as sp

t = sp.symbols('t')
cand = json.load(open(r'E:\study\ADB\runtime\minpoly_candidate.json', encoding='utf-8'))
checks = json.load(open(r'E:\study\ADB\verify\out\minpoly_checks.json', encoding='utf-8'))
kx = json.load(open(r'E:\study\ADB\verify\out\krawczyk.json', encoding='utf-8'))
zero = json.load(open(r'E:\study\ADB\verify\out\minpoly_zero_certificate.json', encoding='utf-8'))
cov = json.load(open(r'E:\study\ADB\verify\out\coverage_certificate.json', encoding='utf-8'))
far = json.load(open(r'E:\study\ADB\verify\out\farkas_independent.json', encoding='utf-8'))
en = json.load(open(r'E:\study\ADB\verify\out\energy_independent.json', encoding='utf-8'))
cv = json.load(open(r'E:\study\ADB\verify\out\convexity_independent.json', encoding='utf-8'))

coeffs = [int(x) for x in cand['P_coeffs_desc']]
P = sp.Poly(sum(c * t ** i for i, c in enumerate(reversed(coeffs))), t)

out = {
    'problem': 'r_D(12): cover the closed unit disk by 12 closed congruent disks with minimal radius',
    'answer': {
        'minimal_polynomial': {
            'degree': int(P.degree()),
            'coefficients_high_to_low': coeffs,
            'polynomial_tex': sp.latex(P.as_expr()),
            'primitive': bool(checks['primitive']),
            'leading_coefficient': int(checks['leading_coeff']),
            'height': int(checks['height']),
            'irreducible_over_Q': True,
            'irreducibility_certificate': {
                'exact_factorisation_factor_degrees': checks['factor_degrees'],
                'modular_prime': int(checks['modular_prime']),
                'irreducible_mod_p': bool(checks['irreducible_mod_p']),
            },
            'isolating_interval': {
                'a': checks['a'], 'b': checks['b'],
                'a_decimal': checks['a_decimal'], 'b_decimal': checks['b_decimal'],
                'P_a_nonzero': bool(checks['P(a)_nonzero']),
                'P_b_nonzero': bool(checks['P(b)_nonzero']),
                'roots_in_interval': int(checks['roots_in_ab']),
                'real_roots_of_P': int(checks['real_roots_total']),
            },
        },
        'optimal_radius_decimal': (
            '0.361102963744508644113087702017065180848530565591618515449660087986'
            '3145593819893952803094927006995747013190719138921601'),
        'r_star_in_isolating_interval': bool(checks['r_star_in_ab']),
    },
    'configuration': {
        'symmetry': 'D3 (order 6)',
        'rotation_R': 'R(x,y) = ( -(x + sqrt(3) y)/2 , (sqrt(3) x - y)/2 )  (2*pi/3)',
        'centers_ordered': [
            'R^k (u c,  u s)', 'R^k (u c, -u s)', 'R^k (-v, 0)', 'R^k (w, 0)',
            'for k = 0,1,2 successively',
        ],
        'parameters': 'c = cos h, s = sin h, z = sqrt(3)',
        'defining_system': '(see docs/RESULT.md section 1.2: E1..E6 plus the seven linear stress equations and the normalisation)',
        'uniqueness': {
            'method': 'Krawczyk operator with exact rational interval arithmetic',
            'K(X) subset int(X)': bool(kx['krawczyk_containment']),
            'contraction_inf_norm_upper': kx['contraction_inf_norm_upper'],
            'unique_root_in_box': bool(kx['unique_root_in_box']),
            'box_radius': kx['rho'],
        },
        'coordinates_certified_box': {n: kx['box'][i] for i, n in enumerate(kx['variable_order'])},
    },
    'P_of_root_is_zero': {
        'certificate': 'verify/out/minpoly_zero_certificate.json',
        'all_checks_passed': bool(zero['all_passed']),
        'elimination_resultant_degree': int(zero['E_degree']),
    },
    'coverage': {
        'certificate': 'verify/out/coverage_certificate.json',
        'all_checks_passed': bool(cov['all_passed']),
        'triangulation': {'vertices': 21, 'edges': 51, 'faces': 31},
        'min_inactive_r2_margin': cov['inactive_r2_margins'],
    },
    'global_optimality': {
        'upper_bound': 'proved here (verify/coverage_cert.py)',
        'lower_bound': ('every computational certificate of the third-party proof '
                        '(enumeration completeness, Farkas layer, energy layer, '
                        'candidate convexity) has been recomputed here by '
                        'independent code; the reduction itself is a mathematical '
                        'argument that was checked by reading, not formalised'),
        'independent_rechecks_done': {
            'brown_enumeration_counts': 'verified (verify/brown_counts.py)',
            'farkas_layer': far,
            'energy_layer': en,
            'candidate_convexity': cv,
            'lean_formalisation': 'lean/Covering.lean (triangle covering lemma, Mathlib v4.34.0-rc2)',
            'third_party_master_verifier_replayed': True,
        },
        'computational_certificates_independently_recomputed': True,
        'mathematical_reduction_independently_formalised': False,
        'see': 'docs/RESULT.md sections 4.3 and 4.4',
    },
}
with open(r'E:\study\ADB\verify\out\FINAL_ANSWER.json', 'w', encoding='utf-8') as fh:
    json.dump(out, fh, indent=1)
print(json.dumps({k: v for k, v in out.items() if k != 'configuration'}, indent=1)[:3000])
print('\nwritten verify/out/FINAL_ANSWER.json')
