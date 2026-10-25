---
title: Dev server URLs
description: The URLs the development server answers under /_nite, and what each one returns.
---

# Dev server URLs

<p class="lead">In development, <code>UseNite()</code> answers every request under <code>/_nite</code>. You rarely need these URLs directly, but they help when reading the network tab.</p>

All URLs are relative to the app's path base.

| URL | Returns |
|---|---|
| `/_nite/src/<path>` | A file from the client root. Modules (`.ts`, `.tsx`, `.jsx`, `.js`, `.mts`, `.mjs`) are compiled to JavaScript; stylesheets are built to CSS; anything else is sent as is. |
| `/_nite/src/<path>?import` | The same file as a JavaScript module: a stylesheet that injects itself (with the class map for CSS modules), JSON as its default export, or an asset's URL. |
| `/_nite/src/<path>?t=<timestamp>` | A module after a hot update; the timestamp makes the browser fetch the new version. |
| `/_nite/deps/<name>.js?v=<hash>` | A pre-bundled dependency (from the import map). Cached by the browser for a year: the hash changes when the dependencies do. |
| `/_nite/deps/chunk-<hash>.js` | Code shared between pre-bundled dependencies. |
| `/_nite/npm/<package>/<file>` | A file from `node_modules`, such as a font a package's CSS references. Package stylesheets (`@mantine/core/styles.css`) are built through the stylesheet pipeline. |
| `/_nite/client.js` | The dev client. |
| `/_nite/refresh.js` | The Fast Refresh runtime. |
| `/_nite/runtime/islands.js` | The island loader. |
| `/_nite/runtime/renderer.js` | The island renderer (React, or yours). |
| `/_nite/ws` | The hot-update WebSocket. |

Source files are served with `Cache-Control: no-cache` and an `ETag`, so a reload revalidates rather than re-downloads.

When compiling fails, a module request returns a small module that shows the error overlay and throws, so the overlay appears even on a fresh page load.

## Messages on the WebSocket

The server sends JSON messages; the dev client handles them.

| `type` | Fields | Client action |
|---|---|---|
| `update` | `updates: [{ path, url, timestamp }]`, `cleared: string[]` | Re-import the modules and run Fast Refresh; hide overlays for the cleared files. |
| `css` | `path`, `url` | Swap the stylesheet in place. |
| `reload` | | Reload the page (once the server answers). |
| `error` | `message`, `file`, `line`, `column`, `lineText` | Show the overlay. |
| `server-update` | `types: string[]` | Dispatch `nite:server-update`. |

These are internal and may change between versions.
