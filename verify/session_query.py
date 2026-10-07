"""Query the DSH session log by keyword and print relative times.

    python verify/session_query.py run_all "ALL VERIFIED"
    python verify/session_query.py --type tool/call pwsh
"""
import io
import json
import sys

import zstandard

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SESSION = (r'C:\Users\lenovo\.dsh\sessions\--E-study-ADB--'
           r'\session-4eaf037b-fa17-4ed5-93a8-0b8f47cb2fe4\session.v3.jsonl.zstd')


def hms(sec):
    sec = int(round(sec))
    return 'T+%02d:%02d:%02d' % (sec // 3600, (sec % 3600) // 60, sec % 60)


def flatten(x):
    """All text inside an arbitrary nested structure."""
    out = []
    if isinstance(x, str):
        out.append(x)
    elif isinstance(x, dict):
        for v in x.values():
            out.extend(flatten(v))
    elif isinstance(x, list):
        for v in x:
            out.extend(flatten(v))
    return out


def main():
    opts = dict(a[2:].split('=', 1) for a in sys.argv[1:] if a.startswith('--') and '=' in a)
    switches = {a[2:] for a in sys.argv[1:] if a.startswith('--') and '=' not in a}
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    types = [opts['type']] if 'type' in opts else []
    width = int(opts.get('width', 220))
    only_turn = int(opts['turn']) if 'turn' in opts else None
    stride = int(opts.get('stride', 1))
    skip_first = int(opts.get('skip', 0))
    seen = 0

    dctx = zstandard.ZstdDecompressor()
    recs = []
    with open(SESSION, 'rb') as fh:
        with dctx.stream_reader(fh) as r:
            buf = io.TextIOWrapper(r, encoding='utf-8', errors='replace')
            for line in buf:
                line = line.strip()
                if line:
                    try:
                        recs.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    t0 = next(r['createdAt'] for r in recs if r.get('type') == 'session') / 1000.0

    for rec in recs:
        t = rec.get('time')
        if not isinstance(t, (int, float)):
            continue
        if types and rec.get('type') not in types:
            continue
        blob = ' '.join(flatten(rec.get('data')))
        if args and not all(a.lower() in blob.lower() for a in args):
            continue
        data = rec.get('data') or {}
        turn = data.get('turn')
        step = data.get('step')
        if only_turn is not None and turn != only_turn:
            continue
        seen += 1
        if seen <= skip_first or (seen - skip_first - 1) % stride:
            continue
        name = data.get('name') or ''
        prefix = '%s  %-16s' % (hms(t / 1000.0 - t0), rec.get('type'))
        if turn is not None:
            prefix += ' t%s/%s' % (turn, step)
        if name:
            prefix += ' %s' % name
        print(prefix)
        print('    ' + ' '.join(blob.split())[:width])
    return 0


if __name__ == '__main__':
    sys.exit(main())
