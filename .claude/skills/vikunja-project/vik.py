#!/usr/bin/env python3
"""Lojicloop Vikunja project tool for a Claude Code session.

Works on one Vikunja project with that project's key: list, create and update its tasks
and comment on them. Python 3.8+, standard library only.

The URL and key come from the environment (LOJICLOOP_VIKUNJA_URL, LOJICLOOP_VIKUNJA_TOKEN)
or from the .vikunja.env file beside this tool, which the Claude tooling download puts there
(an older setup's .vikunja.env in the repository root still works). Keep .vikunja.env out of
git: the .gitignore beside this tool does.

  vik.py project                         the project, its statuses and people
  vik.py tasks [--all]                   open tasks (--all: done ones too)
  vik.py show REF                        one task with its description and comments
  vik.py add "Title" [--desc TEXT] [--status S] [--due YYYY-MM-DD] [--claude] [--percent N]
  vik.py start REF                       move to the in-progress status
  vik.py move REF "Status"               move to any status
  vik.py progress REF N                  percent done, 0-100
  vik.py done REF [--comment TEXT]       mark done (with an optional closing comment)
  vik.py reopen REF                      back to the first status
  vik.py comment REF TEXT                add a comment (TEXT - reads standard input)
  vik.py edit REF [--title T] [--desc D] [--due D] [--claude | --no-claude]

Add --json before the command for the raw JSON answer.
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


def config():
    values = {}
    for folder in [Path(__file__).resolve().parent, Path.cwd(), *Path.cwd().parents]:
        env_file = folder / '.vikunja.env'
        if env_file.is_file():
            for line in env_file.read_text(encoding='utf-8').splitlines():
                if '=' in line and not line.lstrip().startswith('#'):
                    key, value = line.split('=', 1)
                    values[key.strip()] = value.strip().strip('"\'')
            break
    url = os.environ.get('LOJICLOOP_VIKUNJA_URL') or values.get('LOJICLOOP_VIKUNJA_URL')
    token = os.environ.get('LOJICLOOP_VIKUNJA_TOKEN') or values.get('LOJICLOOP_VIKUNJA_TOKEN')
    if not url or not token:
        sys.exit('Missing LOJICLOOP_VIKUNJA_URL or LOJICLOOP_VIKUNJA_TOKEN (environment or .vikunja.env beside vik.py).')
    return url.rstrip('/'), token


def call(method, path, body=None):
    url, token = config()
    req = urllib.request.Request(url + '/dashboard/api/p' + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json',
                                          'Accept': 'application/json', 'User-Agent': 'lojicloop-vik/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read() or b'null')
    except urllib.error.HTTPError as e:
        try:
            message = json.loads(e.read()).get('error') or e.reason
        except ValueError:
            message = e.reason
        sys.exit(f'Error {e.code}: {message}')
    except urllib.error.URLError as e:
        sys.exit(f'Cannot reach {url}: {e.reason}')


def text(html_text):
    """Vikunja keeps descriptions and comments as HTML; show them as plain text."""
    t = re.sub(r'<br\s*/?>|</p>|</li>|</h\d>', '\n', html_text or '', flags=re.I)
    return html.unescape(re.sub(r'<[^>]+>', '', t)).strip()


def line(t):
    who = ', '.join(t['assignees']) or '-'
    return f"{t['ref']:<9} {t['status'][:14]:<14} {t['percent']:>3}%  {who[:24]:<24} {t['title']}"


def show_task(t):
    print(line(t))
    if t.get('due'):
        print('due:', t['due'][:10])
    if t.get('description'):
        print('\n' + text(t['description']))
    for c in t.get('comments') or []:
        print(f"\n[{c['created'][:16].replace('T', ' ')}] {c['author']}:\n{text(c['text'])}")


def in_progress_status():
    statuses = call('GET', '/project')['statuses']
    for s in statuses:
        if 'progress' in s.lower() or 'doing' in s.lower():
            return s
    sys.exit('No in-progress status on this board; use: vik.py move REF "Status" (one of: ' + ', '.join(statuses) + ')')


def main():
    ap = argparse.ArgumentParser(description='Lojicloop Vikunja project tool', formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__.split('\n\n', 2)[2])
    ap.add_argument('--json', action='store_true', help='print the raw JSON answer')
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('project')
    p = sub.add_parser('tasks')
    p.add_argument('--all', action='store_true')
    sub.add_parser('show').add_argument('ref')
    p = sub.add_parser('add')
    p.add_argument('title')
    p.add_argument('--desc')
    p.add_argument('--status')
    p.add_argument('--due')
    p.add_argument('--percent', type=int)
    p.add_argument('--claude', action='store_true', help='Claude works on this task too')
    sub.add_parser('start').add_argument('ref')
    p = sub.add_parser('move')
    p.add_argument('ref')
    p.add_argument('status')
    p = sub.add_parser('progress')
    p.add_argument('ref')
    p.add_argument('percent', type=int)
    p = sub.add_parser('done')
    p.add_argument('ref')
    p.add_argument('--comment')
    sub.add_parser('reopen').add_argument('ref')
    p = sub.add_parser('comment')
    p.add_argument('ref')
    p.add_argument('text')
    p = sub.add_parser('edit')
    p.add_argument('ref')
    p.add_argument('--title')
    p.add_argument('--desc')
    p.add_argument('--due')
    g = p.add_mutually_exclusive_group()
    g.add_argument('--claude', dest='claude', action='store_true', default=None)
    g.add_argument('--no-claude', dest='claude', action='store_false')
    a = ap.parse_args()

    def out(result, printer):
        if a.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            printer(result)

    if a.cmd == 'project':
        out(call('GET', '/project'), lambda p: print(f"{p['title']} ({p['identifier']})\nstatuses: {', '.join(p['statuses'])}\n"
                                                     f"owner: {p['owner']}, Claude: {p['claude']}"))
    elif a.cmd == 'tasks':
        tasks = [t for t in call('GET', '/tasks') if a.all or not t['done']]
        out(tasks, lambda ts: print('\n'.join(line(t) for t in ts) or 'No open tasks.'))
    elif a.cmd == 'show':
        out(call('GET', '/tasks/' + a.ref), show_task)
    elif a.cmd == 'add':
        body = {'title': a.title, 'claude': a.claude}
        for key, value in (('description', a.desc), ('status', a.status), ('due', a.due), ('percent', a.percent)):
            if value is not None:
                body[key] = value
        out(call('POST', '/tasks', body), lambda t: print('Created', line(t)))
    elif a.cmd in ('start', 'move'):
        status = in_progress_status() if a.cmd == 'start' else a.status
        out(call('PATCH', '/tasks/' + a.ref, {'status': status}), lambda t: print(line(t)))
    elif a.cmd == 'progress':
        out(call('PATCH', '/tasks/' + a.ref, {'percent': a.percent}), lambda t: print(line(t)))
    elif a.cmd == 'done':
        if a.comment:
            call('POST', f'/tasks/{a.ref}/comments', {'text': a.comment})
        out(call('PATCH', '/tasks/' + a.ref, {'done': True}), lambda t: print(line(t)))
    elif a.cmd == 'reopen':
        out(call('PATCH', '/tasks/' + a.ref, {'done': False}), lambda t: print(line(t)))
    elif a.cmd == 'comment':
        body = sys.stdin.read() if a.text == '-' else a.text
        out(call('POST', f'/tasks/{a.ref}/comments', {'text': body}), lambda r: print('Commented on', r['ref']))
    elif a.cmd == 'edit':
        body = {}
        for key, value in (('title', a.title), ('description', a.desc), ('due', a.due), ('claude', a.claude)):
            if value is not None:
                body[key] = value
        if not body:
            sys.exit('Nothing to change: give --title, --desc, --due, --claude or --no-claude.')
        out(call('PATCH', '/tasks/' + a.ref, body), lambda t: print(line(t)))


if __name__ == '__main__':
    main()
