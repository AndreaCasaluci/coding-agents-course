# Field guide: concepts → real tools

The lessons teach the mechanism. This page maps each mechanism onto concrete
configuration in tools you may already use, so you can apply the course at work
without re-deriving it.

**Primary target: Claude Code** (v2.1.x). **Second: OpenCode V2**, because this
course's own agent runs on it. Both move fast: every claim here was checked
against the vendor docs on **2026-11-02**. When a version number appears, it is
a real minimum, not decoration.

> Rule for this page: if the vendor docs and this page disagree, the vendor docs
> win. The *concepts* are stable; the *field names* are not.

## The translation table

| Concept | This course (`mini_agent`) | Claude Code | OpenCode V2 |
|---|---|---|---|
| Instructions | `instructions.discover` → `AGENTS.md` | `CLAUDE.md` (or `AGENTS.md`) + `.claude/rules/` | `AGENTS.md` + `instructions[]` |
| Skill | `SkillLibrary` + `SKILL.md` | `.claude/skills/<id>/SKILL.md` | `.opencode/skills/<id>/SKILL.md` |
| Tool | `@tool` + `ToolRegistry` | built-in tools, MCP tools, plugin tools | built-in tools, MCP tools, plugin tools |
| Hook | `HookBus` on `pre_tool` / `post_tool` / … | `hooks` in `settings.json` (shell/HTTP/MCP/prompt/agent) | permissions + TypeScript plugin hooks |
| Subagent | `run_subagent` / `Agent.fork` | `.claude/agents/<name>.md` | `agents` with `mode: "subagent"` |
| MCP | `mcp_lite.py` | `claude mcp add`, `.mcp.json` | `mcp.servers` |
| Permissions | `read_only`, path jail, guard hooks | `permissions.allow/deny/ask` + modes + sandbox | `permissions[]` + `policies` |
| Evals | `run_evals` | `claude -p` in CI | `opencode run` in CI |

## 1. Instructions

### Claude Code

```markdown
<!-- ./CLAUDE.md -->
# Project instructions

## Commands
- Test: `python3 run.py test`
- Lint: `python3 run.py lint`

## Invariants
- Never push to `main`. Branch first.
- Do not edit generated files.

## Traps
- `make` is not installed here; use `run.py`.
```

Where it lives, broadest to narrowest:

```
/etc/claude-code/CLAUDE.md        managed policy (org)
~/.claude/CLAUDE.md               you, all projects
./CLAUDE.md or ./.claude/CLAUDE.md  project, committed
./CLAUDE.local.md                 you, this project (gitignored)
```

Subdirectory `CLAUDE.md` files load on demand when Claude touches a file there.
For path-scoped rules without a whole file per directory, use
`.claude/rules/*.md` with `paths:` frontmatter:

```markdown
---
paths:
  - "src/api/**/*.ts"
---
- Every handler validates its input.
```

**The `AGENTS.md` gotcha.** Claude Code reads `AGENTS.md` directly since
**v2.1.277**, but only when there is **no** `CLAUDE.md`/`CLAUDE.local.md` in the
working directory or above it. If you add a `CLAUDE.md`, `AGENTS.md` stops
loading unless you either import it:

```markdown
<!-- CLAUDE.md -->
@AGENTS.md

## Claude Code-specific
Use plan mode for changes under `src/billing/`.
```

or set **Project instructions** to `claude-md-and-agents-md` in `/config`.

This repo has `AGENTS.md` and no `CLAUDE.md`, so a current Claude Code reads it
as-is. That is the happy path; the gotcha appears the day someone adds a
`CLAUDE.md`.

Also useful: `@path/to/file` imports (max depth 4), and `<!-- comments -->` are
stripped before the content reaches the model.

### OpenCode V2

OpenCode loads `AGENTS.md` and lets you add more files:

```jsonc
// opencode.jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": ["CONTRIBUTING.md", "docs/guidelines/*.md"]
}
```

Same rule as the course: commands that are not guessable, invariants that are
not obvious, traps that cost time. Nothing else.

## 2. Skills

Both tools converged on the same [Agent Skills](https://agentskills.io) shape:
a folder with `SKILL.md`, YAML frontmatter, and optional resources.

```markdown
<!-- .claude/skills/release-notes/SKILL.md  (or .opencode/skills/release-notes/SKILL.md) -->
---
name: release-notes
description: Write release notes from git history. Use when asked to prepare a release, changelog, or "what changed since vX".
---

1. Get the range: `git log --oneline <last-tag>..HEAD`.
2. Group: features, fixes, breaking changes, chores.
3. Follow `template.md`. Bullets under 100 characters.
```

| | Claude Code | OpenCode V2 |
|---|---|---|
| Project path | `.claude/skills/<id>/SKILL.md` | `.opencode/skills/<id>/SKILL.md` |
| Personal path | `~/.claude/skills/` | `~/.config/opencode/skills/` |
| Compatibility | reads `.claude/skills` | reads `.claude/skills`, `.agents/skills` |
| Invoke manually | `/release-notes` | `@release-notes` (or the `skill` tool) |
| Model-invoked | yes, by `description` | yes, by `description` |
| Disable auto-invoke | `disable-model-invocation: true` | `metadata.opencode/autoinvoke: false` |
| Pre-approve tools | `allowed-tools: Read, Grep` | via `permissions` on action `skill` |
| Run in a subagent | `context: fork` | define a subagent and have it load the skill |

Claude Code extras worth knowing: `paths:` scopes a skill to file globs;
`when_to_use:` adds trigger phrases; `.claude/commands/*.md` still works and is
now merged into the same mechanism.

OpenCode extras: skill IDs are **path-derived and case-sensitive** — the folder
name is the ID, not the frontmatter `name`. `git-release/SKILL.md` is
`git-release` even if `name: Git Release`.

**What carries over from lesson 07:** the description is the trigger. In both
tools, a vague description means the skill never loads and a keyword-soup
description means it loads constantly. Test it by asking a neighbouring task and
checking it does *not* load.

## 3. Tools

Neither tool lets you write a Python function and register it as a tool the way
`@tool` does in this course. The equivalents are:

| Need | Claude Code | OpenCode V2 |
|---|---|---|
| Read / search / edit files | built-in tools | built-in tools |
| Run commands | `Bash` / `PowerShell` | shell tool |
| External system | MCP server | MCP server |
| Custom logic | plugin / skill script | TypeScript plugin |

The lesson still applies verbatim: **the description is prompt text**. For MCP
tools, that text comes from the server, which is exactly the trust problem in
module 10. Claude Code names MCP tools `mcp__<server>__<tool>`, which is also how
you write permission rules and hook matchers.

If you need a tool with side effects, prefer a **skill script** over a new
server: it is versioned with the repo, needs no protocol, and is reviewable like
any other code.

## 4. Hooks

This is where the two tools diverge most.

### Claude Code: JSON config + shell commands

Hooks live in `settings.json` and are external processes. Input arrives as JSON
on stdin; output is a JSON decision or an exit code.

Block a push (the course's `pre_tool` + `deny`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-push.sh"
          }
        ]
      }
    ]
  }
}
```

```bash
#!/usr/bin/env bash
# .claude/hooks/block-push.sh
cmd=$(jq -r '.tool_input.command')

if [[ "$cmd" == *"git push"* ]]; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "push requires a human"
    }
  }'
fi
# exit 0 with no output = no decision; the normal permission flow continues
```

Events worth mapping to the course:

| Course event | Claude Code | Can block? |
|---|---|---|
| `session_start` | `SessionStart` | no |
| `user_prompt` | `UserPromptSubmit` | yes |
| `pre_tool` | `PreToolUse` | **yes** |
| `post_tool` | `PostToolUse` / `PostToolUseFailure` | no (can add context) |
| `pre_edit` | `PreToolUse` with matcher `Edit\|Write` | **yes** |
| `post_edit` | `PostToolUse` with matcher `Edit\|Write` | no |
| `session_end` | `SessionEnd` | no |
| compaction | `PreCompact` / `PostCompact` | `PreCompact` yes |

Handlers can be `command`, `http`, `mcp_tool`, `prompt`, or `agent`. Prefer
`command` for deterministic guards, `prompt`/`agent` only for judgement calls.

Two properties from lesson 08 hold exactly: **first denial wins**, and a hook
that must never fail open needs `onFailure: "block"` (Claude Code v2.1.295+) or
your script must fail closed itself. A plain `exit 0` abstains, which is not the
same as approving.

### OpenCode V2: permissions for rules, plugins for code

There is no JSON shell-command hook. Split the job:

**Guardrails → `permissions`** (ordered rules, last match wins):

```jsonc
// opencode.jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "permissions": [
    { "action": "shell", "resource": "*", "effect": "ask" },
    { "action": "shell", "resource": "git status *", "effect": "allow" },
    { "action": "shell", "resource": "git diff *", "effect": "allow" },
    { "action": "shell", "resource": "git push *", "effect": "deny" },
    { "action": "read", "resource": "*.env", "effect": "deny" },
    { "action": "edit", "resource": "src/**", "effect": "allow" }
  ]
}
```

**Observation and mutation → a plugin** (TypeScript, in-process):

```ts
// .opencode/plugins/audit/index.ts
import { Plugin } from "@opencode/plugin"

export default Plugin.define({
  id: "audit",
  async setup(ctx) {
    const controller = new AbortController()

    void (async () => {
      for await (const event of ctx.event.subscribe({ signal: controller.signal })) {
        console.log(event.type)
      }
    })()

    await ctx.session.hook("context", (event) => {
      event.system.push({ type: "text", text: "Review for correctness, security, missing tests." })
    })

    return () => controller.abort()
  },
})
```

The closest analogues:

| Course hook | OpenCode V2 |
|---|---|
| observe every tool call | `ctx.event.subscribe(...)` |
| add context before the model call | `ctx.session.hook("context", ...)` |
| rewrite the user prompt | `ctx.session.hook("prompt", ...)` |
| custom compaction | `ctx.session.hook("compaction", ...)` |
| block an action | `permissions` (or `ctx.permission.assert` in a custom tool) |
| add a tool | `ctx.tool.transform(...)` |

**Design consequence:** in Claude Code a guard is a script in JSON; in OpenCode
it is a permission rule or a plugin you maintain. Both are outside the model,
which is the property that matters.

## 5. Subagents

### Claude Code

```markdown
<!-- .claude/agents/reviewer.md -->
---
name: reviewer
description: Reviews diffs for correctness, security, and missing tests. Use after code changes.
tools: Read, Grep, Glob
model: sonnet
---

You are a senior reviewer. Cite file:line for every finding. Do not edit files.
```

Built-ins already exist: **Explore** (read-only search), **Plan** (research for
plan mode), **general-purpose**. `isolation: worktree` gives the subagent its own
checkout — the worktree pattern from lesson 09, built in. `maxTurns` bounds it.

The description is what triggers delegation, so keep it short: Claude Code warns
when combined subagent descriptions exceed 15,000 tokens.

### OpenCode V2

```jsonc
// opencode.jsonc
{
  "agents": {
    "reviewer": {
      "description": "Reviews diffs for correctness and missing tests",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-5-5",
      "permissions": [
        { "action": "edit", "resource": "*", "effect": "deny" }
      ]
    }
  }
}
```

Or a file under `.opencode/agents/` with frontmatter. Note the difference from
lesson 09: here the subagent's permissions are its own, not a subset inherited
from the parent, so a read-only reviewer must say so explicitly.

## 6. MCP

### Claude Code

```bash
# remote HTTP server, shared with the project
claude mcp add --transport http notion https://mcp.notion.com/mcp --scope project

# local stdio server; everything after -- goes to the server
claude mcp add --scope project --env API_KEY=... my-server -- npx -y my-mcp-server
```

`--scope project` writes `.mcp.json`; `local` (default) and `user` write to
`~/.claude.json`. Project servers need approval the first time you open the repo,
which is the right default: a cloned repo must not be able to approve its own
servers.

### OpenCode V2

```jsonc
// opencode.jsonc
{
  "mcp": {
    "servers": {
      "playwright": {
        "type": "local",
        "command": ["bunx", "@playwright/mcp"]
      },
      "docs": {
        "type": "remote",
        "url": "https://mcp.example.com"
      }
    }
  }
}
```

or `opencode mcp add <name> --global --url <url>`.

**Both:** a server is a program you are handing your agent. Review tool
descriptions, not just tool names — lesson 10's poisoning attack is a description
that tells the model to read `~/.ssh`.

## 7. Permissions and sandbox

### Claude Code

Rules are evaluated **deny → ask → allow**, first match wins:

```json
{
  "permissions": {
    "allow": ["Bash(python3 run.py *)", "Bash(git status *)"],
    "ask":   ["Bash(git push *)"],
    "deny":  ["Read(./.env)", "Read(./secrets/**)", "Bash(rm -rf *)"]
  }
}
```

Modes: `default` (manual), `acceptEdits`, `plan`, `auto`, `dontAsk`,
`bypassPermissions`. `plan` is the mechanical version of the course's "plan
before editing". For OS-level enforcement there is a separate sandbox with
filesystem and network isolation — the container layer from module 12.

Limits worth knowing: Bash rules match command text, so `/bin/rm` or
`sh -c 'rm …'` can slip past `Bash(rm *)`. Deny rules are a guard, not a security
boundary; the sandbox is the boundary.

### OpenCode V2

```jsonc
{
  "permissions": [
    { "action": "*", "resource": "*", "effect": "allow" },
    { "action": "read", "resource": "*.env", "effect": "ask" },
    { "action": "edit", "resource": "src/**", "effect": "allow" },
    { "action": "external_directory", "resource": "*", "effect": "ask" },
    { "action": "shell", "resource": "git push *", "effect": "deny" }
  ],
  "policies": [
    { "action": "tool.use", "resource": "shell:sudo *", "effect": "deny" }
  ]
}
```

Unlike Claude Code, **last match wins**, and the default is `ask` when nothing
matches. `policies` are a hard deny that project config cannot override — the
managed-policy layer.

## 8. Evals and CI

Both tools run headless:

```bash
# Claude Code
claude -p "run the tests and fix only test-file issues" --output-format json

# OpenCode
opencode run "run the tests and fix only test-file issues"
```

The course's eval rules map directly:

- fresh checkout per case (CI gives you this for free),
- grade the workspace (`git diff`, test exit code), not the transcript,
- pin the model and the prompt,
- cap turns and budget,
- include a refusal case and a no-op case.

Neither tool ships a grader, so the eval harness stays yours — which is the
point of module 11.

## The same policy, three ways

"Never push, never read `.env`, format after edits."

| Layer | This course | Claude Code | OpenCode V2 |
|---|---|---|---|
| Instruction | `AGENTS.md` | `CLAUDE.md` | `AGENTS.md` |
| Enforcement | `PRE_EDIT` hook + path jail | `permissions.deny` + `PreToolUse` hook | `permissions` |
| Side effect | `POST_EDIT` hook | `PostToolUse` hook on `Edit\|Write` | `permissions` + formatter config |
| Observation | `audit_log` | `PostToolUse` logging hook | `ctx.event.subscribe` |

The progression is identical: **say it → enforce it → observe it**. Only the
syntax changes.

## Gotchas that bite in practice

1. **`AGENTS.md` vs `CLAUDE.md` precedence.** Adding a `CLAUDE.md` silently
   disables `AGENTS.md` unless you import it or change the setting.
2. **Deny is not a sandbox.** Command-text matching has bypasses in every tool.
   Use OS isolation when the blast radius matters.
3. **Hooks run with your shell's authority.** A hook that reads its input with
   `eval` reintroduces the injection you were trying to stop.
4. **Skill IDs are path-derived in OpenCode**, frontmatter `name` is display
   only. Renaming the folder changes how you invoke it.
5. **Subagent descriptions cost context.** They are loaded so the parent knows
   when to delegate; dozens of verbose descriptions are a real tax.
6. **MCP tool descriptions are untrusted prompt text.** Review servers like
   dependencies.
7. **Project-scoped config needs approval.** `.mcp.json` and project hooks are
   gated on workspace trust for a reason; do not bake approval into the repo.

## Sources

- Claude Code: <https://code.claude.com/docs/en/memory>, `/skills`, `/hooks`,
  `/sub-agents`, `/mcp`, `/permissions`, `/sandboxing`
- OpenCode V2: <https://opencode.ai/v2/docs/config>, `/skills`, `/permissions`,
  `/build/plugins`, `/build/plugins/server`
- Agent Skills standard: <https://agentskills.io>

If you use another tool (Cursor, Copilot, Codex), the mapping is the same shape
but the field names differ; verify each one against its current docs before
committing config to a team repo.
