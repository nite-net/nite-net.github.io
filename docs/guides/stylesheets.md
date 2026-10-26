---
title: Stylesheets
description: CSS, CSS modules, Sass, Less, Tailwind CSS and PostCSS in Nite, how the pipeline runs in development and production, and how hot updates follow your dependencies.
---

# Stylesheets

<p class="lead">Nite processes stylesheets the way Vite does: Sass or Less by extension, then Tailwind, then your PostCSS config, then esbuild for imports, CSS modules and assets. The same pipeline runs in development and in production builds, so the two agree.</p>

## Ways to load CSS

| How | Example | Development | Production |
|---|---|---|---|
| Import from code | `import "./app.css"` | A `<style>` tag, updated in place on save | Extracted into the entry's `.css` file |
| Import a CSS module | `import styles from "./Card.module.css"` | A `<style>` tag plus the class map | Extracted; class names minified |
| Import from a package | `import "@mantine/core/styles.css"` | Served from `node_modules` | Bundled |
| Link from `index.html` | `<link rel="stylesheet" href="./styles.css">` | Served as CSS | Replaced by the hashed file |
| `@import` in CSS | `@import "./theme.css";` | Inlined | Inlined |

Static stylesheets in `wwwroot` (`<link href="~/site.css">` in a Razor layout) are ordinary static files: Nite does not touch them.

## The pipeline

Every stylesheet in your client folder goes through these steps, in order:

1. **Sass** for `.scss` and `.sass`, or **Less** for `.less`.
2. **Tailwind CSS 4**, when the file uses it (`@import "tailwindcss"`, `@apply`, `@theme`, `@reference`, `@utility` and friends).
3. **PostCSS**, when the project has a config, with its plugins.
4. **esbuild**: inlines `@import` (packages too, through their `exports` and the `style` condition), scopes CSS modules, resolves `url()` assets, and in production minifies and lowers modern syntax (nesting, for one) for the target browsers.

Each step is optional and only runs when you use it. Plain CSS without a PostCSS config goes straight to esbuild.

## Installing the tools

Install the tools you use as dev dependencies, exactly as you would for Vite. Nite runs them; you never need Node:

```bash
nite add -D sass-embedded                  # or: sass
nite add -D less
nite add -D tailwindcss
nite add -D postcss autoprefixer           # plus any PostCSS plugins your config names
```

How each one runs:

| Tool | Runs as |
|---|---|
| **Sass** | The native Dart Sass compiler, from the `sass-embedded-<platform>` npm package matching your `sass` or `sass-embedded` version. Downloaded once into the user cache, like esbuild, and driven over Sass's embedded protocol: one compiler process serves every compile, in tens of milliseconds. |
| **Less**, **PostCSS** (and plugins), **Tailwind** | These are plain JavaScript. Nite bundles them from your `node_modules` with esbuild and runs them in [Jint](https://github.com/sebastienros/jint), a JavaScript interpreter written in C#, with a small stand-in for the Node built-ins they use (`fs`, `path`, `url`…). |

The interpreter is slower than Node. The first compile of a Tailwind stylesheet takes a second or two, which the dev server does at startup alongside dependency pre-bundling; after that, updates take tens of milliseconds. A production build pays it once.

> [!NOTE]
> Plugins must be plain JavaScript. A PostCSS or Tailwind plugin that loads a native addon (a `.node` file) cannot run in the interpreter.

## CSS modules

Files named `*.module.css` (or `.module.scss`, `.module.less`) are CSS modules: class names are scoped to the file and imported as an object.

```css
/* Card.module.css */
.card { padding: 1rem; border-radius: 8px; }
.title { composes: heading from "./type.module.css"; font-weight: 700; }
.is-active { outline: 2px solid; }
```

```tsx
import styles from "./Card.module.css";
// or individual names: import { card, title } from "./Card.module.css";

<div className={styles.card}>
  <h2 className={styles.title}>…</h2>
  <div className={styles["is-active"]} />
</div>
```

- `composes` works, within a file and from other modules.
- Named imports work for names that are valid JavaScript identifiers; use the default export for names like `is-active`.
- In development, class names look like `Card_3fa2c1_card` (readable, unique per file); in production they are minified.
- Editing a CSS module refreshes the components that use it, keeping their state.

## Sass

```scss
// Card.module.scss
@use "sass:math";
@use "./tokens" as t;

.card {
  padding: t.$space-3;
  border-radius: math.div(t.$radius, 2);

  &:hover { background: t.$surface-hover; }
}
```

- The client root and `node_modules` are load paths, so `@use "tokens"` finds `Client/_tokens.scss` and `@use "bootstrap/scss/functions"` finds the package.
- `pkg:` URLs work (`@use "pkg:bootstrap"`), resolved through `package.json`.
- Warnings from packages (`quietDeps`) are silenced; your own deprecation warnings appear in the log. Silence specific ones with `silenceDeprecations`.

Options use Vite's names, under `css.preprocessorOptions.scss` in `nite.json`:

```json
{
  "css": {
    "preprocessorOptions": {
      "scss": {
        "additionalData": "@use \"tokens\" as t;",
        "loadPaths": ["shared/styles"],
        "silenceDeprecations": ["import"]
      }
    }
  }
}
```

**`additionalData`** is prepended to every Sass file. It is how a project shares variables and mixins without importing them everywhere. Error line numbers account for it, so they still point at the right line in your file.

## Less

```less
@import "./variables";

.button {
  .rounded(6px);
  color: darken(@brand, 10%);
}
```

The importing file's folder, the client root and `node_modules` are search paths. Options go under `css.preprocessorOptions.less`:

```json
{
  "css": {
    "preprocessorOptions": {
      "less": {
        "additionalData": "@import \"variables\";",
        "paths": ["shared/less"],
        "javascriptEnabled": false,
        "globalVars": { "brand": "#1f74a0" },
        "modifyVars": { "radius": "4px" }
      }
    }
  }
}
```

## PostCSS

Nite finds your PostCSS config the way `postcss-load-config` does, in the client root first and then the project folder:

- `postcss.config.js`, `.cjs`, `.mjs`, `.ts`, `.cts`, `.mts`
- `.postcssrc`, `.postcssrc.json`, `.postcssrc.js`, `.postcssrc.cjs`, `.postcssrc.mjs`
- a `"postcss"` field in `package.json`

All the usual forms work: an object of plugin names and options, an array of plugins (`require("autoprefixer")`), and a function of `ctx` (where `ctx.env` is `"development"` or `"production"`).

```js
// postcss.config.cjs
module.exports = {
  plugins: {
    "postcss-preset-mantine": {},
    autoprefixer: {},
  },
};
```

Plugins load from your `node_modules`. `@tailwindcss/postcss` is skipped if listed, because Nite runs Tailwind itself, before PostCSS, the same order the plugin would have.

PostCSS runs on your stylesheets only, not on CSS shipped inside packages (that CSS is already built, and re-processing a large framework stylesheet in the interpreter is slow). Turn PostCSS off entirely with:

```json
{ "css": { "postCss": false } }
```

Editing the PostCSS config updates every stylesheet that used it, in place.

## Assets in CSS

`url()` references are resolved like imports:

```css
.hero { background: url("./images/hero.webp"); }        /* relative to this file */
@font-face { src: url("~@fontsource/inter/files/inter-latin-400-normal.woff2"); }  /* a package */
.logo { background: url("/logo.svg"); }                  /* site root: wwwroot, left as is */
```

- In development, relative and package URLs point straight at the files through the dev server.
- In production, they are copied to `wwwroot/_nite/assets/` with a content hash.
- Root-relative URLs (`/logo.svg`), absolute URLs and `data:` URLs are left exactly as written.

> [!NOTE]
> Relative `url()`s inside a Sass partial resolve against the file that uses the partial, not the partial itself (Vite rebases them). Put assets next to the entry stylesheet, or use root-relative or package paths in partials.

## Hot updates

Saving a stylesheet updates it in place, and so does saving anything a stylesheet was built from:

- a file it `@import`s, a Sass partial it `@use`s, a Less import;
- the PostCSS config;
- for Tailwind, any source file that gains a new class name (see [Tailwind CSS](tailwind.md)).

Errors show in the overlay with the file and line, and clear when you fix them.

## Specific setups

- [Tailwind CSS](tailwind.md)
- [Mantine](mantine.md)

## Not supported

- **Stylus.** Convert to CSS, Sass or Less.
- **CSS that a package's own JavaScript imports** (`import "./styles.css"` inside a library). Import the package's stylesheet from your own code instead, as Mantine documents.
- **`css.modules` options** such as `localsConvention` (camelCase class names).
