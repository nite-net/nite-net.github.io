---
title: Tailwind CSS
description: Use Tailwind CSS 4 in a nite project, with class names found in React components and Razor views alike.
---

# Tailwind CSS

<p class="lead">nite runs Tailwind CSS 4 itself: Tailwind's own compiler from your <code>node_modules</code>, fed by a class scanner that covers the whole project, Razor views included. No <code>@tailwindcss/vite</code>, no <code>@tailwindcss/postcss</code>, no CLI process.</p>

## Set up

```bash
nite add -D tailwindcss
```

Import Tailwind in a stylesheet:

```css
/* Client/app.css */
@import "tailwindcss";
```

Load that stylesheet like any other. In a single-page app, import it from the entry module (`import "./app.css"`) or link it from `index.html`. In a Razor site, give the layout a small entry module that imports it:

```ts
// Client/site.ts
import "./app.css";
```

```json
// nite.json
{ "entries": ["site.ts"] }
```

```cshtml
@* Pages/Shared/_Layout.cshtml, in <head> after <nite-head /> *@
<nite-module src="site.ts" />
```

In production `<nite-module>` emits a plain `<link rel="stylesheet">` for the built CSS, so pages render styled from the first paint. Then use classes:

```tsx
export function Card({ title }: { title: string }) {
  return (
    <div className="rounded-xl bg-white p-6 shadow-lg dark:bg-slate-800">
      <h2 className="text-lg font-semibold text-slate-900 dark:text-white">{title}</h2>
    </div>
  );
}
```

```cshtml
<section class="mx-auto max-w-3xl px-4 py-12">
    <h1 class="text-4xl font-bold tracking-tight">@Model.Title</h1>
</section>
```

## Where classes are found

Tailwind generates CSS only for the classes your project uses. Its own scanner is native code, so nite has one written in C# that follows the same rules:

- **Automatic detection** scans the **whole project folder**, not just the client root. Classes used only in `.cshtml` and `.razor` files count.
- Skipped: `node_modules`, `bin`, `obj`, `.git`, `.nite`, `wwwroot/_nite`, folders listed in your `.gitignore` (plain folder names such as `dist/`), lockfiles, stylesheets, and binary files (images, fonts, archives).
- Explicit sources work as documented by Tailwind:

```css
@import "tailwindcss";

@source "../node_modules/@acme/ui/dist";   /* scan a package's compiled components too */
@source not "./legacy";                      /* skip a folder */
@source inline("underline line-through");    /* always generate these */
```

Like Tailwind's own scanner, nite over-collects on purpose: anything that might be a class goes to the compiler, which ignores what is not one. Build class names from complete strings, not concatenation, so they can be found:

```tsx
// Found: both full class names appear in the source.
const color = error ? "text-red-600" : "text-green-600";

// Not found: "text-red-600" never appears anywhere.
const color = `text-${error ? "red" : "green"}-600`;
```

## Theme, utilities and variants

Everything Tailwind 4 does in CSS works, because it is Tailwind's compiler doing it:

```css
@import "tailwindcss";

@theme {
  --color-brand: oklch(0.62 0.19 250);
  --font-display: "Inter", sans-serif;
}

@utility glass {
  backdrop-filter: blur(8px);
  background: rgb(255 255 255 / 0.4);
}

@custom-variant dark (&:where(.dark, .dark *));
```

## Plugins

```bash
nite add -D @tailwindcss/typography @tailwindcss/forms
```

```css
@import "tailwindcss";
@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms";
```

`@plugin` and `@config` (for a legacy JavaScript config) load from `node_modules` or relative paths. Plugins must be plain JavaScript.

## @apply in CSS modules

To use `@apply` in another stylesheet, reference the main one so Tailwind knows your theme without emitting it twice:

```css
/* Panel.module.css */
@reference "./app.css";

.panel {
  @apply rounded-xl p-6 shadow-lg bg-brand/10;
}
```

## Hot updates

- Saving a component (or a Razor view) that uses a class nothing used before rebuilds the Tailwind stylesheet and swaps it in, without touching component state.
- Saving `app.css` (say, a `@theme` change) updates it, and every stylesheet that `@reference`s it.
- Classes are never forgotten during a session, as with Tailwind's own dev servers, so removing a class does not reorder CSS while you work. The production build only contains classes in use.

The first Tailwind compile in a dev session takes a second or two (Tailwind's compiler runs in a JavaScript interpreter). nite starts it while the app starts, so pages are usually ready by the time you open them.

## Production

`nite build` scans the project, compiles once, and esbuild minifies the result and lowers modern CSS such as nesting for the target browsers. The output is about the same size as a Vite build of the same project (within a few percent in our tests).

## Coming from Vite

`nite init --from` takes care of this, but by hand:

- Remove `@tailwindcss/vite` (and `@tailwindcss/postcss`, if you used PostCSS); keep `tailwindcss` and any plugins.
- Your stylesheet and classes stay exactly as they are.

## Tailwind 3

Tailwind 3 is not supported: its JavaScript configuration and content globs were replaced by CSS-first configuration in version 4, which is what nite runs. Upgrade with Tailwind's tool (`npx @tailwindcss/upgrade`, run once with Node) and the [upgrade guide](https://tailwindcss.com/docs/upgrade-guide).
