---
title: Roadmap
description: Where Nite is going next, in the order we plan to ship it.
---

# Roadmap

<p class="lead">What we plan to build next, in order. These are plans, not promises: priorities change when you tell us what hurts. Open or vote on an <a href="https://github.com/nite-net/nite/issues">issue</a> to move something up.</p>

Released work is in the [changelog](changelog.md); what Nite deliberately does not do is in [Limits and non-goals](limits.md).

## 0.9: safer and faster production builds

Small changes that close gaps in [Limits](limits.md) and continue the security work in 0.8.

- **Subresource integrity.** Production scripts and the import map carry `integrity` hashes, so a CDN or proxy that alters a bundle gets it refused by the browser. Pairs with the [Content Security Policy](reference/aspnet.md#content-security-policy) support in 0.8.
- **Immutable caching for hashed files.** Bundles, chunks and assets have content hashes in their names but are served with `no-cache` today, which costs a `304` per file on every visit. They will be served as `immutable` instead.
- **A minimum release age for packages.** A setting in `nite.json` (for example `"minimumReleaseAge": "3d"`) makes `nite add` and `nite update` pass over versions published more recently than that. Malicious package versions are usually found and removed within days, so waiting a few days avoids most of them.
- **`?raw` and `?url` imports**, and SVGs imported as React components, for code coming from Vite.
- **Hosting under a path base.** URLs inside production JavaScript and CSS (lazy chunks, `url()` assets) work when the app is served from a subfolder such as `/shop`, not only from the site root.

## 0.10: knowing and fixing vulnerable packages

- **`nite audit`.** Checks every package in `nite.lock.json` against the npm advisory database and reports known vulnerabilities. `nite build` can fail on them above a severity you choose, so CI catches them.
- **`overrides`.** Pin a dependency of a dependency to a patched version without waiting for every package above it to release one. These two ship together: a report you cannot act on is only half a feature.

## 1.0: one set of types from C# to TypeScript

- **Generated API types.** ASP.NET Core already describes your endpoints as an OpenAPI document. In development, Nite will turn it into TypeScript types and a typed `fetch` wrapper, and refresh them on every C# hot reload, so renaming a property on a C# record shows up as a type error in the TypeScript that uses it. The same will cover [client config](guides/environment.md#values-from-the-running-server) when it returns a named type.
- **A stable API.** From 1.0, Nite follows semantic versioning for its whole public surface, not only `AddNite`, `UseNite`, `MapNiteSpa`, the tag helpers and `nite.json`.

## Not planned

These come up, and the answer is no for now, for these reasons:

- **Platform-specific optional dependencies.** Nite already fetches the right esbuild and Dart Sass binaries for each platform. Most other packages that need this are native Node addons, which cannot run in a browser. If a browser package you need depends on it, open an issue with its name.
- **Built-in type checking.** It needs Node, or a JavaScript interpreter that would make every save slow. Run `tsc --noEmit` in your editor and CI; the generated API types in 1.0 add the checking Nite can do best.
- **Server-side rendering, and Vue, Svelte or other Vite plugins.** See [Limits and non-goals](limits.md#non-goals).
- **A security-headers package.** Headers like a Content Security Policy are your application's policy, and a library default is one nobody revisits. Nite gives you the hooks (`NiteOptions.CspNonce`), and [`samples/Nite.Identity`](https://github.com/nite-net/nite/tree/main/samples/Nite.Identity) shows a complete, strict setup to copy.
