"""Publish this repository to GitHub using the credential git already has.

The token is never printed and never written to disk: it is read from the git
credential helper in-process, used for one API call, and dropped.

    python verify/github_publish.py --check                 # who am I?
    python verify/github_publish.py --create OWNER/NAME     # create if missing
"""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
UA = {'User-Agent': 'adb-publish', 'Accept': 'application/vnd.github+json'}


def credential():
    """Ask git's configured credential helper for github.com credentials."""
    env = dict(os.environ, GIT_TERMINAL_PROMPT='0')
    p = subprocess.run(['git', 'credential', 'fill'], input='protocol=https\nhost=github.com\n\n',
                       capture_output=True, text=True, encoding='utf-8', errors='replace',
                       env=env, timeout=120)
    if p.returncode != 0:
        raise SystemExit('git credential fill failed: %s' % (p.stderr or '').strip()[:200])
    user = pw = None
    for line in p.stdout.splitlines():
        if line.startswith('username='):
            user = line.split('=', 1)[1]
        elif line.startswith('password='):
            pw = line.split('=', 1)[1]
    if not pw:
        raise SystemExit('no stored credential for github.com')
    return user, pw


def api(method, url, token, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=UA)
    req.add_header('Authorization', 'Bearer ' + token)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.load(e)
        except Exception:
            return e.code, {'raw': e.reason}


def main():
    args = sys.argv[1:]
    mode = args[0] if args else '--check'
    user, token = credential()
    print('credential helper returned username =', user)

    st, me = api('GET', 'https://api.github.com/user', token)
    if st != 200:
        print('GET /user ->', st, str(me)[:200])
        return 1
    login = me['login']
    print('authenticated as            =', login)
    scopes = None
    print('token scopes not reported by fine-grained tokens; relying on API results')

    if mode == '--check':
        st, repos = api('GET', 'https://api.github.com/user/repos?per_page=100', token)
        print('visible repos (%d):' % (len(repos) if isinstance(repos, list) else -1),
              sorted(r['name'] for r in repos) if isinstance(repos, list) else repos)
        return 0

    if mode == '--create':
        spec = args[1]
        owner, name = spec.split('/', 1)
        if owner != login:
            raise SystemExit('owner %r is not the authenticated user %r' % (owner, login))
        st, repo = api('GET', 'https://api.github.com/repos/%s/%s' % (owner, name), token)
        if st == 200:
            print('repo already exists        =', repo['full_name'], '| private =', repo['private'])
        else:
            st, repo = api('POST', 'https://api.github.com/user/repos', token, {
                'name': name,
                'description': ('r_D(12): minimal polynomial, D3 configuration, coverage proof and '
                                'computer-assisted verification material (protocol '
                                'diskcover-minpoly-v1)'),
                'homepage': 'https://pikaaa345.github.io/disk-covering-benchmark/index.zh.html?lang=zh',
                'private': False,
                'has_issues': True, 'has_wiki': False, 'has_projects': False,
                'auto_init': False,
            })
            if st not in (200, 201):
                print('POST /user/repos ->', st, str(repo)[:300])
                return 1
            print('created repo               =', repo['full_name'], '| private =', repo['private'])
        print('clone url                  =', repo['clone_url'])
        return 0

    print('unknown mode', mode)
    return 2


if __name__ == '__main__':
    sys.exit(main())
