---
title: MSBuild properties
description: The MSBuild targets the Nite package adds to a project, and the properties that control them.
---

# MSBuild properties

<p class="lead">The <code>Nite</code> package brings MSBuild targets (<code>build/Nite.targets</code>), imported automatically into any project that references it. They keep client files out of the build, and run <code>nite build</code> for Release builds.</p>

## What the targets do

| When | What |
|---|---|
| Always | Add `node_modules/**` and `.nite/**` to `DefaultItemExcludes`, so MSBuild never walks them. |
| Always | Mark the client root, `nite.json` and `nite.lock.json` as never copied to the build or publish output. |
| Always | Remove `wwwroot/_nite/**` from content, so a Debug build never serves a stale production build. |
| `NiteBuildEnabled` is `true` (Release by default) | Run `$(NiteCommand) build --dir "$(MSBuildProjectDirectory)"` after project references resolve and before static web assets are collected, then add `wwwroot/_nite/**` as content so it publishes. |
| `dotnet clean` | Delete `wwwroot/_nite`. |

## Properties

| Property | Default | Meaning |
|---|---|---|
| `NiteBuildEnabled` | `true` when `Configuration` is `Release`, otherwise empty | Whether builds run `nite build`. Set `false` to skip it (a separate CI step builds the client, say), or `true` to build the client in Debug too. |
| `NiteCommand` | `nite`, or `"dotnet" "$(NiteCliPath)"` when `NiteCliPath` is set | The command that runs the CLI. Use `dotnet tool run nite` for a [local tool](https://learn.microsoft.com/dotnet/core/tools/local-tools-how-to-use). |
| `NiteCliPath` | empty | Path to `Nite.Cli.dll`, for projects that build against a nite source checkout (`nite init --nite-source` sets it). |
| `NiteClientRoot` | `Client` | The client folder kept out of the build output. Set it when `clientRoot` in `nite.json` is something else. |
| `NiteDotnet` | `$(DOTNET_HOST_PATH)`, or `dotnet` | The `dotnet` executable used with `NiteCliPath`. |

Set them in the project file:

```xml
<PropertyGroup>
  <!-- nite is a local tool in this repository (.config/dotnet-tools.json). -->
  <NiteCommand>dotnet tool run nite</NiteCommand>

  <!-- The client lives in "frontend" (and nite.json says so). -->
  <NiteClientRoot>frontend</NiteClientRoot>
</PropertyGroup>
```

Or on the command line:

```bash
dotnet publish -c Release -p:NiteBuildEnabled=false
```

## Building against a source checkout

Projects created with `nite init --nite-source <path>` reference the library and the CLI project directly and import the targets from the checkout:

```xml
<ItemGroup>
  <ProjectReference Include="..\nite\src\Nite\Nite.csproj" />
  <!-- Built first so Release builds can run `nite build`; not referenced as an assembly. -->
  <ProjectReference Include="..\nite\src\Nite.Cli\Nite.Cli.csproj" ReferenceOutputAssembly="false" Private="false" />
</ItemGroup>

<PropertyGroup>
  <NiteCliPath>$(MSBuildThisFileDirectory)..\nite\src\Nite.Cli\bin\$(Configuration)\net10.0\Nite.Cli.dll</NiteCliPath>
</PropertyGroup>

<Import Project="..\nite\build\Nite.targets" />
```

If `NiteCliPath` points at a file that does not exist, the build fails with a message saying so.
