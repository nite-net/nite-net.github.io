---
title: Single-page apps
description: Serve a React (or plain TypeScript) single-page app from ASP.NET Core with index.html as the entry, client-side routing and an API on the same origin.
---

# Single-page apps

<p class="lead">A single-page app is <code>Client/index.html</code>, the modules it loads, and <code>app.MapNiteSpa()</code> to serve it. Your API lives in the same app, on the same origin.</p>

## The setup

```csharp
using Nite;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddNite();

var app = builder.Build();
app.UseNite();                       // dev server under /_nite; does nothing in production

app.MapGet("/api/todos", ...);       // your API

app.MapStaticAssets();               // wwwroot, including the production build
app.MapNiteSpa();                    // index.html for "/" and client-side routes
app.Run();
```

Order matters in one place: `UseNite()` must come before anything that would answer `/_nite/...` requests. Calling it right after `builder.Build()` is always safe.

## index.html is the entry

As in Vite, the HTML page is a real entry point, not a template that a bundler injects into:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>My app</title>
    <link rel="icon" href="/favicon.ico" />
    <link rel="stylesheet" href="./styles.css" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="./main.tsx"></script>
  </body>
</html>
```

nite looks at two kinds of tags and leaves everything else alone:

| Tag | Development | Production |
|---|---|---|
| `<script type="module" src="...">` pointing into the client root | Served from `/_nite/src/...`, compiled on request | Replaced by the hashed bundle, its CSS `<link>`s and `modulepreload` hints for its chunks |
| `<link rel="stylesheet" href="...">` pointing into the client root | Served through the [stylesheet pipeline](stylesheets.md) | Replaced by the hashed, minified CSS |

URLs can be relative to the page (`./main.tsx`) or root-relative (`/src/main.tsx`, resolved against the client root, as Vite does). External URLs (`https://...`, `//cdn...`, `data:`), and local URLs that do not point to a file in the client root, are left exactly as written. That is how you reference static files in `wwwroot`: `<link rel="icon" href="/favicon.ico" />` keeps pointing at `wwwroot/favicon.ico`.

In development the page gets nite's head injected first: the import map for dependencies, the dev client, and the Fast Refresh runtime. In production it gets nothing extra.

> [!NOTE]
> `index.html` is read from source on every request in development, so edits show up on the next load. Saving it reloads open pages.

## Client-side routing

`MapNiteSpa()` is a fallback endpoint. It answers `GET` and `HEAD` requests that no other endpoint or static file handled, for any path without a file extension. Deep links such as `/todos/3` therefore load the app, and the client router takes over.

Real endpoints always win, so you never have to order routes around it. Three cases return 404 instead of the page:

- paths under `/api` (change with `apiPrefix`, or pass `null` to disable): a mistyped API call gets a 404 rather than a page of HTML that fails to parse as JSON;
- methods other than `GET` and `HEAD`;
- paths with a file extension (`/missing.png`).

```csharp
app.MapNiteSpa(apiPrefix: "/backend");   // the API lives under /backend instead
app.MapNiteSpa(apiPrefix: null);         // every extension-less GET falls back
```

The page itself is sent with `Cache-Control: no-cache`, because it is what points at the current hashed bundles.

## Calling your API

The app and the API share an origin, so `fetch("/api/todos")` just works: no CORS policy, no dev proxy, no base URL per environment. Cookies and ASP.NET Core authentication work as they do for any same-origin request.

```ts
export async function getTodos(): Promise<Todo[]> {
  const response = await fetch("/api/todos");
  if (!response.ok) throw new Error(`GET /api/todos failed: ${response.status}`);
  return response.json();
}
```

Re-fetch when C# changes during development with the [`nite:server-update`](hot-reload.md#c-changes) event.

## More than one page

An `index.html` in the client root is picked up automatically. Other HTML pages are entries too when you list them in `nite.json`:

```json
{
  "entries": ["login/index.html"]
}
```

Give each its own path with `MapNiteSpa`'s `path`: that page answers the path and everything under it, with its own client-side routes, and the more specific path wins over the catch-all.

```csharp
app.MapNiteSpa("login/index.html", path: "/login").AllowAnonymous(); // /login, /login/forgot, ...
app.MapNiteSpa();                                                    // everything else: index.html
```

Each is an ordinary endpoint, so authorization conventions apply per app. Both get [client config](environment.md#values-from-the-running-server) and the same caching headers. The apps share chunks in production builds, so a second app costs only its own code. [`samples/Nite.Identity`](https://github.com/nite-net/nite/tree/main/samples/Nite.Identity) has a public login app and a protected main app.

For full control, <xref:Nite.Assets.INiteAssets> returns any page as it should be served in the current mode: `await assets.GetHtmlAsync("admin.html", context)`.

## Hosting under a path base

When the app runs under a path base (`app.UsePathBase("/shop")`, or a reverse proxy that sets one), `MapNiteSpa` adds the path base to the URLs in the page it serves, and the dev server works under it. Production URLs inside JavaScript and CSS (dynamic imports, `url()` assets) are root-relative to `/_nite/`; see [Limits](../limits.md).

## Using another framework

Nothing about the SPA setup is React-specific. `main.ts` can render with plain DOM APIs, Preact (`"jsxImportSource": "preact"`), Lit or anything else that ships ES modules. React Fast Refresh only applies to React; other code reloads the page when it changes.

## See also

- [Tutorial: a full-stack app](../tutorial.md)
- [ASP.NET Core integration](../reference/aspnet.md) for every option of `AddNite`, `UseNite` and `MapNiteSpa`
- [Production builds and deployment](deployment.md)
