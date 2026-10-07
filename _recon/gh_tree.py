import urllib.request, json, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
UA = {'User-Agent': 'Mozilla/5.0'}
def get(u, timeout=60):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=timeout).read()

# 1) repo tree via API
try:
    d = json.loads(get('https://api.github.com/repos/VonEquinox/DiskCoveringSolve/git/trees/main?recursive=1'))
    open(r'E:\study\ADB\_recon\repo_tree.json', 'w', encoding='utf-8').write(json.dumps(d, indent=1))
    items = d.get('tree', [])
    print('tree entries:', len(items), 'truncated:', d.get('truncated'))
    for it in items:
        if it['type'] == 'blob':
            print(f"{it.get('size',0):>10}  {it['path']}")
except Exception as e:
    print('API ERR', e)
