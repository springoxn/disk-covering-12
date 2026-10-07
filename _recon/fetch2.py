import urllib.request, os, sys, re
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
urls = {
 'circovcir': 'https://erich-friedman.github.io/packing/circovcir/',
 'cirincir': 'https://erich-friedman.github.io/packing/cirincir/',
}
os.makedirs(r'E:\study\ADB\_recon', exist_ok=True)
for k, u in urls.items():
    try:
        d = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read()
        p = rf'E:\study\ADB\_recon\{k}.html'
        open(p, 'wb').write(d)
        print(k, len(d), '->', p)
    except Exception as e:
        print(k, 'ERR', e)
