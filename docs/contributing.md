---
title: Contributing
description: Build Nite from source, run its tests, and contribute to Nite or to this documentation.
---

# Contributing

<p class="lead">Nite is developed on GitHub at <a href="https://github.com/nite-net/nite">nite-net/nite</a>. Bug reports, documentation fixes and pull requests are welcome.</p>

## Building from source

You need the .NET 10 SDK. No other tools.

```bash
git clone https://github.com/nite-net/nite
cd nite
dotnet build
```

The repository:

```text
src/Nite/            the library: dev server, esbuild client, npm client, CSS pipeline, build, tag helpers
src/Nite.Cli/        the `nite` command-line tool
src/Nite.Templates/  the dotnet new templates, which `nite init` also writes
build/Nite.targets   MSBuild integration, packed into the Nite package
samples/Nite.Spa     a React SPA with a minimal API
samples/Nite.Sample  Razor Pages with React islands
tests/Nite.Tests     unit and integration tests
```

Run the CLI from source with `dotnet run --project src/Nite.Cli -- <command>`, and point a test project at your checkout with `nite init my-app --nite-source <path-to-nite>` (see [Getting started](getting-started.md#install-nite)).

## Tests

```bash
dotnet test                                          # everything; integration tests need network
dotnet test --filter "Category!=Integration"         # offline
```

Integration tests run a real esbuild process and install real packages (PostCSS, Less, Sass, Tailwind) from npm into temporary folders. They download once per machine and use the cache afterwards.

## Templates

The project templates are ordinary files in `src/Nite.Templates/content/spa` and `content/islands`. `dotnet new` reads them through each folder's `.template.config/template.json`; the CLI embeds the same files and fills the placeholders itself for `nite init`. The placeholders are `NiteApp` (the project file name), `NITE_TITLE`, `NITE_NAMESPACE`, `NITE_PORT` and `NITE_VERSION`. `TemplateTests` fails if a file uses a placeholder that template.json has no symbol for, if the CLI is missing one of the folder's files, or if `nite init` would leave a placeholder unfilled.

To try the template pack locally:

```bash
dotnet pack src/Nite.Templates -o /tmp/nite-templates
dotnet new install /tmp/nite-templates/Nite.Templates.<version>.nupkg
dotnet new nite-spa -o /tmp/try-it
```

## Continuous integration and releases

[`.github/workflows/ci.yml`](https://github.com/nite-net/nite/blob/main/.github/workflows/ci.yml) builds and tests every push and pull request, including the integration tests, and packs `Nite`, `Nite.Cli` and `Nite.Templates`. CI packages are prereleases of the next patch after the newest release tag (`0.6.1-ci.<run number>` after `v0.6.0`) and are kept as the run's `packages` artifact, so you can try a pull request's build without packing it yourself.

The release tag is the version; nothing in the repository holds it. (`Directory.Build.props` says `0.0.0-dev`, which only local builds use. `nite init` from a local build needs `--nite-source`, since no package of that version exists.) To release:

1. Move the changelog's "Unreleased" section under the new version's heading.
2. Push the tag: `git tag v0.6.0 && git push origin v0.6.0`. Prereleases work too: `v0.6.0-beta.1`.

The tag's build packs that version and pushes the three packages to nuget.org with [trusted publishing](https://learn.microsoft.com/nuget/nuget-org/trusted-publishing): the job trades a GitHub OIDC token for an API key that lasts an hour, so no long-lived key is stored anywhere. It runs in the `nuget` environment, where you can require an approval before publishing.

Publishing needs two things set up once:

- A trusted publishing policy on nuget.org (**Account settings > Trusted Publishing**), created by the account that owns the `Nite`, `Nite.Cli` and `Nite.Templates` packages: repository owner `nite-net`, repository `nite`, workflow file `ci.yml`, environment `nuget`.
- A `NUGET_USER` secret in the Nite repository holding that account's nuget.org profile name (not its email address).

Re-running a release that half-failed is safe: packages already on nuget.org are skipped. A tag that is not a version (`v1`, `vnext`) fails the build before anything is packed.

## Pull requests

- Keep changes focused, and include tests for behavior changes.
- Match the style of the surrounding code: comments explain why, not what.
- For a new feature, an issue first is a good idea, so the design can be agreed before the code.
- Update the [README](https://github.com/nite-net/nite/blob/main/README.md) and this documentation when behavior changes.

## This documentation

The site is built with [DocFX](https://dotnet.github.io/docfx/) from [nite-net/nite-net.github.io](https://github.com/nite-net/nite-net.github.io). Every page has an "Edit this page" link. To preview locally:

```bash
git clone https://github.com/nite-net/nite-net.github.io
cd nite-net.github.io
./build.sh serve           # builds the API reference from a nite checkout, then serves the site
```

Pages are Markdown with [DocFX extensions](https://dotnet.github.io/docfx/docs/markdown.html) (alerts such as `> [!NOTE]`, tabs, cross-references to API types with `<xref:Nite.NiteOptions>`). The API reference is generated from the XML documentation comments in the Nite source, so improving a `/// <summary>` improves the docs too.

## License

Nite is licensed under the [Apache License 2.0](https://github.com/nite-net/nite/blob/main/LICENSE). By contributing, you agree that your contributions are licensed under it too.
