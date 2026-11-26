---
title: Testing
description: Run client tests with Vitest through nite test, configured from nite.json.
---

# Testing

<p class="lead"><code>nite test</code> runs your client's tests with <a href="https://vitest.dev">Vitest</a>, the runner most React projects use. NiteFx writes the Vitest configuration from <code>nite.json</code>, so path aliases, environment variables and <code>nite:config</code> work in tests the way they do in the app.</p>

Vitest is a Node.js program, so **running tests needs Node.js**: 20.19 or later, or 22.12 or later, whatever the installed Vite asks for. Building and running a NiteFx app never needs Node.

## Getting started

```bash
nite add -D vitest jsdom @testing-library/react
nite test
```

Put tests next to the code they test, named `*.test.ts(x)` or `*.spec.ts(x)`, anywhere under the client root:

```tsx
// Client/src/Counter.test.tsx
import { expect, test } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Counter } from "./Counter";

test("counts clicks", () => {
  render(<Counter />);
  fireEvent.click(screen.getByRole("button"));
  expect(screen.getByRole("button").textContent).toBe("Clicked 1 time");
});
```

```bash
nite test                 # run once, as in CI
nite test Counter         # only test files whose path contains "Counter"
nite test --watch         # re-run as files change
nite test --ui            # the Vitest UI, also at /_nite/vitest/ in your app
nite test --coverage      # collect coverage for this run
nite test -- --reporter verbose   # anything after -- goes to Vitest
```

`nite test` installs packages first, as `nite build` does, so it works straight after a clone.

## What carries over from nite.json

Vitest compiles tests with Vite's compiler, not NiteFx's. The configuration NiteFx generates (`.nite/vitest.config.mjs`, rewritten on every run) carries over the settings that change how code resolves and compiles, so tests see what the app sees:

| In the app | In tests |
|---|---|
| Path aliases from the client tsconfig's `paths` | `resolve.alias` |
| `import.meta.env.NITE_PUBLIC_*` (and `process.env.*`) | The same values, from `.env`, `.env.test` and the environment, in `test` mode |
| `import { config } from "nite:config"` | The values in `test.config` in `nite.json` (the server is not running) |
| `jsxImportSource` (Preact and others) | Vite's JSX import source |
| `jsxInJs` (Create React App) | JSX in `.js` files compiles, as in the app |
| The client root | Vitest's `root` |

Vite reads the tsconfig itself, so `experimentalDecorators` and similar options apply as in the app. A tsconfig `baseUrl` on its own (bare imports from the client root) is not carried over; use `paths`.

## Settings

```jsonc
{
  "test": {
    "environment": "jsdom",          // default: jsdom or happy-dom when installed, else node
    "globals": false,                // describe, it, expect and vi without imports, as in Jest
    "setupFiles": ["src/setupTests.ts"],
    "include": [],                   // test file globs; Vitest's default when empty
    "coverage": null,                // "v8" or "istanbul" to collect coverage on every run
    "config": { "apiBase": "/api" }  // what nite:config gives code under test
  }
}
```

Paths are relative to the client root. See [nite.json](../reference/nite-json.md#test).

### Your own Vitest configuration

For anything else, add a `vitest.config.ts` next to `nite.json` (or in the client root). The generated configuration merges it over its own, so your settings win:

```ts
// vitest.config.ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: { testTimeout: 10_000 },
});
```

## Coming from Jest

Vitest runs most Jest tests as they are once `globals` is on: `describe`, `it`, `expect`, `beforeEach` and Testing Library's matchers work the same. `nite import` sets this up for you (see [Tests](importing.md#what-it-does) in the import guide); by hand, it is:

```json
{
  "test": {
    "environment": "jsdom",
    "globals": true,
    "setupFiles": ["src/setupTests.ts"]
  }
}
```

plus `nite add -D vitest jsdom`. The differences that need edits:

- `jest.fn()`, `jest.spyOn()` and the fake timers are `vi.fn()`, `vi.spyOn()` and `vi.useFakeTimers()`. A setup file containing `globalThis.jest = vi;` keeps the old name working.
- `jest.mock(...)` must become `vi.mock(...)`. Vitest moves `vi.mock` calls above the imports, as Jest does for `jest.mock`, but it does not know the `jest` name, so a `jest.mock` would run after the module was already imported.
- `moduleNameMapper` entries become tsconfig `paths` (which NiteFx carries over) or `resolve.alias` in a `vitest.config.ts`. CSS and image mocks are not needed: Vite imports those files itself.
- Snapshots are rewritten in Vitest's format on the first run.

## The Vitest UI in your app

`nite test --ui` starts the Vitest UI (add it first with `nite add -D @vitest/ui` at Vitest's version). While it runs, the app's dev server shows the same UI at `/_nite/vitest/`, so it sits next to the app on the app's own address:

1. Start the app (`nite watch` or `dotnet run`) and, in another terminal, `nite test --ui`.
2. Vitest prints a link such as `http://127.0.0.1:51735/_nite/vitest/?token=…`. Open it as printed, or swap in the app's address: `https://localhost:5001/_nite/vitest/?token=…`. The browser keeps the token in a cookie for that path, so later visits need only `/_nite/vitest/`.

The UI can edit test files and run code, so NiteFx adds nothing to Vitest's own guard and takes nothing away: requests pass through with their token and cookie as they are, and the dev server never learns the token. On top of that it answers only requests from the local machine and from pages of the app itself, and only in Development. Vitest's UI starts with `nite test`, not with the app, so restarting the app (as `dotnet watch` does after a C# change) leaves it running.

When `nite test --ui` is not running, `/_nite/vitest/` says so.

## Coverage

```bash
nite add -D @vitest/coverage-v8    # at the same version as vitest
nite test --coverage
```

Or set `"coverage": "v8"` (or `"istanbul"`) in `test` to collect it on every run. Reports go to `.nite/coverage`: a summary in the terminal and an HTML report in `.nite/coverage/index.html`, which the app also serves at `/_nite/coverage/` in development. If the provider package is missing, `nite test` says which one to add.

## In CI

Install Node next to .NET and run `nite test`; it exits with Vitest's exit code. For GitHub Actions:

```yaml
- uses: actions/setup-dotnet@v4
  with: { dotnet-version: 10.0.x }
- uses: actions/setup-node@v4
  with: { node-version: 22 }
- run: dotnet tool install --global Nite.Cli
- run: nite test
```

## Which Node

`nite test` uses `node` from `PATH`, or the executable `NITE_NODE_PATH` names. It checks the version against what the installed Vite supports before starting, and says which version it needs.
