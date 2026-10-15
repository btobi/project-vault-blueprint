"""Tests for the vault query tool (fixture vault, fictional data only).

Run: python3 -m pytest scripts/vault -q
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from parse import extract_links, extract_tags, link_target, parse_frontmatter, parse_task  # noqa: E402
from vault import main  # noqa: E402

TODAY = "2026-10-14"

FILES = {
    "context/people/Alice Example.md": """---
type: "[[Person]]"
date: 2026-10-13
aliases:
  - Ally
org: ACME Corp
---
""",
    "context/people/Bob Builder.md": """---
type: "[[Person]]"
date: 2026-10-13
aliases: [Bobby, "B. Builder"]
org: Globex Ltd
---
""",
    "context/people/Carol Client.md": """---
type: "[[Person]]"
date: 2026-08-01
aliases:
  - Caz
org: Initech
---
""",
    "context/categories/Meeting.md": """---
type: "[[Category]]"
date: 2026-08-01
---
""",
    "source/meetings/2026-10-13 globex call.md": """---
type: "[[Meeting]]"
date: 2026-10-13
persons:
  - "[[Bob Builder]]"
  - "[[Alice Example]]"
---
# globex call

Talked with [[Alice Example|Ally]] about the offer. #followup
""",
    "source/meetings/2026-10-09 Caz.md": """---
type: "[[Meeting]]"
date: 2026-10-09
persons:
  - "[[Carol Client]]"
---
# Caz
""",
    "context/topics/Billing Service.md": """---
type: "[[Topic]]"
date: 2026-08-01
updated: 2026-08-20
status: current
vendor: globex
tags:
  - monitoring
  - waiting
---
# Billing Service

See [[2026-10-13 globex call#Briefing]] and ![[Carol Client]].

- [ ] #todo Who owns alerting? ⏫ ➕ 2026-10-08
- [ ] #todo ⏫ Prio before text ➕ 2026-10-09
- [x] #todo Done one ➕ 2026-09-01 ✅ 2026-09-02 — resolved: no
	- [ ] #todo Subtask low 🔽 ➕ 2026-08-14
- [-] #todo Dropped ➕ 2026-08-14 ❌ 2026-08-20

```text
- [ ] not a task, inside code #notatag
```
""",
    "context/topics/Network Setup.md": """---
type: "[[Topic]]"
date: 2026-10-01
updated: 2026-10-10
status: draft
---
# Network Setup #42 and # heading and [[Billing Service#Alerting]]
""",
    "projects/2026-10-01 alpha/Alpha.md": """---
type: "[[Project]]"
date: 2026-10-01
status: waiting
due: 2026-10-20
---
# Alpha

- [ ] #todo Alpha ⏫ 📅 2026-10-20 ➕ 2026-10-01 #waiting
- [ ] Ask [[Caz]] about the API ⏳ 2026-10-15
- [x] Plan step done ✅ 2026-10-02
""",
    "projects/tasks.md": """---
type: "[[Task]]"
date: 2026-10-01
---
- [ ] #todo Overdue thing 📅 2026-10-10 ➕ 2026-10-01
- [ ] #todo Far future 📅 2026-12-01 ➕ 2026-10-01
- [ ] #todo Talk to [[Carol Client]] 🔺 📅 2026-10-16 ➕ 2026-10-02
""",
    "templates/Project Template.md": """---
type: "[[Project]]"
date: {{DATE}}
---
- [ ] #todo template task
""",
}


@pytest.fixture
def vault(tmp_path):
    for rel, text in FILES.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return tmp_path


def run(vault, capsys, *args):
    code = main(["--root", str(vault), "--today", TODAY, *args])
    out, err = capsys.readouterr()
    return code, out, err


def paths(out):
    return sorted({line.split("  ")[0].split(":")[0] for line in out.splitlines() if line.strip()})


# --- parse -------------------------------------------------------------------

def test_frontmatter_scalars_lists_comments():
    fm, end = parse_frontmatter('---\ntype: "[[Topic]]"\ndate: 2026-10-01  # created\n'
                                "tags: [a, 'b c']\npersons:\n  - \"[[X]]\"\n  - Y\nempty:\n"
                                "nested:\n  k: v\n---\nbody")
    assert fm["type"] == "[[Topic]]"
    assert fm["date"] == "2026-10-01"
    assert fm["tags"] == ["a", "b c"]
    assert fm["persons"] == ["[[X]]", "Y"]
    assert fm["empty"] == ""
    assert fm["nested"] == "k: v"
    assert end == 10


def test_frontmatter_missing_or_unclosed():
    assert parse_frontmatter("# no fm\n") == ({}, 0)
    assert parse_frontmatter("---\ntype: x\n") == ({}, 0)


def test_frontmatter_edge_cases():
    fm, _ = parse_frontmatter('---\ntype: "[[Topic]]"  # c\naliases: [Ally, "Builder, B."]\n'
                              "desc: |\n  line1\n  - line2\nurl: https://example.com/a#b\n---\n")
    assert fm["type"] == "[[Topic]]"
    assert fm["aliases"] == ["Ally", "Builder, B."]
    assert fm["desc"] == "line1\n- line2"
    assert fm["url"] == "https://example.com/a#b"  # '#' without leading space is not a comment
    fm, end = parse_frontmatter("---\ntype: x\n...\nbody")
    assert (fm, end) == ({"type": "x"}, 2)


def test_task_edge_cases():
    assert parse_task("- [ ] see [[N|🔺 alias]] then ⏫")["prio"] == "high"
    assert parse_task("- [ ] low 🔽 first, later 🔺")["prio"] == "low"
    assert parse_task("1. [ ] numbered 📅 2026-10-10")["due"] == "2026-10-10"
    assert parse_task("> - [ ] in callout")["status"] == "open"
    assert parse_task("- [ ] code `⏫` only")["prio"] == "normal"
    assert parse_task("- [/] started")["status"] == "in-progress"
    assert parse_task("- [?] odd mark")["status"] == "other"


def test_task_priority_after_and_before_text():
    t = parse_task("- [ ] #todo Who owns alerting? ⏫ ➕ 2026-10-08")
    assert (t["status"], t["prio"], t["created"], t["todo"]) == ("open", "high", "2026-10-08", True)
    assert parse_task("- [ ] #todo ⏫ Prio before text ➕ 2026-10-09")["prio"] == "high"
    assert parse_task("- [ ] plain")["prio"] == "normal"


def test_task_done_with_trailing_text_and_subtask_and_cancelled():
    t = parse_task("- [x] #todo Done one ➕ 2026-09-01 ✅ 2026-09-02 — resolved: no")
    assert (t["status"], t["done"]) == ("done", "2026-09-02")
    s = parse_task("\t- [ ] #todo Subtask low 🔽 ➕ 2026-08-14")
    assert (s["indent"], s["prio"]) == (1, "low")
    assert parse_task("  - [ ] two spaces")["indent"] == 1
    c = parse_task("- [-] #todo Dropped ❌ 2026-08-20")
    assert (c["status"], c["cancelled_on"]) == ("cancelled", "2026-08-20")


def test_task_plain_step_scheduled_tags_links():
    t = parse_task("- [ ] Ask [[Caz]] about the API ⏳ 2026-10-15 #waiting")
    assert (t["todo"], t["scheduled"], t["prio"]) == (False, "2026-10-15", "normal")
    assert t["tags"] == ["waiting"]
    assert t["links"] == ["Caz"]
    assert parse_task("- [ ] x 🛫 2026-10-01 📅 2026-10-09")["start"] == "2026-10-01"
    assert parse_task("Just text") is None
    assert parse_task("- not a checkbox") is None


def test_links_and_tags():
    assert extract_links("[[a/b/Note.md|x]] [[Other#H]] ![[Emb]] [[#Local]]") == ["Note", "Other", "Emb"]
    assert extract_tags("# Head #ok #42 [[N#sec]] `#code` #a/b x#no") == ["ok", "a/b"]
    assert link_target("https://example.com/wiki/a/b") == "https://example.com/wiki/a/b"
    assert link_target("[[f/Note.md|alias]]") == "Note"
    assert link_target("  plain  ") == "plain"


def test_plain_url_value_kept_and_path_resolves(vault, capsys):
    (vault / "context/Page.md").write_text("---\ntype: x\nurl: https://example.com/a/b\n---\n", encoding="utf-8")
    _, out, _ = run(vault, capsys, "find", "url~example.com", "--show", "url")
    assert "url=https://example.com/a/b" in out
    _, out, _ = run(vault, capsys, "backlinks", "context/people/Alice Example.md")
    assert "globex call.md:10" in out


# --- find --------------------------------------------------------------------

def test_find_type_skips_templates(vault, capsys):
    code, out, _ = run(vault, capsys, "find", "type=Meeting")
    assert code == 0
    assert paths(out) == ["source/meetings/2026-10-09 Caz.md", "source/meetings/2026-10-13 globex call.md"]
    assert "type=Meeting" in out and "date=2026-10-13" in out  # default --show


def test_find_alias_and_link_hop(vault, capsys):
    _, out, _ = run(vault, capsys, "find", "persons=Ally")
    assert paths(out) == ["source/meetings/2026-10-13 globex call.md"]
    _, out, _ = run(vault, capsys, "find", "type=Meeting", "persons.org~globex")
    assert paths(out) == ["source/meetings/2026-10-13 globex call.md"]
    _, out, _ = run(vault, capsys, "find", "persons.org=Initech")
    assert paths(out) == ["source/meetings/2026-10-09 Caz.md"]


def test_find_dates_presence_and_negation(vault, capsys):
    _, out, _ = run(vault, capsys, "find", "type=Topic", "updated<today-30")
    assert paths(out) == ["context/topics/Billing Service.md"]
    _, out, _ = run(vault, capsys, "find", "vendor?")
    assert paths(out) == ["context/topics/Billing Service.md"]
    _, out, _ = run(vault, capsys, "find", "type=Topic", "vendor!")
    assert paths(out) == ["context/topics/Network Setup.md"]
    _, out, _ = run(vault, capsys, "find", "type=Topic", "status!=current")
    assert paths(out) == ["context/topics/Network Setup.md"]
    _, out, _ = run(vault, capsys, "find", "type=Topic", "status!~cur")
    assert paths(out) == ["context/topics/Network Setup.md"]


def test_find_comparison_operators(vault, capsys):
    _, out, _ = run(vault, capsys, "find", "type=Topic", "updated>today-10")
    assert paths(out) == ["context/topics/Network Setup.md"]
    _, out, _ = run(vault, capsys, "find", "type=Person", "date<2026-09-01")
    assert paths(out) == ["context/people/Carol Client.md"]
    _, out, _ = run(vault, capsys, "find", "type=Person", "date<=2026-08-01")
    assert paths(out) == ["context/people/Carol Client.md"]
    _, out, _ = run(vault, capsys, "find", "type=Person", "date>2026-10-13")
    assert out == ""


def test_find_show_and_json(vault, capsys):
    _, out, _ = run(vault, capsys, "find", "type=Meeting", "--show", "persons", "--json")
    rows = json.loads(out)
    globex = next(r for r in rows if "globex" in r["path"])
    assert globex["persons"] == ["Bob Builder", "Alice Example"]
    _, out, _ = run(vault, capsys, "find", "name~globex", "--show", "date,persons")
    assert "date=2026-10-13" in out and "persons=Bob Builder, Alice Example" in out


def test_find_limit(vault, capsys):
    _, out, _ = run(vault, capsys, "find", "type=Meeting", "--limit", "1")
    assert len(out.splitlines()) == 1


def test_find_in_scope_and_unknown_key_hint(vault, capsys):
    _, out, _ = run(vault, capsys, "find", "type=Project", "--in", "templates")
    assert paths(out) == ["templates/Project Template.md"]
    code, out, err = run(vault, capsys, "find", "vendr=globex")
    assert code == 0 and out == "" and "vendor" in err


def test_equality_dates_placeholders_and_literal_paths(vault, capsys):
    _, out, _ = run(vault, capsys, "find", "date=today-1")
    assert "source/meetings/2026-10-13 globex call.md" in paths(out)
    _, out, _ = run(vault, capsys, "find", "date>=today-30", "--in", "templates")
    assert out == ""  # {{DATE}} placeholder is not a date
    _, out, _ = run(vault, capsys, "find", "path=projects/2026-10-01 alpha/Alpha.md")
    assert paths(out) == ["projects/2026-10-01 alpha/Alpha.md"]


def test_link_value_forms_are_equivalent(vault, capsys):
    _, a, _ = run(vault, capsys, "find", "persons=[[Carol Client]]")
    _, b, _ = run(vault, capsys, "find", "persons=Carol Client")
    _, c, _ = run(vault, capsys, "find", "persons=caz")
    assert paths(a) == paths(b) == paths(c) == ["source/meetings/2026-10-09 Caz.md"]


def test_filter_syntax_error(vault, capsys):
    code, _, err = run(vault, capsys, "find", "justaword")
    assert code == 2 and "cannot parse filter" in err


def test_filters_after_options(vault, capsys):
    code, out, _ = run(vault, capsys, "tasks", "--in", "projects", "open", "prio>=high")
    assert code == 0 and len(out.splitlines()) == 2


def test_two_hops_rejected(vault, capsys):
    code, _, err = run(vault, capsys, "find", "persons.org.x=y")
    assert code == 2 and "one hop" in err


def test_unknown_option_rejected(vault, capsys):
    with pytest.raises(SystemExit) as e:
        run(vault, capsys, "find", "type=Meeting", "--bogus")
    assert e.value.code == 2


# --- tasks -------------------------------------------------------------------

def test_tasks_open_high_prio(vault, capsys):
    _, out, _ = run(vault, capsys, "tasks", "open", "prio>=high")
    lines = out.splitlines()
    assert len(lines) == 4
    assert any("Talk to [[Carol Client]]" in l for l in lines)
    assert not any("Subtask" in l for l in lines)


def test_tasks_status_words(vault, capsys):
    _, out, _ = run(vault, capsys, "tasks", "done", "--in", "context")
    assert len(out.splitlines()) == 1 and "Done one" in out
    _, out, _ = run(vault, capsys, "tasks", "cancelled", "--in", "context")
    assert len(out.splitlines()) == 1 and "Dropped" in out


def test_tasks_due_window_sort_and_file_prop(vault, capsys):
    _, out, _ = run(vault, capsys, "tasks", "open", "due<=today+7", "--sort", "due")
    texts = [l.split("  ", 1)[1] for l in out.splitlines()]
    assert texts[0].startswith("- [ ] #todo Overdue thing")
    assert len(texts) == 3
    _, out, _ = run(vault, capsys, "tasks", "open", "file.status=waiting")
    assert len(out.splitlines()) == 2


def test_tasks_sort_prio_and_json(vault, capsys):
    _, out, _ = run(vault, capsys, "tasks", "open", "--in", "projects", "--sort", "prio", "--json")
    rows = json.loads(out)
    assert rows[0]["prio"] == "highest" and rows[0]["path"] == "projects/tasks.md"
    assert {"path", "line", "status", "due", "text", "tags", "links", "todo", "indent"} <= set(rows[0])
    prios = [r["prio"] for r in rows]
    assert prios == sorted(prios, key=lambda p: {"highest": 0, "high": 1, "normal": 2}[p])


def test_tasks_scheduled_and_text(vault, capsys):
    _, out, _ = run(vault, capsys, "tasks", "scheduled=today+1")
    assert len(out.splitlines()) == 1 and "Ask [[Caz]]" in out
    _, out, _ = run(vault, capsys, "tasks", "text~overdue")
    assert len(out.splitlines()) == 1


def test_tasks_links_alias_todo_and_scope(vault, capsys):
    _, out, _ = run(vault, capsys, "tasks", "open", "links=Carol Client")
    assert len(out.splitlines()) == 2  # [[Carol Client]] and [[Caz]] (alias)
    _, out, _ = run(vault, capsys, "tasks", "open", "todo!=true", "--in", "projects")
    assert [l.split(":")[0] for l in out.splitlines()] == ["projects/2026-10-01 alpha/Alpha.md"]
    _, out, _ = run(vault, capsys, "tasks", "tags=#waiting")
    assert len(out.splitlines()) == 1
    _, out, _ = run(vault, capsys, "tasks", "--in", "context")
    assert "inside code" not in out
    assert out.splitlines()[0].startswith("context/topics/Billing Service.md:15  ")


def test_tasks_link_hop_and_bad_fields(vault, capsys):
    _, out, _ = run(vault, capsys, "tasks", "open", "links.org=Initech")
    assert len(out.splitlines()) == 2
    code, _, err = run(vault, capsys, "tasks", "bogus=1")
    assert code == 2 and "unknown task field" in err
    code, _, err = run(vault, capsys, "tasks", "prio>=urgent")
    assert code == 2 and "unknown priority" in err
    code, _, err = run(vault, capsys, "tasks", "due.x=1")
    assert code == 2 and "one hop" in err


# --- tag / backlinks / props --------------------------------------------------

def test_tag_frontmatter_and_inline(vault, capsys):
    _, out, _ = run(vault, capsys, "tag", "waiting")
    assert paths(out) == ["context/topics/Billing Service.md", "projects/2026-10-01 alpha/Alpha.md"]
    assert "frontmatter" in out
    _, out, _ = run(vault, capsys, "tag", "#followup")
    assert paths(out) == ["source/meetings/2026-10-13 globex call.md"]
    _, out, _ = run(vault, capsys, "tag", "notatag")
    assert out == ""


def test_tag_nested_match(vault, capsys):
    (vault / "context/Nested.md").write_text("---\ntype: x\n---\nText #area/infra here\n", encoding="utf-8")
    _, out, _ = run(vault, capsys, "tag", "area")
    assert paths(out) == ["context/Nested.md"]
    _, out, _ = run(vault, capsys, "tag", "are")
    assert out == ""


def test_backlinks(vault, capsys):
    _, out, _ = run(vault, capsys, "backlinks", "Carol Client")
    assert paths(out) == ["context/topics/Billing Service.md", "projects/2026-10-01 alpha/Alpha.md",
                          "projects/tasks.md", "source/meetings/2026-10-09 Caz.md"]
    _, out, _ = run(vault, capsys, "backlinks", "Ally")
    assert "source/meetings/2026-10-13 globex call.md:6  " in out  # frontmatter
    assert "source/meetings/2026-10-13 globex call.md:10  " in out  # body, aliased link
    code, _, err = run(vault, capsys, "backlinks", "Nobody")
    assert code == 1 and "no note" in err


def test_backlinks_json_and_heading_links(vault, capsys):
    _, out, _ = run(vault, capsys, "backlinks", "Billing Service", "--json")
    rows = json.loads(out)
    assert [r["path"] for r in rows] == ["context/topics/Network Setup.md"]
    assert rows[0]["line"] == 7 and "[[Billing Service#Alerting]]" in rows[0]["text"]


def test_props(vault, capsys):
    _, out, _ = run(vault, capsys, "props")
    assert "persons (2)" in out
    _, out, _ = run(vault, capsys, "props", "org")
    assert "Globex Ltd (1)" in out
    _, out, _ = run(vault, capsys, "props", "type", "--json")
    rows = {r["value"]: r["count"] for r in json.loads(out)}
    assert rows["Person"] == 3 and rows["Meeting"] == 2
    _, out, _ = run(vault, capsys, "props", "missing")
    assert out == ""


# --- robustness ---------------------------------------------------------------

def test_unreadable_bytes_do_not_abort(vault, capsys):
    (vault / "context/Bad.md").write_bytes(b"---\ntype: x\n---\n\xff\xfe broken\n")
    code, out, _ = run(vault, capsys, "find", "type=x")
    assert code == 0 and "context/Bad.md" in out
