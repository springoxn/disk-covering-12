"""Session timeline: locate the idle gaps that separate the turns."""
import os
import sys
from datetime import datetime

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
        rows.append((st.st_ctime, os.path.relpath(p, ROOT)))
rows.sort()

print('start :', datetime.fromtimestamp(rows[0][0]), rows[0][1])
print('end   :', datetime.fromtimestamp(rows[-1][0]), rows[-1][1])
print()
print('gaps > 1500 s (candidate idle boundaries):')
prev_t, prev_f = rows[0]
total_gap = 0.0
for c, rel in rows[1:]:
    d = c - prev_t
    if d > 1500:
        total_gap += d
        print(f'  {d:7.0f} s = {d/60:5.1f} min   {datetime.fromtimestamp(prev_t):%H:%M:%S} '
              f'({prev_f})  ->  {datetime.fromtimestamp(c):%H:%M:%S} ({rel})')
    prev_t, prev_f = c, rel
print()
print(f'total idle (gaps>1500s) = {total_gap:.0f} s = {total_gap/3600:.2f} h')
span = rows[-1][0] - rows[0][0]
print(f'wall span               = {span:.0f} s = {span/3600:.2f} h')
print(f'span minus idle gaps    = {span-total_gap:.0f} s = {(span-total_gap)/3600:.2f} h')
