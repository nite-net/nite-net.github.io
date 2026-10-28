---
title: Limits and non-goals
description: What NiteFx deliberately does not do, and what it does not do yet.
---

# Limits and non-goals

<p class="lead">NiteFx is intentionally smaller than Vite. Knowing where the edges are before you start saves you finding them halfway through a project.</p>

## Non-goals

**Vite and Rollup plugins.** Vue single-file components, Svelte, Astro, MDX and similar need Vite's plugin pipeline and a JavaScript runtime in the build. If your project depends on them, Vite is the right tool. (PostCSS plugins and Tailwind plugins do work: see [Stylesheets](guides/stylesheets.md).)

**Server-side rendering of components.** Islands render on the client; use the fallback content inside `<island>` for what the server shows first. Meta-frameworks with their own servers (Next.js, Remix, Nuxt) are out of scope.

**Type checking.** Like Vite, NiteFx strips types without checking them, so compiling stays fast. Your editor checks as you type; run `tsc --noEmit` in CI. See [TypeScript](guides/typescript.md#type-checking).

**Running arbitrary Node tooling.** NiteFx does not provide a Node-compatible runtime for your scripts: linters, test runners and code generators keep running however you run them today.

## Packages

- **Registry packages only.** `git:`, `file:`, `link:`, `workspace:`, tarball URLs and `npm:` aliases are not supported.
- **Install scripts never run.** Packages that compile native addons or download binaries in `postinstall` do not work. NiteFx warns about them when it resolves them ([Install scripts](guides/packages.md#install-scripts)).
- **Optional dependencies are skipped.**
- **No `overrides` or `resolutions`.** Versions come from the ranges, the lockfile and `nite update`.
- **No workspaces.** One `nite.json` per project.

## Compilation

- **Fast Refresh is heuristic.** Components are found in esbuild's output by shape: PascalCase functions, arrow functions, `memo` and `forwardRef`. Class components and other higher-order components refresh by propagating to their importers. If a custom hook changes its internal hook order, save again or reload.
- **No Babel plugins** and no syntax that needs one.
- **No `import.meta.glob`**, and no Vite import suffixes (`?raw`, `?url`, `?worker`, `?inline`). Use explicit imports, `fetch`, and `new Worker(new URL("./worker.ts", import.meta.url), { type: "module" })`.
- **SVGs import as URLs**, not as React components (no svgr).

## Stylesheets

- **No Stylus.**
- **Tailwind CSS 4 only**, not 3.
- **PostCSS and Tailwind plugins must be plain JavaScript**, since they run in an interpreter. The interpreter is also slower than Node: the first Tailwind compile in a session takes a second or two.
- **CSS that a package's own JavaScript imports** is not collected; import the package's stylesheet from your code.
- **No `css.modules` options** such as `localsConvention`.
- **Relative `url()`s inside Sass partials** are not rebased to the partial's folder.

## Hosting

- **Production asset URLs assume the site root.** Bundles and chunks load from `/_nite/...`. HTML from `MapNiteSpa` and the tag helpers include the request's path base, but URLs inside JavaScript and CSS (lazy chunks, `url()` assets) do not, so hosting under a subfolder (`/shop`) does not fully work yet.

## Platform

- **.NET 10** and ASP.NET Core 10.
- **Linux, macOS and Windows on x64 and Arm64.** Other platforms work wherever esbuild (and, for Sass, Dart Sass) publish binaries, or with `NITE_ESBUILD_PATH` / `NITE_SASS_PATH`.

## Status

NiteFx is at version 0.8. APIs outside `AddNite`, `UseNite`, `MapNiteSpa`, the tag helpers and `nite.json` may change between minor versions. Bugs and gaps are tracked on [GitHub](https://github.com/nite-net/nite/issues). Which of these limits go away next is on the [roadmap](roadmap.md).
