---
title: Packages and the lockfile
description: Add, remove and update npm packages with the nite CLI, how versions are resolved and locked, and what the installer does and does not do.
---

# Packages and the lockfile

<p class="lead">nite installs packages from the npm registry into an ordinary <code>node_modules</code> folder, with a small npm client written in C#. You manage them with <code>nite add</code>, <code>nite rm</code> and <code>nite update</code>; there is no <code>package.json</code>.</p>

## Dependencies live in nite.json

```json
{
  "dependencies": {
    "react": "^19.3.1",
    "react-dom": "^19.3.1",
    "react-router": "^8.5.0"
  },
  "devDependencies": {
    "@types/react": "^19.2.0",
    "typescript": "~6.0.3"
  }
}
```

- **`dependencies`** are what your client code imports. They are bundled.
- **`devDependencies`** are installed but never bundled: type packages for your editor, TypeScript, and stylesheet tools such as `sass-embedded`, `tailwindcss` and PostCSS plugins (nite runs those itself; see [Stylesheets](stylesheets.md)).

The split only matters for clarity, as with any bundler: what ends up in the bundle is what your code imports.

## Adding packages

```bash
nite add react-router             # latest version, saved as ^8.5.0
nite add react@^19                # a range, saved as written
nite add zod@latest               # a dist-tag, saved as ^<that version>
nite add -D @types/node           # to devDependencies
nite add -E lodash-es             # pin the exact version: 4.17.21, not ^4.17.21
nite add react-router zod clsx    # several at once
```

`nite add` (also `nite install <pkg>` or `nite i <pkg>`) edits `nite.json` (keeping your comments and formatting), resolves, updates `nite.lock.json` and installs. Without arguments, `nite install` installs everything in `nite.json`.

You can also edit `nite.json` by hand. If the app is running in development, the dev server notices, installs, pre-bundles the new packages and reloads the page.

## Removing packages

```bash
nite rm react-router              # also: nite remove, nite delete, nite uninstall
```

Removes the package from `nite.json` and from `node_modules`, along with anything only it depended on.

## Seeing what is installed

```bash
nite list            # direct packages: range and installed version
nite list --all      # every installed package, with where it sits if nested
```

## Updating

```bash
nite update --check       # report current, wanted and latest; change nothing
nite update               # move everything to the newest version its range allows
nite update react         # just these packages
nite update --latest      # move ranges to the latest versions, across majors too
```

*Wanted* is the newest version the range in `nite.json` allows; *latest* is the registry's `latest` tag. `--latest` rewrites the range, keeping its style: `^18.3.1` becomes `^19.3.1`, an exact `4.17.20` becomes `4.17.21`.

## The lockfile

`nite.lock.json` records the exact version, tarball URL and integrity hash of every installed package, and where in `node_modules` it goes. **Commit it.** It is what makes installs repeatable:

- With a lockfile that matches `nite.json`, an install does not ask the registry for metadata at all; it only downloads tarballs it does not have cached.
- Adding a package keeps every other package at its locked version unless a range forces a change. Adding one package never quietly upgrades the rest; that is what `nite update` is for.
- Editing a range in `nite.json` re-resolves, preferring locked versions wherever they still fit.

Do not edit the lockfile by hand. If it gets into a bad state (a merge conflict, say), delete it and run `nite install`: versions are re-resolved from the ranges.

## How resolution works

| Feature | Supported |
|---|---|
| Semver ranges: `^1.2.3`, `~1.2`, `>=1 <2`, `1.x`, `1.2.3 - 1.4`, `||` | Yes |
| Dist-tags: `latest`, `next`, and tags inside ranges (`>=4 \|\| next`) | Yes |
| Exact versions and prereleases (`1.0.0-beta.2`) | Yes |
| Scoped packages (`@scope/name`) and per-scope registries | Yes |
| Peer dependencies | Installed when missing, like npm 7+ (optional peers skipped) |
| Hoisting | Top level unless it would conflict, otherwise nested under the dependent |
| `git:`, `file:`, `link:`, `workspace:`, URL and `npm:` alias dependencies | No |
| Optional dependencies | Skipped |
| Install scripts (`preinstall`, `postinstall`) | **Never run**, with a warning ([below](#install-scripts)) |

Not running install scripts is deliberate: it removes a common supply-chain attack path and the need for a JavaScript runtime. The cost is that packages that build native addons or download binaries in `postinstall` do not work. Packages that ship platform binaries as optional dependencies (esbuild, Sass, lightningcss) are not installed either; nite fetches the esbuild and Sass binaries it needs itself.

### Install scripts

The registry marks every version that has a `preinstall`, `install` or `postinstall` script (or a `binding.gyp`, which implies one) with `hasInstallScript`. When nite resolves such a package, it tells you, once per package and after resolution has finished, so the messages are not buried:

```text
› Resolving 4 package(s) from https://registry.npmjs.org
warn  bcrypt@5.1.1 has an install script, which Nite does not run; it is a native Node.js addon, which cannot run in a browser. Server-side work like this belongs in your ASP.NET Core code.
› core-js@3.51.0 has an install script, which Nite does not run; it only prints a message, so nothing is missing.
› esbuild@0.25.12 has an install script, which Nite does not run; it fetches the esbuild binary, which Nite downloads and runs itself.
```

A short list of well-known packages gets a specific message; scripts known to be harmless to skip are reported as information rather than warnings:

| Package | Level | Why |
|---|---|---|
| `core-js`, `core-js-pure`, `es5-ext` | info | The script only prints a message. Nothing is missing. |
| `esbuild` | info | The script fetches the esbuild binary. nite downloads and runs its own. |
| `node-sass` | warning | The script builds LibSass, a native addon. nite compiles Sass with Dart Sass's native binary; replace `node-sass` with `sass`. |
| `bcrypt`, `better-sqlite3`, `sqlite3`, `argon2`, `canvas` | warning | Native Node.js addons, which cannot run in a browser. That work belongs in your ASP.NET Core code. |
| Anything else | warning | If the package needs its script to download or build something, it may not work. |

The messages appear whenever the lockfile is resolved: `nite add`, `nite update`, or a changed `nite.json`. An install from a current `nite.lock.json` does not resolve anything, so it does not repeat them.

## Integrity and caching

Every tarball is checked against the `integrity` hash the registry published (SHA-512, or SHA-1 for very old packages) before it is extracted. Tarballs and registry metadata are cached per user, in `~/.cache/nite` on Linux and macOS (see [Settings and directories](../reference/settings.md)); metadata is revalidated with its ETag, so resolving an unchanged package costs a `304`.

```bash
nite cache verify    # re-check cached tarballs, drop corrupt ones
nite cache clean     # delete the cache
nite cache dir       # print where it is
```

## Installs and the running app

The dev server installs on startup and whenever `nite.json` changes, and `nite install` can run at the same time: a lock file in `.nite/` makes sure only one of them touches `node_modules` at a time.

## Using packages

Import packages by name, as with any bundler:

```ts
import { useState } from "react";
import { z } from "zod";
import debounce from "lodash-es/debounce";
import "@fontsource/inter/400.css";        // CSS from a package
```

Subpaths go through the package's `exports` field. CommonJS packages work, including named imports (`import { useState } from "react"`, while React is still CommonJS). CSS imported from code goes through the [stylesheet pipeline](stylesheets.md).

Importing a package that is not in `nite.json` shows an error overlay naming it, so you can `nite add` it.

## Private registries

Scoped registries and credentials come from your existing `.npmrc`. See [Private registries](private-registries.md).
