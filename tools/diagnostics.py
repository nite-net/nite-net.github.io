#!/usr/bin/env python3
"""Writes the log message reference (docs/reference/diagnostics/) from the nite source.

Run before `docfx build`, from the repository root: python3 tools/diagnostics.py [nite-src]

Each NiteFx log message is a Markdown file in src/Nite/Diagnostics: front matter that the
Nite.Diagnostics source generator compiles into a logging method, and a body that explains the
message. This turns each file into a page (the front matter as a table, then the body), plus an
index and a toc.yml. The output is generated, so it is not committed (.gitignore).
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "nite-src") / "src" / "Nite" / "Diagnostics"
OUT = ROOT / "docs" / "reference" / "diagnostics"
REPO = "https://github.com/nite-net/nite/blob/main/src/Nite/Diagnostics"

INTRO = (
    "NiteFx's log messages that have a code, with what each one means and how to fix it. The code "
    "is the event's name and the event ID its number: the console logger shows the number "
    "(as `[1002]` after the category), and logging providers that record event names, such "
    "as Application Insights, record the code too. These pages are generated from the same "
    "Markdown files the messages are compiled from, with "
    "[Nite.Diagnostics](../../guides/log-messages.md)."
)


def parse(path):
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        sys.exit(f"{path}: no front matter")
    meta = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line[0].isspace() or ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        meta[key.strip()] = value
    body = text[m.end():]
    title_match = re.search(r"^# (.+)$", body, re.M)
    title = title_match.group(1).strip() if title_match else meta.get("method", path.stem)
    if title_match:
        body = body[:title_match.start()] + body[title_match.end():]
    return meta, title, body.strip()


def cell(value):
    return value.replace("|", "\\|")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*"):
        old.unlink()

    files = sorted(SOURCE.glob("*.md")) if SOURCE.is_dir() else []
    entries = []
    for path in files:
        meta, title, body = parse(path)
        code = meta["code"]
        page = OUT / f"{code}.md"
        message = meta["message"]
        page.write_text(
            "---\n"
            f"title: \"{code}: {title}\"\n"
            # Generated: the page to edit is the source file linked at the bottom.
            "_disableContribution: true\n"
            f"description: \"{message.replace(chr(92), chr(92) * 2).replace(chr(34), chr(39))}\"\n"
            "---\n\n"
            f"# {code}: {title}\n\n"
            "| Code | Event ID | Level | Message |\n"
            "|---|---|---|---|\n"
            f"| `{code}` | {meta['eventId']} | {meta['level'].capitalize()} | `{cell(message)}` |\n\n"
            f"{body}\n\n"
            f"<sub>Source: [{path.name}]({REPO}/{path.name})</sub>\n",
            encoding="utf-8",
        )
        entries.append((code, title, meta))

    index = ["---", "title: Log messages", "_disableContribution: true", "description: \"The warnings NiteFx logs by code, what each one means and how to fix it.\"", "---", "",
             "# Log messages", "", INTRO, ""]
    if entries:
        index += ["| Code | Level | Title |", "|---|---|---|"]
        index += [f"| [{code}]({code}.md) | {meta['level'].capitalize()} | {cell(title)} |" for code, title, meta in entries]
    else:
        index += ["The list is generated from the NiteFx source, which this build of the site did not have."]
    (OUT / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8")

    toc = ["- name: Overview", "  href: index.md"]
    toc += [f"- name: \"{code}: {title}\"\n  href: {code}.md" for code, title, _ in entries]
    (OUT / "toc.yml").write_text("\n".join(toc) + "\n", encoding="utf-8")
    print(f"diagnostics: {len(entries)} log message page(s) from {SOURCE}")


if __name__ == "__main__":
    main()
