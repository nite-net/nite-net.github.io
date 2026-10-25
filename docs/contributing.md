---
title: Contributing
description: Build nite from source, run its tests, and contribute to nite or to this documentation.
---

# Contributing

<p class="lead">nite is developed on GitHub at <a href="https://github.com/nite-net/nite">nite-net/nite</a>. Bug reports, documentation fixes and pull requests are welcome.</p>

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

Pages are Markdown with [DocFX extensions](https://dotnet.github.io/docfx/docs/markdown.html) (alerts such as `> [!NOTE]`, tabs, cross-references to API types with `<xref:Nite.NiteOptions>`). The API reference is generated from the XML documentation comments in the nite source, so improving a `/// <summary>` improves the docs too.

## License

nite is licensed under the [Apache License 2.0](https://github.com/nite-net/nite/blob/main/LICENSE). By contributing, you agree that your contributions are licensed under it too.
