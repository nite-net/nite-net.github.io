---
title: Telemetry, health checks and Aspire
description: Nite's OpenTelemetry traces and metrics, its health check, and running a Nite app under Aspire.
---

# Telemetry, health checks and Aspire

<p class="lead">Nite reports what it does as OpenTelemetry traces and metrics and offers a health check, so a slow first page load or a broken <code>nite.json</code> shows up in your dashboard instead of in a guess. Under <a href="https://aspire.dev">Aspire</a>, a Nite app is an ordinary project resource.</p>

## Traces and metrics

Nite uses .NET's own `ActivitySource` and `Meter`, both named `Nite`, so the library takes no OpenTelemetry dependency, and nothing is recorded (or costs anything) until a listener subscribes. Add the names to your OpenTelemetry setup:

```csharp
using Nite.Observability;

builder.Services.AddOpenTelemetry()
    .WithTracing(tracing => tracing.AddSource(NiteTelemetry.SourceName))
    .WithMetrics(metrics => metrics.AddMeter(NiteTelemetry.MeterName));
```

### Spans

| Span | When | Tags |
|---|---|---|
| `nite.dev.startup` | The dev server starting: package install, initial compiles and pre-bundling in one trace | |
| `nite.dev.compile` | A module compiled for a request; a child of that request's span | `nite.file` |
| `nite.dev.stylesheet` | A stylesheet built for a request | `nite.file` |
| `nite.css.sass`, `nite.css.less`, `nite.css.tailwind`, `nite.css.postcss` | Each stylesheet tool, under the stylesheet it ran for | `nite.file` |
| `nite.dev.hot_update` | A batch of saved files and what the browser was told to do | `nite.files.changed`, `nite.update.kind`, `nite.update.modules` |
| `nite.dev.prebundle` | Pre-bundling dependencies (at startup, or when a new import appears) | `nite.dependencies` |
| `nite.packages.install` | Making `node_modules` match `nite.json` | `nite.packages.count` |
| `nite.packages.resolve` | Resolving versions; only when the lockfile changes | `nite.packages.requested` |
| `nite.packages.materialize` | Extracting packages into `node_modules` | `nite.packages.installed` |
| `nite.tool.download` | Downloading the esbuild or Dart Sass binary, the first time | `nite.package` |
| `nite.build` | A production build | `nite.build.entries` |

Cache hits make no spans, so a warm dev server's request traces stay short. `nite.update.kind` is `update` (Fast Refresh), `css`, `error` (an overlay) or `reload`. A failed span has the error status and an `exception` event, so a Sass syntax error or a package that does not exist is one click away from the request that hit it.

The startup trace waits for the host to start before it begins, because OpenTelemetry subscribes as the host starts. Requests that arrive first wait for startup, as they always have.

### Metrics

| Metric | Unit | Tags |
|---|---|---|
| `nite.dev.compile.duration` | s | `nite.kind` (module, stylesheet) |
| `nite.dev.compiles` | {compile} | `nite.kind`, `nite.cache` (hit, miss) |
| `nite.css.tool.duration` | s | `nite.css.tool` (sass, less, tailwind, postcss) |
| `nite.dev.hot_updates` | {update} | `nite.update.kind` |
| `nite.dev.prebundle.duration` | s | |
| `nite.packages.install.duration` | s | |
| `nite.packages.tarballs` | {tarball} | `nite.cache` (hit, miss) |
| `nite.build.duration` | s | |

## Health check

```csharp
builder.Services.AddHealthChecks().AddNite();
// ...
app.MapHealthChecks("/health");
```

| Where | Status |
|---|---|
| Development | **Degraded** while packages install or dependencies pre-bundle; **Unhealthy** if that failed (often a typo in `nite.json`) or `app.UseNite()` never ran; **Healthy** otherwise, with the number of compiled modules and pre-bundled dependencies |
| Production | **Unhealthy** if `wwwroot/_nite/manifest.json` is missing or unreadable, which usually means the publish did not run `nite build`; **Healthy** otherwise |

It is a readiness check: restarting the app does not fix a broken `nite.json`, so it carries no tags. Pass `tags` to `AddNite` to change that. `MapHealthChecks` answers 200 for Healthy and Degraded and 503 for Unhealthy, unless you set `ResultStatusCodes`.

## Aspire

A Nite app needs nothing special to run under Aspire: Nite is middleware in your ASP.NET Core project, so `AddProject` runs the dev server along with your API.

```csharp
// AppHost.cs
var builder = DistributedApplication.CreateBuilder(args);

var api = builder.AddProject<Projects.Api>("api");

builder.AddProject<Projects.Web>("web")
    .WithExternalHttpEndpoints()
    .WithHttpHealthCheck("/health")
    .WithReference(api);

builder.Build().Run();
```

In the ServiceDefaults project, add Nite's names to `ConfigureOpenTelemetry` and its health check to `AddDefaultHealthChecks`:

```csharp
.WithMetrics(metrics => metrics.AddMeter(NiteTelemetry.MeterName) /* ... */)
.WithTracing(tracing => tracing.AddSource(NiteTelemetry.SourceName) /* ... */)

builder.Services.AddHealthChecks()
    .AddCheck("self", () => HealthCheckResult.Healthy(), ["live"])
    .AddNite();
```

ServiceDefaults references `Nite` for this (a package reference, or a project reference to a Nite checkout). The dashboard then shows Nite's logs and its startup and compile spans inside your request traces, and the web resource turns unhealthy if the dev server fails to start, with the reason in the health check's description. (`MapHealthChecks` answers 200 for Degraded as well as Healthy, so a dev server that is still starting does not count against the resource.)

What to know:

- **Hot reload.** Saved TypeScript, JSX and CSS update in the browser as usual: the dev server watches files itself. Aspire runs projects with `dotnet run`, not `dotnet watch`, so C# changes need a restart, and the browser's `nite:server-update` event does not fire.
- **Other services' URLs in client code.** Variables with your `envPrefix` (`NITE_PUBLIC_` by default) reach client code, including ones the AppHost sets: `.WithEnvironment("NITE_PUBLIC_API_URL", api.GetEndpoint("http"))`. They are inlined when code is compiled, so this works in development; production builds bake in whatever was set when `nite build` ran. For production, call your API on the same origin (proxy it, or serve the frontend from the API project) or fetch the URL at runtime from a small config endpoint.
- **Deploying.** `aspire deploy` builds container images with `dotnet publish`, which runs `nite build`, which needs the `nite` tool on the machine that builds the image. Install it there (`dotnet tool install --global Nite.Cli`), as in [CI](deployment.md).
