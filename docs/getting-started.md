---
title: Getting started
description: Install the nite CLI, create a React single-page app or a Razor site with islands, and run it with hot reload.
---

# Getting started

<p class="lead">Install the CLI, create an app, and run it with <code>nite watch</code>. About five minutes, most of it the first package download.</p>

## Requirements

- **The .NET 10 SDK.** Check with `dotnet --version`.
- **Linux, macOS or Windows** on x64 or Arm64. nite downloads the matching esbuild (and, if you use Sass, Dart Sass) binary for your platform.
- **Network access to the npm registry** the first time: nite downloads esbuild and your packages, then caches them per user. After that, startup reuses the cache and the lockfile. A private registry or mirror works too; see [Private registries](guides/private-registries.md).

You do **not** need Node.js, npm, or any global JavaScript tooling.

## Install nite

nite is two packages: **`Nite`**, the library your web project references, and **`Nite.Cli`**, the `nite` command-line tool. They are not published to NuGet yet. Until they are, build them from source into a local package feed. This takes about a minute and behaves exactly like the published packages will.

# [Local package feed (recommended)](#tab/feed)

```bash
git clone https://github.com/nite-net/nite
cd nite

# Build both packages into a folder that acts as a NuGet feed.
dotnet pack src/Nite -c Release -o ~/.nite-packages
dotnet pack src/Nite.Cli -c Release -o ~/.nite-packages

# Install the `nite` tool from it.
dotnet tool install --global Nite.Cli --add-source ~/.nite-packages

# Let every project restore the Nite package from it.
dotnet nuget add source ~/.nite-packages --name nite-local
```

Check the installation:

```bash
nite version
```

To update later, pull the repository, pack again (bump `Version` in `Directory.Build.props` if you want NuGet to see a new version) and run `dotnet tool update --global Nite.Cli --add-source ~/.nite-packages`. (`nite update-self` does the same against your configured NuGet sources, which is the simpler option once the packages are on NuGet.)

# [Reference a source checkout](#tab/source)

If you are working on nite itself, point new projects at your checkout instead. The project then references `src/Nite` and `src/Nite.Cli` directly, so changes to nite take effect on the next build.

```bash
git clone https://github.com/nite-net/nite
cd nite && dotnet build

# Run the CLI from the checkout.
dotnet run --project src/Nite.Cli -- init ../my-app --nite-source .
```

Inside such a project, run the CLI the same way (`dotnet run --project <nite>/src/Nite.Cli -- watch`), or install the tool as in the other tab.

# [NuGet (once published)](#tab/nuget)

```bash
dotnet tool install --global Nite.Cli
```

New projects reference the `Nite` package from nuget.org with no further setup.

---

## Create an app

`nite init` creates a project in a new folder (or the current one) and installs its packages.

# [Single-page app](#tab/spa)

```bash
nite init my-app
cd my-app
```

```text
my-app/
  my-app.csproj
  Program.cs              AddNite, UseNite, an /api/hello endpoint, MapNiteSpa
  nite.json               packages and settings for the client
  nite.lock.json          resolved versions (commit it)
  Client/
    index.html            the entry page
    main.tsx              createRoot(...).render(<App />)
    App.tsx               calls /api/hello and re-fetches on C# changes
    styles.css
    tsconfig.json
  node_modules/           installed packages (ignored by git)
```

# [Razor Pages with islands](#tab/islands)

```bash
nite init my-site --template islands
cd my-site
```

```text
my-site/
  my-site.csproj
  Program.cs              Razor Pages, AddNite, UseNite
  nite.json
  Pages/
    _ViewImports.cshtml   @addTagHelper *, Nite
    Shared/_Layout.cshtml <nite-head /> in <head>
    Index.cshtml          <island name="Counter" props="new { start = 0 }">
  Client/
    islands/Counter.tsx   a React component used as an island
  wwwroot/site.css
```

---

> [!TIP]
> Set your preferred template once with `nite config set init.template islands`.

## Run it

```bash
nite watch
```

`nite watch` runs `dotnet watch` with nite handling the browser. The first start downloads esbuild and pre-bundles React (a few seconds); after that it starts in about as long as the app takes to build. `dotnet watch` opens your browser at the URL in `Properties/launchSettings.json`.

Now try the loop:

1. **Edit `Client/App.tsx`.** Change the heading and save. The page updates in place in about 150 ms. Click the button a few times first: the count survives the edit.
2. **Edit `Program.cs`.** Change the message `/api/hello` returns and save. Hot reload applies it in the running app and the page re-fetches, still without a reload.
3. **Break something.** Delete a closing brace in `App.tsx`. An overlay shows the error with its location; fixing it clears the overlay.
4. **Add an endpoint.** Add a new `app.MapGet(...)` line to `Program.cs`. That needs a restart, so `nite watch` restarts the app and the page reloads once it is back (about 10 seconds).

For the Razor template, run `nite watch --browser-refresh` instead, so `dotnet watch` reloads the page when a `.cshtml` file changes. See [Hot reload and nite watch](guides/hot-reload.md).

## Add a package

```bash
nite add react-router          # a runtime dependency
nite add -D @types/node        # a dev dependency (types, tooling)
```

`nite add` updates `nite.json`, resolves versions into `nite.lock.json` and installs into `node_modules`. If the app is running, the dev server notices the change, pre-bundles the new package and reloads the page. See [Packages](guides/packages.md).

## Publish

```bash
dotnet publish -c Release
```

Release builds run `nite build`, which writes minified, content-hashed bundles to `wwwroot/_nite`; the publish output serves them precompressed through `MapStaticAssets`. Nothing in the published app needs Node, esbuild or `node_modules`. See [Production builds and deployment](guides/deployment.md).

## Already have a Vite app?

```bash
nite init my-app --from ../my-vite-app --dry-run   # see the plan
nite init my-app --from ../my-vite-app             # do it; the source is not changed
```

See [Importing a project](guides/importing.md).

## Next steps

- [Tutorial: a full-stack app](tutorial.md) builds on the SPA template step by step.
- [Single-page apps](guides/single-page-apps.md) and [Islands](guides/islands.md) cover each model in depth.
- [nite.json reference](reference/nite-json.md) lists every setting.
