---
title: Environment variables
description: Every environment variable NiteFx reads or sets.
---

# Environment variables

<p class="lead">Variables that change how NiteFx behaves. For variables your client code reads (<code>NITE_PUBLIC_*</code>), see <a href="../guides/environment.md">Environment variables and path aliases</a>.</p>

## Read by NiteFx

| Variable | Meaning |
|---|---|
| `NITE_REGISTRY` | The registry for unscoped packages, overriding every other setting. |
| `NITE_CONFIG_DIR` | The folder for `config.json`. |
| `NITE_CACHE_DIR` | The download cache folder. |
| `NITE_DATA_DIR`, `NITE_STATE_DIR` | Data and state folders (reserved). |
| `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`, `XDG_DATA_HOME`, `XDG_STATE_HOME` | Base folders, on every OS, when the `NITE_*_DIR` variable is not set. `nite` is appended. |
| `NITE_ESBUILD_PATH` | Use this esbuild binary instead of downloading one. It must be the version NiteFx expects (`nite version` prints it). |
| `NITE_SASS_PATH` | Use this Dart Sass folder (as in Dart Sass's standalone release: `src/dart` and `src/sass.snapshot`) instead of downloading one. |
| `NPM_CONFIG_USERCONFIG` | The user `.npmrc` to read instead of `~/.npmrc`. |
| `COLUMNS` | Terminal width for CLI tables when output is redirected. |
| `ASPNETCORE_ENVIRONMENT` | Through ASP.NET Core: `Development` turns on the dev server (see [Development and production](../concepts/development-and-production.md)). |
| `NITE_PUBLIC_*` (or your `envPrefix`) | Exposed to client code at build time. |

Any variable can also appear in `.npmrc` values as `${NAME}`.

## Set by nite watch

| Variable | Value | Effect |
|---|---|---|
| `DOTNET_WATCH_SUPPRESS_BROWSER_REFRESH` | `1` | `dotnet watch` does not inject its reload script; NiteFx's client handles the browser. Skipped with `--browser-refresh`. |
| `DOTNET_WATCH_RESTART_ON_RUDE_EDIT` | `1` | Edits that need a restart restart the app instead of prompting. Skipped with `--no-auto-restart`. |

A value you set yourself is left alone. See [Hot reload](../guides/hot-reload.md).

## Offline and air-gapped machines

NiteFx downloads three kinds of things: packages, the esbuild binary and (for Sass) the Dart Sass binary. On a machine without registry access:

1. Point `NITE_REGISTRY` (or `.npmrc`) at an internal mirror, which serves all three; or
2. Pre-fill the cache on a connected machine and copy `~/.cache/nite` over; or
3. Provide the binaries with `NITE_ESBUILD_PATH` and `NITE_SASS_PATH`, and commit `nite.lock.json` so installs need only tarballs (from a mirror or the cache).
