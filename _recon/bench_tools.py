import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
t = json.load(open(r'E:\study\ADB\_recon\benchmark\tree.json', encoding='utf-8'))['tree']
for it in t:
    p = it['path']
    if p.startswith('tools/') or 'protocol' in p or 'answer' in p.lower() or p.endswith('.py'):
        print(f"{it.get('size',0):>9}  {p}")
