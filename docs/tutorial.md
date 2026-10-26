---
title: "Tutorial: a full-stack app"
description: Build a small todo app with an ASP.NET Core API and a React frontend, and use every part of NiteFx's dev loop along the way.
---

# Tutorial: a full-stack app

<p class="lead">Build a todo app with a minimal API and a React frontend in one project. Along the way you will use Fast Refresh, C# hot reload that reaches the page, client-side routing, CSS modules, environment variables and a production publish.</p>

You need NiteFx installed ([Getting started](getting-started.md#install-nitefx)). The whole tutorial takes about half an hour.

## 1. Create the project

```bash
nite init todos
cd todos
nite watch
```

The browser opens on the template's page. Leave `nite watch` running for the rest of the tutorial; every step below is a save, not a restart.

## 2. Write the API

Replace `Program.cs` with an in-memory store and a few endpoints:

```csharp
using System.Collections.Concurrent;
using Nite;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddNite();
builder.Services.AddSingleton<TodoStore>();

var app = builder.Build();
app.UseNite();

var api = app.MapGroup("/api");
api.MapGet("/todos", (TodoStore store) => store.All());
api.MapPost("/todos", (NewTodo input, TodoStore store) =>
    string.IsNullOrWhiteSpace(input.Title)
        ? Results.ValidationProblem(new Dictionary<string, string[]> { ["title"] = ["A title is required."] })
        : Results.Created("/api/todos", store.Add(input.Title.Trim())));
api.MapPatch("/todos/{id:int}", (int id, TodoPatch patch, TodoStore store) =>
    store.SetDone(id, patch.Done) is { } todo ? Results.Ok(todo) : Results.NotFound());

app.MapStaticAssets();
app.MapNiteSpa();
app.Run();

record Todo(int Id, string Title, bool Done);
record NewTodo(string Title);
record TodoPatch(bool Done);

class TodoStore
{
    private readonly ConcurrentDictionary<int, Todo> _todos = new();
    private int _nextId;

    public TodoStore()
    {
        Add("Write the API in C#");
        Add("Write the UI in React");
    }

    public IReadOnlyList<Todo> All() => _todos.Values.OrderBy(t => t.Id).ToList();

    public Todo Add(string title)
    {
        var todo = new Todo(Interlocked.Increment(ref _nextId), title, false);
        _todos[todo.Id] = todo;
        return todo;
    }

    public Todo? SetDone(int id, bool done) =>
        _todos.TryGetValue(id, out var todo) ? _todos[id] = todo with { Done = done } : null;
}
```

New endpoints and a new service need a restart, so `nite watch` restarts the app. The page waits for the server to come back and reloads (about ten seconds). Check the API directly at `/api/todos`.

> [!NOTE]
> `app.MapNiteSpa()` serves `Client/index.html` for every path without a file extension, **except** paths under `/api`. A mistyped API URL gets a 404, not a page of HTML.

## 3. A typed API client

Create `Client/api.ts`:

```ts
// Same origin as the ASP.NET Core app: no CORS, no proxy, no base URL.
export type Todo = { id: number; title: string; done: boolean };

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) throw new Error(`${init?.method ?? "GET"} ${url}: ${response.status}`);
  return response.json() as Promise<T>;
}

export const api = {
  todos: () => request<Todo[]>("/api/todos"),
  add: (title: string) => request<Todo>("/api/todos", { method: "POST", body: JSON.stringify({ title }) }),
  setDone: (id: number, done: boolean) =>
    request<Todo>(`/api/todos/${id}`, { method: "PATCH", body: JSON.stringify({ done }) }),
};

/** Runs `callback` when C# hot reload changes the server. Returns the unsubscribe function. */
export function onServerUpdate(callback: () => void) {
  addEventListener("nite:server-update", callback);
  return () => removeEventListener("nite:server-update", callback);
}
```

Nothing reloads when you save this file: no module on the page imports it yet.

## 4. The todo list

Create `Client/TodoList.tsx`:

```tsx
import { useEffect, useState, type FormEvent } from "react";
import { api, onServerUpdate, type Todo } from "./api";

export function TodoList() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [draft, setDraft] = useState("");

  useEffect(() => {
    const load = () => api.todos().then(setTodos);
    load();
    return onServerUpdate(load);
  }, []);

  async function add(event: FormEvent) {
    event.preventDefault();
    if (!draft.trim()) return;
    const todo = await api.add(draft);
    setTodos((current) => [...current, todo]);
    setDraft("");
  }

  async function toggle(todo: Todo) {
    const updated = await api.setDone(todo.id, !todo.done);
    setTodos((current) => current.map((t) => (t.id === updated.id ? updated : t)));
  }

  return (
    <section>
      <h1>Todos</h1>
      <ul>
        {todos.map((todo) => (
          <li key={todo.id}>
            <label>
              <input type="checkbox" checked={todo.done} onChange={() => toggle(todo)} /> {todo.title}
            </label>
          </li>
        ))}
      </ul>
      <form onSubmit={add}>
        <input value={draft} onChange={(e) => setDraft(e.target.value)} placeholder="What needs doing?" />
        <button>Add</button>
      </form>
    </section>
  );
}
```

And render it from `Client/App.tsx`:

```tsx
import { TodoList } from "./TodoList";

export function App() {
  return (
    <main>
      <TodoList />
    </main>
  );
}
```

The page updates without a reload.

## 5. Feel Fast Refresh

Type something into the "What needs doing?" box, but do not submit it. Now edit `TodoList.tsx`: change `<h1>Todos</h1>` to `<h1>Things to do</h1>` and save.

The heading changes in about 150 ms, and your half-typed text is still there. NiteFx found that `TodoList.tsx` exports only components, re-imported just that module, and let React swap the new function in while keeping its state. Edits to `api.ts` work too: NiteFx walks up from the changed module to the components that import it and refreshes those.

What resets state, and why:

- **Adding or removing a hook** in a component remounts that component (its hook list changed, so old state cannot map onto it).
- **Editing `main.tsx`** reloads the page: the entry module has no component boundary above it.

## 6. C# changes reach the page

Change the seed data in `TodoStore`'s constructor, or the validation message, and save `Program.cs`. Hot reload applies the change in the running app and NiteFx sends the page a `nite:server-update` event; `TodoList` re-fetches through `onServerUpdate`, and the list updates with nothing reloaded.

> [!TIP]
> The event never fires in production, so `onServerUpdate` costs nothing there. Use it in any component that shows server data.

## 7. Routing

Add React Router:

```bash
nite add react-router
```

The running dev server notices `nite.json` changed, pre-bundles the package and reloads the page. Wrap the app in a router in `Client/main.tsx`:

```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router";
import { App } from "./App";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
);
```

Add an about page and routes in `Client/App.tsx`:

```tsx
import { NavLink, Route, Routes } from "react-router";
import { TodoList } from "./TodoList";

function About() {
  return <p>A todo app with an ASP.NET Core API and a React frontend, built with nite.</p>;
}

export function App() {
  return (
    <>
      <nav>
        <NavLink to="/" end>Todos</NavLink> · <NavLink to="/about">About</NavLink>
      </nav>
      <main>
        <Routes>
          <Route path="/" element={<TodoList />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>
    </>
  );
}
```

Open `/about` directly in a new tab: `MapNiteSpa` serves `index.html` for it, and the router takes over.

## 8. Scoped styles with a CSS module

Create `Client/TodoList.module.css`:

```css
.list {
  list-style: none;
  padding: 0;
}

.done {
  color: gray;
  text-decoration: line-through;
}
```

Use it in `TodoList.tsx`:

```tsx
import styles from "./TodoList.module.css";

// ...
<ul className={styles.list}>
  {todos.map((todo) => (
    <li key={todo.id} className={todo.done ? styles.done : undefined}>
```

Class names are scoped to the file, so `.done` here never collides with a `.done` anywhere else. Edit the CSS and save: the components using it refresh in place. Plain `.css` files, Sass, Less, Tailwind and PostCSS work the same way; see [Stylesheets](guides/stylesheets.md).

## 9. Configuration from the environment

Create `.env` in the project folder (next to `nite.json`):

```ini
NITE_PUBLIC_APP_NAME=Todos
DATABASE_PASSWORD=never-reaches-the-browser
```

Use it in `TodoList.tsx`:

```tsx
<h1>{import.meta.env.NITE_PUBLIC_APP_NAME}</h1>
```

Only variables starting with `NITE_PUBLIC_` reach client code; the password stays on the server. Editing `.env` reloads the page with the new values. See [Environment variables](guides/environment.md).

## 10. Publish

Stop `nite watch` (Ctrl+C) and publish:

```bash
dotnet publish -c Release -o publish
cd publish
dotnet todos.dll
```

The Release build ran `nite build`: `publish/wwwroot/_nite` holds the minified, content-hashed bundles (with `.br` and `.gz` copies) and `index.html` pointing at them. `MapNiteSpa` serves that built page, and `MapStaticAssets` serves the bundles, compressed with Brotli for browsers that accept it. The published app has no `node_modules`, no esbuild and no dev server.

## What you used

| Step | Feature | Read more |
|---|---|---|
| 2 | A restart for a structural C# change, handled by `nite watch` | [Hot reload](guides/hot-reload.md) |
| 4, 5 | Fast Refresh and the module graph | [How NiteFx works](concepts/architecture.md) |
| 6 | `nite:server-update` | [Browser runtime](reference/browser-runtime.md) |
| 7 | `nite add`, `MapNiteSpa` fallback routing | [Packages](guides/packages.md), [Single-page apps](guides/single-page-apps.md) |
| 8 | CSS modules | [Stylesheets](guides/stylesheets.md) |
| 9 | `.env` and `envPrefix` | [Environment variables](guides/environment.md) |
| 10 | `nite build` and `MapStaticAssets` | [Deployment](guides/deployment.md) |
