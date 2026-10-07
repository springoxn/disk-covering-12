import re
h = open(r'E:\study\ADB\_recon_friedman_index.html', encoding='utf-8', errors='replace').read()
for m in re.finditer(r'<A\s+HREF="([^"]+)"\s*>(.*?)</A>', h, re.S | re.I):
    label = re.sub(r'<[^>]+>', '', m.group(2)).strip()
    print(m.group(1), '|', label[:70])
print('=' * 40)
# print any anchor text mentioning cover
for m in re.finditer(r'cover', h, re.I):
    print('HIT', h[max(0, m.start()-120):m.start()+120].replace('\n', ' '))
