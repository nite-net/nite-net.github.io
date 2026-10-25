---
title: Tag helpers
description: Reference for the nite-head, island and nite-module tag helpers used in Razor Pages and MVC views.
---

# Tag helpers

<p class="lead">Three tag helpers put nite into Razor views. Import them once in <code>_ViewImports.cshtml</code>:</p>

```cshtml
@addTagHelper *, Nite
```

## &lt;nite-head&gt;

Writes what a page needs in `<head>` for islands and modules. Put it in your layout, inside `<head>`, before any `<island>` or `<nite-module>`:

```cshtml
<head>
    <meta charset="utf-8" />
    <nite-head />
</head>
```

| Mode | Output |
|---|---|
| Development | The import map for dependencies, the Fast Refresh runtime (when enabled), the dev client and the island loader |
| Production | The island loader with `modulepreload` hints for its chunks (only if the project has islands) |
| Both | The values of `NiteOptions.ClientConfig`, when it is set, for `nite:config` ([details](../guides/environment.md#values-from-the-running-server)) |

It takes no attributes. Without it, islands do not mount.

## &lt;island&gt;

Renders a component from the islands folder.

```cshtml
<island name="TodoList"
        props='new { title = "Today", items = Model.Todos }'
        client="visible">
    <p>Loading…</p>
</island>
```

| Attribute | Type | Default | Meaning |
|---|---|---|---|
| `name` | `string` | (required) | The island's path under the islands folder, without extension: `Counter`, `admin/UserTable`. |
| `props` | `object` | none | Props for the component, serialized as camelCase JSON. |
| `client` | `string` | `load` | When to load: `load`, `idle`, `visible` or `media`. |
| `media` | `string` | `all` | The media query for `client="media"`. |
| `export` | `string` | `default` | The export to render, when it is not the default export. |
| `tag` | `string` | `div` | The wrapper element's tag name. |

The content between the tags is rendered on the server and shown until the island mounts.

**Output**, for `<island name="Counter" props="new { start = 5 }" client="idle" />` in development:

```html
<div data-island="/_nite/src/islands/Counter.tsx" data-name="Counter"
     data-props="{&quot;start&quot;:5}" data-client="idle"></div>
```

In production, `data-island` points at the hashed bundle, and a `<link rel="stylesheet">` for the island's CSS is written right before the element (once per page, however many islands share it).

**Errors.** An unknown `name` throws when the view renders, listing the islands that exist (development) or saying the island is not in the build (production).

## &lt;nite-module&gt;

Loads a module that is not an island, such as page-specific behavior or a stylesheet entry.

```cshtml
<nite-module src="pages/checkout.ts" />
```

| Attribute | Type | Meaning |
|---|---|---|
| `src` | `string` | The module's path relative to the client root. The extension may be left off. |

Writes a `<script type="module">`, plus in production `<link rel="stylesheet">` for its CSS and `modulepreload` hints for its chunks. List the module in [`entries`](nite-json.md#entries) so production builds include it; development logs a warning when you forget.

## Data attributes

The island loader reads these from any element, so you can also write islands by hand (from a JavaScript template, say):

| Attribute | Meaning |
|---|---|
| `data-island` | The module URL to import. |
| `data-name` | A name for error messages. |
| `data-props` | Props as JSON. |
| `data-client` | `load`, `idle`, `visible` or `media`. |
| `data-media` | The media query for `media`. |
| `data-export` | The export to render. |

See [Browser runtime](browser-runtime.md#the-island-loader).
