---
title: Private registries
description: Install packages from a private npm registry, a mirror or a per-scope registry, with credentials from .npmrc.
---

# Private registries

<p class="lead">Nite reads registries and credentials from the <code>.npmrc</code> files you already have. Scoped packages can come from their own registry, and credentials are only ever sent to the host they belong to.</p>

## A scoped registry

The usual setup: your organization publishes `@acme/*` to its own registry, and everything else comes from npmjs.org. Put this in a `.npmrc` next to `nite.json` (or in `~/.npmrc` for all projects):

```ini
@acme:registry=https://npm.acme.dev/
//npm.acme.dev/:_authToken=${ACME_NPM_TOKEN}
```

`${ACME_NPM_TOKEN}` is expanded from the environment, so the token itself stays out of the file and out of git. Then:

```bash
export ACME_NPM_TOKEN=...      # or set it in your shell profile, or CI secrets
nite add @acme/design-system
```

## A mirror or proxy for everything

To send all requests to a mirror (Artifactory, Verdaccio, a corporate proxy):

```ini
registry=https://artifacts.acme.dev/api/npm/npm/
//artifacts.acme.dev/api/npm/npm/:_authToken=${ARTIFACTORY_TOKEN}
```

Or without touching `.npmrc`:

```bash
nite config set registry https://artifacts.acme.dev/api/npm/npm/   # this user, every project
NITE_REGISTRY=https://artifacts.acme.dev/api/npm/npm/ nite install   # one command
```

`"registry"` in `nite.json` sets it for one project, for everyone who builds it.

## Credentials

Credentials use npm's "nerf-dart" keys: `//host/path/:` followed by the setting.

| Setting | Meaning |
|---|---|
| `//host/path/:_authToken=TOKEN` | Bearer token (most registries) |
| `//host/path/:_auth=BASE64` | Basic auth, `user:password` already base64-encoded |
| `//host/path/:username=USER` and `//host/path/:_password=BASE64` | Basic auth, password base64-encoded |

A credential is sent **only** to URLs under its host and path. A tarball served from another host (a CDN, say) never receives it. Nite refuses to store credentials in its own config: `nite config set` rejects them, and they stay in `.npmrc` where npm, your editor and other tools also find them.

## Where settings come from

Highest first:

1. `NITE_REGISTRY` (environment)
2. `"registry"` in the project's `nite.json`
3. The project's `.npmrc`
4. Nite's user config (`nite config set`)
5. The user's `~/.npmrc` (or the file `$NPM_CONFIG_USERCONFIG` names)
6. The default: `https://registry.npmjs.org/`

See exactly what applies, and where each value comes from:

```bash
nite config list --show-origin
```

```text
╭────────────────────────────┬─────────────────────────────┬─────────╮
│ Key                        │ Value                       │ Origin  │
├────────────────────────────┼─────────────────────────────┼─────────┤
│ //npm.acme.dev/:_authToken │ (set)                       │ .npmrc  │
│ @acme:registry             │ https://npm.acme.dev/       │ .npmrc  │
│ init.template              │ spa                         │ default │
│ registry                   │ https://registry.npmjs.org/ │ default │
╰────────────────────────────┴─────────────────────────────┴─────────╯
User config: /home/you/.config/nite/config.json
```

Credentials are never printed: a token shows as `(set)`.

## In CI

Pass the token as a secret environment variable and keep `.npmrc` (with `${VAR}` placeholders) in the repository:

```yaml
- run: nite install
  env:
    ACME_NPM_TOKEN: ${{ secrets.ACME_NPM_TOKEN }}
```

`dotnet publish -c Release` runs `nite build`, which installs first, so the variable has to be set for the publish step too (or run `nite install` in an earlier step with it).

## The esbuild and Sass binaries

Nite downloads the esbuild binary (and the Dart Sass binary, if you use Sass) from the npm registry too, through the same settings: a mirror that proxies npmjs.org serves them. Fully offline machines can point Nite at binaries they supply instead, with `NITE_ESBUILD_PATH` and `NITE_SASS_PATH`; see [Environment variables](../reference/environment-variables.md).
