---
title: Changelog
description: Notable changes in each version of nite.
---

# Changelog

<p class="lead">Notable changes, newest first. nite follows semantic versioning; while it is below 1.0, minor versions may change APIs outside the documented surface.</p>

## Unreleased (main)

### Added

- **Stylesheets.** Sass (the native Dart Sass compiler, over its embedded protocol), Less, Tailwind CSS 4 and the project's PostCSS config, in development and production, in the same order as Vite. CSS modules (`*.module.css`, `.module.scss`, `.module.less`) with `composes` and named exports. Package stylesheets imported from code (`import "@mantine/core/styles.css"`), and `url()` assets served in place during development. Hot updates follow everything a stylesheet depends on: imports, Sass partials, the PostCSS config, and new Tailwind classes in any project file, Razor views included. [Mantine](guides/mantine.md) works out of the box. ([Stylesheets](guides/stylesheets.md))
- **esbuild plugins in .NET.** The esbuild client implements esbuild's plugin protocol (`onResolve`, `onLoad`), so builds can call back into C#.
- **Importing projects.** `nite init --from` imports Vite and Create React App projects managed by npm, Yarn (classic and Berry), pnpm or Bun, keeping the versions their lockfiles pin, and reports what it could not bring along. Stylesheet tooling and `additionalData` are carried over. ([Importing](guides/importing.md))
- **Per-user directories and settings.** Configuration and caches follow the XDG Base Directory spec (`~/.config/nite`, `~/.cache/nite`). Layered settings from `NITE_REGISTRY`, `nite.json`, project and user `.npmrc`, and a user config edited with `nite config`. ([Settings](reference/settings.md))
- **Private registries.** Per-scope registries and `.npmrc` credentials (`_authToken`, `_auth`, `username`/`_password`, with `${VAR}` expansion), sent only to their own host. Registry metadata is cached and revalidated with ETags.
- **Install script warnings.** Packages the registry marks with `hasInstallScript` are reported when they are resolved, with specific messages for well-known ones (`core-js`, `esbuild`, `node-sass`, native addons such as `bcrypt`). ([Install scripts](guides/packages.md#install-scripts))
- **Continuous integration and NuGet releases.** A GitHub Actions workflow builds, tests and packs `Nite` and `Nite.Cli` on every push, and publishes them to nuget.org when a `v*` tag matching `Version` in `Directory.Build.props` is pushed. ([Contributing](contributing.md#continuous-integration-and-releases))
- `nite cache dir|clean|verify` and `nite config list|get|set|unset|path`.
- `nite watch --no-auto-restart`.

### Changed

- `nite watch` sets `DOTNET_WATCH_RESTART_ON_RUDE_EDIT=1`, so edits that need a restart (such as a new endpoint in `Program.cs`'s top-level code) restart the app instead of being applied as a no-op that waits for Ctrl+R.
- Production builds add Vite's default browser targets when `target` names only a language version, so CSS nesting and other new syntax are lowered.

### Fixed

- Version ranges whose alternatives include a dist-tag (`>=3.0.0 || >=4.0.0 || insiders`) no longer fail to install.

## 0.2.0

### Added

- **A new `nite` CLI** built on Spectre.Console: `init` (with `spa` and `islands` templates), `install` (`add`, `i`), `remove` (`rm`, `delete`, `uninstall`), `list` (`ls`), `update` (`up`, with `--check` and `--latest`), `build`, `watch`, `version` and `update-self`.
- `nite watch` runs `dotnet watch` with its browser refresh turned off, so single-page apps keep their state on C# changes; `--browser-refresh` keeps it for Razor Pages.
- The project logo and icon, used for the NuGet packages.

### Changed

- Licensed under the Apache License 2.0.

## 0.1.0

The first version.

- A development server inside ASP.NET Core (`UseNite`): TypeScript and JSX compiled on request by a long-lived esbuild service, bare imports through an import map to pre-bundled dependencies, and hot updates over a WebSocket.
- React Fast Refresh without Babel, driven by a module graph.
- C# hot reload forwarded to the page as a `nite:server-update` event.
- Single-page apps with `index.html` as an entry and `MapNiteSpa` for client-side routing.
- React islands in Razor Pages and MVC: `<island>`, `<nite-head>` and `<nite-module>`, with `load`, `idle`, `visible` and `media` loading strategies.
- An npm client in C#: semver resolution, hoisting, `nite.lock.json`, integrity checks.
- Production builds into `wwwroot/_nite` (minified, code-split, content-hashed), run automatically by `dotnet publish`.
- Environment variables from `.env` files with a public prefix, and tsconfig path aliases.
