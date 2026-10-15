"""Parsers for vault Markdown: frontmatter (YAML subset), task lines, wikilinks, tags. Stdlib only."""
import re

KEY_RE = re.compile(r"^([A-Za-z0-9_][\w\-]*):\s*(.*)$")
LIST_ITEM_RE = re.compile(r"^\s*-\s+(.*)$")
LINK_RE = re.compile(r"!?\[\[([^\]\|#]*)(?:#[^\]\|]*)?(?:\|[^\]]*)?\]\]")
TAG_RE = re.compile(r"(?:^|(?<=\s))#([\w\-/]*[^\W\d][\w\-/]*)")
CODE_RE = re.compile(r"`[^`]*`")
TASK_RE = re.compile(r"^(?:>\s?)*(\s*)(?:[-*+]|\d+[.)]) \[(.)\] (.*)$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")

STATUS = {" ": "open", "x": "done", "X": "done", "-": "cancelled", "/": "in-progress"}
PRIO_EMOJI = {"🔺": "highest", "⏫": "high", "🔼": "medium", "🔽": "low", "⏬": "lowest"}
PRIO_RANK = {"lowest": 0, "low": 1, "normal": 2, "medium": 3, "high": 4, "highest": 5}
DATE_EMOJI = {"📅": "due", "📆": "due", "🗓": "due", "⏳": "scheduled", "⌛": "scheduled",
              "🛫": "start", "➕": "created", "✅": "done", "❌": "cancelled_on"}
DATE_FIELD_RE = re.compile("(" + "|".join(DATE_EMOJI) + r")️?\s*(\d{4}-\d{2}-\d{2})")


QUOTED_RE = re.compile(r"^(\"[^\"]*\"|'[^']*')(?:\s+#.*)?$")
BLOCK_SCALAR_RE = re.compile(r"^[|>][+-]?$")


def _scalar(raw):
    raw = raw.strip()
    m = QUOTED_RE.match(raw)
    if m:
        return m.group(1)[1:-1]
    return re.sub(r"\s+#.*$", "", raw)


def _inline_list(raw):
    items = re.findall(r"\s*(\"[^\"]*\"|'[^']*'|[^,]+)", raw.strip()[1:-1])
    return [v for v in (_scalar(i) for i in items) if v != ""]


def parse_frontmatter(text):
    """Return (dict, closing_line_index). Values are str or list[str]; unparseable blocks stay raw str."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, 0
    end = next((i for i in range(1, len(lines)) if lines[i].strip() in ("---", "...")), None)
    if end is None:
        return {}, 0
    fm, key, block, scalar_block = {}, None, [], False

    def flush():
        if key is None:
            return
        if block and not scalar_block and all(LIST_ITEM_RE.match(b) for b in block):
            fm[key] = [_scalar(LIST_ITEM_RE.match(b).group(1)) for b in block]
        elif block:
            fm[key] = "\n".join(b.strip() for b in block)
        else:
            fm[key] = ""

    for line in lines[1:end]:
        m = KEY_RE.match(line)
        if m and not line[0].isspace():
            flush()
            key, value, block = m.group(1), m.group(2).strip(), []
            scalar_block = bool(BLOCK_SCALAR_RE.match(value))
            if scalar_block:
                continue
            if value.startswith("[") and value.endswith("]") and not value.startswith("[["):
                fm[key], key = _inline_list(value), None
            elif value and not value.startswith("#"):
                fm[key], key = _scalar(value), None
        elif key is not None and line.strip():
            block.append(line)
    flush()
    return fm, end


def note_name(inner):
    s = inner.strip().rsplit("/", 1)[-1]
    return s[:-3] if s.lower().endswith(".md") else s


def link_target(raw):
    """[[folder/Note#h|alias]] -> Note; plain values (URLs, text) are returned stripped, unchanged."""
    s = raw.strip()
    m = LINK_RE.fullmatch(s)
    return note_name(m.group(1)) if m else s


def extract_links(text):
    return [t for t in (note_name(m.group(1)) for m in LINK_RE.finditer(text)) if t]


def extract_tags(text):
    clean = LINK_RE.sub(" ", CODE_RE.sub(" ", text))
    return TAG_RE.findall(clean)


def parse_task(line):
    """Parse an Obsidian Tasks checkbox line; None if the line is not a task."""
    m = TASK_RE.match(line)
    if not m:
        return None
    indent, mark, body = m.groups()
    task = {"status": STATUS.get(mark, "other"), "indent": indent.count("\t") + len(indent.replace("\t", "")) // 2,
            "text": body.strip(), "prio": "normal"}
    plain = LINK_RE.sub(" ", CODE_RE.sub(" ", body))
    found = [(plain.find(e), name) for e, name in PRIO_EMOJI.items() if e in plain]
    if found:
        task["prio"] = min(found)[1]
    for emoji, date in DATE_FIELD_RE.findall(body):
        task.setdefault(DATE_EMOJI[emoji], date)
    task["tags"] = extract_tags(body)
    task["links"] = extract_links(body)
    task["todo"] = "todo" in task["tags"]
    return task


def iter_body_lines(lines, start):
    """Yield (line_no, line) outside fenced code blocks, from index start; line_no is 1-based."""
    fenced = False
    for i in range(start, len(lines)):
        if FENCE_RE.match(lines[i]):
            fenced = not fenced
            continue
        if not fenced:
            yield i + 1, lines[i]
