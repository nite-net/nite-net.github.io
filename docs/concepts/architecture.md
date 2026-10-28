---
title: How NiteFx works
description: The moving parts behind NiteFx, from the esbuild service and the npm client to Fast Refresh, the stylesheet pipeline and the production build.
---

# How NiteFx works

<p class="lead">NiteFx does the orchestration in .NET and hands compilation to esbuild. This page walks through each piece, roughly in the order a request meets them.</p>

```text
 browser ──GET /_nite/src/App.tsx──▶ ASP.NET Core app
                                      │  UseNite(): NiteDevServer
                                      │    ├─ transform (esbuild service) ─▶ cached JS
                                      │    ├─ rewrite imports (import map, ?import, ?t=)
                                      │    └─ Fast Refresh registration
 browser ◀──────── ESM module ────────┘
 browser ◀──WebSocket /_nite/ws── file watcher ─▶ module graph ─▶ update / css / reload
```

## esbuild, as a service

[esbuild](https://esbuild.github.io) compiles TypeScript and JSX. NiteFx downloads the platform's binary from the same npm package esbuild's own installer uses (`@esbuild/linux-x64`, `@esbuild/darwin-arm64` and so on), verifies it against the registry's integrity hash, and caches it per user.

It does not run esbuild once per file. It starts one `esbuild --service` process and keeps it for the life of the app, talking esbuild's binary stdio protocol: the same channel esbuild's JavaScript API uses. Transforms take a few milliseconds and run concurrently. Builds can call back into .NET through esbuild's plugin protocol, which is how stylesheets reach the [CSS pipeline](#the-stylesheet-pipeline).

## Packages without npm

A small npm client written in C# reads `dependencies` and `devDependencies` from `nite.json`, resolves semver ranges against the registry, and installs into an ordinary `node_modules` folder, hoisted the way npm does it. Editors, the TypeScript language service and esbuild all find packages where they expect them.

- Resolution is recorded in **`nite.lock.json`**. With a current lockfile, an install never asks the registry for metadata.
- Tarballs are verified against their integrity hash and cached per user.
- **Install scripts never run.** Packages that need a `postinstall` step (native addons, mostly) do not work; NiteFx warns when it resolves one.
- Optional dependencies are skipped.

See [Packages and the lockfile](../guides/packages.md).

## The dev server

`app.UseNite()` mounts the dev server at `/_nite`, inside your app, in the Development environment only. Each source file is compiled on request and cached until it changes. Before serving a module, NiteFx rewrites its import specifiers:

| In your code | Served as | Why |
|---|---|---|
| `import { x } from "./util"` | `./util.ts` | One canonical URL per file, so a module is never instantiated twice. |
| `import logo from "./logo.svg"` | `./logo.svg?import` | Non-JavaScript imports become small JavaScript modules (a URL, CSS, JSON). |
| `import "react"` | `react` (unchanged) | Bare imports resolve through an **import map** to pre-bundled dependencies. |
| A module that just changed | `./Button.tsx?t=1729…` | The timestamp makes importers fetch the new version. |

Path aliases from your tsconfig (`@/components/Button`) are resolved the same way. The full URL layout is in [Dev server URLs](../reference/dev-server-urls.md).

## Dependency pre-bundling

Browsers can import ES modules, but most packages are not shaped for it: React is still CommonJS, and a package can be hundreds of files. Like Vite, NiteFx pre-bundles every bare import your code uses into a single ESM file per package, in **one** esbuild pass with code splitting, so `react-dom` and your code share one copy of React.

CommonJS packages get a generated wrapper whose named exports come from a scan of the package's code (the same approach as Node's `cjs-module-lexer`), so `import { useState } from "react"` works. The result is cached under `.nite/deps` and only rebuilt when your bare imports or the lockfile change. Importing a package for the first time while the app runs triggers a re-bundle and a page reload.

## React Fast Refresh, without Babel

esbuild has no Fast Refresh transform, so NiteFx adds one after the fact. It reads esbuild's output for each JSX or TSX module and:

1. finds components by shape: PascalCase functions, arrow functions assigned to PascalCase names, `memo` and `forwardRef` wrappers, and default exports that are components;
2. registers each with `react-refresh`'s runtime and signs it with its hook calls, so a change in hook order is detected;
3. marks the module a **refresh boundary** if every export is a component.

A module graph records who imports what among the modules the browser has loaded. When a file changes, NiteFx walks up from it to the nearest boundaries, recompiles, and tells the browser to re-import those modules with a new timestamp. React then swaps the new implementations in and keeps state. If the walk reaches the page's entry module (`main.tsx`), nothing can accept the update, and the page reloads.

## The file watcher and the browser client

A file watcher on the client folder debounces saves (editors often write in several steps) and decides, per change:

| Change | Message to the browser |
|---|---|
| A component module, or a module only components import | `update`: re-import the boundaries |
| A stylesheet, or a file a stylesheet depends on | `css`: swap the stylesheet in place |
| A CSS module | `update` for the components that import it |
| `index.html`, the entry module, a deleted file | `reload` |
| A compile error | `error`: show the overlay; the next good save clears it |
| `nite.json` | Install, re-bundle, `reload` |
| `.env*`, `tsconfig*.json` | Recompile, `reload` |

The browser client (`/_nite/client.js`) receives these over a WebSocket at `/_nite/ws`. If the socket drops (the server restarting under `dotnet watch`), it reconnects and reloads, waiting until the server answers first so the tab never lands on a "can't connect" page.

## C# hot reload, forwarded

NiteFx registers a .NET `MetadataUpdateHandler`. When `dotnet watch` applies a C# change inside the running app, the runtime calls it, and the dev server broadcasts a `server-update` message. The client turns that into a `nite:server-update` DOM event, which pages use to re-fetch data. See [Hot reload](../guides/hot-reload.md).

## The stylesheet pipeline

Stylesheets go through the same steps as in Vite, in development and production:

1. **Sass** (`.scss`, `.sass`) or **Less** (`.less`), by extension;
2. **Tailwind CSS 4**, when the file uses it;
3. **PostCSS**, when the project has a config;
4. **esbuild**: `@import` inlining, CSS modules, `url()` assets, and in production, minifying and lowering.

Sass runs as the native Dart Sass binary over its embedded protocol, one long-lived compiler like esbuild. PostCSS (with your plugins), Tailwind's compiler and Less are plain JavaScript: NiteFx bundles them from your `node_modules` with esbuild and runs them in [Jint](https://github.com/sebastienros/jint), a JavaScript interpreter written in C#, with a small shim for the Node built-ins they use. Tailwind's file scanner is native code, so NiteFx has its own in C#; it scans the whole project, including Razor views. See [Stylesheets](../guides/stylesheets.md).

## The production build

`nite build` (which `dotnet publish` runs for Release builds) does one esbuild build for every entry: islands, HTML pages and the modules listed in `entries`. The output is minified, split into shared chunks, content-hashed and written to `wwwroot/_nite` with a `manifest.json` that maps each entry to its files, CSS and preloads.

At runtime in production, the tag helpers and `MapNiteSpa` read the manifest, and `MapStaticAssets` serves the files (precompressed with Brotli and gzip by the static web assets pipeline). `UseNite()` only marks the files with a content hash in their name as immutable, so browsers never ask for them again. See [Development and production](development-and-production.md).

## Where things live

| Path | What | Commit it? |
|---|---|---|
| `nite.json` | Packages and settings | Yes |
| `nite.lock.json` | Resolved package versions | Yes |
| `node_modules/` | Installed packages | No |
| `.nite/` | Dev server cache: pre-bundled dependencies, bundled CSS tools | No |
| `wwwroot/_nite/` | Production build output | No (built on publish) |
| `~/.cache/nite/` | Per-user download cache: tarballs, registry metadata, esbuild, Sass | Not in the project |
