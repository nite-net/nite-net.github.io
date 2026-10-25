---
title: Application Insights in the browser
description: Send page views, errors, events and fetch calls from a nite app to Application Insights, configured per environment and correlated with the server.
---

# Application Insights in the browser

<p class="lead">The Application Insights JavaScript SDK works in a nite app like any other package. Nite adds three things: the connection string comes from the running server, so one build serves every environment; the SDK loads as its own chunk, after the page; and the browser's telemetry joins the trace of the request that served the page.</p>

[`samples/Nite.Aspire`](https://github.com/nite-net/nite/tree/main/samples/Nite.Aspire) does everything on this page, for both its services and the browser.

## Install

```bash
nite add @microsoft/applicationinsights-web
```

`@microsoft/applicationinsights-react-js` adds a React context and hooks such as `useTrackEvent`; it works too, but this page uses the core SDK directly, which is all most apps need.

## Hand the browser its connection string

The connection string differs per environment, and Azure (or Aspire) sets it on the server as `APPLICATIONINSIGHTS_CONNECTION_STRING` when the app is deployed, after it was built. Pass it through [client config](environment.md#values-from-the-running-server), which the server writes into each page:

```csharp
builder.Services.AddNite(options => options.ClientConfig = context => new
{
    AppInsights = builder.Configuration["APPLICATIONINSIGHTS_CONNECTION_STRING"],
    // The trace of the request serving this page, so the browser can join it.
    TraceId = System.Diagnostics.Activity.Current?.TraceId.ToString(),
});
```

```ts
// Client/nite-env.d.ts
declare module "nite:config" {
  export interface NiteClientConfig {
    appInsights?: string;
    traceId?: string;
  }
  export const config: Readonly<NiteClientConfig>;
  export default config;
}
```

The connection string is not a secret: the browser SDK sends it with every batch anyway. (A `NITE_PUBLIC_` variable would also reach the browser, but it is inlined at build time, so each environment would need its own build.)

## Start the SDK after the page

The SDK is about 200 KB minified (80 KB gzipped), as much as React and ReactDOM together. Import it dynamically: production builds put it in a chunk of its own, loaded after the page has rendered, and an app without a connection string never loads it.

```ts
// Client/telemetry.ts
import { config } from "nite:config";
import type { ApplicationInsights } from "@microsoft/applicationinsights-web";

let insights: ApplicationInsights | undefined;

export async function startTelemetry() {
  if (!config.appInsights) return;
  const { ApplicationInsights } = await import("@microsoft/applicationinsights-web");
  insights = new ApplicationInsights({
    config: { connectionString: config.appInsights, enableAutoRouteTracking: true },
  });
  insights.loadAppInsights();
  if (config.traceId) {
    insights.context.telemetryTrace.traceID = config.traceId;   // join the page request's trace
  }
  insights.trackPageView();
}

export function trackEvent(name: string, properties?: Record<string, unknown>) {
  insights?.trackEvent({ name }, properties);
}
```

```tsx
// Client/main.tsx, after createRoot(...).render(...)
void startTelemetry();
```

`enableAutoRouteTracking` records a page view for each client-side route change. To leave development out entirely, guard the call with `if (import.meta.env.PROD)`: the condition is false in development, so the SDK is never imported there.

## One transaction, from page load to the API

With the server sending its own telemetry to the same resource (in an Aspire app, uncomment `UseAzureMonitor()` in ServiceDefaults; elsewhere add the `Azure.Monitor.OpenTelemetry.AspNetCore` package and call `builder.Services.AddOpenTelemetry().UseAzureMonitor()`), these share one operation id:

1. the server request that rendered the page (its trace id went to the browser through client config);
2. the browser's page view, its performance timings and custom events;
3. the browser's `fetch` to your API: the SDK adds a W3C `traceparent` header to same-origin requests;
4. the server request handling that call, and everything it calls in turn, other services included.

So Application Insights' transaction view shows a click from the browser down through every service. Calls to another origin get the header only with `enableCorsCorrelation: true`, and that origin must allow the `traceparent` and `Request-Id` headers in CORS. Calling other services through your own app, on the same origin, avoids both.

## Source maps

Production builds write source maps next to the bundles (`wwwroot/_nite/*.js.map`), and the bundles point at them, so browser developer tools and Application Insights' "unminify" can show original TypeScript and line numbers. To un-minify call stacks in the portal, upload the maps to the storage container linked to your Application Insights resource as part of your release.

## In development

Nite's own [telemetry](observability.md) also reaches Application Insights while you develop, if a connection string is set: dev server startup, compiles and `/_nite` requests. That is useful when debugging nite itself and noise otherwise; set the connection string only in deployed environments (the Aspire sample only adds it when one is configured), or use the Aspire dashboard locally.
