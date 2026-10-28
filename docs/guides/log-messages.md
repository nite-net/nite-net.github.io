---
title: Log messages as Markdown
description: Write each log message as a Markdown file with Nite.Diagnostics; a source generator turns it into a fast, structured ILogger method, and the same file documents the message.
---

# Log messages as Markdown

<p class="lead"><code>Nite.Diagnostics</code> is a source generator for any .NET project that logs with <code>Microsoft.Extensions.Logging</code>. Each log message is a Markdown file: its front matter becomes an <code>ILogger</code> extension method, and its body is the message's documentation. It is a separate package from NiteFx, and has nothing to do with the frontend.</p>

NiteFx uses it for its own warnings: the [log message reference](../reference/diagnostics/index.md) is generated from the same files.

## Install

```bash
dotnet add package Nite.Diagnostics
```

It is a development dependency: it runs during the build and adds nothing to your app at run time.

## Write a message

Create `Diagnostics/AGENT007.md` in the project:

```markdown
---
code: AGENT007
eventId: 7007
level: Warning
message: Agent {AgentId} disconnected after {Seconds} seconds
parameters:
  AgentId: Guid
  Seconds: int
---
# Agent disconnected

The agent stopped sending heartbeats. Usually the host went to sleep or lost its network.

## What to check
...
```

And log it:

```csharp
logger.AgentDisconnected(agentId, 42);
// warn: MyApp.AgentMonitor[7007] Agent 6f1c… disconnected after 42 seconds
```

The generated methods are in a class named `Log` in the project's root namespace. The package imports that namespace in every file as a global using (the same mechanism as `ImplicitUsings`, and it works with them on or off), so the methods are found everywhere, top-level statements in `Program.cs` included. It does so only when the project has message files, since importing a namespace with no types in it would not compile. Already importing it yourself is harmless; set `NiteDiagnosticsGlobalUsing` to `false` to manage it yourself.

| Front matter | Required | |
|---|---|---|
| `code` | yes | The message's code: the event's name, and the name of its documentation page. Letters, digits, `.`, `-` and `_`. |
| `eventId` | yes | The event's number. |
| `level` | yes | `Trace`, `Debug`, `Information`, `Warning`, `Error` or `Critical`. |
| `message` | yes | A [message template](https://learn.microsoft.com/dotnet/core/extensions/logging#log-message-template): each `{Placeholder}` becomes a parameter, logged as a structured property. |
| `method` | no | The method's name. Without it, the `# Title` is used: "Agent disconnected" becomes `AgentDisconnected`. |
| `parameters` | no | The placeholders' types, indented under it. Without it they are `object?`; if you list any, list them all. |
| `exception` | no | `true` adds an `Exception?` parameter, first after the logger. |

Quote a `message` that contains `: ` or starts with a quote or a brace, as in YAML.

What the generated method does:

- It uses `LoggerMessage.Define`, so the template is parsed once, and nothing is formatted when the level is off. Messages with more than six placeholders use `ILogger.Log` instead.
- The event ID is `eventId` and its name is `code`, so log tools can filter on either.
- Its IntelliSense shows the code, title and message, and links to the message's page when `NiteDiagnosticsHelpUrl` is set.

## One meaning per code

Give each situation its own code and one level. If verbose logging should add detail, make the detail a separate `Debug` message with its own code, and turn it on with the usual logging configuration (`Logging__LogLevel__Default=Debug`, or a level per category). A code that changes level or text depending on configuration breaks the filters and alerts built on it.

## Settings

In the project file:

| Property | Default | |
|---|---|---|
| `NiteDiagnosticsDirectory` | `Diagnostics` | Where the Markdown files are, relative to the project. |
| `NiteDiagnosticsNamespace` | `$(RootNamespace)` | Namespace of the generated class. |
| `NiteDiagnosticsClass` | `Log` | Name of the generated class. |
| `NiteDiagnosticsPublic` | `false` | `true` makes the class public, for messages shared with other projects. |
| `NiteDiagnosticsGlobalUsing` | `true` | Import the class's namespace in every file. With `false`, add `using MyApp;` (or a `<Using>` item) yourself. |
| `NiteDiagnosticsHelpUrl` | none | A URL with `{code}` in it, such as `https://example.com/logs/{code}.html`, linked from each method's documentation. |

## Mistakes are build errors

Problems in a file are compiler errors at that file and line, so the IDE takes you there:

```text
Diagnostics/AGENT008.md(4,1): error NDIAG004: 'Loud' is not a valid level: use Trace, Debug, Information, Warning, Error, Critical
Diagnostics/AGENT008.md(5,1): error NDIAG007: The message uses {A} more than once: give each value its own name
```

| ID | |
|---|---|
| NDIAG001–NDIAG004 | Missing or malformed front matter, a missing required key, or a value that is not valid |
| NDIAG005, NDIAG006 | No `# Title` or `method:` to name the method, or a name that is not a C# identifier |
| NDIAG007–NDIAG009 | A placeholder used twice, a `parameters` entry that is not in the message, or a placeholder without a type |
| NDIAG010–NDIAG012 | Two files with the same code, event ID or method name |
| NDIAG013 | An unknown front matter key (a warning, for typos) |

A file with errors generates no method, so fix those first; a clash with another file shows up once the file itself is valid.

## Publish the documentation

Everything after the front matter is yours: the cause, what to check, how to fix it. The files are ordinary Markdown, so any documentation site can publish the folder as it is. This site turns NiteFx's into the [log message reference](../reference/diagnostics/index.md) with a short script that adds a table of the front matter to each page and writes an index; see `tools/diagnostics.py` in its [repository](https://github.com/nite-net/nite-net.github.io).
