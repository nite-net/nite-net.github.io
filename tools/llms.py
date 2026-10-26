#!/usr/bin/env python3
"""Writes llms.txt, llms-full.txt and a Markdown copy of every page into the built site.

Run after `docfx build`, from the repository root: python3 tools/llms.py [_site]

llms.txt (https://llmstxt.org) is an index of the docs for AI coding agents; llms-full.txt is
every page in one file, in table-of-contents order. Each page is also published next to its HTML
as plain Markdown (docs/guides/islands.md beside docs/guides/islands.html), with links made
absolute so a page read on its own still leads somewhere.
"""

import html
import posixpath
import re
import sys
from pathlib import Path

BASE = "https://nite-net.github.io/"
ROOT = Path(__file__).resolve().parent.parent
SITE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_site"

# Read on their own when needed, not part of llms-full.txt.
OPTIONAL = {"docs/contributing.md"}

SUMMARY = (
    "Nite is TypeScript and React for ASP.NET Core with a Vite-style dev loop and no Node.js "
    "toolchain. It compiles client code on request with esbuild, keeps component state across "
    "hot updates, installs npm packages with its own C# client, and ships hashed, code-split "
    "bundles from `dotnet publish`. It needs the .NET SDK and nothing else."
)

AGENT_NOTES = """\
Nite looks like Vite but is not Vite, and habits from Vite and Node projects produce code that
does not work. In a Nite project:

- There is no `package.json`, `node`, `npm`, `npx` or `vite.config.*`. Do not create them.
  Packages are listed in `nite.json` and locked in `nite.lock.json`.
- Add packages with `nite add <name>` (`nite add -D <name>` for dev-only ones such as types),
  remove them with `nite remove <name>`, and update them with `nite update`. Never `npm install`.
- Run the app with `nite watch` (or `dotnet watch` / `dotnet run`); there is no separate frontend
  server or dev proxy. `dotnet publish -c Release` runs `nite build` and needs the `nite` tool
  (`dotnet tool install --global Nite.Cli`).
- Client code lives in the client root, `Client/` by default. `Program.cs` calls `AddNite()`,
  `UseNite()` and, for a single-page app, `MapNiteSpa()`; Razor apps use `<island>` tag helpers.
  The API is on the same origin, so there is no CORS to configure.
- Build-time settings come from `import.meta.env.NITE_PUBLIC_*`; `envPrefix` in `nite.json` sets
  other prefixes (projects imported from Vite keep `VITE_`). Per-request values from the server
  come from `NiteOptions.ClientConfig` and `import { config } from "nite:config"`.
- Not supported: `import.meta.glob`, Vite import suffixes (`?raw`, `?url`, `?worker`), Vite,
  Rollup and Babel plugins, and server-side rendering. Nite strips types without checking them;
  run `tsc --noEmit` for type errors.
- The name is Nite, pronounced "night". The `nite` command and file names are lowercase."""


def parse_toc(path):
    """Reads DocFX's toc.yml format (name, href, topicHref, nested items) without a YAML library."""
    entries, stack = [], [(-1, None)]
    for line in path.read_text().splitlines():
        m = re.match(r"^(\s*)(- )?(\w+):\s*(.*)$", line)
        if not m:
            continue
        indent, dash, key, value = len(m.group(1)), m.group(2), m.group(3), m.group(4).strip().strip('"')
        if dash:
            node = {"items": []}
            while stack[-1][0] >= indent:
                stack.pop()
            (stack[-1][1]["items"] if stack[-1][1] else entries).append(node)
            stack.append((indent, node))
        node = stack[-1][1]
        if key != "items" and node is not None:
            node[key] = value
    return entries


def pages():
    """(section name, page path relative to the repo) in site order."""
    for section in parse_toc(ROOT / "toc.yml"):
        folder = section.get("href", "")
        if not folder.startswith("docs"):
            continue
        def walk(items):
            for item in items:
                if item.get("href", "").endswith(".md"):
                    yield section["name"], posixpath.join(folder, item["href"])
                yield from walk(item["items"])
        yield from walk(parse_toc(ROOT / folder / "toc.yml"))


def front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip().strip('"')
    return meta, text[m.end():]


def inline_html(text):
    """The few HTML elements the docs use in prose, as Markdown."""
    text = re.sub(r"<code>(.*?)</code>", lambda m: "`" + html.unescape(m.group(1)) + "`", text)
    text = re.sub(r'<a href="([^"]*)">(.*?)</a>', r"[\2](\1)", text)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text)


def to_markdown(page, body, inline_anchors):
    """The page as standalone Markdown: lead paragraphs unwrapped, links and xrefs absolute."""
    folder = posixpath.dirname(page)

    def url(target):
        if re.match(r"^(\w+:|#)", target):
            if target.startswith("#") and not inline_anchors:
                return BASE + page + target
            return target
        path, _, anchor = target.partition("#")
        resolved = posixpath.normpath(posixpath.join(folder, path))
        if resolved.startswith("api/"):
            # The API reference is HTML only.
            resolved = re.sub(r"\.md$", ".html", resolved)
        return BASE + resolved + ("#" + anchor if anchor else "")

    def prose(text):
        text = re.sub(r'<p class="lead">(.*?)</p>', lambda m: inline_html(m.group(1)), text, flags=re.S)
        text = re.sub(r"<xref:([\w.`]+)>", lambda m: f"[{m.group(1)}]({BASE}api/{m.group(1)}.html)", text)
        text = re.sub(r"(\]\()([^)\s]+)(\))", lambda m: m.group(1) + url(m.group(2)) + m.group(3), text)
        return text

    # Leave fenced code and inline code alone.
    parts = re.split(r"(```.*?```|`[^`\n]*`)", body, flags=re.S)
    return "".join(p if p.startswith("`") else prose(p) for p in parts).strip() + "\n"


def main():
    if not SITE.is_dir():
        sys.exit(f"{SITE} does not exist: run docfx build first")

    sections, full = {}, []
    for section, page in pages():
        meta, body = front_matter((ROOT / page).read_text())
        title = meta.get("title", Path(page).stem)
        description = meta.get("description", "")
        markdown = to_markdown(page, body, inline_anchors=True)

        out = SITE / page
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(markdown)

        group = "Optional" if page in OPTIONAL else section
        sections.setdefault(group, []).append(f"- [{title}]({BASE}{page}): {description}")
        if page not in OPTIONAL:
            full.append(f"<!-- Source: {BASE}{page.removesuffix('.md')}.html -->\n\n"
                        + to_markdown(page, body, inline_anchors=False))

    if (SITE / "api" / "index.html").exists():
        sections.setdefault("Optional", []).append(
            f"- [API reference]({BASE}api/index.html): every public type and member of the Nite library, generated from its XML documentation comments")

    header = f"# Nite\n\n> {SUMMARY}\n\n## Notes for AI coding agents\n\n{AGENT_NOTES}\n"
    order = [name for name in sections if name != "Optional"] + (["Optional"] if "Optional" in sections else [])
    index = header + (
        f"\nEvery page below is plain Markdown. All of them except the optional ones are also in one "
        f"file: [llms-full.txt]({BASE}llms-full.txt).\n"
    )
    for name in order:
        index += f"\n## {name}\n\n" + "\n".join(sections[name]) + "\n"
    (SITE / "llms.txt").write_text(index)

    (SITE / "llms-full.txt").write_text(header + "\n" + "\n\n".join(full))
    print(f"llms.txt: {sum(len(v) for v in sections.values())} links; "
          f"llms-full.txt: {len(full)} pages, {(SITE / 'llms-full.txt').stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
