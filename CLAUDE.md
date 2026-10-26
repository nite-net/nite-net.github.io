# NiteFx documentation site

DocFX site for [NiteFx](https://github.com/nite-net/nite), published at <https://nitefx.dev>. Pages are Markdown under `docs/`; the
API reference is generated from the nite source.

## Building

```bash
export PATH=$HOME/.dotnet:$HOME/.dotnet/tools:$PATH DOTNET_ROOT=$HOME/.dotnet
NITE_SRC=/path/to/nite ./build.sh        # build into _site/; without NITE_SRC it clones nite
NITE_SRC=/path/to/nite ./build.sh serve  # build, then serve on http://localhost:8080
```

Build with no warnings before committing. A new page needs an entry in the `toc.yml` of its folder.
Released changes go in `docs/changelog.md`, plans in `docs/roadmap.md`.

`tools/llms.py` runs after DocFX (in `build.sh` and the Pages workflow) and writes `llms.txt`,
`llms-full.txt` and a Markdown copy of each page into `_site`, in `toc.yml` order. Its notes for
agents repeat facts from the docs; keep them in step when commands or defaults change.

## Writing

- The project is **NiteFx** (short for Nite Framework); use that name in prose, titles and
  descriptions. The NuGet packages (`Nite`, `Nite.Cli`, `Nite.Templates`), the C# namespace
  (`Nite`), the `nite` command and its files keep the short name: write those as code. Quoted
  output stays exactly as the program prints it ("nite: command not found", "is not in the Nite
  build").
- The site is <https://nitefx.dev>; the repositories are still under `nite-net` on GitHub.
- The `(n)ite` in the logo is a visual joke; do not write the name that way.

## Stopping processes you started

Never `pkill -f` (or `pgrep -f | kill`) with a pattern that appears in your own command line: `-f`
matches full command lines, including the shell running the command, so it kills itself (exit
code 144). Keep the PID of what you start and kill exactly that:

```bash
python3 -m http.server 8091 & echo $! > server.pid
kill "$(cat server.pid)"
```

If you must match by pattern, bracket one character so the pattern does not match itself:
`pkill -f '[h]ttp.server 8091'`. That only protects the pattern's own text: a command that also
mentions the name elsewhere (a `cd` into its folder, a path) still matches, so prefer the PID.
