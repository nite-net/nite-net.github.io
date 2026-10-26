---
title: Privacy policy
description: NiteFx collects no personal information and has no telemetry. These are the only network connections it makes, and why.
---

# Privacy policy

<p class="lead">NiteFx does not collect, store or share any information about you, your projects or how you use it. It has no analytics or usage telemetry, and it never contacts the NiteFx project.</p>

This policy covers the NiteFx library, the `nite` command-line tool, the project templates and this documentation site.

## Network connections

NiteFx transfers data to other networked systems only when you ask it to, and only to do what you asked:

| When | Where | What is sent |
|---|---|---|
| Installing, adding or updating packages (`nite add`, `nite install`, `nite update`, and the dev server or `nite build` installing what `nite.json` lists) | The npm registry, `https://registry.npmjs.org/` unless you configure another registry or mirror | Requests for the packages you listed and their dependencies, with a `User-Agent` of `nite/<version>`. Credentials from your `.npmrc` go only to the registry they are configured for. See [Private registries](guides/private-registries.md). |
| The first compile or stylesheet build on a machine | The same registry | Requests for the esbuild (and, when you use Sass, Dart Sass) binaries for your platform. They are cached afterwards. |
| `nite update-self` | NuGet, through `dotnet tool update` | What the .NET SDK sends when updating a tool. |

Nothing else is sent anywhere. The registries you use have their own privacy policies, such as [npm's](https://docs.npmjs.com/policies/privacy).

## Telemetry in your app

NiteFx reports traces and metrics through .NET's standard `ActivitySource` and `Meter` ([Telemetry](guides/observability.md)). They stay inside your app: they are recorded only if you configure OpenTelemetry, and they go only where you send them.

## This website

This site is static HTML hosted on GitHub Pages. It uses no cookies, analytics or tracking scripts. GitHub, as the host, may log requests, such as your IP address, under the [GitHub Privacy Statement](https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement).

## Questions

Email tim.mcqueen@nitefx.dev or open an [issue](https://github.com/nite-net/nite/issues).
