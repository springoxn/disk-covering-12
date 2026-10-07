"""Score this run with the benchmark's official score.py.

Timing conventions
------------------
Two zero points exist in the record, and every elapsed value below names which
one it uses:

``session-log``    T+00:00:00 = the DSH session header ``createdAt``
                   (epoch ms 1791366570764).  This is the recorder of record:
                   every event in the session log carries a timestamp, so the
                   whole run can be replayed against one clock.
                   Source: ``verify/session_timeline.py``.
``first-artifact`` T+00:00:00 = creation time of the earliest file produced by
                   the run (17:52:01, a ``_recon`` scrape taken 151 s after the
                   session header).  Used by the earlier reconstruction in
                   ``verify/timing_evidence.py``.

Neither was pre-registered.  The benchmark requires a frozen timing contract for
formal records; this run does not have one, so the scores below are self-computed
under the published formula, not a formal entry.

Milestones are taken from the session log (``verify/session_timeline.py``) and
cross-checked against filesystem mtimes (``verify/file_timeline.py``); they agree
to within a few seconds.
"""
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r'E:\study\ADB'
SCORE = os.path.join(ROOT, r'_recon\benchmark\score.py')
REF = '21600'
FIRST_ARTIFACT_OFFSET = 151          # session-log zero is 151 s before first artifact
HUMAN_GAPS = 749                     # total human-side gap, session log

# (label, elapsed_seconds, zero_point, note)
CASES = [
    ('A  round-1 delivery presented (T+02:21:43)',
     8503, 'session-log', 'first complete delivery of round 1'),
    ('A\' same node, first-artifact zero',
     8503 - FIRST_ARTIFACT_OFFSET, 'first-artifact', 'reconstructed from filesystem ctime'),
    ('B  round-1 turn finished (T+03:29:13)',
     12553, 'session-log', 'end of turn 1, after the LLL cross-check landed'),
    ('C  round-2 end-to-end ALL VERIFIED (T+04:44:20)',
     17060, 'session-log', 'mathematical delivery; run_all.py 14 steps / 8 certificates'),
    ('C\' same node, first-artifact zero',
     17060 - FIRST_ARTIFACT_OFFSET, 'first-artifact', 'value published in the earlier draft'),
    ('C\'\' mathematical delivery, human-side gaps excluded',
     17060 - HUMAN_GAPS, 'session-log', 'minus 749 s of human response time (5 gaps)'),
    ('D  goal complete / turn 2 end (T+04:44:56)',
     17096, 'session-log', 'goal marked complete, 36 s after ALL VERIFIED'),
    ('E  fingerprint follow-up recorded (T+04:55:21)',
     17721, 'session-log', 'benchmark_fingerprint.json written'),
    ('E\' same node, first-artifact zero',
     17721 - FIRST_ARTIFACT_OFFSET, 'first-artifact', 'reconstructed from filesystem ctime'),
]

out = []
for label, t, zero, note in CASES:
    p = subprocess.run([sys.executable, SCORE, '--n', '12', '--reference-seconds', REF,
                        '--elapsed-seconds', str(t), '--status', 'completed'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    j = json.loads(p.stdout)
    out.append({'case': label, 'note': note, 'zero_point': zero, **j})
    print('%-52s  T=%6d s (%4.2f h)  %-14s -> score = %s'
          % (label, t, t / 3600, zero, j['score']))
print()
print('reference_seconds =', REF, '(published value in results/n12.json)')
json.dump({'reference_seconds': REF, 'cases': out},
          open(os.path.join(ROOT, r'verify\out\benchmark_score.json'), 'w', encoding='utf-8'),
          indent=1)
print('written verify/out/benchmark_score.json')
