---
title: Settings and directories
description: Where Nite keeps per-user configuration and cache files, the settings it reads, and the order they apply in.
---

# Settings and directories

<p class="lead">Per-project settings live in <code>nite.json</code>. Per-user settings and downloads live where the XDG Base Directory spec says they go, and npm's <code>.npmrc</code> files are honored as they are.</p>

## Directories

| | Linux and macOS | Windows | Override |
|---|---|---|---|
| Config (`config.json`) | `~/.config/nite` | `%APPDATA%\nite` | `NITE_CONFIG_DIR`, then `XDG_CONFIG_HOME` |
| Cache | `~/.cache/nite` | `%LOCALAPPDATA%\nite\cache` | `NITE_CACHE_DIR`, then `XDG_CACHE_HOME` |
| Data | `~/.local/share/nite` | `%LOCALAPPDATA%\nite\data` | `NITE_DATA_DIR`, then `XDG_DATA_HOME` |
| State | `~/.local/state/nite` | `%LOCALAPPDATA%\nite\state` | `NITE_STATE_DIR`, then `XDG_STATE_HOME` |

`XDG_*` variables apply on every OS when set to an absolute path; `nite` is appended to them. `NITE_*_DIR` variables name the folder itself.

The cache holds:

| Folder | Contents |
|---|---|
| `tarballs/` | Package tarballs, by integrity hash |
| `metadata/` | Registry metadata, with ETags for revalidation |
| `esbuild/` | The esbuild binary, per version and platform |
| `sass/` | The Dart Sass binary, per version and platform |

Everything in it can be deleted at any time (`nite cache clean`); it is downloaded again on demand. `nite cache clean` also removes the download folders earlier Nite builds used (`~/.local/share/nite/tarballs` and `esbuild` on Linux and macOS, the same under `%LOCALAPPDATA%\nite` on Windows).

## The user config

`config.json` in the config folder, edited with `nite config`:

```json
{
  "registry": "https://artifacts.acme.dev/api/npm/npm/",
  "@acme:registry": "https://npm.acme.dev/",
  "init.template": "islands"
}
```

| Key | Meaning |
|---|---|
| `registry` | The registry for unscoped packages. |
| `@scope:registry` | The registry for one scope. |
| `init.template` | The template `nite init` uses when `--template` is not given: `spa` or `islands`. |

Credentials are refused here; keep them in `.npmrc`. See [Private registries](../guides/private-registries.md).

## Precedence

Highest first:

1. `NITE_REGISTRY` (for `registry` only)
2. `registry` in the project's `nite.json`
3. The project's `.npmrc` (next to `nite.json`)
4. The user config (`config.json`)
5. The user's `~/.npmrc` (or the file named by `NPM_CONFIG_USERCONFIG`)
6. Defaults: `registry` is `https://registry.npmjs.org/`, `init.template` is `spa`

`nite config list --show-origin` shows the effective value of each setting and where it came from.

## .npmrc support

| Setting | Supported |
|---|---|
| `registry=` | Yes |
| `@scope:registry=` | Yes |
| `//host/path/:_authToken=` | Yes |
| `//host/path/:_auth=` | Yes |
| `//host/path/:username=` and `:_password=` | Yes |
| `${VAR}` expansion in values | Yes |
| `always-auth`, proxies, certificates, `strict-ssl` | No; Nite uses the system's proxy and certificate settings through .NET |

## Project-level files

| File | Purpose |
|---|---|
| `nite.json` | Project settings and packages. [Reference](nite-json.md). |
| `nite.lock.json` | Resolved package versions. |
| `.npmrc` | Registries and credentials for this project. |
| `.env*` | Public environment variables for client code. [Guide](../guides/environment.md). |
