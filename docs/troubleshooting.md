---
title: Troubleshooting
description: Common problems with nite and how to fix them.
---

# Troubleshooting

<p class="lead">Symptoms, their usual causes, and the fix. Run CLI commands with <code>--verbose</code> for debug output; in the app, raise the <code>Nite</code> log category to <code>Debug</code> in <code>appsettings.Development.json</code>.</p>

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Nite": "Debug"
    }
  }
}
```

## Installing and starting

### "Package 'x' is not installed. Add it to dependencies in nite.json."

Code imports a package that is not in `node_modules`. Run `nite add x`. If it is in `nite.json` already, run `nite install` and check the output for errors.

### The first start is slow, or fails without network

The first run downloads esbuild and your packages. Later runs use the cache (`~/.cache/nite`) and the lockfile. Behind a proxy or without registry access, see [Private registries](guides/private-registries.md) and [Offline machines](reference/environment-variables.md#offline-and-air-gapped-machines).

### "'name@range' is not supported. Nite installs registry versions and ranges only."

A dependency uses `git:`, `file:`, `workspace:`, a URL or an `npm:` alias. Publish the package to a registry, or vendor its code into the client folder.

### A package fails at runtime with errors about a missing binary or `.node` file

It needs an install script or a native addon, which nite does not run. Look for a pure-JavaScript alternative, or a browser build of the package.

### "This nite is not running as a dotnet tool"

`nite update-self` only works for an installed tool. Running from a source checkout, pull and rebuild instead.

## Development

### Edits do not show up

- Check the file is under the client root (`Client/` by default). Files elsewhere are not watched, except Razor views for Tailwind.
- Check the page actually loads the module. Edits to files nothing imports do nothing, by design.
- Check the browser console for `[nite]` messages (they log at the `debug` level, so enable verbose logs) and for WebSocket errors.

### Every component edit reloads the page

Fast Refresh needs React as a dependency, `jsxImportSource` set to `react` and `fastRefresh` not `false`. If those are right, the edited module probably exports something besides components, so it is not a refresh boundary; move the non-component exports to another file. See [How Fast Refresh decides](guides/hot-reload.md#how-fast-refresh-decides).

### "Rendered more hooks than during the previous render" after an edit

A custom hook changed the order of the hooks it calls, which hook signatures do not see. Save again or reload.

### Adding an endpoint in Program.cs does nothing

`dotnet watch` treated the edit as one that "might not have any effect until the application is restarted" (ENC0118) and waited for Ctrl+R. `nite watch` restarts automatically; with plain `dotnet watch`, set `DOTNET_WATCH_RESTART_ON_RUDE_EDIT=1`. See [Hot reload](guides/hot-reload.md#changes-that-need-a-restart).

### The page reloads after every C# change

Plain `dotnet watch` injects a reload script. Use `nite watch`, or set `DOTNET_WATCH_SUPPRESS_BROWSER_REFRESH=1` in the environment (it is ignored in `launchSettings.json`).

### A Tailwind class has no effect

- Make sure the class name appears in full somewhere in the project, not assembled from pieces (`` `text-${color}-600` `` is never found).
- Check the file is not in a folder your `.gitignore` lists, or add `@source "<folder>"`.
- Tailwind 3 is not supported; check `nite list` shows `tailwindcss` 4.

### "Nite supports Tailwind CSS 4; this project has 3.x"

Upgrade with `npx @tailwindcss/upgrade` and the [upgrade guide](https://tailwindcss.com/docs/upgrade-guide).

### A PostCSS plugin fails with "Cannot find module" or a native addon error

The plugin needs a Node built-in nite does not provide, or native code. Check the plugin's issue tracker for a browser-compatible build, or remove it. Run with `Nite` logging at `Debug` to see the full error.

### "Sass stylesheets need the sass-embedded (or sass) package"

Install it: `nite add -D sass-embedded`. nite uses its version to download the matching native compiler.

### An island does not mount

- `<nite-head />` must be in the layout's `<head>`.
- `@addTagHelper *, Nite` must be in `_ViewImports.cshtml`; without it, `<island>` is rendered as an unknown HTML tag.
- The `name` is the path under the islands folder without extension, and is case-sensitive on Linux.
- Check the console for `[nite] island <name> failed`.

## Production

### "wwwroot/_nite/manifest.json was not found"

The app runs in production mode without a build. Publish with `-c Release` (which runs `nite build`), or run `nite build`. Check `NiteBuildEnabled` is not `false`, and that `ASPNETCORE_ENVIRONMENT` is what you expect.

### "Island 'x' is not in the Nite build" or "Module 'x' is not in the Nite build"

The build output is older than the code. Rebuild. For `<nite-module>`, add the module to `entries` in `nite.json`.

### Publish fails with "nite: command not found"

The build runs `nite build` with the `nite` tool on the `PATH`. Install the tool on the build machine, or set `NiteCommand` (for example to `dotnet tool run nite`). See [MSBuild properties](reference/msbuild.md).

### Assets 404 when the app runs under a path base

Production URLs inside JavaScript and CSS assume the site root. See [Limits](limits.md#hosting).

## Still stuck?

Open an issue on [GitHub](https://github.com/nite-net/nite/issues) with `nite version`, the command or request that fails, and the output with `--verbose` (or `Nite` logging at `Debug`).
