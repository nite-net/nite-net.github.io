---
title: Project layout
description: The files and folders in a NiteFx project, what each one is for, and which ones belong in source control.
---

# Project layout

<p class="lead">A NiteFx project is an ordinary ASP.NET Core project with a client folder and a <code>nite.json</code> next to the project file.</p>

## A single-page app

```text
MyApp/
  MyApp.csproj
  AGENTS.md                  instructions for AI coding agents
  Program.cs                 AddNite, UseNite, your API, MapNiteSpa
  nite.json                  client packages and settings
  nite.lock.json             resolved package versions
  .env                       optional; NITE_PUBLIC_* values reach the client
  Client/                    the client root ("clientRoot" in nite.json)
    index.html               the entry page
    main.tsx                 the entry module
    App.tsx
    styles.css
    tsconfig.json
  wwwroot/                   static files served as-is (favicon, robots.txt, images)
  node_modules/              installed packages
  .nite/                     dev server cache
```

## Razor Pages with islands

```text
MySite/
  MySite.csproj
  AGENTS.md
  Program.cs                 AddRazorPages, AddNite, UseNite
  nite.json
  nite.lock.json
  Pages/
    _ViewImports.cshtml      @addTagHelper *, Nite
    Shared/_Layout.cshtml    <nite-head /> inside <head>
    Index.cshtml             <island name="Counter" ... />
  Client/
    islands/                 every module here can be an <island> ("islands" in nite.json)
      Counter.tsx
      admin/UserTable.tsx    used as <island name="admin/UserTable" />
    lib/                     shared code, not islands
  wwwroot/site.css
```

Both models can live in one project: an `index.html` in the client root and an islands folder work side by side.

## The client root

Everything NiteFx compiles lives under the client root, `Client` by default. In development its files are served under `/_nite/src/`, so `Client/App.tsx` is `/_nite/src/App.tsx`. Nothing outside the client root is served by the dev server, with two exceptions: packages from `node_modules` (pre-bundled under `/_nite/deps/`, or as files under `/_nite/npm/`) and the dev runtime itself.

Change it with `"clientRoot"` in `nite.json`. Islands are looked up in `"islands"` relative to the client root.

## Files NiteFx reads

| File | Read by | Purpose |
|---|---|---|
| `nite.json` | Dev server, CLI, build | Packages and settings. Reloaded live in development. [Reference](../reference/nite-json.md). |
| `nite.lock.json` | Installer | Exact versions. Written by installs; do not edit by hand. |
| `Client/tsconfig.json` (and what it `extends` or `references`) | Dev server, build | `compilerOptions.paths` aliases; the build uses the file that declares them. |
| `.env`, `.env.local`, `.env.development`, `.env.production`, `.env.*.local` | Dev server, build | Public environment variables. [Guide](../guides/environment.md). |
| `postcss.config.*`, `.postcssrc*`, `package.json` `"postcss"` | CSS pipeline | PostCSS plugins. Looked up in the client root, then the project folder. |
| `.npmrc` (project and user) | Installer | Registries and credentials. [Guide](../guides/private-registries.md). |
| `.gitignore` | Tailwind scanner | Folders to skip when looking for class names. |

## Files NiteFx writes

| Path | Contents | In git? |
|---|---|---|
| `nite.lock.json` | Resolved versions and integrity hashes | **Yes** |
| `node_modules/` | Installed packages | No |
| `node_modules/.nite-state.json` | What the last install wrote, for cleanup | No |
| `.nite/deps/` | Pre-bundled dependencies | No |
| `.nite/tools/` | PostCSS, Tailwind and Less bundled for the JavaScript engine | No |
| `.nite/css/`, `.nite/runtime/` | Scratch files for stylesheet and production builds | No |
| `wwwroot/_nite/` | Production build output | No |

The `.gitignore` that `nite init` writes covers all of these:

```text
bin/
obj/
node_modules/
.nite/
wwwroot/_nite/
.env*.local
```

## Build integration

The `Nite` package brings MSBuild targets that:

- keep `node_modules` and `.nite` out of the project's default items, so the build does not walk thousands of files;
- never copy the client sources, `nite.json` or `nite.lock.json` to the build or publish output;
- run `nite build` before Release builds and include `wwwroot/_nite` in the publish output;
- remove `wwwroot/_nite` on `dotnet clean`.

See [MSBuild properties](../reference/msbuild.md).
