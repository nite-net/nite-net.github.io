---
title: Hot reload and nite watch
description: How client and server changes reach the browser during development, what keeps state and what reloads, and how nite watch drives dotnet watch.
---

# Hot reload and nite watch

<p class="lead"><code>nite watch</code> runs <code>dotnet watch</code> for the C# side while NiteFx handles the client side. Most edits land in the page in a fraction of a second without losing state.</p>

## Start it

```bash
nite watch                      # single-page apps
nite watch --browser-refresh    # Razor Pages and MVC
```

Arguments after `--` go to `dotnet watch`:

```bash
nite watch -- --launch-profile https
nite watch -- --project src/Web/Web.csproj
```

You can also run the app any other way (`dotnet run`, Visual Studio, Rider). The client side still hot-updates; only C# changes need `dotnet watch` (or your IDE's hot reload) to apply.

## What happens when you save

| You edit | What happens | State |
|---|---|---|
| A React component | Fast Refresh updates it in place, in about 100 to 200 ms | Kept |
| A helper module (`format.ts`, `api.ts`) | The components that import it, directly or not, refresh | Kept |
| A component, adding or removing a hook | The component remounts | That component's state resets |
| A stylesheet, or a Sass partial, Less import or PostCSS config it uses | Swapped in place | Kept |
| A CSS module | The components using it refresh | Kept |
| A component using a new Tailwind class (or a Razor view) | The Tailwind stylesheet is rebuilt and swapped in | Kept |
| The entry module (`main.tsx`) or `index.html` | Page reloads | Lost |
| `nite.json` | Packages install, dependencies re-bundle, page reloads | Lost |
| `.env*` or `tsconfig*.json` | Modules recompile, page reloads | Lost |
| C# that hot reload can apply | Applied in the running app; the page gets `nite:server-update` | Kept |
| C# that needs a restart | The app restarts; the page waits and reloads (about 10 s) | Lost |

## Compile errors

A syntax or type-stripping error shows an overlay with the file, line and the offending code, without reloading the page. The page underneath keeps running. Fix the file and the overlay closes on its own; click outside the message to dismiss it early. Stylesheet errors (Sass, Less, PostCSS, Tailwind) show the same way, with line numbers in your source file.

Errors are only shown in development. A production build with an error fails with the same message on the command line.

## How Fast Refresh decides

NiteFx keeps a graph of which modules import which, limited to modules the browser has actually loaded. On a change, it walks up from the changed file:

- a module whose exports are **all React components** is a *boundary*: it is re-imported, and React swaps the new components in, keeping state;
- any other module passes the update to the modules that import it;
- if the walk reaches a module nothing imports (the page's entry), the page reloads.

Things that keep a module from being a boundary, so edits to it propagate further up or reload:

- exporting non-components next to components (`export const routes = [...]` in the same file as `export function App()`);
- class components and higher-order components other than `memo` and `forwardRef`.

Keep components in their own modules and Fast Refresh does the right thing.

> [!NOTE]
> Hook signatures cover a component's own hook calls. If a *custom* hook changes the order of hooks it calls internally, the next render may warn about hook order; save again or reload.

## C# changes

NiteFx registers a hot reload handler in your app. When `dotnet watch` applies a C# change, NiteFx sends the page a `server-update` message, and the dev client dispatches a `nite:server-update` event on `window`. Re-fetch on it:

```ts
export function onServerUpdate(callback: () => void) {
  addEventListener("nite:server-update", callback);
  return () => removeEventListener("nite:server-update", callback);
}

useEffect(() => {
  load();
  return onServerUpdate(load);   // edit the endpoint in C#, see the new data, keep your state
}, []);
```

`event.detail.types` lists the full names of the types that changed, if you want to be selective. The event never fires in production.

### Changes that need a restart

Some C# edits cannot be applied to a running app: a new endpoint in `Program.cs`'s top-level code (that code already ran), a new service registration, a changed method signature. `nite watch` sets `DOTNET_WATCH_RESTART_ON_RUDE_EDIT=1`, so `dotnet watch` restarts the app instead of asking. The dev client notices the socket drop, waits until the server answers again, and reloads.

> [!IMPORTANT]
> Without that variable, an interactive `dotnet watch` treats some of these edits as warnings (`ENC0118: Changing 'top-level code' might not have any effect until the application is restarted`), applies an update that changes nothing, and waits for Ctrl+R. The page then calls an endpoint that does not exist yet. If you run plain `dotnet watch`, set the variable yourself.

To keep `dotnet watch`'s prompt instead, run `nite watch --no-auto-restart`. A value you have already set for the variable is left alone.

## Why nite watch turns off dotnet watch's browser refresh

Plain `dotnet watch` injects a script into HTML responses that reloads the page after **every** C# change, even one hot reload applied. In a single-page app that throws away client state for an API-only change. `nite watch` sets `DOTNET_WATCH_SUPPRESS_BROWSER_REFRESH=1` (which only works from the environment, not from `launchSettings.json`), and NiteFx's own client takes over: it reloads after restarts by itself and leaves the page alone otherwise.

## Razor Pages

For Razor Pages and MVC, server-rendered markup changes do need a reload to show. Keep `dotnet watch`'s refresh:

```bash
nite watch --browser-refresh
```

`.cshtml` edits then reload the page through `dotnet watch`, while island components still update in place through Fast Refresh.

## Variables nite watch sets

| Variable | Value | Unless |
|---|---|---|
| `DOTNET_WATCH_SUPPRESS_BROWSER_REFRESH` | `1` | `--browser-refresh`, or you set it |
| `DOTNET_WATCH_RESTART_ON_RUDE_EDIT` | `1` | `--no-auto-restart`, or you set it |

`nite watch` prints the command and the variables it set when it starts.

## Troubleshooting

- **Edits do nothing.** Check that the file is under the client root and that the page actually loads it. Changes to files nothing on the page imports are ignored on purpose.
- **The page reloads on every component edit.** The module probably exports something besides components, or is imported by the entry module directly; see [How Fast Refresh decides](#how-fast-refresh-decides). Check also that `fastRefresh` is not `false` in `nite.json` and that React is a dependency.
- **Saving in a particular editor misses changes.** Editors that save through a temporary file and a rename are handled; if yours does something unusual, add the folder to your editor's "safe write" exclusions.

More in [Troubleshooting](../troubleshooting.md).
