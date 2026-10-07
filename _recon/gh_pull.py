import urllib.request, json, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
UA = {'User-Agent': 'Mozilla/5.0'}
ROOT = r'E:\study\ADB\lit\DiskCoveringSolve'
tree = json.load(open(r'E:\study\ADB\_recon\repo_tree.json', encoding='utf-8'))['tree']
prefixes = ('cover12/', 'cover13/')
extra = {'README.md', 'Makefile', '.gitignore'}
paths = [it['path'] for it in tree if it['type'] == 'blob' and (it['path'].startswith(prefixes) or it['path'] in extra)]
print('to download:', len(paths))
ok = fail = 0
for p in paths:
    dst = os.path.join(ROOT, p.replace('/', os.sep))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        ok += 1; continue
    url = 'https://raw.githubusercontent.com/VonEquinox/DiskCoveringSolve/main/' + urllib.parse.quote(p)
    for attempt in range(3):
        try:
            d = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
            open(dst, 'wb').write(d)
            ok += 1
            print(f'  ok {len(d):>9} {p}')
            break
        except Exception as e:
            if attempt == 2:
                fail += 1; print(f'  FAIL {p}: {e}')
            else:
                time.sleep(2)
print('ok', ok, 'fail', fail)
