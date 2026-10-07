import json
import os
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
UA = {'User-Agent': 'Mozilla/5.0'}
OUT = r'E:\study\ADB\_recon\benchmark'
os.makedirs(OUT, exist_ok=True)


def get(u, timeout=60):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=timeout).read()


tree = json.loads(get('https://api.github.com/repos/pikaaa345/disk-covering-benchmark/git/trees/main?recursive=1'))
items = [it for it in tree.get('tree', []) if it['type'] == 'blob']
print('files in repo:', len(items), 'truncated:', tree.get('truncated'))
for it in items:
    print(f"  {it.get('size',0):>9}  {it['path']}")
json.dump(tree, open(os.path.join(OUT, 'tree.json'), 'w', encoding='utf-8'), indent=1)
