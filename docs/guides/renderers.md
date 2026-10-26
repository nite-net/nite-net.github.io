---
title: Custom renderers
description: Render islands with Preact, Solid, Lit or plain DOM code by replacing Nite's React renderer with a module of your own.
---

# Custom renderers

<p class="lead">Islands are mounted by a renderer: a module with one function. Nite ships one for React; point <code>"renderer"</code> at your own to use something else.</p>

## The contract

A renderer is a module in the client root that exports `mount`:

```ts
export function mount(
  element: HTMLElement,   // the island's wrapper element
  component: unknown,     // the island module's export (default, or the one named by export="…")
  props: object,          // the props from the tag helper, parsed from JSON
): void | (() => void) | Promise<void | (() => void)>;
```

Return a function to clean up when the island's element is removed from the page; the loader calls it then. The built-in React renderer is the whole reference implementation:

```js
import { createElement } from "react";
import { createRoot } from "react-dom/client";

export function mount(el, Component, props) {
  const root = createRoot(el);
  root.render(createElement(Component, props));
  return () => root.unmount();
}
```

Register yours in `nite.json`, relative to the client root:

```json
{ "renderer": "renderer.ts" }
```

## Preact

```bash
nite rm react react-dom @types/react @types/react-dom
nite add preact
```

```json
{
  "jsxImportSource": "preact",
  "renderer": "renderer.ts"
}
```

```ts
// Client/renderer.ts
import { h, render, type ComponentType } from "preact";

export function mount(el: HTMLElement, Component: ComponentType<any>, props: object) {
  el.replaceChildren();                       // drop the server-rendered fallback
  render(h(Component, props), el);
  return () => render(null, el);
}
```

Islands are now Preact components with the same `<island>` tag helper. Set `"jsxImportSource": "preact"` in your tsconfig too (`"jsx": "react-jsx"`, `"jsxImportSource": "preact"`) for the editor.

## Plain DOM

Islands do not have to be components at all. With this renderer, an island module's default export is a function that receives the element and props:

```ts
// Client/renderer.ts
type Island = (el: HTMLElement, props: object) => void | (() => void);

export function mount(el: HTMLElement, island: Island, props: object) {
  return island(el, props);
}
```

```ts
// Client/islands/Clock.ts
export default function Clock(el: HTMLElement, { zone }: { zone: string }) {
  const tick = () => (el.textContent = new Date().toLocaleTimeString("en", { timeZone: zone }));
  tick();
  const timer = setInterval(tick, 1000);
  return () => clearInterval(timer);
}
```

```cshtml
<island name="Clock" props='new { zone = "Europe/Oslo" }' tag="span" />
```

## Hot reload with other renderers

React Fast Refresh only applies when `jsxImportSource` is `react` and React is a dependency. With another renderer, edits to island modules reload the page; stylesheets still swap in place.
