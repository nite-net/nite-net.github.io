---
title: TypeScript and JSX
description: How nite compiles TypeScript and JSX, how to set up tsconfig and type declarations, and how to type-check in CI.
---

# TypeScript and JSX

<p class="lead">nite compiles <code>.ts</code>, <code>.tsx</code>, <code>.jsx</code> and <code>.js</code> with esbuild. Types are stripped, not checked: your editor checks as you type, and <code>tsc --noEmit</code> checks in CI. This is the same model as Vite.</p>

## What gets compiled

| Extension | Treated as |
|---|---|
| `.ts`, `.mts` | TypeScript |
| `.tsx` | TypeScript with JSX |
| `.jsx` | JavaScript with JSX |
| `.js`, `.mjs` | JavaScript (with JSX too when `"jsxInJs": true`, as in Create React App) |
| `.json` | A module whose default export is the parsed JSON |
| `.css`, `.scss`, `.sass`, `.less` | Stylesheets; see [Stylesheets](stylesheets.md) |
| Anything else (`.svg`, `.png`, `.woff2`…) | A module whose default export is the file's URL |

Imports can leave off the extension (`./Button` finds `Button.tsx`), can use the TypeScript convention of importing `.js` for a `.ts` file (`./util.js` finds `util.ts`), and can point at a folder with an `index` file.

## JSX

JSX uses the **automatic runtime** (`react/jsx-runtime`), so components do not need `import React`. Set `jsxImportSource` in `nite.json` to use another library's runtime:

```json
{ "jsxImportSource": "preact" }
```

In development nite uses the dev runtime (`react/jsx-dev-runtime`), which adds component stacks and source locations to React's warnings.

## tsconfig.json

The tsconfig in the client root is for your editor and for `tsc`. nite uses `compilerOptions.paths` and `baseUrl` from it (see [path aliases](environment.md#path-aliases)); how code is compiled (JSX runtime, target) is set in `nite.json`, not here. The template's config is a good starting point:

```json
{
  // Editor settings only: nite compiles with esbuild, which strips types without
  // checking them. Run `tsc --noEmit` in CI for type checking.
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noEmit": true,
    "isolatedModules": true,
    "skipLibCheck": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "typeRoots": ["../node_modules/@types"]
  },
  "include": ["**/*.ts", "**/*.tsx"]
}
```

Two settings matter more than they look:

- **`isolatedModules: true`** makes the editor flag code that a per-file compiler like esbuild cannot handle, such as re-exporting a type without `export type`.
- **`moduleResolution: "Bundler"`** matches how nite resolves imports: package `exports`, extensionless relative imports and `index` files.

nite follows `extends` and Vite's `references` layout, so a `tsconfig.json` that references `tsconfig.app.json` works.

## Declarations for what nite provides

TypeScript does not know about `import.meta.env`, stylesheet imports or asset URLs until you declare them. Add `Client/nite-env.d.ts` (imported projects get one automatically):

```ts
// What nite provides to client code.
interface ImportMetaEnv {
  readonly MODE: string;
  readonly DEV: boolean;
  readonly PROD: boolean;
  readonly BASE_URL: string;
  readonly SSR: boolean;
  readonly [key: string]: string | boolean | undefined;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare module "*.module.css" { const classes: Record<string, string>; export default classes; }
declare module "*.module.scss" { const classes: Record<string, string>; export default classes; }
declare module "*.module.less" { const classes: Record<string, string>; export default classes; }
declare module "*.css";
declare module "*.scss";
declare module "*.less";
declare module "*.svg" { const url: string; export default url; }
declare module "*.png" { const url: string; export default url; }
declare module "*.jpg" { const url: string; export default url; }
declare module "*.webp" { const url: string; export default url; }
declare module "*.woff2" { const url: string; export default url; }

// process.env.NODE_ENV and public variables are inlined at build time.
declare const process: { env: { readonly NODE_ENV: "development" | "production"; readonly [key: string]: string | undefined } };
```

Leave out the `process` declaration if you install `@types/node`, which declares it already. Name your public variables in `ImportMetaEnv` for autocompletion:

```ts
interface ImportMetaEnv {
  readonly NITE_PUBLIC_API_URL: string;
}
```

## Type checking

Install TypeScript as a dev dependency and run its compiler from `node_modules`. nite does not run it for you, the same as Vite.

```bash
nite add -D typescript
```

`tsc` itself is JavaScript, so it needs a JavaScript runtime to run. On a developer machine your editor already runs it. In CI, GitHub's hosted runners (and most others) have Node preinstalled; run the compiler nite installed:

```yaml
# .github/workflows/ci.yml (excerpt)
- run: nite install
- run: node node_modules/typescript/bin/tsc --noEmit -p Client
```

nite does not create `node_modules/.bin` links, so call the package's script directly rather than through `npx` (which would download TypeScript again).

## Targets

- **Development** compiles to ES2022 for any modern browser.
- **Production** uses `"target"` from `nite.json` (default `es2022`), plus Vite's default browser list when the target names only a language version, so newer syntax in JavaScript and CSS is lowered for browsers from the last few years.

```json
{ "target": "es2020,safari15" }
```

See [nite.json](../reference/nite-json.md#target).
