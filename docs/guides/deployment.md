---
title: Production builds and deployment
description: How nite builds the client for production, how dotnet publish includes it, and how to deploy with CI, Docker and a CDN.
---

# Production builds and deployment

<p class="lead"><code>dotnet publish -c Release</code> runs <code>nite build</code> and includes the result. The published app is an ordinary ASP.NET Core app with static files: no Node, no esbuild, no <code>node_modules</code>.</p>

## What publish does

For Release builds, the targets in the `Nite` package run `nite build` before static web assets are collected:

1. `nite build` installs packages from `nite.lock.json` (a no-op when `node_modules` is current);
2. builds every entry (islands, `index.html` and other HTML pages, modules in `entries`) in one esbuild pass: minified, code-split, content-hashed;
3. writes the output and a `manifest.json` to `wwwroot/_nite/`.

The static web assets pipeline then precompresses the files (Brotli and gzip) and `MapStaticAssets` serves them with `ETag`s and the compressed variant each browser accepts. Client sources, `nite.json`, `nite.lock.json`, `node_modules` and `.nite` never reach the publish output.

```bash
dotnet publish -c Release -o publish
```

Run `nite build` on its own to inspect the output without publishing:

```text
$ nite build
╭────────────┬───────────────────────────────────┬───────────┬────────╮
│ Entry      │ Output                            │      Size │ Shared │
├────────────┼───────────────────────────────────┼───────────┼────────┤
│ main.tsx   │ wwwroot/_nite/main-MUGH3OMJ.js    │ 219.2 KiB │      - │
│ styles.css │ wwwroot/_nite/styles-V7BMX6ER.css │   0.3 KiB │      - │
╰────────────┴───────────────────────────────────┴───────────┴────────╯
html  wwwroot/_nite/index.html
✓ Built 2 entries in 176 ms
```

Sizes are before compression; the template's React app is about 60 KB with Brotli.

## Requirements on the build machine

The machine that **builds** needs the .NET SDK and the `nite` tool, plus network access to the npm registry (or your mirror) unless packages and the esbuild binary are already in the user cache. The machine that **runs** the app needs only the ASP.NET Core runtime.

How the build finds the tool is controlled by `NiteCommand`: by default the global `nite`; set it to `dotnet tool run nite` for a [local tool](https://learn.microsoft.com/dotnet/core/tools/local-tools-how-to-use). See [MSBuild properties](../reference/msbuild.md).

## GitHub Actions

```yaml
name: Publish
on:
  push:
    branches: [main]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: 10.0.x

      - name: Install nite
        run: dotnet tool install --global Nite.Cli

      # Packages and the esbuild binary are cached per user; keep them between runs.
      - uses: actions/cache@v4
        with:
          path: ~/.cache/nite
          key: nite-${{ runner.os }}-${{ hashFiles('**/nite.lock.json') }}
          restore-keys: nite-${{ runner.os }}-

      - name: Publish
        run: dotnet publish -c Release -o publish

      - uses: actions/upload-artifact@v4
        with:
          name: app
          path: publish
```

## Docker

Build in the SDK image, run in the smaller ASP.NET image:

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
RUN dotnet tool install --global Nite.Cli
ENV PATH="${PATH}:/root/.dotnet/tools"
WORKDIR /src

# Restore and install packages first, so these layers are cached until dependencies change.
COPY *.csproj nite.json nite.lock.json ./
RUN dotnet restore && nite install

COPY . .
RUN dotnet publish -c Release -o /app

FROM mcr.microsoft.com/dotnet/aspnet:10.0
WORKDIR /app
COPY --from=build /app .
ENTRYPOINT ["dotnet", "MyApp.dll"]
```

Add `node_modules/`, `.nite/`, `bin/`, `obj/` and `wwwroot/_nite/` to `.dockerignore`.

## Caching and CDNs

- Bundles, chunks and assets have content hashes in their names, so a deployment never changes the contents of an existing URL. Today `MapStaticAssets` serves them with `Cache-Control: no-cache` and an `ETag`: browsers revalidate and get a `304` when nothing changed, which is cheap but still a request per file. A CDN rule that caches `/_nite/*` for a long time is safe because of the hashes.
- HTML pages (`MapNiteSpa`'s output, your Razor pages) must not be cached long: they point at the current hashes. `MapNiteSpa` sends `Cache-Control: no-cache`.
- With a long-lived CDN cache, users who still have the previous page open keep loading the previous version's chunks from the CDN. Without one, a lazy-loaded chunk from the old version may be gone after a deployment; a full page load fixes it.

## Path base and subfolders

Production URLs are root-relative under `/_nite/`. `MapNiteSpa` adds the request's path base to the URLs in the page it serves, and the tag helpers do the same, but URLs inside JavaScript and CSS (lazy-loaded chunks, `url()` assets) assume the app is at the site root. Hosting under a subfolder (`/shop`) is therefore limited for now; see [Limits](../limits.md).

## Turning the build step off

```xml
<PropertyGroup>
  <NiteBuildEnabled>false</NiteBuildEnabled>
</PropertyGroup>
```

Useful when a separate CI step runs `nite build`, or for a server-only build of the project. Release builds then publish whatever is in `wwwroot/_nite`, which `dotnet clean` deletes.

## What if the build output is missing?

In production, `MapNiteSpa` and the tag helpers read `wwwroot/_nite/manifest.json`. If it is missing, requests fail with:

```text
wwwroot/_nite/manifest.json was not found. Run `nite build` (publishing does this for you) or run in Development.
```

Usually that means a Debug build was deployed, `NiteBuildEnabled` was false, or the environment is not Development when you expected it to be.
