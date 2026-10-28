---
title: Changelog
description: Notable changes in each version of NiteFx.
---

# Changelog

<p class="lead">Notable changes, newest first. NiteFx follows semantic versioning; while it is below 1.0, minor versions may change APIs outside the documented surface.</p>

## Unreleased (main)

### Changed

- **Nite is now NiteFx**, short for Nite Framework, and the docs moved to [nitefx.dev](https://nitefx.dev). Old links to `nite-net.github.io` redirect. Nothing in your project changes: the packages, the `Nite` namespace and the `nite` command keep their names.

### Added

- **Nite.Diagnostics: log messages as Markdown.** A new, separate package for any .NET project: each log message is a Markdown file whose front matter a source generator compiles into a structured `ILogger` method (backed by `LoggerMessage.Define`, with the message's code as the event name), and whose body documents it. Mistakes in a file are build errors at that file and line. ([Log messages as Markdown](guides/log-messages.md))
- **Codes for NiteFx's warnings.** Three warnings now have a code, an event ID and a page: NITE1001 (a module missing from `entries`), NITE1002 (nothing to build) and NITE1003 (a peer dependency version mismatch). Their text is unchanged. ([Log messages](reference/diagnostics/index.md))
- **Code signing policy and privacy policy.** Release binaries will be signed through [SignPath Foundation](https://signpath.org); see the [Code signing policy](code-signing.md). The [Privacy policy](privacy.md) lists the only network connections NiteFx makes. It collects no information.

## 0.8.1

### Added

- **`AGENTS.md` in new projects.** `nite init` and the `dotnet new` templates write an `AGENTS.md` for AI coding agents: the commands, the project layout, and the Vite and npm habits that do not apply. ([Working with an AI coding agent](getting-started.md#working-with-an-ai-coding-agent))
- **Docs for agents.** The site publishes [`llms.txt`](https://nitefx.dev/llms.txt), [`llms-full.txt`](https://nitefx.dev/llms-full.txt) and a Markdown copy of every page.

## 0.8.0

### Added

- **Several single-page apps in one app.** `MapNiteSpa(page, path: "/login")` serves a page under its own path (and its client-side routes), next to a catch-all app; each is an endpoint with its own authorization. ([More than one page](guides/single-page-apps.md#more-than-one-page))
- **Content Security Policy nonces.** `NiteOptions.CspNonce` gives NiteFx the request's nonce, which it puts on the import map, client config and module scripts it writes, and in development on the dev client, CSS imported from modules and the error overlay. A strict policy without `'unsafe-inline'` then works in both. `NiteHead.ToHtml(nonce)` does the same for hand-written layouts. ([Content Security Policy](reference/aspnet.md#content-security-policy))
- **Identity sample.** `samples/Nite.Identity`: ASP.NET Core Identity with EF Core and SQLite, two seeded users, a public login app and a protected main app that receives the user's claims through client config. It follows the backend-for-frontend pattern: server-side sessions behind an HttpOnly `__Host-` cookie, antiforgery tokens, a strict nonce-based CSP, rate-limited sign-in with lockout, and a refusal to run outside Development with the published demo passwords.

### Changed

- Pages carrying client config are sent `Cache-Control: private, no-store` instead of `private, no-cache`, so the browser does not keep a signed-in user's page.

## 0.7.0

### Added

- **Client config.** `NiteOptions.ClientConfig` (or `ClientConfigAsync`) hands values from the running server to client code as each page is served: `import { config } from "nite:config"`. Unlike `NITE_PUBLIC_` variables, which are inlined at compile time, they can differ per environment and per request, so one build runs everywhere. `nite init` and the templates add `Client/nite-env.d.ts` to type them. ([Values from the running server](guides/environment.md#values-from-the-running-server))
- **Application Insights guide.** Browser telemetry with the Application Insights SDK: per-environment connection strings through client config, loading the SDK lazily, and one transaction from page load through API calls. The Aspire sample does all of it. ([Application Insights in the browser](guides/application-insights.md))
- **Telemetry.** OpenTelemetry traces and metrics through an `ActivitySource` and a `Meter` named `Nite` (`NiteTelemetry.SourceName`, `NiteTelemetry.MeterName`): dev server startup, per-request compiles, each stylesheet tool, hot updates, pre-bundling, package installs and production builds. No OpenTelemetry dependency. ([Telemetry, health checks and Aspire](guides/observability.md))
- **Health check.** `AddHealthChecks().AddNite()` reports a dev server that is still starting or failed to, and a production app missing its build output.
- **Aspire guide and sample.** Running a NiteFx app under Aspire: wiring, hot reload, passing service URLs to client code, and deploying. `samples/Nite.Aspire` has a NiteFx React app and an API service under one AppHost.
- Requests under `/_nite` are named after their route in traces (`GET /_nite/src/{**path}`) instead of a bare `GET`.

### Changed

- The dev server starts its work once the host has started, so OpenTelemetry sees the startup trace.

## 0.6.0

### Added

- **`dotnet new` templates.** The `Nite.Templates` package adds `nite-spa` and `nite-islands` to `dotnet new` and to the new-project dialogs of Visual Studio and Rider. They are the same files `nite init` writes. ([Getting started](getting-started.md#with-dotnet-new))

### Changed

- **Releases take their version from the tag.** Pushing `v0.6.0` publishes 0.6.0; there is no version to bump in `Directory.Build.props` first. CI builds are prereleases of the next patch after the newest tag. ([Contributing](contributing.md#continuous-integration-and-releases))

## 0.5.0

### Added

- **Install script warnings.** Packages the registry marks with `hasInstallScript` are reported when they are resolved, with specific messages for well-known ones (`core-js`, `esbuild`, `node-sass`, native addons such as `bcrypt`). ([Install scripts](guides/packages.md#install-scripts))
- **Continuous integration and NuGet releases.** A GitHub Actions workflow builds, tests and packs `Nite` and `Nite.Cli` on every push, and publishes them to nuget.org with trusted publishing (no stored API key) when a `v*` tag matching `Version` in `Directory.Build.props` is pushed. ([Contributing](contributing.md#continuous-integration-and-releases))

## 0.4.0

### Added

- `nite watch --no-auto-restart`.

### Changed

- `nite watch` sets `DOTNET_WATCH_RESTART_ON_RUDE_EDIT=1`, so edits that need a restart (such as a new endpoint in `Program.cs`'s top-level code) restart the app instead of being applied as a no-op that waits for Ctrl+R.
- Production builds add Vite's default browser targets when `target` names only a language version, so CSS nesting and other new syntax are lowered.

## 0.3.0

### Added

- **Stylesheets.** Sass (the native Dart Sass compiler, over its embedded protocol), Less, Tailwind CSS 4 and the project's PostCSS config, in development and production, in the same order as Vite. CSS modules (`*.module.css`, `.module.scss`, `.module.less`) with `composes` and named exports. Package stylesheets imported from code (`import "@mantine/core/styles.css"`), and `url()` assets served in place during development. Hot updates follow everything a stylesheet depends on: imports, Sass partials, the PostCSS config, and new Tailwind classes in any project file, Razor views included. [Mantine](guides/mantine.md) works out of the box. ([Stylesheets](guides/stylesheets.md))
- **esbuild plugins in .NET.** The esbuild client implements esbuild's plugin protocol (`onResolve`, `onLoad`), so builds can call back into C#.
- **Importing projects.** `nite init --from` imports Vite and Create React App projects managed by npm, Yarn (classic and Berry), pnpm or Bun, keeping the versions their lockfiles pin, and reports what it could not bring along. Stylesheet tooling and `additionalData` are carried over. ([Importing](guides/importing.md))
- **Per-user directories and settings.** Configuration and caches follow the XDG Base Directory spec (`~/.config/nite`, `~/.cache/nite`). Layered settings from `NITE_REGISTRY`, `nite.json`, project and user `.npmrc`, and a user config edited with `nite config`. ([Settings](reference/settings.md))
- **Private registries.** Per-scope registries and `.npmrc` credentials (`_authToken`, `_auth`, `username`/`_password`, with `${VAR}` expansion), sent only to their own host. Registry metadata is cached and revalidated with ETags.
- `nite cache dir|clean|verify` and `nite config list|get|set|unset|path`.

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
