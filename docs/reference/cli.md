---
title: Command-line interface
description: Every nite command, its arguments, options and aliases.
---

# Command-line interface

<p class="lead">The <code>nite</code> tool creates projects, manages packages, builds for production and runs the dev loop. Run <code>nite --help</code>, or <code>nite &lt;command&gt; --help</code>, for the same information in your terminal.</p>

| Command | Aliases | Summary |
|---|---|---|
| [`nite init`](#nite-init) | | Create a project, or import an existing one |
| [`nite install`](#nite-install) | `add`, `i` | Install packages, or add new ones |
| [`nite remove`](#nite-remove) | `rm`, `delete`, `uninstall` | Remove packages |
| [`nite list`](#nite-list) | `ls` | Show installed packages |
| [`nite update`](#nite-update) | `up` | Check for and apply package updates |
| [`nite build`](#nite-build) | | Production build into `wwwroot/_nite` |
| [`nite watch`](#nite-watch) | | `dotnet watch` with nite handling the browser |
| [`nite config`](#nite-config) | | Show or change settings |
| [`nite cache`](#nite-cache) | | Manage the download cache |
| [`nite version`](#nite-version) | `--version` | Show versions |
| [`nite update-self`](#nite-update-self) | | Update the tool |

## Common options

Commands that work on a project (`install`, `remove`, `list`, `update`, `build`, `watch`) take:

| Option | Meaning |
|---|---|
| `-C`, `--dir <DIRECTORY>` | The project folder (the one with `nite.json`). Defaults to the current folder. |
| `--verbose` | Show debug output. |

Exit codes: `0` on success, `1` on an error, `130` when interrupted with Ctrl+C.

---

## nite init

Create a project, then install its packages.

```text
nite init [DIRECTORY] [OPTIONS]
```

`DIRECTORY` defaults to the current folder. It must be empty (files such as `.git` and `README.md` are fine) unless you pass `--force`, and must not already contain a project file.

| Option | Meaning |
|---|---|
| `-t`, `--template <TEMPLATE>` | `spa` (a React app with an API) or `islands` (Razor Pages with React islands). Defaults to the `init.template` setting, which defaults to `spa`. |
| `-n`, `--name <NAME>` | Project name. Defaults to the folder name. |
| `--from <PATH>` | Import an existing npm, Yarn, pnpm or Bun project (Vite or Create React App). The source is not changed. See [Importing](../guides/importing.md). |
| `--dry-run` | With `--from`: show what would be imported and write nothing. |
| `--force` | Create the project in a folder that already has files. Existing files are never overwritten. |
| `--no-install` | Skip installing packages. |
| `--nite-source <PATH>` | Reference a nite source checkout instead of the `Nite` NuGet package. |
| `--verbose` | Show debug output. |

```bash
nite init                              # SPA in the current folder
nite init my-app                       # SPA in ./my-app
nite init my-site --template islands   # Razor Pages with islands
nite init my-app --from ../vite-app --dry-run
```

## nite install

Install the packages in `nite.json`, or add new ones. Aliases: `nite add`, `nite i`.

```text
nite install [PACKAGES] [OPTIONS]
```

| Argument / option | Meaning |
|---|---|
| `PACKAGES` | Packages to add: `react`, `react@^19`, `@types/react@latest`. Omit to install everything in `nite.json`. |
| `-D`, `--dev` | Add to `devDependencies`. |
| `-E`, `--exact` | Save the exact version instead of a `^` range. |

A bare name or a dist-tag is saved as `^<version>` (or the exact version with `-E`); a range is saved as written. Comments and formatting in `nite.json` are kept.

```bash
nite install
nite add react-router zod
nite add -D @types/node typescript
nite add -E lodash-es@4.17.21
```

## nite remove

Remove packages from `nite.json` and `node_modules`. Aliases: `nite rm`, `nite delete`, `nite uninstall`.

```text
nite remove <PACKAGES> [OPTIONS]
```

```bash
nite rm react-router
```

## nite list

Show installed packages: each direct dependency's range and installed version. Alias: `nite ls`.

```text
nite list [OPTIONS]
```

| Option | Meaning |
|---|---|
| `-a`, `--all` | Include transitive dependencies, with the package they are nested under when not hoisted. |

## nite update

Show current, wanted and latest versions, then update. Alias: `nite up`.

```text
nite update [PACKAGES] [OPTIONS]
```

| Argument / option | Meaning |
|---|---|
| `PACKAGES` | Only these packages. Omit to update everything. |
| `-c`, `--check` | Only report what is outdated; change nothing. |
| `-L`, `--latest` | Move ranges in `nite.json` to the latest versions, across major versions too. |

*Wanted* is the newest version the current range allows; *latest* is the registry's `latest` tag. Without `--latest`, ranges stay as they are and the lockfile moves to the wanted versions.

```bash
nite update --check
nite update
nite update react react-dom --latest
```

## nite build

The production build: installs packages, then builds every entry into `wwwroot/_nite` and prints a table of the outputs and their sizes. `dotnet publish -c Release` runs it for you.

```text
nite build [OPTIONS]
```

See [Production builds and deployment](../guides/deployment.md).

## nite watch

Run `dotnet watch` with nite handling the browser.

```text
nite watch [OPTIONS] [-- DOTNET_WATCH_ARGUMENTS]
```

| Option | Meaning |
|---|---|
| `--browser-refresh` | Keep `dotnet watch`'s own browser refresh, which reloads the page after every C# change. Useful for Razor Pages and MVC; off by default so single-page apps keep their state. |
| `--no-auto-restart` | Let `dotnet watch` ask (or wait for Ctrl+R) when an edit needs a restart, instead of restarting the app automatically. |

Everything after `--` goes to `dotnet watch`. The variables `nite watch` sets, and why, are on [Hot reload](../guides/hot-reload.md#variables-nite-watch-sets).

```bash
nite watch
nite watch --browser-refresh
nite watch -- --launch-profile https
```

## nite config

Show or change settings. Credentials are never stored here; they stay in `.npmrc`. See [Settings and directories](settings.md).

| Command | Meaning |
|---|---|
| `nite config list` (`ls`) | Effective settings for the current folder. `--show-origin` shows where each value comes from; `-C <dir>` includes another project's `nite.json` and `.npmrc`. |
| `nite config get <KEY>` | Print one setting. |
| `nite config set <KEY> <VALUE>` | Set a value in the user config. |
| `nite config unset <KEY>` (`delete`) | Remove a value from the user config. |
| `nite config path` | Print the user config file's path. |

Keys: `registry`, `@scope:registry` and `init.template`. Registry values must be `http` or `https` URLs; `init.template` must be `spa` or `islands`.

```bash
nite config set @acme:registry https://npm.acme.dev/
nite config set init.template islands
nite config list --show-origin
```

## nite cache

Manage the per-user download cache: package tarballs, registry metadata, and the esbuild and Sass binaries.

| Command | Meaning |
|---|---|
| `nite cache dir` | Print the cache folder. |
| `nite cache clean` (`clear`) | Delete the cache, including folders older nite versions left behind. Everything downloads again on next use. |
| `nite cache verify` | Re-check cached tarballs against their integrity hashes and remove corrupt ones. |

## nite version

Print the nite version, with the esbuild version it drives and the .NET runtime.

```text
$ nite version
nite 0.2.0 (876181ad44e9)
esbuild 0.28.2, .NET 10.0.13
```

## nite update-self

Update the `nite` tool with `dotnet tool update`, wherever it is installed: a local tool manifest (when one in the current folder or above lists `Nite.Cli`), the global tools folder, or a custom `--tool-path`.

| Option | Meaning |
|---|---|
| `--version <VERSION>` | Install a specific version. |
| `--prerelease` | Allow prerelease versions. |
