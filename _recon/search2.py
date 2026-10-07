import urllib.request, urllib.parse, re, gzip, os, sys, time, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'}
OUT = r'E:\study\ADB\_recon'


def get(u, timeout=60):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=timeout)
    d = r.read()
    if r.headers.get('Content-Encoding') == 'gzip':
        d = gzip.decompress(d)
    return d


def ddg(q):
    h = get('https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(q)).decode('utf-8', 'replace')
    links = re.findall(r'result__a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', h, re.S)
    snips = re.findall(r'result__snippet[^>]*>(.*?)</a>', h, re.S)
    print('###', q)
    for u2, t2 in links[:10]:
        t2 = re.sub(r'<[^>]+>', '', t2); t2 = re.sub(r'\s+', ' ', t2).strip()
        m = re.search(r'uddg=([^&]+)', u2)
        real = urllib.parse.unquote(m.group(1)) if m else u2
        print(f'  {t2[:90]}  <{real[:150]}>')
    for s in snips[:8]:
        s = re.sub(r'<[^>]+>', '', s); s = re.sub(r'\s+', ' ', s).strip()
        print('    snip:', s[:220])


for q in ['Melissen "Packing and covering with circles" thesis pdf utrecht',
          'Melissen 1997 covering a circle 12 circles optimal radius 2.769',
          'site:repository.uu.nl Melissen packing covering circles']:
    try:
        ddg(q)
    except Exception as e:
        print('ERR', e)
    time.sleep(2)
