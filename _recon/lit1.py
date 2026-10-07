import urllib.request, urllib.parse, re, os, json, time

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
OUT = r'E:\study\ADB\_recon'


def get(u, timeout=45):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=timeout).read()


def arxiv(q, n=20, tag='q'):
    u = ('https://export.arxiv.org/api/query?search_query=' + urllib.parse.quote(q) +
         f'&start=0&max_results={n}&sortBy=relevance')
    try:
        d = get(u).decode('utf-8', 'replace')
    except Exception as e:
        print('  ERR', e)
        return
    ents = re.findall(r'<entry>(.*?)</entry>', d, re.S)
    print(f'--- arXiv [{tag}] {q!r}: {len(ents)} hits')
    for e in ents:
        t = re.sub(r'\s+', ' ', re.search(r'<title>(.*?)</title>', e, re.S).group(1)).strip()
        i = re.search(r'<id>(.*?)</id>', e, re.S).group(1).strip()
        p = re.search(r'<published>(.*?)</published>', e, re.S)
        au = re.findall(r'<name>(.*?)</name>', e)
        print(f'  {p.group(1)[:10] if p else "?"} | {t[:110]} | {i} | {", ".join(au[:4])}')


for q in ['all:"covering a circle with congruent circles"',
          'ti:"covering" AND ti:"congruent circles"',
          'all:"Melissen" AND all:"covering"',
          'all:"VoxEquinox"',
          'abs:"unit disk" AND abs:"covering" AND abs:"12"',
          'all:"covering a disk with circles"']:
    arxiv(q)
    time.sleep(3)
