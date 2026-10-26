---
title: Importing a Vite or CRA project
description: Bring an existing Vite or Create React App frontend into a NiteFx project, keeping the exact package versions it runs today.
---

# Importing a Vite or Create React App project

<p class="lead"><code>nite init --from</code> turns an existing npm, Yarn, pnpm or Bun frontend into the client half of a NiteFx project. It keeps the package versions your lockfile pins, carries over the settings it understands, and tells you plainly about the ones it does not.</p>

## Preview, then import

```bash
nite init my-app --from ../vite-app --dry-run   # show the plan, write nothing
nite init my-app --from ../vite-app             # do it
```

The source project is never modified. The new project is a complete ASP.NET Core app (`Program.cs` with `MapNiteSpa`, a sample `/api/hello` endpoint) with your frontend in `Client/`.

## What it supports

| Source | Detected by |
|---|---|
| **Vite** (React) | `index.html` at the project root, plus `vite` in package.json or a `vite.config.*` |
| **Create React App** | `react-scripts` in package.json; `public/index.html` |
| A static `index.html` with modules | `index.html` at the root, no Vite |

| Package manager | Lockfile read |
|---|---|
| npm | `package-lock.json` (v1 to v3), `npm-shrinkwrap.json` |
| Yarn classic | `yarn.lock` v1 |
| Yarn Berry | `yarn.lock` v2+ |
| pnpm | `pnpm-lock.yaml` (v5 to v9) |
| Bun | `bun.lock` (text). The binary `bun.lockb` is not read: run `bun install --save-text-lockfile` first. |

Monorepos (`workspaces`, `pnpm-workspace.yaml`) are refused; import one app at a time with `--from <repo>/packages/<app>`. Next.js, Remix and Astro apps have their own servers and are out of scope.

## What it does

**Files**

- `index.html` and `src/` go to `Client/` (Create React App's `public/index.html` becomes `Client/index.html`, with `%PUBLIC_URL%` removed and the entry script tag CRA used to inject added).
- `public/` goes to `wwwroot/`, where ASP.NET Core serves static files.
- tsconfig files, `postcss.config.*` and `tailwind.config.*` go to `Client/`.
- `.env` files go to the project folder.
- `vite-env.d.ts` / `react-app-env.d.ts` become `nite-env.d.ts` with declarations for what NiteFx provides, and `"types": ["vite/client"]` is dropped from tsconfig (comments in the file survive).

**Packages**

- Runtime `dependencies` are imported, plus any devDependency your source actually imports (bundlers never cared which list a library was in), plus `@types/*` and `typescript`.
- Stylesheet tools are kept as dev dependencies: PostCSS and its plugins, Sass, Less, Tailwind and its plugins.
- Build, lint and test tooling (Vite and its plugins, Babel, ESLint, oxlint, Prettier, Jest, Vitest, Testing Library, …) is skipped: NiteFx replaces the build, and does not run the rest. Imports from test files do not count as runtime imports.
- `@tailwindcss/vite` and `@tailwindcss/postcss` are replaced by `tailwindcss` itself, which NiteFx runs.
- **Versions come from your lockfile.** NiteFx resolves the ranges but prefers the exact versions you run today wherever they still satisfy them, so the imported app runs what it ran before.

**Settings**

- `envPrefix`: `VITE_` for Vite (or the `envPrefix` in `vite.config`), `REACT_APP_` for Create React App.
- `jsxInJs: true` for Create React App, which allows JSX in `.js` files.
- `css.preprocessorOptions.*.additionalData` from `vite.config`, including the path-building template literal in Mantine's Sass guide.

## What it reports

The plan lists everything it could not bring along, so nothing is silently lost:

| Warning | What to do |
|---|---|
| A Vite plugin other than React's and Tailwind's | Nothing replaces it; see whether you still need what it did |
| `resolve.alias` in `vite.config` | Move aliases to tsconfig `paths`, which NiteFx reads |
| `base` in `vite.config` | NiteFx serves from the site root |
| `import.meta.glob`, `?raw`, `?url`, `?worker` imports | Rewrite with explicit imports, `fetch`, or `new Worker(new URL(...))` |
| SVGs imported as React components (svgr) | Import as URLs, or inline the SVG in a component |
| Stylus | Convert to CSS, Sass or Less |
| Tailwind 3 | Upgrade to Tailwind 4 |
| `overrides` / `resolutions` / `pnpm.overrides` | Not supported; versions come from ranges and the lockfile |
| A dependency that is not a registry version (`file:`, `workspace:`, git) | Publish it, or vendor it into `Client/` |
| An imported package package.json does not list | `nite add` it |

It also notes things you no longer need, such as the dev server `proxy` (the app and API now share an origin) and package.json `scripts` (use `nite watch` and `nite build`).

## After importing

```bash
cd my-app
nite watch
```

Then:

1. **Move API calls to relative URLs.** If the app called `http://localhost:5000/api/...` through a proxy, call `/api/...` and implement or proxy those endpoints in `Program.cs`.
2. **Check environment variables.** `import.meta.env.VITE_*` keeps working; values come from the copied `.env` files.
3. **Run your type checker** (`tsc --noEmit`) and tests with the tools you used before; NiteFx does not replace them.
4. **Publish** with `dotnet publish -c Release` and compare the result with your old build.

## Options

| Option | Meaning |
|---|---|
| `--from <path>` | The project to import |
| `--dry-run` | Show the plan; write nothing |
| `--force` | Import into a folder that already has files (existing files are never overwritten) |
| `--no-install` | Write the project without installing packages |
| `--name <name>` | Project name (defaults to the folder name) |
| `--nite-source <path>` | Reference a NiteFx source checkout instead of the NuGet package |
| `--verbose` | Debug output |

See [CLI reference](../reference/cli.md#nite-init).
