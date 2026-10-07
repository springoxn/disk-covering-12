import json
import os
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
UA = {'User-Agent': 'Mozilla/5.0'}
OUT = r'E:\study\ADB\_recon\benchmark'
for p in ['problems/n12.zh.json', 'problems/n12.json', 'benchmark.json']:
    u = 'https://raw.githubusercontent.com/pikaaa345/disk-covering-benchmark/main/' + p
    try:
        d = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
    except Exception as e:
        print('FAIL', p, e)
        continue
    dst = os.path.join(OUT, p.replace('/', '_'))
    open(dst, 'wb').write(d)
    print(f'--- {p} ({len(d)} bytes) -> {dst}')
    try:
        j = json.loads(d)
        print(json.dumps(j, ensure_ascii=False, indent=1)[:3000])
    except Exception:
        pass
