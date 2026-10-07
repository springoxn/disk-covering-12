"""Filesystem timeline in relative time.

Zero point = the DSH session header ``createdAt`` (same zero as
``verify/session_timeline.py``), so file evidence and session evidence share one
clock. Writes the full listing to ``runtime/file_timeline.txt`` and prints a
curated subset.
"""
import os
import sys
from datetime import datetime

import zstandard
import io
import json

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = r'E:\study\ADB'
SESSION = (r'C:\Users\lenovo\.dsh\sessions\--E-study-ADB--'
           r'\session-4eaf037b-fa17-4ed5-93a8-0b8f47cb2fe4\session.v3.jsonl.zstd')
OUT = r'E:\study\ADB\runtime\file_timeline.txt'
SKIP = {'lit', '_recon', '.git', '__pycache__', '.agents', 'node_modules'}


def session_start():
    with open(SESSION, 'rb') as fh:
        with zstandard.ZstdDecompressor().stream_reader(fh) as r:
            for line in io.TextIOWrapper(r, encoding='utf-8', errors='replace'):
                rec = json.loads(line)
                if rec.get('type') == 'session':
                    return rec['createdAt'] / 1000.0
    raise SystemExit('no session header')


def hms(sec):
    sec = int(round(sec))
    sign = '-' if sec < 0 else ''
    sec = abs(sec)
    return 'T%s%02d:%02d:%02d' % (sign, sec // 3600, (sec % 3600) // 60, sec % 60)


def main():
    t0 = session_start()
    rows = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP]
        for f in filenames:
            p = os.path.join(dirpath, f)
            try:
                st = os.stat(p)
            except OSError:
                continue
            rows.append((st.st_mtime, os.path.relpath(p, ROOT).replace('\\', '/'), st.st_size))
    rows.sort()
    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write('offset   mtime                bytes  path\n')
        for m, rel, size in rows:
            fh.write('%-9s  %s  %8d  %s\n'
                     % (hms(m - t0), datetime.fromtimestamp(m).strftime('%Y-%m-%d %H:%M:%S'), size, rel))
    print('files:', len(rows), ' full listing ->', OUT)
    print()
    print('first :', hms(rows[0][0] - t0), rows[0][1])
    print('last  :', hms(rows[-1][0] - t0), rows[-1][1])

    keep = ('tools/', 'verify/', 'runtime/', 'lean/', 'docs/', 'README', 'handoff', 'AGENTS')
    print()
    print('--- scripts, certificates and docs (first appearance per basename) ---')
    seen = set()
    for m, rel, size in rows:
        b = os.path.basename(rel)
        if b in seen or not rel.startswith(keep) or b.endswith(('.pyc',)):
            continue
        seen.add(b)
        print('  %-9s  %-52s %8d' % (hms(m - t0), rel, size))


if __name__ == '__main__':
    main()
