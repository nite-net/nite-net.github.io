---
title: Introduction
description: What NiteFx is, the problem it solves, and how it compares to the usual ways of putting a React frontend on ASP.NET Core.
---

# Introduction

<p class="lead">NiteFx runs TypeScript and React inside ASP.NET Core the way Vite runs them in Node: compiled on request, with hot updates that keep component state, and a production build that ships hashed, code-split bundles. It needs the .NET SDK and nothing else.</p>

*NiteFx* is short for **Nite Framework**, and *Nite* is pronounced like **night**, not *neat*. (Vite, whose dev loop it borrows, is French for "quick" and is pronounced *veet*.) The NuGet packages (`Nite`, `Nite.Cli`, `Nite.Templates`), the C# namespace and the `nite` command keep the short name.

## The problem

Putting a modern frontend on an ASP.NET Core app usually means running two toolchains side by side:

- a Node.js install, `package.json`, a lockfile and a bundler (Vite, webpack) for the client;
- the .NET SDK, a project file and `dotnet watch` for the server;
- a dev proxy or CORS settings so the two servers can talk, and a build step in CI that stitches the outputs together.

Each half is good at what it does. The seams between them are where the time goes: two terminals, two hot-reload systems that know nothing about each other, a proxy configuration that drifts from production, and a Node version to keep current on every machine and build agent.

## What NiteFx does instead

NiteFx moves the frontend dev server into your ASP.NET Core app. One project, one process, one `dotnet watch`:

- **Edit a React component** and it updates in place, with its state intact (React Fast Refresh).
- **Edit a C# endpoint** and hot reload applies it in the running app; the page gets a `nite:server-update` event and re-fetches, without reloading.
- **Run `dotnet publish`** and the client is built into minified, content-hashed bundles in `wwwroot/_nite`, served precompressed by `MapStaticAssets`.

There is no `node`, `npm`, `package.json` or Vite anywhere. Compilation is done by [esbuild](https://esbuild.github.io), the same Go binary Vite uses for dependency pre-bundling, which NiteFx downloads and drives itself. Packages come from the npm registry through a small npm client written in C#.

## Two ways to use it

**A single-page app.** `Client/index.html` and React (or plain TypeScript), served by `app.MapNiteSpa()` next to your API. The app and the API share an origin, so there is no CORS and no proxy. See [Single-page apps](guides/single-page-apps.md).

**Islands in Razor pages.** Server-rendered Razor Pages or MVC views with interactive React components exactly where you need them:

```cshtml
<island name="TodoList" props='new { title = "Today", items = Model.Todos }' client="visible">
    @* Server-rendered fallback until the island loads *@
    <ul>@foreach (var t in Model.Todos) { <li>@t.Title</li> }</ul>
</island>
```

See [Islands in Razor Pages](guides/islands.md).

## How it compares

| | NiteFx | Vite + ASP.NET Core | SPA templates (`SpaProxy`) | LibMan / CDN scripts |
|---|---|---|---|---|
| Node.js required | No | Yes | Yes | No |
| Processes in development | One | Two | Two (proxied) | One |
| TypeScript and JSX | Yes (esbuild) | Yes | Yes | No |
| React Fast Refresh | Yes | Yes | Yes | No |
| C# changes reach the page without a reload | Yes (`nite:server-update`) | No | No | No |
| npm packages | Yes (C# client) | Yes | Yes | A curated subset |
| Sass, Less, Tailwind, PostCSS, CSS modules | Yes | Yes | Yes | No |
| Islands in Razor views | Built in | Manual | No | Manual |
| Vite and Rollup plugins | No | Yes | Yes | No |
| Framework-specific SSR (Next.js, Remix) | No | Via the framework | Via the framework | No |

NiteFx is deliberately smaller than Vite. If your project depends on Vite plugins (Vue single-file components, Svelte, MDX), or on a meta-framework with its own server, keep using those tools. [Limits and non-goals](limits.md) lists what NiteFx does not do.

## What it is good for

- Internal tools, dashboards and line-of-business apps where the team writes C# and wants a React frontend without adopting the Node ecosystem's operations.
- Razor sites that need a handful of interactive widgets without becoming a single-page app.
- Teams that want one build, one deployment artifact and one dev command.
- Moving an existing Vite or Create React App frontend next to its API, keeping the exact package versions it runs today ([Importing a project](guides/importing.md)).

## Status

NiteFx is at version **0.8**. The core loop (compilation, Fast Refresh, islands, packages, stylesheets, production builds) is complete and tested against real applications, including a [Mantine](guides/mantine.md) app and a [Tailwind CSS 4](guides/tailwind.md) app. The packages are [on NuGet](https://www.nuget.org/packages/Nite.Cli), so [installation](getting-started.md#install-nitefx) is one `dotnet tool install`.

## Next steps

- [Getting started](getting-started.md): install the CLI and create your first app.
- [Tutorial](tutorial.md): build a small full-stack app and see each part of the dev loop.
- [How NiteFx works](concepts/architecture.md): the moving parts, for when you want to know what happens on save.
