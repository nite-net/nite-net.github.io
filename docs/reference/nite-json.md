---
title: nite.json
description: Every setting in nite.json, with its type, default and effect.
---

# nite.json

<p class="lead"><code>nite.json</code> sits next to the project file and describes the client: where it lives, its packages, and how it is compiled. The dev server, the CLI and production builds all read it, so they always agree.</p>

```jsonc
{
  "clientRoot": "Client",
  "islands": "islands",
  "entries": [],
  "renderer": "react",
  "jsxImportSource": "react",
  "fastRefresh": true,
  "envPrefix": ["NITE_PUBLIC_"],
  "jsxInJs": false,
  "target": "es2022",
  "registry": null,
  "css": {
    "postCss": true,
    "preprocessorOptions": {
      "scss": { "additionalData": null, "loadPaths": [], "silenceDeprecations": [] },
      "less": { "additionalData": null, "paths": [], "javascriptEnabled": false, "globalVars": {}, "modifyVars": {} }
    }
  },
  "dependencies": {},
  "devDependencies": {}
}
```

Every setting is optional; the values above are the defaults. The file may contain `//` and `/* */` comments and trailing commas, and property names are case-insensitive. `nite add` and `nite rm` edit it in place and keep your comments.

While the app runs in development, saving `nite.json` installs packages, re-bundles dependencies and reloads the page. A changed `clientRoot` needs a restart.

## Project structure

### clientRoot

`string`, default `"Client"`

The folder, relative to the project, that holds client source. Everything nite compiles lives under it, and in development its files are served under `/_nite/src/`.

### islands

`string`, default `"islands"`

The folder, relative to `clientRoot`, whose modules can be used as `<island name="...">`. Subfolders become part of the name: `islands/admin/UserTable.tsx` is `admin/UserTable`. See [Islands](../guides/islands.md).

### entries

`string[]`, default `[]`

Extra entry points, relative to `clientRoot`, for the production build:

- HTML pages other than `index.html` (which is an entry automatically when it exists), for example `"admin.html"`;
- modules loaded with `<nite-module src="...">`, for example `"pages/checkout.ts"`.

Islands are entries automatically. In development nothing needs to be listed, but nite warns when a `<nite-module>` points at a module that is missing here, since the production build would not include it.

## Compilation

### jsxImportSource

`string`, default `"react"`

The package that provides the automatic JSX runtime (`<source>/jsx-runtime`, and `<source>/jsx-dev-runtime` in development). Use `"preact"` for Preact, or any library that ships those modules.

### fastRefresh

`boolean`, default `true`

React Fast Refresh in development. It applies when `jsxImportSource` is `"react"` and `react` is in `dependencies`; nite then installs `react-refresh` as an implicit dev dependency. Set to `false` to reload the page on component edits instead.

### jsxInJs

`boolean`, default `false`

Allow JSX in `.js` files, as Create React App does. Off by default, as in Vite. Imported Create React App projects get `true`.

### target

`string`, default `"es2022"`

The esbuild target for production output, a comma-separated list of language versions and browsers (`"es2020"`, `"es2022,safari15"`, `"chrome110,firefox110,safari16"`). When it names only language versions, nite adds Vite's default browser list (`chrome107, edge107, firefox104, safari16`), so CSS gets lowered for those browsers too. Development always compiles for modern browsers.

### renderer

`string`, default `"react"`

The island renderer: `"react"`, or the path (relative to `clientRoot`) of a module that exports `mount(element, component, props)`. See [Custom renderers](../guides/renderers.md).

## Environment

### envPrefix

`string[]`, default `["NITE_PUBLIC_"]`

Environment variables whose names start with one of these prefixes are exposed to client code as `import.meta.env.NAME` and `process.env.NAME`. Others never reach the browser. See [Environment variables](../guides/environment.md).

## Stylesheets

### css.postCss

`boolean`, default `true`

Run the project's PostCSS config (when one exists) on stylesheets. Package stylesheets in `node_modules` are never run through it.

### css.preprocessorOptions.scss

Options for Sass (`.scss` and `.sass`), named as in Vite.

| Key | Type | Default | Meaning |
|---|---|---|---|
| `additionalData` | `string` | none | Prepended to every Sass file, typically `@use` rules for shared variables and mixins. The client root is a load path, so files there can be used by name. |
| `loadPaths` | `string[]` | `[]` | Extra folders (relative to the project) to resolve `@use` and `@import` from. The client root and `node_modules` are always load paths. |
| `silenceDeprecations` | `string[]` | `[]` | Sass deprecation IDs to keep quiet, such as `"import"` or `"global-builtin"`. |

### css.preprocessorOptions.less

Options for Less.

| Key | Type | Default | Meaning |
|---|---|---|---|
| `additionalData` | `string` | none | Prepended to every Less file. |
| `paths` | `string[]` | `[]` | Extra folders (relative to the project) for `@import`. The importing file's folder, the client root and `node_modules` are always searched. |
| `javascriptEnabled` | `boolean` | `false` | Allow inline JavaScript in Less files. |
| `globalVars` | `object` | `{}` | Variables defined before every file, overridable by it. |
| `modifyVars` | `object` | `{}` | Variables defined after every file, overriding it. |

See [Stylesheets](../guides/stylesheets.md).

## Packages

### dependencies

`object` of package name → version range, default `{}`

Packages your client code imports. Manage with `nite add` and `nite rm`. See [Packages](../guides/packages.md).

### devDependencies

`object` of package name → version range, default `{}`

Packages installed but never bundled: type packages (`@types/react`), `typescript`, and stylesheet tools (`sass-embedded`, `less`, `tailwindcss`, PostCSS and its plugins).

### registry

`string`, default none

The registry for this project's unscoped packages, for everyone who builds it. It overrides `.npmrc` and the user config; `NITE_REGISTRY` overrides it. Usually `.npmrc` is the better place. See [Private registries](../guides/private-registries.md).

## Examples

A single-page app with React Router and Tailwind:

```json
{
  "clientRoot": "Client",
  "dependencies": {
    "react": "^19.3.1",
    "react-dom": "^19.3.1",
    "react-router": "^8.5.0"
  },
  "devDependencies": {
    "@types/react": "^19.2.0",
    "@types/react-dom": "^19.2.0",
    "tailwindcss": "^4.3.3"
  }
}
```

A Razor site with islands, a page module, and an imported Vite project's environment prefix:

```jsonc
{
  "clientRoot": "Client",
  "islands": "islands",
  "entries": ["site.ts"],              // <nite-module src="site.ts" /> in _Layout.cshtml
  "envPrefix": ["VITE_"],
  "dependencies": { "react": "^19.3.1", "react-dom": "^19.3.1" }
}
```
