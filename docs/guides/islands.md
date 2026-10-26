---
title: Islands in Razor Pages
description: Put interactive React components into server-rendered Razor Pages and MVC views with the island tag helper, with control over when each one loads.
---

# Islands in Razor Pages

<p class="lead">Keep your pages server-rendered with Razor, and make the parts that need it interactive with React. Each island is a component, loaded only when it is needed, with props straight from your page model.</p>

```cshtml
<island name="Counter" props="new { start = 5 }" />
```

## Set up

Starting fresh, `nite init my-site --template islands` creates all of this. To add islands to an existing Razor Pages or MVC app:

**1. Register NiteFx** in `Program.cs`:

```csharp
builder.Services.AddRazorPages();
builder.Services.AddNite();

var app = builder.Build();
app.UseNite();          // before routing and static assets
app.UseRouting();
app.MapStaticAssets();
app.MapRazorPages().WithStaticAssets();
```

**2. Import the tag helpers** in `Pages/_ViewImports.cshtml` (or `Views/_ViewImports.cshtml`):

```cshtml
@addTagHelper *, Nite
```

**3. Add `<nite-head />` to your layout's `<head>`.** It emits the island loader, and in development the import map, the dev client and the Fast Refresh runtime:

```cshtml
<head>
    <meta charset="utf-8" />
    <title>@ViewData["Title"]</title>
    <link rel="stylesheet" href="~/site.css" asp-append-version="true" />
    <nite-head />
</head>
```

**4. Add a `nite.json`** next to the project file, with React:

```json
{
  "clientRoot": "Client",
  "islands": "islands",
  "dependencies": { "react": "^19.3.1", "react-dom": "^19.3.1" },
  "devDependencies": { "@types/react": "^19.2.0", "@types/react-dom": "^19.2.0" }
}
```

Then `nite install`.

## Write an island

Any module in `Client/islands/` is an island. Its default export is the component:

```tsx
// Client/islands/Counter.tsx
import { useState } from "react";

export default function Counter({ start }: { start: number }) {
  const [count, setCount] = useState(start);
  return <button onClick={() => setCount(count + 1)}>Clicked {count} times</button>;
}
```

Place it in any page or view:

```cshtml
<island name="Counter" props="new { start = 5 }" />
```

Islands are found by path, without the extension: `Client/islands/admin/UserTable.tsx` is `<island name="admin/UserTable" />`. Code that islands share (hooks, API clients, components that are never islands themselves) belongs outside the islands folder, in `Client/lib/` or wherever you like.

## Props

`props` takes any object. It is serialized to JSON with **camelCase** names (the same convention as ASP.NET Core's JSON APIs) and passed to the component:

```cshtml
<island name="TodoList" props='new { title = "Today", items = Model.Todos }' />
```

```tsx
type Props = { title: string; items: { id: number; title: string; done: boolean }[] };

export default function TodoList({ title, items }: Props) { /* ... */ }
```

Props are plain data: strings, numbers, booleans, arrays, objects, `null`. They are embedded in the page as a `data-props` attribute, so do not pass anything you would not put in the HTML.

> [!TIP]
> Razor attribute values use C# syntax inside `props="..."`. When the object contains string literals, wrap the attribute in single quotes: `props='new { title = "Today" }'`.

## When islands load

By default an island loads as soon as the page does. The `client` attribute defers it:

| `client=` | Loads | Good for |
|---|---|---|
| `load` (default) | Immediately | Above-the-fold interactivity |
| `idle` | When the browser is idle (`requestIdleCallback`, at most 2 seconds later) | Secondary widgets |
| `visible` | When the element comes within 200 px of the viewport | Charts, comments, anything below the fold |
| `media` | When the media query in `media` matches | Components that only exist at some screen sizes |

```cshtml
<island name="Chart" props="Model.Series" client="visible" />
<island name="Sidebar" client="media" media="(min-width: 900px)" />
```

Nothing is downloaded for an island until its strategy fires: not the module, not its dependencies.

## Fallback content

Content inside the tag is rendered by the server and shown until the island mounts, then replaced:

```cshtml
<island name="TodoList" props='new { items = Model.Todos }' client="visible">
    <ul>
        @foreach (var todo in Model.Todos)
        {
            <li>@todo.Title</li>
        }
    </ul>
</island>
```

Use it as a loading state, or as real content for crawlers and users without JavaScript. Islands render on the client only; NiteFx does not server-render React.

## Other options

| Attribute | Default | Meaning |
|---|---|---|
| `name` | (required) | The module's path under the islands folder, without extension. |
| `props` | none | Props, serialized as camelCase JSON. |
| `client` | `load` | When to load; see above. |
| `media` | `all` | The media query for `client="media"`. |
| `export` | `default` | A named export to render instead of the default one: `export="UserTable"`. |
| `tag` | `div` | The wrapper element: `tag="section"`, `tag="span"`. |

The full reference is on [Tag helpers](../reference/tag-helpers.md).

## Islands and dynamic HTML

The island loader watches the document with a `MutationObserver`. Islands added later, by htmx, Turbo, Blazor's enhanced navigation or your own `innerHTML`, mount automatically, and islands that are removed are unmounted (React roots are cleaned up). There is nothing to call.

The observer watches the document, not shadow roots: an island rendered inside a web component's shadow DOM is not found.

## Sharing state between islands

Each island is its own React root, so React context does not cross between them. Share state through a module both import (a small store, a signal, an event bus), or through the server:

```ts
// Client/lib/cart.ts: one module instance per page, shared by every island that imports it
import { useSyncExternalStore } from "react";

let count = 0;
const listeners = new Set<() => void>();

export const cart = {
  add() { count++; listeners.forEach((l) => l()); },
  subscribe(l: () => void) { listeners.add(l); return () => listeners.delete(l); },
};

export const useCartCount = () => useSyncExternalStore(cart.subscribe, () => count);
```

## Styles

Islands can import CSS, CSS modules, Sass and so on, exactly like any other module. In production, the tag helper emits a `<link rel="stylesheet">` for each island's CSS right before the island (once per page), so it never flashes unstyled. In development each import injects its own `<style>` element.

## Modules that are not islands

For a script that should run on a page without being a component (analytics, a page-specific enhancement), use `<nite-module>`:

```cshtml
<nite-module src="pages/checkout.ts" />
```

`src` is relative to the client root. List the module in `entries` in `nite.json` so the production build includes it; in development NiteFx logs a warning when you forget.

```json
{ "entries": ["pages/checkout.ts"] }
```

## Hot reload

Under `nite watch --browser-refresh`, island components update in place with Fast Refresh like any other React component, and Razor changes reload the page through `dotnet watch`. See [Hot reload](hot-reload.md#razor-pages).

## Not using React

Islands are rendered by a small renderer module. Preact, Solid or plain DOM code work with a custom one; see [Custom renderers](renderers.md).
