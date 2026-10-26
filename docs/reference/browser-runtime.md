---
title: Browser runtime
description: The client-side pieces Nite adds to pages, the events they raise and the contracts they expect.
---

# Browser runtime

<p class="lead">Nite adds a little JavaScript to your pages: the island loader in development and production, and the dev client and Fast Refresh runtime in development only.</p>

## Events

### nite:server-update

Dispatched on `window` in development when C# hot reload changes the running server.

```ts
addEventListener("nite:server-update", (event) => {
  const { types } = (event as CustomEvent<{ types: string[] }>).detail;
  console.log("server changed:", types);   // ["MyApp.TodoStore", ...]
  reload();
});
```

| `detail` property | Type | Meaning |
|---|---|---|
| `types` | `string[]` | Full names of the .NET types the update changed (may be empty). |

It never fires in production. A small helper that fits `useEffect`:

```ts
export function onServerUpdate(callback: () => void) {
  addEventListener("nite:server-update", callback);
  return () => removeEventListener("nite:server-update", callback);
}
```

## The dev client

`/_nite/client.js`, injected in development. It:

- connects to the dev server's WebSocket (`/_nite/ws`) and applies messages: hot updates, stylesheet swaps, reloads and errors;
- shows the error overlay (a `<nite-error-overlay>` element with its own shadow DOM) and clears it when the failing file is fixed;
- reconnects when the connection drops, and if the server restarted, reloads the page once the server answers again;
- dispatches `nite:server-update`.

Updates are logged to the console at the `debug` level (`[nite] hot updated src/App.tsx`).

## The Fast Refresh runtime

`/_nite/refresh.js`, injected before any React code runs when Fast Refresh is enabled. It sets up `react-refresh`'s runtime, which modules compiled by the dev server register their components with. Nothing in your code calls it.

## The island loader

Loaded by `<nite-head>` on pages with islands. It finds elements with a `data-island` attribute, loads each one's module when its strategy says so, and mounts the component through the renderer.

| `data-client` | Loads |
|---|---|
| `load` (or none) | Immediately |
| `idle` | On `requestIdleCallback` (2 s timeout), or after 200 ms where unsupported |
| `visible` | When the element is within 200 px of the viewport (`IntersectionObserver`) |
| `media` | When `matchMedia(data-media)` matches, now or later |

A `MutationObserver` on the document mounts islands added later and unmounts islands that are removed, calling the cleanup function the renderer returned. An island that fails to load logs `[nite] island <name> failed:` with the error and does not affect other islands.

## The renderer contract

```ts
export function mount(
  element: HTMLElement,
  component: unknown,
  props: object,
): void | (() => void) | Promise<void | (() => void)>;
```

The default renderer uses React's `createRoot`. See [Custom renderers](../guides/renderers.md).

## Global names

The runtime defines no globals in production. In development, `window.__NITE_REFRESH__` holds the Fast Refresh runtime when it is enabled, and `react-refresh` installs React's DevTools hook (`__REACT_DEVTOOLS_GLOBAL_HOOK__`) if no DevTools extension already has.
