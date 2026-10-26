---
title: Mantine
description: Use the Mantine React component library in a Nite project, with postcss-preset-mantine, CSS modules and optional Sass, following Mantine's Vite guide.
---

# Mantine

<p class="lead"><a href="https://mantine.dev">Mantine</a> works in Nite the way its Vite guide sets it up: its stylesheet imported from code, <code>postcss-preset-mantine</code> for your own CSS modules, and optionally Sass with Mantine's helpers.</p>

## Install

```bash
nite add @mantine/core @mantine/hooks
nite add -D postcss postcss-preset-mantine postcss-simple-vars
```

Add other Mantine packages the same way (`@mantine/dates`, `@mantine/notifications`, …), each with its own stylesheet import.

## PostCSS

Create `Client/postcss.config.cjs`, exactly as in Mantine's guide:

```js
module.exports = {
  plugins: {
    "postcss-preset-mantine": {},
    "postcss-simple-vars": {
      variables: {
        "mantine-breakpoint-xs": "36em",
        "mantine-breakpoint-sm": "48em",
        "mantine-breakpoint-md": "62em",
        "mantine-breakpoint-lg": "75em",
        "mantine-breakpoint-xl": "88em",
      },
    },
  },
};
```

## The provider and styles

Import Mantine's styles once, before your own, and wrap the app in `MantineProvider`:

```tsx
// Client/main.tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "@mantine/core/styles.css";
import { MantineProvider } from "@mantine/core";
import { App } from "./App";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <MantineProvider>
      <App />
    </MantineProvider>
  </StrictMode>,
);
```

## Your own styles

CSS modules get everything `postcss-preset-mantine` provides: `rem()` and `em()`, `light-dark()`, `alpha()`, and the `dark`, `light`, `hover`, `rtl` and breakpoint mixins.

```css
/* Client/Card.module.css */
.card {
  padding: rem(20px);
  border: 1px solid light-dark(var(--mantine-color-gray-3), var(--mantine-color-dark-4));
  background: alpha(var(--mantine-color-blue-6), 0.1);

  @mixin hover {
    background: alpha(var(--mantine-color-blue-6), 0.2);
  }

  @media (max-width: $mantine-breakpoint-sm) {
    padding: rem(8px);
  }
}
```

```tsx
import { Button, Text } from "@mantine/core";
import classes from "./Card.module.css";

export function Card() {
  return (
    <div className={classes.card}>
      <Text>Hello from Mantine</Text>
      <Button>Click me</Button>
    </div>
  );
}
```

## With Sass

Mantine's Sass guide shares a `_mantine.scss` file of helpers through `additionalData`. Install Sass and put the file in the client root:

```bash
nite add -D sass-embedded
```

```scss
// Client/_mantine.scss
@use "sass:math";

$mantine-breakpoint-md: "62em";

@function rem($value) {
  @return #{math.div(math.div($value, $value * 0 + 1), 16)}rem;
}

@mixin dark {
  [data-mantine-color-scheme="dark"] & {
    @content;
  }
}

@mixin smaller-than($breakpoint) {
  @media (max-width: $breakpoint) {
    @content;
  }
}
```

Then share it with every Sass file. Where Vite's config builds an absolute path, Nite only needs the name, because the client root is a Sass load path:

```json
{
  "css": {
    "preprocessorOptions": {
      "scss": { "additionalData": "@use \"mantine\" as mantine;" }
    }
  }
}
```

```scss
// Client/Hero.module.scss
.title {
  font-size: mantine.rem(48px);

  @include mantine.dark {
    color: white;
  }

  @include mantine.smaller-than(mantine.$mantine-breakpoint-md) {
    font-size: mantine.rem(24px);
  }
}
```

PostCSS still runs after Sass, so `light-dark()` and the other preset functions work in `.scss` files too.

## Importing a Mantine Vite app

`nite init my-app --from ../my-mantine-app` carries the whole setup over: the dependencies, `postcss.config.cjs`, and the `additionalData` from `vite.config` (it understands the `path.join(process.cwd(), 'src/_mantine')` form in Mantine's guide). See [Importing a project](importing.md).

## Notes

- Mantine's own stylesheets (`@mantine/core/styles.css`) are already built, so Nite does not run PostCSS over them. That keeps startup fast; the result is identical.
- `@mantine/core/styles.layer.css` (the cascade-layer variant) works the same way.
- Hot updates work for all of it: CSS modules refresh their components with state kept, and editing `_mantine.scss` or `postcss.config.cjs` updates every stylesheet that used it.
