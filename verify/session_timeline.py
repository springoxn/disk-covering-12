"""Extract an authoritative relative-time timeline from the DSH session log.

The session log is the recorder of record: every event carries an epoch-ms
timestamp (``time``), and the session header carries the task start
(``createdAt``). We emit only elapsed offsets, never absolute clock times, so
the report can be written in relative time.

Usage:
    python verify/session_timeline.py            # human digest
    python verify/session_timeline.py --json     # also dump verify/out/session_timeline.json
"""
import io
import json
import os
import sys

import zstandard

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SESSION = (r'C:\Users\lenovo\.dsh\sessions\--E-study-ADB--'
           r'\session-4eaf037b-fa17-4ed5-93a8-0b8f47cb2fe4\session.v3.jsonl.zstd')
OUT = r'E:\study\ADB\verify\out\session_timeline.json'


def hms(sec):
    sec = int(round(sec))
    return 'T+%02d:%02d:%02d' % (sec // 3600, (sec % 3600) // 60, sec % 60)


def blocks(msg):
    """Flatten one message's content blocks into (kind, text)."""
    out = []
    content = (msg or {}).get('content')
    if isinstance(content, str):
        return [('text', content)]
    for c in content or []:
        if not isinstance(c, dict):
            continue
        k = c.get('type')
        if k == 'text':
            out.append(('text', c.get('text', '')))
        elif k == 'reasoning':
            out.append(('reasoning', c.get('text', '')))
        elif k in ('tool-call', 'tool_use'):
            out.append(('tool-call', c.get('name', '?')))
        elif k in ('tool-result', 'tool_result'):
            out.append(('tool-result', ''))
        elif k == 'file':
            out.append(('file', (c.get('attachment') or {}).get('name', '?')))
    return out


def main():
    want_json = '--json' in sys.argv
    dctx = zstandard.ZstdDecompressor()
    recs = []
    with open(SESSION, 'rb') as fh:
        with dctx.stream_reader(fh) as r:
            buf = io.TextIOWrapper(r, encoding='utf-8', errors='replace')
            for line in buf:
                line = line.strip()
                if not line:
                    continue
                try:
                    recs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    t0 = next(r['createdAt'] for r in recs if r.get('type') == 'session') / 1000.0
    events = []
    for r in recs:
        t = r.get('time')
        if not isinstance(t, (int, float)):
            continue
        events.append((t / 1000.0 - t0, r))
    events.sort(key=lambda x: x[0])
    span = events[-1][0]

    print('session start = T+00:00:00  (session header createdAt)')
    print('records=%d  span=%s  (%.2f h)' % (len(events), hms(span), span / 3600))
    print()

    print('=== user turns ===')
    for e, r in events:
        if r.get('type') != 'user/message':
            continue
        txt = ' '.join(x for k, x in blocks(r['data']) if k in ('text', 'file'))
        print('  %s  %s' % (hms(e), ' '.join(txt.split())[:150]))

    print()
    print('=== turn boundaries ===')
    for e, r in events:
        if r.get('type') == 'turn/end':
            print('  %s  turn %s end  reason=%s'
                  % (hms(e), r['data'].get('turn'), (r['data'].get('reason') or {}).get('kind')))
        elif r.get('type') == 'compaction/start':
            print('  %s  >>> compaction start' % hms(e))
        elif r.get('type') == 'compaction/end':
            print('  %s  <<< compaction end' % hms(e))
        elif r.get('type') == 'command/done':
            print('  %s  command %s : %s'
                  % (hms(e), r['data'].get('name'), str(r['data'].get('text'))[:90]))
        elif r.get('type') == 'deliverables/presented':
            files = ', '.join(os.path.basename(f['path']) for f in r['data'].get('files', []))
            print('  %s  presented: %s' % (hms(e), files))
        elif r.get('type') == 'goal/change':
            print('  %s  goal %s -> phase=%s'
                  % (hms(e), r['data'].get('operation'),
                     (r['data'].get('goal') or {}).get('phase')))

    print()
    print('=== assistant text milestones ===')
    for e, r in events:
        if r.get('type') != 'assistant/message':
            continue
        txt = ' '.join(x for k, x in blocks(r['data'].get('message')) if k == 'text')
        txt = ' '.join(txt.split())
        if txt:
            print('  %s  %s' % (hms(e), txt[:140]))

    print()
    print('=== human-side gaps (assistant idle -> next human message) ===')
    marks = []
    for e, r in events:
        t = r.get('type')
        d = r.get('data') or {}
        if t == 'turn/end':
            marks.append((e, 'assistant turn %s ended' % d.get('turn')))
        elif t == 'user/message':
            txt = ' '.join(x for k, x in blocks(d) if k in ('text', 'file'))
            txt = ' '.join(txt.split())
            if txt and not txt.startswith('<system-reminder>') \
                    and not txt.startswith('Current runtime context') \
                    and 'automatically generated checkpoint' not in txt:
                marks.append((e, 'human: %s' % txt[:70]))
    prev = None
    total = 0.0
    for e, what in marks:
        if prev is not None and what.startswith('human:') and prev[1].startswith('assistant'):
            gap = e - prev[0]
            total += gap
            print('  %s -> %s   %6.0f s = %4.1f min   %s'
                  % (hms(prev[0]), hms(e), gap, gap / 60, what))
        prev = (e, what)
    print('  total human-side gap = %.0f s = %.1f min' % (total, total / 60))

    print()
    print('=== tool usage by turn ===')
    per_turn = {}
    for e, r in events:
        if r.get('type') == 'tool/call':
            d = r['data']
            per_turn.setdefault(d.get('turn'), []).append((e, d.get('name')))
    for turn in sorted(per_turn, key=lambda x: (x is None, x)):
        calls = per_turn[turn]
        names = {}
        for _, n in calls:
            names[n] = names.get(n, 0) + 1
        top = ', '.join('%s x%d' % (k, v) for k, v in sorted(names.items(), key=lambda kv: -kv[1]))
        print('  turn %-4s %s -> %s   %s   (%d calls)'
              % (turn, hms(calls[0][0]), hms(calls[-1][0]), top, len(calls)))

    if want_json:
        json.dump({
            'session_file': SESSION,
            'span_seconds': round(span, 3),
            'n_records': len(events),
            'events': [{'elapsed': round(e, 3), 'hhmmss': hms(e), 'type': r.get('type'),
                        'turn': (r.get('data') or {}).get('turn')} for e, r in events],
        }, open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        print('\nwritten:', OUT)
    return 0


if __name__ == '__main__':
    sys.exit(main())
