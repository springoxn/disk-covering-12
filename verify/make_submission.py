"""Assemble the self-contained submission package under submission/.

Follows the benchmark's answer protocol v1 (``diskcover-minpoly-v1``):
what a submitter must hand over is the integer coefficient array (constant term
first), a high-precision radius, and the fingerprint produced by the publisher's
own script.  The proof package is not required by the protocol.

Writes, all byte-deterministic:
    submission/coefficients.json   low -> high integer array, no floats
    submission/radius.txt          high-precision decimal radius (1000 digits)
    submission/command.txt         the exact command a verifier should run
    submission/selfcheck.txt       raw stdout/stderr + exit code of that command
    submission/answer.json         canonical JSON, its sha256, match flag
"""
import json
import os
import subprocess
import sys

sys.set_int_max_str_digits(400000)
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = r'E:\study\ADB'
TOOL = os.path.join(ROOT, r'_recon\benchmark\diskcover_answer.py')
OUT = os.path.join(ROOT, 'submission')
EXPECTED = '35d604a5ea1b1fe5c52c30337743c1a8142b69827023284f9597e1ca9cb8f947'


def main():
    os.makedirs(OUT, exist_ok=True)

    cand = json.load(open(os.path.join(ROOT, r'runtime\minpoly_candidate.json'),
                          encoding='utf-8'))
    desc = [int(x) for x in cand['P_coeffs_desc']]       # a_37 ... a_0
    asc = list(reversed(desc))                           # a_0 ... a_37
    coef = os.path.join(OUT, 'coefficients.json')
    with open(coef, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(asc, fh)
    print('degree                :', len(asc) - 1)
    print('coefficients.json     :', os.path.getsize(coef), 'bytes')

    r_str = json.load(open(os.path.join(ROOT, r'runtime\hp_root_1000.json'),
                           encoding='utf-8'))['r']
    rad = os.path.join(OUT, 'radius.txt')
    with open(rad, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(r_str.strip() + '\n')
    print('radius.txt            : %d significant digits' % len(r_str.strip().replace('.', '')))

    cmd_txt = ('python _recon/benchmark/diskcover_answer.py --n 12 '
               '--coefficients submission/coefficients.json '
               '--radius "$(cat submission/radius.txt)" '
               '--expected-sha256 ' + EXPECTED + '\n')
    with open(os.path.join(OUT, 'command.txt'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(cmd_txt)
    print('command.txt           : written')

    cmd = [sys.executable, TOOL, '--n', '12', '--coefficients', coef,
           '--radius', r_str, '--expected-sha256', EXPECTED]
    p = subprocess.run(cmd, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    with open(os.path.join(OUT, 'selfcheck.txt'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('$ python _recon/benchmark/diskcover_answer.py --n 12 '
                 '--coefficients submission/coefficients.json '
                 '--radius "<submission/radius.txt>" '
                 '--expected-sha256 %s\n\n' % EXPECTED)
        fh.write(p.stdout)
        if p.stderr:
            fh.write('\nSTDERR:\n' + p.stderr)
        fh.write('\nexit code: %d\n' % p.returncode)
    print('selfcheck.txt         : exit code', p.returncode)

    out = json.loads(p.stdout)
    json.dump({'protocol': out.get('protocol_version') or 'diskcover-minpoly-v1',
               'n': out.get('n'),
               'sha256': out.get('sha256'),
               'expected_sha256': EXPECTED,
               'matches_reference': out.get('matches_reference'),
               'canonical_json': out.get('canonical_json'),
               'payload': out.get('answer')},
              open(os.path.join(OUT, 'answer.json'), 'w', encoding='utf-8'),
              indent=1, ensure_ascii=False)
    print('answer.json           : sha256 =', out.get('sha256'),
          ' match =', out.get('matches_reference'))
    return 0 if p.returncode == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
