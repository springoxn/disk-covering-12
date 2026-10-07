import json
import os
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
UA = {'User-Agent': 'Mozilla/5.0'}
OUT = r'E:\study\ADB\_recon\benchmark'
for p in ['results/n12.json', 'results/README.md']:
    u = 'https://raw.githubusercontent.com/pikaaa345/disk-covering-benchmark/main/' + p
    try:
        d = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
    except Exception as e:
        print('FAIL', p, e)
        continue
    dst = os.path.join(OUT, p.replace('/', '_'))
    open(dst, 'wb').write(d)
    print(f'===== {p} ({len(d)} bytes) =====')
    print(d.decode('utf-8', 'replace')[:4000])
    print()

# tail of benchmark.json: the n=12 entry plus any scoring block
j = json.load(open(os.path.join(OUT, 'benchmark.json'), encoding='utf-8'))
print('top-level keys:', list(j.keys()))
for k in ('scoring', 'score_formula', 'reference_seconds', 'notes'):
    if k in j:
        print(k, '=', json.dumps(j[k], ensure_ascii=False)[:600])
for t in j['tasks']:
    if t['n'] in (11, 12):
        print()
        print('task n =', t['n'], ':')
        print(json.dumps(t, ensure_ascii=False, indent=1))
