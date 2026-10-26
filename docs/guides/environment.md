---
title: Environment variables and path aliases
description: Expose configuration to client code safely with .env files and envPrefix, and use tsconfig path aliases such as @/components.
---

# Environment variables and path aliases

<p class="lead">Client code reads configuration from <code>import.meta.env</code>, filled at compile time from <code>.env</code> files and the environment. Only variables with a public prefix ever reach the browser.</p>

## Public variables

Put variables in a `.env` file in the project folder, next to `nite.json`:

```ini
# .env
NITE_PUBLIC_API_URL=/api
NITE_PUBLIC_SENTRY_DSN=https://abc@o1.ingest.sentry.io/1
DATABASE_PASSWORD=hunter2          # never reaches the browser
```

Read them in client code:

```ts
const api = import.meta.env.NITE_PUBLIC_API_URL;       // "/api"
const mode = import.meta.env.MODE;                     // "development" or "production"
if (import.meta.env.DEV) console.debug("debug build");
```

**Only names that start with an `envPrefix`** are exposed. The default prefix is `NITE_PUBLIC_`; everything else in `.env` (database passwords, API keys for the server) stays on the server. Values are inlined into the compiled code as string literals, so they are public in the bundle: never give a secret a public prefix.

## Values from the running server

Public variables are inlined when code is compiled, so a production build carries whatever was set when `nite build` ran. That is wrong for values that differ between environments when the same build is deployed to each (an Application Insights connection string, another service's URL), and impossible for values that differ per request (the signed-in user, a feature flag, a tenant). For those, the server hands values to the page as it serves it:

```csharp
// Program.cs
builder.Services.AddNite(options => options.ClientConfig = context => new
{
    AppInsights = builder.Configuration["APPLICATIONINSIGHTS_CONNECTION_STRING"],
    User = context.User.Identity?.Name,
    Features = new { NewCheckout = context.User.IsInRole("beta") },
});
```

```ts
import { config } from "nite:config";

if (config.features.newCheckout) { /* ... */ }
```

How it works:

- The callback runs for each page `MapNiteSpa` serves and each page with `<nite-head />`. The result is serialized as camelCase JSON into a `<script type="application/json" id="nite-config">` element at the top of `<head>`; `nite:config` parses it once and exports it frozen. There is no extra request.
- It works the same in development and production, and the same build runs in every environment.
- For values that take awaiting (a database, `IFeatureManager`), set `ClientConfigAsync = async context => new { ... }` instead.
- Pages that carry client config are sent with `Cache-Control: private, no-store`, so a shared cache or CDN never hands one user's page to another, and the browser does not keep a signed-in user's page after they sign out.

Everything in it is readable by anyone who can load the page, like the rest of the HTML: send what the page needs, never secrets. (An Application Insights connection string is fine: the browser SDK needs it anyway.) The JSON is escaped so values cannot break out of the script element.

### Typing it

`nite init` and the `dotnet new` templates create `Client/nite-env.d.ts`. Describe what your callback returns there:

```ts
declare module "nite:config" {
  export interface NiteClientConfig {
    appInsights?: string;
    user?: string;
    features: { newCheckout: boolean };
  }

  export const config: Readonly<NiteClientConfig>;
  export default config;
}
```

### Client config, cookies or an API call?

| | Client config | A cookie | An API call |
|---|---|---|---|
| Arrives | With the page | With the page, and on every later request | After the page has loaded |
| Size | As big as the page can bear | About 4 KB | Any |
| Readable by scripts | Yes | Only if not `HttpOnly` | Yes |
| Changes during the visit | No | Yes | Yes |

Use client config for what the page needs to start: settings, who the user is, flags. Keep authentication in an `HttpOnly` cookie, which scripts cannot read and the browser sends for you. Fetch anything that changes while the page is open.

## Built-in values

| Expression | Development | Production |
|---|---|---|
| `import.meta.env.MODE` | `"development"` | `"production"` |
| `import.meta.env.DEV` | `true` | `false` |
| `import.meta.env.PROD` | `false` | `true` |
| `import.meta.env.BASE_URL` | `"/"` | `"/"` |
| `import.meta.env.SSR` | `false` | `false` |
| `process.env.NODE_ENV` | `"development"` | `"production"` |

These match Vite, so code and libraries written for Vite work unchanged. Public variables are also available as `process.env.NAME`, the Create React App convention, and `process.env.PUBLIC_URL` is `""` when the `REACT_APP_` prefix is in use.

## Files and precedence

Files are read from the project folder, later ones overriding earlier ones:

1. `.env`
2. `.env.local`
3. `.env.development` or `.env.production` (by mode)
4. `.env.development.local` or `.env.production.local`

**Variables already set in the process environment win over all files**, so CI can override a committed `.env` without editing it:

```bash
NITE_PUBLIC_API_URL=https://api.example.com dotnet publish -c Release
```

Commit `.env` and `.env.development` / `.env.production` with non-secret defaults. Keep `.env*.local` out of git (the generated `.gitignore` already does) for per-machine values.

### Syntax

```ini
# Comments start with #
NITE_PUBLIC_A=plain value
NITE_PUBLIC_B="double quoted, with \n newlines"
NITE_PUBLIC_C='single quoted, taken literally'
export NITE_PUBLIC_D=works too       # inline comments after an unquoted value
```

## Changing the prefix

```json
{ "envPrefix": ["VITE_", "NITE_PUBLIC_"] }
```

Projects imported from Vite get `["VITE_"]` (or whatever `envPrefix` the Vite config set), and Create React App projects get `["REACT_APP_"]`, so their code keeps working.

## Reloading

Editing a `.env` file while the app runs recompiles the client and reloads the page with the new values. In production, values are fixed at build time: change them and rebuild.

> [!NOTE]
> These are build-time values for the client. For runtime configuration that differs between environments without a rebuild, serve it from your API (`/api/config`) and fetch it on startup.

## Types

Declare your variables for autocompletion and type checking in `Client/nite-env.d.ts` (see [TypeScript](typescript.md#declarations-for-what-nite-provides)):

```ts
interface ImportMetaEnv {
  readonly NITE_PUBLIC_API_URL: string;
  readonly NITE_PUBLIC_SENTRY_DSN?: string;
}
```

## Path aliases

Aliases from `compilerOptions.paths` in the client's tsconfig work in development and production, so imports resolve exactly as they do in your editor:

```json
// Client/tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@ui": ["./src/components/index.ts"]
    }
  }
}
```

```ts
import { cn } from "@/lib/utils";
import { Button } from "@ui";
```

Nite follows `extends` (relative files) and Vite's `references` layout, where paths usually live in `tsconfig.app.json`. Aliases can point at code, stylesheets and assets alike. A `baseUrl` also makes a non-relative import resolve against it when a matching file exists there (`import "lib/utils"` finds `Client/lib/utils.ts` with `"baseUrl": "."`), as in TypeScript.

Editing a tsconfig while the app runs recompiles everything and reloads the page, since any import could now resolve differently.

> [!TIP]
> Vite projects sometimes define aliases in `vite.config` (`resolve.alias`) instead. Nite reads only tsconfig, which your editor needs anyway; move them there. The importer warns when it sees this.
