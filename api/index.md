---
title: API reference
description: The public .NET API of the Nite library, generated from its source.
---

# API reference

<p class="lead">The public .NET surface of the <code>Nite</code> library, generated from the source on every documentation build.</p>

Most applications use only a handful of these types. Start with the ones in the first table; the rest exist because the `nite` command-line tool is built on the same library, and they are public so you can script nite's pieces (the esbuild client, the package installer, the production builder) from your own tools.

## Used by applications

| Type | What it is for |
|---|---|
| <xref:Nite.NiteExtensions> | `AddNite`, `UseNite` and `MapNiteSpa`: everything `Program.cs` needs. See [ASP.NET Core integration](../docs/reference/aspnet.md). |
| <xref:Nite.NiteOptions> and <xref:Nite.NiteMode> | Options for `AddNite`: force development or production mode, or point at a different project folder. |
| <xref:Nite.TagHelpers.IslandTagHelper>, <xref:Nite.TagHelpers.NiteHeadTagHelper>, <xref:Nite.TagHelpers.NiteModuleTagHelper> | `<island>`, `<nite-head>` and `<nite-module>` for Razor views. See [Tag helpers](../docs/reference/tag-helpers.md). |
| <xref:Nite.Assets.INiteAssets> | The URLs a page needs, in development or production. Use it to write your own tag helper or render nite's head into a non-Razor page. |
| <xref:Nite.NiteConfig> | The contents of `nite.json`, as loaded. See [nite.json](../docs/reference/nite-json.md). |

## For tools and integrations

| Namespace | Contents |
|---|---|
| <xref:Nite.Esbuild> | A client for a long-lived `esbuild --service` process: transforms, builds and .NET plugins. |
| <xref:Nite.Packages> | The npm client: semver ranges, registry access, tarballs and the installer that writes `nite.lock.json`. |
| <xref:Nite.Build> | The production builder and its manifest. |
| <xref:Nite.Css> | The stylesheet pipeline: Sass, Less, Tailwind and PostCSS in front of esbuild. |
| <xref:Nite.Dev> | The development server behind `/_nite`. |
| <xref:Nite.Import> | Importing Vite and Create React App projects, and reading npm, Yarn, pnpm and Bun lockfiles. |
| <xref:Nite.Configuration> | Per-user directories, `.npmrc` parsing and layered settings. |

> [!NOTE]
> nite is pre-1.0. Types outside the first table may change between minor versions.
