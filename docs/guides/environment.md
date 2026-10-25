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

nite follows `extends` (relative files) and Vite's `references` layout, where paths usually live in `tsconfig.app.json`. Aliases can point at code, stylesheets and assets alike. A `baseUrl` also makes a non-relative import resolve against it when a matching file exists there (`import "lib/utils"` finds `Client/lib/utils.ts` with `"baseUrl": "."`), as in TypeScript.

Editing a tsconfig while the app runs recompiles everything and reloads the page, since any import could now resolve differently.

> [!TIP]
> Vite projects sometimes define aliases in `vite.config` (`resolve.alias`) instead. nite reads only tsconfig, which your editor needs anyway; move them there. The importer warns when it sees this.
