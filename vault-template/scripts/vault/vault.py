#!/usr/bin/env python3
"""Read-only query CLI for the vault: files by frontmatter, tasks, tags, backlinks, properties.

Usage:
  vault.py find  [filters…] [--show a,b]     e.g. find type=Meeting persons.org~acme --show date,persons
  vault.py tasks [filters…] [--sort due]     e.g. tasks open prio>=high due<=today+7 --in projects
  vault.py tag <name>                        frontmatter `tags` + inline #tags (nested tags match)
  vault.py backlinks <note>                  notes linking to <note> (name or alias)
  vault.py props [key]                       property keys with counts, or one key's values

Filters (AND): key=v key!=v key~text key!~text key<v key<=v key>v key>=v key? (present) key! (missing)
  a.b follows the link(s) in a and reads b in the target note (one hop). Values: [[X]] == X, aliases resolve,
  dates accept today, today+N, today-N. Task fields: status prio due scheduled start created done text tags
  links todo indent file.<prop>; bare words: open done cancelled todo.
Common: --in <path> (repeatable; default context source projects daily _inbox), --json, --limit N
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from parse import PRIO_RANK, link_target  # noqa: E402
from query import FilterError, Vault  # noqa: E402

TASK_JSON_FIELDS = ("status", "prio", "due", "scheduled", "start", "created", "done", "tags", "links", "todo",
                    "indent", "text")


def _display(v):
    return [link_target(str(x)) for x in v] if isinstance(v, list) else link_target(str(v))


def _emit(rows, args, text_line):
    rows = rows[: args.limit] if args.limit else rows
    if args.json:
        print(json.dumps([r for r, _ in rows], ensure_ascii=False, indent=1))
    else:
        for _, line in rows:
            print(text_line(line))


def cmd_find(v, args):
    filters = v.parse_filters(args.filters)
    show = [s for s in (args.show or "type,date").split(",") if s]
    rows = []
    for n in v.find(filters):
        rec = {"path": n.path}
        parts = []
        for s in show:
            vals = v.note_values(n, s)
            if not vals:
                continue
            raw = n.fm.get(s)
            rec[s] = _display(vals if isinstance(raw, list) or "." in s or len(vals) > 1 else vals[0])
            parts.append(f"{s}={', '.join(_display(vals))}")
        rows.append((rec, f"{n.path}  {' '.join(parts)}".rstrip()))
    _emit(rows, args, str)


def cmd_tasks(v, args):
    filters = v.parse_filters(args.filters, tasks=True)
    tasks = v.tasks(filters)
    if args.sort in ("due", "scheduled", "created"):
        tasks.sort(key=lambda t: (t.get(args.sort) is None, t.get(args.sort) or ""))
    elif args.sort == "prio":
        tasks.sort(key=lambda t: -PRIO_RANK[t["prio"]])
    rows = []
    for t in tasks:
        rec = {"path": t["note"].path, "line": t["line"]}
        rec.update({k: t[k] for k in TASK_JSON_FIELDS if k in t})
        rows.append((rec, f"{t['note'].path}:{t['line']}  {t['note'].lines[t['line'] - 1].strip()}"))
    _emit(rows, args, str)


def cmd_tag(v, args):
    rows = [({"path": n.path, "where": where}, f"{n.path}  {', '.join(where)}") for n, where in v.tag(args.name)]
    _emit(rows, args, str)


def cmd_backlinks(v, args):
    target = v.resolve(args.note)
    if not target:
        print(f"error: no note named or aliased '{args.note}'", file=sys.stderr)
        return 1
    rows = []
    for n, no in v.backlinks(target):
        line = n.lines[no - 1].strip()
        rows.append(({"path": n.path, "line": no, "text": line}, f"{n.path}:{no}  {line[:160]}"))
    _emit(rows, args, str)
    return 0


def cmd_props(v, args):
    props = v.props()
    if args.key:
        _, values = props.get(args.key, (0, []))
        rows = [({"value": val, "count": c}, f"{val} ({c})") for val, c in values]
    else:
        rows = []
        for key, (c, values) in props.items():
            sample = [val for val, _ in values[:3]]
            rows.append(({"key": key, "count": c, "top": sample}, f"{key} ({c})  {', '.join(sample)}"[:200]))
    _emit(rows, args, str)


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--in", dest="scopes", action="append", metavar="PATH", help="limit to path (repeatable)")
    common.add_argument("--json", action="store_true", help="JSON output")
    common.add_argument("--limit", type=int, help="max rows")

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--root", default=str(Path(__file__).resolve().parents[2]), help=argparse.SUPPRESS)
    p.add_argument("--today", type=date.fromisoformat, help=argparse.SUPPRESS)
    sub = p.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("find", parents=[common], help="files by frontmatter")
    f.add_argument("filters", nargs="*")
    f.add_argument("--show", help="comma-separated fields to print (default type,date)")
    f.set_defaults(func=cmd_find)

    t = sub.add_parser("tasks", parents=[common], help="checkbox tasks")
    t.add_argument("filters", nargs="*")
    t.add_argument("--sort", choices=("file", "due", "scheduled", "created", "prio"), default="file")
    t.set_defaults(func=cmd_tasks)

    g = sub.add_parser("tag", parents=[common], help="notes with a tag")
    g.add_argument("name")
    g.set_defaults(func=cmd_tag)

    b = sub.add_parser("backlinks", parents=[common], help="notes linking to a note")
    b.add_argument("note")
    b.set_defaults(func=cmd_backlinks)

    r = sub.add_parser("props", parents=[common], help="property keys / values")
    r.add_argument("key", nargs="?")
    r.set_defaults(func=cmd_props)
    return p


def main(argv=None):
    parser = build_parser()
    args, extra = parser.parse_known_args(argv)  # filters may follow options: tasks --in x open
    if (extra and not hasattr(args, "filters")) or any(e.startswith("-") for e in extra):
        parser.error(f"unrecognized arguments: {' '.join(extra)}")
    if extra:
        args.filters += extra
    v = Vault(args.root, scopes=args.scopes, today=args.today)
    try:
        code = args.func(v, args) or 0
    except FilterError as e:
        print(f"error: {e}", file=sys.stderr)
        code = 2
    for msg in v.errors:
        print(f"warning: {msg}", file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
