import os
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
UA = {'User-Agent': 'Mozilla/5.0'}
OUT = r'E:\study\ADB\_recon\benchmark'
os.makedirs(OUT, exist_ok=True)
paths = ['docs/diskcover_answer.py', 'docs/check_tools.py', 'docs/answer-protocol.txt',
         'docs/protocol.txt', 'docs/delivery.md', 'tools/score.py']
for p in paths:
    u = 'https://raw.githubusercontent.com/pikaaa345/disk-covering-benchmark/main/' + p
    try:
        d = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
    except Exception as e:
        print('FAIL', p, e)
        continue
    dst = os.path.join(OUT, os.path.basename(p))
    open(dst, 'wb').write(d)
    print(f'{len(d):>8}  {p} -> {dst}')
