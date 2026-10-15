"""Vault index and filter evaluation (frontmatter, tasks, one-hop link following)."""
import difflib
import re
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from parse import (PRIO_RANK, extract_links, extract_tags, iter_body_lines, link_target, note_name,
                   parse_frontmatter, parse_task)

DEFAULT_ROOTS = ("context", "source", "projects", "daily", "_inbox")
FILE_FIELDS = ("name", "path")
TASK_FIELDS = ("status", "prio", "due", "scheduled", "start", "created", "done", "cancelled_on", "text", "tags",
               "links", "todo", "indent")
LITERAL_FIELDS = set(FILE_FIELDS) | (set(TASK_FIELDS) - {"links"})  # compared as-is, never resolved to a note
TASK_WORDS = {"open": ("status", "=", "open"), "done": ("status", "=", "done"),
              "cancelled": ("status", "=", "cancelled"), "todo": ("todo", "=", "true")}
FILTER_RE = re.compile(r"^([\w.\-]+?)(!=|<=|>=|!~|=|~|<|>)(.*)$")
PRESENCE_RE = re.compile(r"^([\w.\-]+)([?!])$")
DATE_EXPR_RE = re.compile(r"^today(?:([+-])(\d+))?$")
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")


class FilterError(ValueError):
    pass


class Note:
    def __init__(self, rel, text):
        self.path = rel
        self.name = Path(rel).stem
        self.fm, end = parse_frontmatter(text)
        lines = text.split("\n")
        start = end + 1 if end else 0
        self.links = []  # (line_no, target)
        for i in range(start):
            self.links += [(i + 1, t) for t in extract_links(lines[i])]
        self.tags = [t for v in _as_list(self.fm.get("tags")) for t in [v.lstrip("#")] if t]
        self.inline_tags = []  # (line_no, tag)
        self.tasks = []
        for no, line in iter_body_lines(lines, start):
            self.links += [(no, t) for t in extract_links(line)]
            self.inline_tags += [(no, t) for t in extract_tags(line)]
            task = parse_task(line)
            if task:
                task["line"], task["note"] = no, self
                self.tasks.append(task)
        self.lines = lines


def _as_list(v):
    if v is None or v == "":
        return []
    return v if isinstance(v, list) else [v]


class Vault:
    def __init__(self, root, scopes=None, today=None):
        self.root = Path(root)
        self.today = today or date.today()
        dirs = set(DEFAULT_ROOTS) | set(scopes or ())
        self.scopes = [s.strip("/") for s in scopes] if scopes else list(DEFAULT_ROOTS)
        self.notes, self.errors = [], []
        seen = set()
        for d in sorted(dirs):
            base = self.root / d
            files = [base] if base.is_file() else sorted(base.rglob("*.md")) if base.is_dir() else []
            for f in files:
                rel = f.relative_to(self.root).as_posix()
                if rel in seen:
                    continue
                seen.add(rel)
                try:
                    self.notes.append(Note(rel, f.read_text(encoding="utf-8", errors="replace")))
                except Exception as e:  # noqa: BLE001 — skip one bad file, never abort the query
                    self.errors.append(f"{rel}: {e}")
        self.notes.sort(key=lambda n: n.path)
        self.by_name = {n.name.lower(): n for n in self.notes}
        self.by_alias = {}
        for n in self.notes:
            for a in _as_list(n.fm.get("aliases")):
                self.by_alias.setdefault(a.lower(), n)
        self.keys = {k for n in self.notes for k in n.fm}

    def in_scope(self, note):
        return any(note.path == s or note.path.startswith(s + "/") for s in self.scopes)

    def resolve(self, value):
        t = link_target(str(value))
        if t.lower().endswith(".md"):
            t = note_name(t)
        t = t.lower()
        return self.by_name.get(t) or self.by_alias.get(t)

    def canonical(self, value):
        n = self.resolve(value)
        return n.name if n else link_target(str(value))

    # --- filters ---------------------------------------------------------------

    def parse_filters(self, args, tasks=False):
        out = []
        for a in args:
            if tasks and a in TASK_WORDS:
                out.append(TASK_WORDS[a])
                continue
            m = PRESENCE_RE.match(a) or FILTER_RE.match(a)
            if not m:
                raise FilterError(f"cannot parse filter '{a}' (expected key=value, key~text, key<value, key? …)")
            key, op, val = (m.group(1), m.group(2), m.group(3) if m.lastindex == 3 else None)
            self._check_key(key, tasks)
            out.append((key, op, val))
        return out

    def _check_key(self, key, tasks):
        parts = key.split(".")
        if tasks and parts[0] == "file":
            parts = parts[1:]
        elif tasks:
            if parts[0] not in TASK_FIELDS:
                raise FilterError(f"unknown task field '{parts[0]}'; fields: {', '.join(TASK_FIELDS)}, file.<prop>")
            if len(parts) > 2 or (len(parts) == 2 and parts[0] != "links"):
                raise FilterError(f"'{key}': only links.<prop> follows a link from a task (one hop)")
            return
        if not parts or not all(parts):
            raise FilterError(f"'{key}': empty property name")
        if len(parts) > 2:
            raise FilterError(f"'{key}': link following is limited to one hop (a.b)")
        known = self.keys | set(FILE_FIELDS)
        for p in parts:
            if p not in known:
                hint = difflib.get_close_matches(p, sorted(known), n=1)
                self.warn(f"unknown property '{p}'" + (f"; did you mean '{hint[0]}'?" if hint else ""))

    def warn(self, msg):
        self.errors.append(msg)

    def note_values(self, note, key):
        """Values of a frontmatter key (or a.b one-hop path) as a list of str."""
        head, _, tail = key.partition(".")
        vals = self._own(note, head)
        if not tail:
            return vals
        out = []
        for v in vals:
            target = self.resolve(v)
            if target:
                out += self._own(target, tail)
        return out

    @staticmethod
    def _own(note, key):
        if key == "name":
            return [note.name]
        if key == "path":
            return [note.path]
        return [str(v) for v in _as_list(note.fm.get(key))]

    def task_values(self, task, key):
        if key.startswith("file."):
            return self.note_values(task["note"], key[5:])
        head, _, tail = key.partition(".")
        v = task.get(head)
        if v is None:
            return []
        if isinstance(v, bool):
            return ["true" if v else "false"]
        vals = [str(x) for x in (v if isinstance(v, list) else [v])]
        if tail:
            return [x for t in vals for n in [self.resolve(t)] if n for x in self._own(n, tail)]
        return vals

    def matches(self, values, key, op, val):
        last = key.rsplit(".", 1)[-1]
        if op == "?":
            return bool(values)
        if op == "!":
            return not values
        if op in ("=", "!="):
            want = self._norm(self._date_expr(val), last)
            hit = any(self._norm(v, last) == want for v in values)
            return hit if op == "=" else not hit
        if op in ("~", "!~"):
            want = val.lower()
            hit = any(want in link_target(v).lower() or want in v.lower() for v in values)
            return hit if op == "~" else not hit
        rhs = self._rhs(val, last)
        return any(self._cmp(self._lhs(v, last), op, rhs) for v in values)

    def _norm(self, v, last):
        if last == "tags":
            return v.lstrip("#").lower()
        if last in LITERAL_FIELDS:
            return v.lower()
        return self.canonical(v).lower()

    def _date_expr(self, val):
        m = DATE_EXPR_RE.match(val)
        if not m:
            return val
        days = int(m.group(2) or 0) * (-1 if m.group(1) == "-" else 1)
        return (self.today + timedelta(days=days)).isoformat()

    def _lhs(self, v, last):
        if last == "prio":
            return PRIO_RANK.get(v, -1)
        return v

    def _rhs(self, val, last):
        if last == "prio":
            if val not in PRIO_RANK:
                raise FilterError(f"unknown priority '{val}'; use {', '.join(PRIO_RANK)}")
            return PRIO_RANK[val]
        return self._date_expr(val)

    @staticmethod
    def _cmp(a, op, b):
        if isinstance(a, str) and isinstance(b, str):
            if ISO_RE.match(b):
                if not ISO_RE.match(a):
                    return False  # placeholder or malformed date never matches a date range
                a, b = a[:10], b[:10]
            else:
                try:
                    a, b = float(a), float(b)
                except ValueError:
                    a, b = a.lower(), b.lower()
        return {"<": a < b, "<=": a <= b, ">": a > b, ">=": a >= b}[op]

    # --- queries ---------------------------------------------------------------

    def find(self, filters):
        return [n for n in self.notes if self.in_scope(n)
                and all(self.matches(self.note_values(n, k), k, op, v) for k, op, v in filters)]

    def tasks(self, filters):
        return [t for n in self.notes if self.in_scope(n) for t in n.tasks
                if all(self.matches(self.task_values(t, k), k, op, v) for k, op, v in filters)]

    def tag(self, name):
        name = name.lstrip("#").lower()

        def hit(t):
            t = t.lower()
            return t == name or t.startswith(name + "/")

        out = []
        for n in self.notes:
            if not self.in_scope(n):
                continue
            where = (["frontmatter"] if any(hit(t) for t in n.tags) else []) + \
                    [str(no) for no, t in n.inline_tags if hit(t)]
            if where:
                out.append((n, where))
        return out

    def backlinks(self, target):
        out = []
        for n in self.notes:
            if n is target or not self.in_scope(n):
                continue
            for no, t in n.links:
                if self.resolve(t) is target:
                    out.append((n, no))
        return sorted(set(out), key=lambda x: (x[0].path, x[1]))

    def props(self):
        """{key: (note_count, [(value, count), …] sorted by count desc)} in one pass."""
        keys, values = Counter(), {}
        for n in self.notes:
            if not self.in_scope(n):
                continue
            for k, raw in n.fm.items():
                keys[k] += 1
                values.setdefault(k, Counter()).update(link_target(str(v)) for v in _as_list(raw))
        order = lambda kv: (-kv[1], kv[0])  # noqa: E731
        return {k: (c, sorted(values[k].items(), key=order)) for k, c in sorted(keys.items(), key=order)}
