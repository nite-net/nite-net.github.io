# nite documentation site

DocFX site for [nite](https://github.com/nite-net/nite). Pages are Markdown under `docs/`; the
API reference is generated from the nite source.

## Building

```bash
export PATH=$HOME/.dotnet:$HOME/.dotnet/tools:$PATH DOTNET_ROOT=$HOME/.dotnet
NITE_SRC=/path/to/nite ./build.sh        # build into _site/; without NITE_SRC it clones nite
NITE_SRC=/path/to/nite ./build.sh serve  # build, then serve on http://localhost:8080
```

Build with no warnings before committing. A new page needs an entry in the `toc.yml` of its folder.
Released changes go in `docs/changelog.md`, plans in `docs/roadmap.md`.

## Writing

- **Nite** is a proper noun: capitalize it in prose, including titles and descriptions. Lowercase
  is for code, commands and quoted output only (`nite watch`, `nite.json`, `/_nite`,
  `nite:config`, "nite: command not found").
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
