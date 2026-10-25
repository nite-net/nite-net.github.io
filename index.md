---
layout: landing
title: "nite: TypeScript and React for ASP.NET Core, no Node.js"
---

<div class="nite-hero">
  <img class="nite-logo" src="images/logo-transparent.png" alt="(n)ite">
  <h1>TypeScript and React for ASP.NET Core, with a Vite-style dev loop and no Node.js toolchain</h1>
  <p>Build the frontend and the backend in one project, one process, one <code>dotnet watch</code>. Components update in place with their state intact; C# changes re-fetch without a reload; <code>dotnet publish</code> ships hashed, code-split bundles.</p>
  <div class="nite-actions">
    <a class="nite-button primary" href="docs/getting-started.md">Get started</a>
    <a class="nite-button secondary" href="docs/introduction.md">Why nite?</a>
    <a class="nite-button secondary" href="https://github.com/nite-net/nite">GitHub</a>
  </div>
  <div class="nite-terminal">
    <div><span class="prompt">$ </span>nite init my-app</div>
    <div><span class="prompt">$ </span>cd my-app &amp;&amp; nite watch</div>
    <div class="comment"># edit Client/App.tsx: updated in ~150 ms, state kept</div>
    <div class="comment"># edit Program.cs: the page re-fetches, no reload</div>
    <div><span class="prompt">$ </span>dotnet publish -c Release</div>
  </div>
</div>

<div class="nite-section">
  <h2>One project. One process. No <code>node_modules</code> rituals.</h2>
  <p class="nite-sub">nite does in .NET what Vite does in Node: it compiles your client code on request, serves dependencies through an import map, and pushes hot updates over a WebSocket. esbuild does the compiling; nite does everything around it.</p>
  <div class="nite-grid">
    <div class="nite-card">
      <h3>React Fast Refresh</h3>
      <p>Edit a component and it updates in place in 100 to 200 ms, keeping its state. Helpers refresh the components that use them; the entry module reloads the page.</p>
      <a class="nite-more" href="docs/guides/hot-reload.md">Hot reload →</a>
    </div>
    <div class="nite-card">
      <h3>Full-stack hot reload</h3>
      <p><code>nite watch</code> runs <code>dotnet watch</code>. C# edits apply in the running app and raise a <code>nite:server-update</code> event, so the page re-fetches without losing state.</p>
      <a class="nite-more" href="docs/guides/hot-reload.md#c-changes">C# changes →</a>
    </div>
    <div class="nite-card">
      <h3>Single-page apps</h3>
      <p><code>Client/index.html</code> plus React, served by <code>app.MapNiteSpa()</code> next to your API. Same origin: no CORS, no dev proxy.</p>
      <a class="nite-more" href="docs/guides/single-page-apps.md">SPA guide →</a>
    </div>
    <div class="nite-card">
      <h3>Islands in Razor</h3>
      <p>Server-rendered pages with interactive React exactly where you need it: <code>&lt;island name="Chart" client="visible" /&gt;</code>.</p>
      <a class="nite-more" href="docs/guides/islands.md">Islands guide →</a>
    </div>
    <div class="nite-card">
      <h3>npm packages, from C#</h3>
      <p>A small npm client resolves semver, writes a lockfile and fills a normal <code>node_modules</code>. Private registries work from your <code>.npmrc</code>.</p>
      <a class="nite-more" href="docs/guides/packages.md">Packages →</a>
    </div>
    <div class="nite-card">
      <h3>Sass, Less, Tailwind, PostCSS</h3>
      <p>The same stylesheet pipeline as Vite, CSS modules included. Tailwind finds classes in your Razor views too. Mantine works out of the box.</p>
      <a class="nite-more" href="docs/guides/stylesheets.md">Stylesheets →</a>
    </div>
  </div>
</div>

<div class="nite-section">
  <h2>Looks like ASP.NET Core, because it is</h2>
  <p class="nite-sub">Three calls in <code>Program.cs</code>, and a <code>Client</code> folder next to it.</p>
  <div class="nite-split">
    <div>
      <h3>Program.cs</h3>

```csharp
using Nite;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddNite();

var app = builder.Build();
app.UseNite();   // dev server under /_nite

app.MapGet("/api/todos", () => Todos.All());

app.MapStaticAssets();
app.MapNiteSpa(); // index.html for client routes
app.Run();
```

</div>
<div>
      <h3>Client/App.tsx</h3>

```tsx
import { useEffect, useState } from "react";

export function App() {
  const [todos, setTodos] = useState([]);

  useEffect(() => {
    const load = async () =>
      setTodos(await (await fetch("/api/todos")).json());
    load();
    // C# hot reload: re-fetch, keep state
    addEventListener("nite:server-update", load);
  }, []);

  return <TodoList items={todos} />;
}
```

</div>
  </div>
</div>

<div class="nite-section">
  <h2>Already have a Vite app?</h2>
  <p class="nite-sub">Bring it across in one command. nite reads your lockfile (npm, Yarn, pnpm or Bun) and keeps the exact versions you run today.</p>
  <div class="nite-grid">
    <div class="nite-card">
      <h3>Import</h3>
      <p><code>nite init my-app --from ../vite-app</code> copies the client, keeps your dependencies and stylesheet tooling, and tells you what it could not bring along.</p>
      <a class="nite-more" href="docs/guides/importing.md">Importing projects →</a>
    </div>
    <div class="nite-card">
      <h3>Ship</h3>
      <p><code>dotnet publish</code> runs the production build: minified, code-split, content-hashed bundles in <code>wwwroot/_nite</code>, served precompressed by <code>MapStaticAssets</code>.</p>
      <a class="nite-more" href="docs/guides/deployment.md">Deployment →</a>
    </div>
    <div class="nite-card">
      <h3>Understand it</h3>
      <p>No magic: a long-lived esbuild service, an import map, a module graph and a WebSocket. Read how the pieces fit before you bet a project on it.</p>
      <a class="nite-more" href="docs/concepts/architecture.md">How nite works →</a>
    </div>
  </div>
</div>

<div class="nite-callout">
  <h3>Status</h3>
  <p>nite is young (version 0.2) and its packages are not on NuGet yet; for now you build it from source, which takes a minute. It is honest about what it does not do: read <a href="docs/limits.md">Limits and non-goals</a> before you start.</p>
</div>
