---
title: Development and production
description: How NiteFx behaves in each mode, how it decides which one it is in, and what changes between them.
---

# Development and production

<p class="lead">The same <code>Program.cs</code> runs a compiling dev server in development and serves prebuilt static files in production. This page explains the switch and the differences.</p>

## Which mode am I in?

`AddNite()` picks the mode from the hosting environment: **development** when `IWebHostEnvironment.IsDevelopment()` is true (`ASPNETCORE_ENVIRONMENT=Development`), **production** otherwise. Override it with <xref:Nite.NiteOptions>:

```csharp
builder.Services.AddNite(options =>
{
    // Serve the production build even in Development, to check it locally.
    options.Mode = NiteMode.Production;
});
```

`NiteMode.Development` does the opposite: the dev server in a Staging environment, say.

## What changes

| | Development | Production |
|---|---|---|
| `UseNite()` | Mounts the dev server at `/_nite` and starts the file watcher | Does nothing |
| Source files | Compiled on request, cached until they change | Built ahead of time by `nite build` |
| Packages | Installed on startup from `nite.lock.json`; pre-bundled into `.nite/deps` | Bundled into the output chunks |
| `MapNiteSpa()` | Serves `Client/index.html` from source, with the dev client injected | Serves `wwwroot/_nite/index.html` with hashed URLs |
| `<island>`, `<nite-module>`, `<nite-head>` | Point at `/_nite/src/...` and the import map | Point at hashed files from `manifest.json` |
| CSS imported from code | Injected as `<style>` tags by the importing module | Extracted to `.css` files and linked |
| `import.meta.env.MODE` | `"development"` | `"production"` |
| `process.env.NODE_ENV` | `"development"` | `"production"` |
| Source maps | Inline | Separate `.map` files |
| Minification | None | Yes |
| Errors | Overlay in the page | Build fails |

## Startup in development

On the first request, the dev server:

1. downloads esbuild if this machine has not cached it;
2. installs packages if `node_modules` does not match `nite.lock.json` (a no-op when it does);
3. compiles every module in the client root once, to discover all bare imports;
4. pre-bundles those dependencies (skipped when nothing changed since last time) and, in parallel, warms up the stylesheet tools the project uses.

Requests wait for this to finish, so the first page load is complete rather than a cascade of reloads. On a warm cache it takes about as long as the app takes to start.

## The production build

`nite build` runs before Release builds (and therefore before `dotnet publish -c Release`). It writes:

```text
wwwroot/_nite/
  manifest.json              entry → file, CSS, preloads
  index.html                 the SPA page with hashed URLs (if Client/index.html exists)
  main-MUGH3OMJ.js           an entry, at its path under the client root (Client/main.tsx)
  styles-V7BMX6ER.css        a stylesheet linked from index.html
  islands/Counter-AB12CD34.js
  islands-runtime-….js       the island loader and renderer (if there are islands)
  chunks/…                   code shared between entries
  assets/…                   images and fonts referenced from code or CSS
  *.map                      source maps
```

Entries keep their folder: `Client/src/main.tsx` becomes `src/main-<hash>.js`. CSS that a module imports is collected into one `.css` file per entry, next to it.

Production assumes the build output is present. If `manifest.json` is missing, `MapNiteSpa` and the tag helpers fail with a message telling you to run `nite build`. See [Production builds and deployment](../guides/deployment.md).

## Checking the production build locally

```bash
nite build
ASPNETCORE_ENVIRONMENT=Production dotnet run --no-launch-profile
```

Or set `options.Mode = NiteMode.Production` temporarily, as above. For an exact rehearsal of a deployment, publish and run the output: `dotnet publish -c Release -o publish && dotnet publish/MyApp.dll`. `dotnet clean` removes `wwwroot/_nite` again; Debug builds never include it, so a stale production build cannot leak into development.
