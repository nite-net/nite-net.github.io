---
title: ASP.NET Core integration
description: AddNite, NiteOptions, UseNite, MapNiteSpa and INiteAssets, the parts of nite your Program.cs uses.
---

# ASP.NET Core integration

<p class="lead">Three extension methods connect nite to an app: <code>AddNite</code> registers services, <code>UseNite</code> mounts the dev server, and <code>MapNiteSpa</code> serves an HTML entry. All are in the <code>Nite</code> namespace.</p>

```csharp
using Nite;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddNite();

var app = builder.Build();
app.UseNite();
// ... endpoints, Razor Pages ...
app.MapStaticAssets();
app.MapNiteSpa();
app.Run();
```

## AddNite

```csharp
IServiceCollection AddNite(this IServiceCollection services, Action<NiteOptions>? configure = null)
```

Registers the dev server, the production asset reader and <xref:Nite.Assets.INiteAssets>, which resolves to whichever applies in the current mode. Required by `UseNite`, `MapNiteSpa` and the tag helpers. Calling it more than once is harmless.

### NiteOptions

| Property | Type | Default | Meaning |
|---|---|---|---|
| `Mode` | <xref:Nite.NiteMode> | `Auto` | `Auto`: the dev server in the Development environment, the build output everywhere else. `Development` or `Production` force one. |
| `ProjectDirectory` | `string?` | the content root | The folder holding `nite.json`, when it is not the content root. |
| `ClientConfig` | `Func<HttpContext, object?>?` | none | Values for client code, worked out per request and read with `import { config } from "nite:config"`. See [Values from the running server](../guides/environment.md#values-from-the-running-server). |
| `ClientConfigAsync` | `Func<HttpContext, Task<object?>>?` | none | The same, for an async callback. Set one or the other. |

```csharp
builder.Services.AddNite(options =>
{
    options.Mode = NiteMode.Production;              // serve the build output while developing
    options.ProjectDirectory = Path.Combine(builder.Environment.ContentRootPath, "frontend");
});
```

## UseNite

```csharp
IApplicationBuilder UseNite(this IApplicationBuilder app)
```

In development, starts the dev server (package install, pre-bundling, file watching) in the background and mounts it at `/_nite`: compiled modules, dependencies, the browser runtime and the hot-update WebSocket. In production it does nothing, because the build output is ordinary static files.

Call it early: before `UseRouting`, `MapStaticAssets` and anything else that could answer `/_nite/...`. It enables WebSockets for its own branch only. The URLs it serves are listed in [Dev server URLs](dev-server-urls.md).

## MapNiteSpa

```csharp
IEndpointConventionBuilder MapNiteSpa(this IEndpointRouteBuilder endpoints, string page = "index.html", string? apiPrefix = "/api")
```

Serves an HTML entry from the client root for `/` and, as a fallback, for any other `GET` or `HEAD` request to a path without a file extension that no other endpoint handled. Client-side routes survive a refresh, and real endpoints always win.

| Parameter | Meaning |
|---|---|
| `page` | The HTML entry, relative to the client root. |
| `apiPrefix` | Requests under this path never fall back: a mistyped API call gets a 404 instead of a page of HTML. `null` disables the check. |

In development the page is read from source on every request, with nite's head (import map, dev client, Fast Refresh runtime) injected. In production it is the built copy from `wwwroot/_nite`, with the request's path base added to its URLs. When `NiteOptions.ClientConfig` is set, its values are added at the top of `<head>`. Pages are sent with `Cache-Control: no-cache`, or `private, no-cache` when they carry client config, which may differ per user.

It returns the fallback endpoint's convention builder, so endpoint conventions apply:

```csharp
app.MapNiteSpa().RequireAuthorization();       // the whole SPA behind login
```

## INiteAssets

<xref:Nite.Assets.INiteAssets> answers "what does this page need?" in the current mode. The tag helpers and `MapNiteSpa` are built on it; use it directly for custom endpoints or layouts.

| Member | Returns |
|---|---|
| `IsDevelopment` | Whether the dev server is active. |
| `GetHeadAsync(context)` | A <xref:Nite.Assets.NiteHead>: the import map, preloads and scripts for `<head>`. `ToHtml()` renders it. |
| `GetIslandAsync(name, context)` | A <xref:Nite.Assets.NiteAsset> for an island: its module URL, stylesheets and preloads. |
| `GetModuleAsync(source, context)` | The same for a module in the client root. |
| `GetHtmlAsync(page, context)` | An HTML entry as it should be served. |

Serve a second single-page app at its own path:

```csharp
app.MapGet("/admin/{**path}", async (HttpContext context, INiteAssets assets) =>
    Results.Content(await assets.GetHtmlAsync("admin.html", context), "text/html"));
```

Render nite's head in a layout that is not a Razor view:

```csharp
var head = await assets.GetHeadAsync(context);
html.Append(head.ToHtml());
```

## The C# hot reload event

nite registers a `MetadataUpdateHandler` in its assembly. When `dotnet watch` (or an IDE) applies a hot reload to the running app in development, connected pages receive a `nite:server-update` event. There is nothing to configure. See [Hot reload](../guides/hot-reload.md#c-changes).

## Middleware order

A typical full pipeline:

```csharp
var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseNite();                 // before routing and static assets
app.UseRouting();
app.UseAuthentication();
app.UseAuthorization();

app.MapStaticAssets();
app.MapRazorPages().WithStaticAssets();
app.MapControllers();
app.MapNiteSpa();              // last: it is a fallback

app.Run();
```

## API reference

The generated [API reference](../../api/index.md) has every type and member.
