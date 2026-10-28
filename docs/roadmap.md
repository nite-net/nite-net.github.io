---
title: Roadmap
description: Where NiteFx is going next, in the order we plan to ship it.
---

# Roadmap

<p class="lead">What we plan to build next, in order. These are plans, not promises: priorities change when you tell us what hurts. Open or vote on an <a href="https://github.com/nite-net/nite/issues">issue</a> to move something up.</p>

Released work is in the [changelog](changelog.md); what NiteFx deliberately does not do is in [Limits and non-goals](limits.md).

## 0.9: safer and faster production builds

Small changes that close gaps in [Limits](limits.md) and continue the security work in 0.8. They ship one at a time, as 0.9.x releases.

- **Immutable caching for hashed files.** *Shipped in 0.9.0.* Bundles, chunks and assets, which have content hashes in their names, are served as `immutable`, so repeat visits load them without a request.
- **Subresource integrity.** Production scripts and the import map carry `integrity` hashes, so a CDN or proxy that alters a bundle gets it refused by the browser. Pairs with the [Content Security Policy](reference/aspnet.md#content-security-policy) support in 0.8.
- **A minimum release age for packages.** A setting in `nite.json` (for example `"minimumReleaseAge": "3d"`) makes `nite add` and `nite update` pass over versions published more recently than that. Malicious package versions are usually found and removed within days, so waiting a few days avoids most of them.
- **`?raw` and `?url` imports**, and SVGs imported as React components, for code coming from Vite.
- **Hosting under a path base.** URLs inside production JavaScript and CSS (lazy chunks, `url()` assets) work when the app is served from a subfolder such as `/shop`, not only from the site root.

## 0.10: knowing and fixing vulnerable packages

- **`nite audit`.** Checks every package in `nite.lock.json` against the npm advisory database and reports known vulnerabilities. `nite build` can fail on them above a severity you choose, so CI catches them.
- **`overrides`.** Pin a dependency of a dependency to a patched version without waiting for every package above it to release one. These two ship together: a report you cannot act on is only half a feature.

## 1.0: one set of types from C# to TypeScript

- **A typed client for your endpoints.** NiteFx will generate a TypeScript client from the endpoints your app already has, whether they are minimal APIs, [FastEndpoints](https://fast-endpoints.com) or controllers, by reading the OpenAPI document the app produces:

  ```tsx
  import { api } from "nite:api";

  const user = await api.createUser({ name: "Benson" });
  // user is typed from the C# response; change the record and this stops compiling
  ```

  The dev server runs inside your app, so it regenerates the client on startup and on every C# hot reload, without a build step. Request/response classes in the style of FastEndpoints (a request type, a response type and a validator per endpoint) map one-to-one onto the client.
- **Validation and errors in the client.** The constraints in the OpenAPI schemas (required fields, lengths, patterns, ranges) become [Zod](https://zod.dev) schemas, so forms can check input before sending it while the server stays the authority. Errors arrive as typed [ProblemDetails](https://www.rfc-editor.org/rfc/rfc9457), not thrown strings.
- **Client config** gets the same treatment when its callback returns a named type.
- **A stable API.** From 1.0, NiteFx follows semantic versioning for its whole public surface, not only `AddNite`, `UseNite`, `MapNiteSpa`, the tag helpers and `nite.json`.

## Not planned

These come up, and the answer is no for now, for these reasons:

- **Platform-specific optional dependencies.** NiteFx already fetches the right esbuild and Dart Sass binaries for each platform. Most other packages that need this are native Node addons, which cannot run in a browser. If a browser package you need depends on it, open an issue with its name.
- **Built-in type checking.** It needs Node, or a JavaScript interpreter that would make every save slow. Run `tsc --noEmit` in your editor and CI; the generated API types in 1.0 add the checking NiteFx can do best.
- **Server-side rendering, and Vue, Svelte or other Vite plugins.** See [Limits and non-goals](limits.md#non-goals).
- **An endpoint framework of its own.** Minimal APIs and FastEndpoints already give each endpoint typed requests and responses, validation, filters and access to the user and services. NiteFx's part is the client: the typed bridge into React. The same goes for calling C# from React over a SignalR connection: request/response calls stay on HTTP, where authorization, rate limiting, CSRF protection and caching already apply. SignalR is for streams and server push.
- **A security-headers package.** Headers like a Content Security Policy are your application's policy, and a library default is one nobody revisits. NiteFx gives you the hooks (`NiteOptions.CspNonce`), and [`samples/Nite.Identity`](https://github.com/nite-net/nite/tree/main/samples/Nite.Identity) shows a complete, strict setup to copy.
