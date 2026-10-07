import re
h = open(r'E:\study\ADB\_recon\circovcir.html', encoding='utf-8', errors='replace').read()
t = re.sub(r'<[^>]+>', ' ', h)
t = t.replace('&radic;', 'sqrt').replace('&aacute;', 'a').replace('&oacute;', 'o')
t = re.sub(r'[ \t]+', ' ', t)
t = re.sub(r'\n\s*\n+', '\n', t)
print(t)
