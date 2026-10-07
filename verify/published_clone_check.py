"""Verify the PUBLISHED artifact, not the local one.

Clones the public repository into a scratch directory, then checks it from the
outside:
  1. every file listed in verify/SHA256SUMS hashes to its recorded value
     (this also proves .gitattributes kept the checkout byte-identical);
  2. the publisher's own fingerprint script reproduces the reference sha256
     from the committed submission/ package.

Writes verify/out/published_clone_check.json.
    python verify/published_clone_check.py [repo-url]
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
URL = sys.argv[1] if len(sys.argv) > 1 else 'https://github.com/springoxn/disk-covering-12'
OUT = r'E:\study\ADB\verify\out\published_clone_check.json'

tmp = os.path.join(tempfile.gettempdir(), 'adb-published-clone')
if os.path.isdir(tmp):
    shutil.rmtree(tmp)


def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                       encoding='utf-8', errors='replace', timeout=600)
    return p.returncode, (p.stdout or '') + (p.stderr or '')


rc, out = run(['git', 'clone', '--quiet', URL, tmp])
if rc != 0:
    raise SystemExit('clone failed: ' + out[:400])

rc, listing = run(['git', 'ls-files'], cwd=tmp)
tracked = [x for x in listing.splitlines() if x.strip()]
rc, head = run(['git', 'rev-parse', 'HEAD'], cwd=tmp)
head = head.strip()
rc, when = run(['git', 'log', '-1', '--format=%cI'], cwd=tmp)

ok = bad = 0
mismatches = []
with open(os.path.join(tmp, 'verify', 'SHA256SUMS'), encoding='utf-8') as fh:
    for line in fh:
        line = line.rstrip('\n')
        if not line:
            continue
        want, rel = line.split('  ', 1)
        try:
            got = hashlib.sha256(open(os.path.join(tmp, rel), 'rb').read()).hexdigest()
        except OSError:
            mismatches.append(rel)
            bad += 1
            continue
        if got == want:
            ok += 1
        else:
            mismatches.append(rel)
            bad += 1

radius = open(os.path.join(tmp, 'submission', 'radius.txt'), encoding='utf-8').read().strip()
coef = os.path.join(tmp, 'submission', 'coefficients.json')
tool = os.path.join(tmp, '_recon', 'benchmark', 'diskcover_answer.py')
EXPECTED = '35d604a5ea1b1fe5c52c30337743c1a8142b69827023284f9597e1ca9cb8f947'
rc, out = run([sys.executable, tool, '--n', '12', '--coefficients', coef,
               '--radius', radius, '--expected-sha256', EXPECTED])
body = json.loads(out) if out.strip().startswith('{') else {}

result = {
    'repo_url': URL,
    'commit': head,
    'commit_date': when.strip(),
    'tracked_files': len(tracked),
    'manifest_ok': ok,
    'manifest_bad': bad,
    'manifest_mismatches': mismatches,
    'selfcheck_exit_code': rc,
    'selfcheck_sha256': body.get('sha256'),
    'selfcheck_matches_reference': body.get('matches_reference'),
    'expected_sha256': EXPECTED,
}
json.dump(result, open(OUT, 'w', encoding='utf-8'), indent=1)
print('repo            :', URL)
print('commit          :', head[:12], when.strip())
print('tracked files   :', len(tracked))
print('manifest        : %d ok, %d bad' % (ok, bad))
print('selfcheck       : exit %d, sha256 = %s, match = %s'
      % (rc, body.get('sha256'), body.get('matches_reference')))
print('written         :', OUT)
shutil.rmtree(tmp, ignore_errors=True)
