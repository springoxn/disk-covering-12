import urllib.request, urllib.parse, re, json, time, gzip, os, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
      'Accept-Language': 'en-US,en;q=0.9'}
OUT = r'E:\study\ADB\_recon'


def get(u, timeout=45):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=timeout)
    d = r.read()
    if r.headers.get('Content-Encoding') == 'gzip':
        d = gzip.decompress(d)
    return d.decode('utf-8', 'replace')


def ddg(q, tag):
    allout = []
    for base in ['https://html.duckduckgo.com/html/?q=', 'https://lite.duckduckgo.com/lite/?q=']:
        try:
            h = get(base + urllib.parse.quote(q))
        except Exception as e:
            allout.append(f'  DDG ERR {base} {e}'); continue
        # extract result links + snippets
        links = re.findall(r'result__a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', h, re.S)
        if not links:
            links = re.findall(r'<a[^>]+class="result-link"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', h, re.S)
        allout.append(f'=== {base} :: {q!r} :: {len(links)} links, html {len(h)}')
        for u2, t2 in links[:12]:
            t2 = re.sub(r'<[^>]+>', '', t2)
            t2 = re.sub(r'\s+', ' ', t2).strip()
            allout.append(f'   {t2[:100]}  <{u2[:160]}>')
        snips = re.findall(r'result__snippet[^>]*>(.*?)</a>', h, re.S)
        for s in snips[:10]:
            s = re.sub(r'<[^>]+>', '', s); s = re.sub(r'\s+', ' ', s).strip()
            allout.append(f'     snip: {s[:250]}')
        if links:
            break
    txt = '\n'.join(allout)
    p = os.path.join(OUT, f'ddg_{tag}.txt')
    open(p, 'w', encoding='utf-8').write(txt)
    print(txt)
    print(f'[saved {p}]')


qs = [('Melissen covering a circle with congruent circles 1997', 'melissen'),
      ('VoxEquinox covering circles proof', 'voxequinox'),
      ('"circles covering circles" 12 congruent circles covering radius optimal', 'circov'),
      ('Melissen thesis "Packing and covering with circles" Utrecht', 'thesis')]
for q, tag in qs:
    ddg(q, tag)
    time.sleep(2)
