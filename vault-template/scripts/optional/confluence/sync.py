#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["requests>=2.31", "markdownify>=0.13", "keyring>=24"]
# ///
"""
One-way Confluence -> local Markdown sync (optional vault add-on).

Setup:
  1. Fill in the CONFIG block below (replace every __…__ placeholder).
  2. Run scripts/optional/confluence/setup-token.sh once (stores the API token
     in the macOS Keychain under KEYCHAIN_SERVICE).
  3. List pages in source/confluence/_index.md as a Markdown table: column 1 =
     page URL or numeric page ID, column 2 = "yes" to also sync subpages.
  4. Run from the vault root: uv run scripts/optional/confluence/sync.py

Fetches each listed page (and descendants where requested) from the Confluence
Cloud v1 REST API, converts the rendered body to Markdown, and mirrors the tree
under source/confluence/pages/. Confluence always wins; local files for pages
that disappeared are pruned. The API token is read from the Keychain at runtime
(never stored in this file).
"""
from __future__ import annotations

import getpass
import json
import re
import sys
import time
from datetime import date
from pathlib import Path

import keyring
import requests
from markdownify import markdownify as md

# =============================================================================
# CONFIG -- replace every __…__ placeholder before first run
# =============================================================================
BASE_URL = "__CONFLUENCE_BASE_URL__"    # site URL + /wiki context path
EMAIL = "__CONFLUENCE_EMAIL__"          # Atlassian account email (Basic auth user)
KEYCHAIN_SERVICE = "__KEYCHAIN_SERVICE__"  # Keychain service name; must match setup-token.sh
# =============================================================================

KEYCHAIN_ITEM = KEYCHAIN_SERVICE
VAULT = Path(__file__).resolve().parents[3]  # scripts/optional/confluence/sync.py -> vault root
CONFLUENCE_DIR = VAULT / "source" / "confluence"
INDEX = CONFLUENCE_DIR / "_index.md"
PAGES_DIR = CONFLUENCE_DIR / "pages"
STATE = CONFLUENCE_DIR / ".sync-state.json"

API = BASE_URL + "/rest/api"
ILLEGAL = re.compile(r'[/\\:*?"<>|\x00-\x1f]')


# --- Credential --------------------------------------------------------------
def read_token() -> str:
    """Fetch the API token from the macOS Keychain.

    Reads via `keyring` — the *same* library setup-token.sh writes with — so the
    reading and creating application are identical. That keeps the Keychain
    item's access-control list satisfied and avoids the repeated password
    prompts you get when a different tool (e.g. the `security` CLI) reads an
    item `keyring` created.
    """
    try:
        token = keyring.get_password(KEYCHAIN_ITEM, getpass.getuser())
    except Exception as e:  # noqa: BLE001 — keyring backend / access errors
        sys.exit(f"error: could not read Keychain item '{KEYCHAIN_ITEM}': {e}")
    if not token:
        sys.exit(
            f"error: no token in Keychain item '{KEYCHAIN_ITEM}'.\n"
            "       Run scripts/optional/confluence/setup-token.sh first."
        )
    return token.strip()


# --- HTTP with light retry ---------------------------------------------------
def make_session(token: str) -> requests.Session:
    s = requests.Session()
    s.auth = (EMAIL, token)
    s.headers["Accept"] = "application/json"
    return s


def get_json(session: requests.Session, url: str, params: dict | None = None) -> dict:
    last = None
    for attempt in range(4):
        try:
            resp = session.get(url, params=params, timeout=30)
        except requests.exceptions.RequestException as e:
            last = str(e)
            time.sleep(min(2 ** attempt, 30))
            continue
        if resp.status_code in (429, 500, 502, 503, 504):
            try:
                wait = int(resp.headers.get("Retry-After", ""))
            except ValueError:
                wait = 2 ** attempt  # HTTP-date form or junk -> plain backoff
            last = f"{resp.status_code} on {resp.url}"
            time.sleep(min(wait, 30))
            continue
        if resp.status_code == 401:
            sys.exit("error: 401 Unauthorized — check the API token / email.")
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"giving up after retries: {last}")


# --- Confluence API ----------------------------------------------------------
def fetch_page(session: requests.Session, page_id: str) -> dict:
    return get_json(
        session, f"{API}/content/{page_id}",
        {"expand": "body.view,space,ancestors,version,history"},
    )


def child_ids(session: requests.Session, page_id: str) -> list[str]:
    ids, start, limit = [], 0, 100
    while True:
        data = get_json(
            session, f"{API}/content/{page_id}/child/page",
            {"limit": limit, "start": start},
        )
        results = data.get("results", [])
        ids.extend(c["id"] for c in results)
        if len(results) < limit:
            return ids
        start += limit


def collect_ids(session: requests.Session, root_id: str, recurse: bool) -> set[str]:
    found = {root_id}
    if not recurse:
        return found
    queue = [root_id]
    while queue:
        for cid in child_ids(session, queue.pop()):
            if cid not in found:
                found.add(cid)
                queue.append(cid)
    return found


# --- Index parsing -----------------------------------------------------------
def parse_index() -> list[tuple[str, bool]]:
    if not INDEX.exists():
        sys.exit(f"error: {INDEX} not found.")
    rows: list[tuple[str, bool]] = []
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        url, flag = cells[0], cells[1]
        if url.lower().startswith("confluence") or set(url) <= {"-", ":", " "}:
            continue  # header / separator row
        m = re.search(r"/pages/(\d+)", url) or re.fullmatch(r"\d+", url)
        if not m:
            print(f"  skip: no page id in {url!r}", file=sys.stderr)
            continue
        page_id = m.group(1) if m.re.groups else m.group(0)
        recurse = flag.lower() in {"yes", "y", "true", "1"}
        rows.append((page_id, recurse))
    return rows


# --- Path + content ----------------------------------------------------------
def sanitize(name: str) -> str:
    name = ILLEGAL.sub("-", name)
    name = re.sub(r"\s+", " ", name).strip(" .-")
    return name or "untitled"


def build_paths(pages: dict[str, dict], have: set[str]) -> tuple[dict[str, Path], set[str]]:
    """Compute a deterministic local path for every page.

    One canonical segment name is assigned per page id (top-down, so an
    ancestor's name is final before its children use it), with sibling
    collisions disambiguated by page id. Children derive their ancestor
    directories from the *same* segment map, so a disambiguated parent and
    its children stay together.
    """
    # pages that have at least one synced child (immediate parent == this page)
    children_of: set[str] = set()
    for p in pages.values():
        anc = [a["id"] for a in p.get("ancestors", []) if a["id"] in have]
        if anc:
            children_of.add(anc[-1])

    def depth(p: dict) -> int:
        return sum(1 for a in p.get("ancestors", []) if a["id"] in have)

    ordered = sorted(pages.values(), key=lambda p: (depth(p), p["id"]))
    seg: dict[str, str] = {}          # page id -> final path segment
    taken: dict[tuple, set[str]] = {}  # dir key -> segments used there
    for p in ordered:
        anc_ids = [a["id"] for a in p.get("ancestors", []) if a["id"] in have]
        space = sanitize(p.get("space", {}).get("key", "UNKNOWN"))
        dir_key = (space, tuple(seg[a] for a in anc_ids))
        name = sanitize(p["title"])
        slot = taken.setdefault(dir_key, set())
        if name in slot:
            name = f"{name} ({p['id']})"
        slot.add(name)
        seg[p["id"]] = name

    paths: dict[str, Path] = {}
    for p in pages.values():
        anc_ids = [a["id"] for a in p.get("ancestors", []) if a["id"] in have]
        space = sanitize(p.get("space", {}).get("key", "UNKNOWN"))
        parts = [space] + [seg[a] for a in anc_ids]
        name = seg[p["id"]]
        if p["id"] in children_of:        # folder note: Name/Name.md
            paths[p["id"]] = PAGES_DIR.joinpath(*parts, name, f"{name}.md")
        else:                             # leaf: Name.md
            paths[p["id"]] = PAGES_DIR.joinpath(*parts, f"{name}.md")
    return paths, children_of


def to_markdown(page: dict) -> str:
    html = page.get("body", {}).get("view", {}).get("value", "")
    body = md(html, heading_style="ATX", bullets="-").strip()
    body = re.sub(r"\n{3,}", "\n\n", body)
    created = (page.get("history", {}).get("createdDate") or "")[:10] \
        or date.today().isoformat()
    webui = page.get("_links", {}).get("webui", "")
    fm = [
        "---",
        'type: "[[Source]]"',
        f"date: {created}",
        f"confluence-id: {page['id']}",
        f"confluence-url: {BASE_URL}{webui}",
        f"confluence-version: {page.get('version', {}).get('number', '')}",
        "---",
        "",
        f"# {page['title']}",
        "",
    ]
    return "\n".join(fm) + body + "\n"


# --- State / prune -----------------------------------------------------------
def load_state() -> dict | None:
    if not STATE.exists():
        return None
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def prune(old: dict | None, new_paths: set[str]) -> int:
    if old is None:
        print("  note: no valid previous state — skipping prune.", file=sys.stderr)
        return 0
    deleted = 0
    pages_root = PAGES_DIR.resolve()
    for rec in old.get("pages", {}).values():
        rel = rec.get("path")
        if not rel or rel in new_paths:
            continue
        f = VAULT / rel
        try:
            if f.is_file() and pages_root in f.resolve().parents:
                f.unlink()
                deleted += 1
        except OSError as e:
            print(f"  warn: could not delete {rel}: {e}", file=sys.stderr)
    # remove now-empty dirs under pages/
    if PAGES_DIR.exists():
        for d in sorted(PAGES_DIR.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()
    return deleted


# --- Main --------------------------------------------------------------------
def main() -> int:
    rows = parse_index()
    if not rows:
        print("_index.md lists no pages — nothing to sync.")
        return 0

    session = make_session(read_token())

    # 1. collect every page id to sync
    synced: set[str] = set()
    for page_id, recurse in rows:
        try:
            synced |= collect_ids(session, page_id, recurse)
        except Exception as e:  # noqa: BLE001
            print(f"  error listing {page_id}: {e}", file=sys.stderr)

    # 2. fetch all pages
    pages: dict[str, dict] = {}
    errors = 0
    for pid in synced:
        try:
            pages[pid] = fetch_page(session, pid)
        except Exception as e:  # noqa: BLE001
            errors += 1
            print(f"  error fetching {pid}: {e}", file=sys.stderr)
    have = set(pages)

    # 3. deterministic local paths
    paths, _children = build_paths(pages, have)

    # 4. write files
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    new_state: dict[str, dict] = {}
    written = 0
    for pid, page in pages.items():
        try:
            target = paths[pid]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(to_markdown(page), encoding="utf-8")
            rel = target.relative_to(VAULT).as_posix()
            new_state[pid] = {"path": rel, "title": page["title"],
                              "version": page.get("version", {}).get("number")}
            written += 1
        except Exception as e:  # noqa: BLE001
            errors += 1
            print(f"  error writing {pid}: {e}", file=sys.stderr)

    # 5. prune + persist state. Never prune after a run with errors: a missing
    #    page may be a transient fetch failure, not a real deletion.
    new_paths = {r["path"] for r in new_state.values()}
    if errors:
        print("  note: errors this run — skipping prune to avoid deleting "
              "pages that merely failed to fetch.", file=sys.stderr)
        deleted = 0
    else:
        deleted = prune(load_state(), new_paths)
    STATE.write_text(
        json.dumps({"synced_at": date.today().isoformat(), "pages": new_state},
                   indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"done: {written} synced, {deleted} pruned, {errors} errors.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
