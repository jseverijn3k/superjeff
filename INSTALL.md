# Installing SuperJeff

SuperJeff is a toolbox for your Django projects — it is not copied into your project. You add it once and it works across all your Django projects.

---

## How Claude Code Picks Up SuperJeff

Claude Code reads three locations automatically:

| Location | What gets loaded |
| --- | --- |
| `<project>/.claude/commands/` | Slash commands available in that project |
| `<project>/.claude/settings.local.json` | Hooks that run in that project |
| `<project>/CLAUDE.md` | Rules, instincts, and agent references loaded every session |

SuperJeff's job is to populate these three locations — either globally (once, for all projects) or per-project.

---

## Option A — Global Install (recommended)

Install once. Works in every Django project you open in Claude Code.

### Step 1 — Clone SuperJeff

```bash
git clone https://github.com/yourname/superjeff ~/superjeff
```

### Step 2 — Install commands globally

Claude Code picks up commands from `~/.claude/commands/`. Symlink SuperJeff's commands there:

```bash
mkdir -p ~/.claude/commands
# Symlink each command so updates to superjeff are picked up automatically
ln -s ~/superjeff/commands/brainstorm.md ~/.claude/commands/superjeff-brainstorm.md
ln -s ~/superjeff/commands/decompose.md ~/.claude/commands/superjeff-decompose.md
ln -s ~/superjeff/commands/specify.md ~/.claude/commands/superjeff-specify.md
ln -s ~/superjeff/commands/design.md ~/.claude/commands/superjeff-design.md
ln -s ~/superjeff/commands/build.md ~/.claude/commands/superjeff-build.md
ln -s ~/superjeff/commands/validate.md ~/.claude/commands/superjeff-validate.md
ln -s ~/superjeff/commands/conform.md ~/.claude/commands/superjeff-conform.md
ln -s ~/superjeff/commands/conform-ui.md ~/.claude/commands/superjeff-conform-ui.md
ln -s ~/superjeff/commands/checkpoint.md ~/.claude/commands/superjeff-checkpoint.md
ln -s ~/superjeff/commands/learn.md ~/.claude/commands/superjeff-learn.md
```

After this, `/superjeff:brainstorm` etc. are available in every project.

### Step 3 — Install hooks globally

Add SuperJeff's hooks to `~/.claude/settings.json`. Open the file and merge in the `hooks` block from `~/superjeff/hooks/hooks.json`.

If `~/.claude/settings.json` has no `hooks` key yet:

```bash
# Read the current settings, add hooks, write back
# Do this manually in your editor — merge hooks/hooks.json into ~/.claude/settings.json
```

The hooks block from `hooks/hooks.json` goes directly under the root of `settings.json`:

```json
{
  "permissions": { ... },
  "hooks": {
    "SessionStart": [ ... ],
    "PreToolUse": [ ... ],
    "PostToolUse": [ ... ],
    "Stop": [ ... ],
    "PreCompact": [ ... ]
  }
}
```

### Step 4 — Add instincts to your project's CLAUDE.md

In each Django project's `CLAUDE.md`, add a reference to the SuperJeff instincts:

```markdown
## SuperJeff Rules

@~/superjeff/instincts/django.yaml
@~/superjeff/instincts/security.yaml
@~/superjeff/instincts/testing.yaml
@~/superjeff/instincts/claude-rules-template.md
```

This tells Claude to load the instinct files at the start of every session.

---

## Option B — Per-Project Install (git submodule)

Use this if you want SuperJeff versioned alongside your project code, or if you want project-specific customisation.

### Step 1 — Add SuperJeff as a submodule

```bash
cd your-django-project
git submodule add https://github.com/yourname/superjeff .superjeff
```

### Step 2 — Symlink commands into `.claude/commands/`

```bash
mkdir -p .claude/commands
ln -s ../.superjeff/commands/brainstorm.md .claude/commands/superjeff-brainstorm.md
ln -s ../.superjeff/commands/decompose.md .claude/commands/superjeff-decompose.md
ln -s ../.superjeff/commands/specify.md .claude/commands/superjeff-specify.md
ln -s ../.superjeff/commands/design.md .claude/commands/superjeff-design.md
ln -s ../.superjeff/commands/build.md .claude/commands/superjeff-build.md
ln -s ../.superjeff/commands/validate.md .claude/commands/superjeff-validate.md
ln -s ../.superjeff/commands/conform.md .claude/commands/superjeff-conform.md
ln -s ../.superjeff/commands/conform-ui.md .claude/commands/superjeff-conform-ui.md
ln -s ../.superjeff/commands/checkpoint.md .claude/commands/superjeff-checkpoint.md
ln -s ../.superjeff/commands/learn.md .claude/commands/superjeff-learn.md
```

### Step 3 — Add hooks to `.claude/settings.local.json`

Create or edit `.claude/settings.local.json` in your project root. Copy the `hooks` block from `.superjeff/hooks/hooks.json` into it:

```json
{
  "permissions": {
    "allow": [
      "Bash(pytest:*)",
      "Bash(python manage.py:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)"
    ]
  },
  "hooks": {
    "SessionStart": [ ... ],
    "PreToolUse": [ ... ],
    "PostToolUse": [ ... ],
    "Stop": [ ... ],
    "PreCompact": [ ... ]
  }
}
```

Add `.claude/settings.local.json` to `.gitignore` if it contains machine-specific paths.

### Step 4 — Add instincts to CLAUDE.md

In your project's `CLAUDE.md`:

```markdown
## SuperJeff Rules

@.superjeff/instincts/django.yaml
@.superjeff/instincts/security.yaml
@.superjeff/instincts/testing.yaml
@.superjeff/instincts/claude-rules-template.md
```

---

## Option C — New Django Project From Scratch

If you're starting a new project with SuperJeff from day one, use the generic CLAUDE.md template:

```bash
# After creating your Django project:
cp ~/superjeff/instincts/claude-rules-template.md your-project/CLAUDE.md
# Edit CLAUDE.md: replace {{PROJECT_NAME}} and {{project_slug}} with your project name
```

Then follow Option A steps 2–3 (commands + hooks).

---

## What Goes Where — Summary

```
~/.claude/
├── commands/
│   ├── superjeff-brainstorm.md   ← symlink → ~/superjeff/commands/brainstorm.md
│   ├── superjeff-build.md        ← symlink → ~/superjeff/commands/build.md
│   └── ...
└── settings.json                 ← hooks merged in (global)

your-django-project/
├── CLAUDE.md                     ← @-references to superjeff instincts
├── .claude/
│   └── settings.local.json       ← hooks (per-project, option B only)
├── artifacts/                    ← created by superjeff:init hook on session start
│   ├── specs/
│   ├── requirements/
│   ├── ux/
│   ├── plans/
│   └── reports/
└── ...your Django code
```

---

## Verify Installation

Open your Django project in Claude Code and check:

1. **Commands available**: type `/superjeff` — autocomplete should show all 10 commands
2. **Hooks active**: start a session — you should see `=== SuperJeff session started ===`
3. **Instincts loaded**: ask Claude "what are the FBV rules?" — it should cite the django instincts
4. **Artifacts directory**: `artifacts/` should exist after the first session start

---

## Updating SuperJeff

```bash
cd ~/superjeff
git pull
```

Because commands are symlinked, all projects pick up the update immediately. No reinstall needed.

---

## Troubleshooting

| Problem | Cause | Fix |
| --- | --- | --- |
| `/superjeff:build` not found | Command not symlinked | Check `~/.claude/commands/` for symlink |
| Hooks not firing | Hooks not in `settings.json` | Verify `hooks` key exists in `~/.claude/settings.json` |
| `=== SuperJeff session started ===` not shown | SessionStart hook not registered | Re-check hooks JSON syntax |
| Instincts not loading | `@` path wrong in CLAUDE.md | Use absolute path `@~/superjeff/...` or relative `@.superjeff/...` |
| `artifacts/` not created | SessionStart hook failed | Run `mkdir -p artifacts/specs artifacts/requirements artifacts/ux artifacts/plans artifacts/reports` manually once |
