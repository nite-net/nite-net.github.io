---
title: Code signing policy
description: How Nite's release binaries are signed, who can change the code, and who approves each signing.
---

# Code signing policy

Free code signing provided by [SignPath.io](https://about.signpath.io), certificate by [SignPath Foundation](https://signpath.org).

## What is signed

Only binaries built from the [nite-net/nite](https://github.com/nite-net/nite) repository by its release workflow on GitHub Actions, from a tagged commit, are signed. Nothing built on a developer's machine is. The build scripts and workflow are part of the repository and are reviewed like the rest of its source.

Third-party components that Nite downloads when it runs (the esbuild and Dart Sass binaries, and npm packages) are not part of Nite's packages and are not signed by this project. Their authors publish them.

## Team roles

| Role | Members |
|---|---|
| Owner | [Tim McQueen](https://github.com/tmcqueen) (tim.mcqueen@nicefx.dev) |
| Committers and reviewers | [Tim McQueen](https://github.com/tmcqueen) (tim.mcqueen@nicefx.dev) |
| Approvers | [Tim McQueen](https://github.com/tmcqueen) (tim.mcqueen@nicefx.dev) |

- **Committers** may change the source code without further review.
- **Reviewers** review every change proposed by someone who is not a committer, such as a pull request from a contributor, before it is merged.
- **Approvers** approve each signing request by hand. Every release is approved individually.

All team members use multi-factor authentication for GitHub and SignPath.

## Privacy

See the [privacy policy](privacy.md). In short: Nite collects no information, and it transfers data to other networked systems only when you ask it to.

## Reporting a problem

If you believe a signed Nite binary is malicious or was not built from this project's source, open an [issue](https://github.com/nite-net/nite/issues) or email tim.mcqueen@nicefx.dev.
