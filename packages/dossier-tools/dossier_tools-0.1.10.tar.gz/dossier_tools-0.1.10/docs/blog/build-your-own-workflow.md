# Build Your Own Workflow: Skills and Dossiers Guide

Every team has *that thing*—the setup nobody remembers, the checklist that lives in someone's head, the process that's "documented somewhere." You've seen examples like [Streamlining Your Issue Workflow](./streamlining-issue-workflow.md) and [Finishing What You Started](./finishing-what-you-started.md). Those are *our* workflows for *our* pain points.

Yours are different. This guide shows you how to build them.

> [!TIP]
> **Just want to see an example?** Skip the theory and check out [Streamlining Your Issue Workflow](./streamlining-issue-workflow.md) or [Finishing What You Started](./finishing-what-you-started.md) to see complete workflows in action.

---

## TL;DR

| Concept | What It Is | Where It Lives |
|---------|------------|----------------|
| **Skill** | Natural language trigger | `~/.claude/skills/` (local) |
| **Dossier** | Versioned workflow logic | Registry (shared) |
| **Best pattern** | Skill triggers dossier | Best of both worlds |

### Quick Path

Already know what you're doing? Here's the fast track:

```bash
dossier new                                    # Create interactively
dossier checksum my-workflow.ds.md --update    # Add integrity hash
dossier validate my-workflow.ds.md             # Verify schema
dossier publish my-workflow.ds.md --namespace yourorg/skills/my-workflow
```

---

## What is a Claude Code Skill?

A **skill** is a markdown file that teaches Claude Code to respond to natural language triggers.

```
~/.claude/skills/
└── my-workflow/
    └── SKILL.md
```

When you say something like "deploy to staging", Claude Code checks your skills directory and finds the matching skill. The skill tells Claude what to do.

**Key characteristics:**
- Auto-discovered by Claude Code on session start
- Triggers on natural language ("start issue", "run tests", etc.)
- Lives locally on your machine
- No versioning, no registry, no signatures

For more details, see the [official Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code).

---

## What is a Dossier?

A **dossier** is a structured instruction file (`.ds.md`) that AI agents can execute. It's like a script, but designed for LLMs—providing clear guidance that agents can follow intelligently.

```yaml
---
schema_version: "1.0.0"
name: my-workflow
title: My Workflow
version: "1.0.0"
status: stable
objective: What this workflow accomplishes
authors:
  - name: Your Name
checksum:
  algorithm: sha256
  hash: abc123...
---

# My Workflow

## Steps
1. Do this
2. Then do that
3. Verify it worked

## Validation
- [ ] Success criteria here
```

**Key characteristics:**
- Versioned (semantic versioning)
- Shareable via registry
- Checksums verify content integrity
- Optional cryptographic signatures verify authorship
- Discoverable with `dossier search` and `dossier list`

---

## Skills vs Dossiers: When to Use Each

| Feature | Skill | Dossier |
|---------|-------|---------|
| Natural language trigger | Yes | No |
| Auto-discovery | Yes | No |
| Versioning | No | Yes |
| Registry/sharing | No | Yes |
| Checksums | No | Yes |
| Signatures | No | Yes |
| Best for | Personal shortcuts | Team workflows |

### Decision Guide

**Use a Skill alone when:**
- It's a personal shortcut only you use
- It doesn't need versioning
- It's simple enough to fit in one file

**Use a Dossier alone when:**
- It's a team workflow
- It needs versioning
- You want to share it via the registry
- You don't need a natural language trigger

**Use Skill + Dossier when:**
- It's a frequently-used team workflow
- You want natural language triggers AND versioning
- You want the skill to always run the latest (or pinned) version

---

## The Full Cycle: From Idea to Installed Workflow

### Step 1: Scope Your Workflow

Before writing anything, answer these questions:

1. **What problem are you solving?**
   - What's tedious or error-prone today?
   - What would save time if automated?

2. **Who will use it?**
   - Just you → Skill only
   - Your team → Dossier (with optional skill)
   - Public/cross-org → Dossier with signature

3. **Does it need versioning?**
   - Will it evolve over time?
   - Do you need to pin versions for stability?

---

### Step 2: Create a Dossier

Use the CLI to create a new dossier:

```bash
dossier new
```

This walks you through creating a dossier interactively. Alternatively, create a file manually:

```bash
touch my-workflow.ds.md
```

**Required frontmatter fields:**

```yaml
---
schema_version: "1.0.0"
name: your-workflow-name        # Slug: lowercase, hyphens only
title: Your Workflow Title
version: "1.0.0"
status: draft                   # draft | stable | deprecated | experimental
objective: One sentence describing what this accomplishes
authors:
  - name: Your Name
checksum:
  algorithm: sha256
  hash: ""                      # Filled in by `dossier checksum --update`
---
```

**Optional fields:**

```yaml
risk_level: low               # low | medium | high | critical
requires_approval: false
category:
  - development
  - git
tags:
  - automation
  - git
estimated_duration:
  min_minutes: 2
  max_minutes: 10
```

**Writing the body:**

```markdown
# Your Workflow Title

## Prerequisites
- What needs to be installed/configured before running

## Steps
1. First, do this
2. Then, do that
3. Finally, verify

## Validation
- [ ] Success criterion 1
- [ ] Success criterion 2
```

**Generate the checksum:**

```bash
dossier checksum my-workflow.ds.md --update
```

This calculates the SHA256 hash of the body content and updates the frontmatter.

---

### Step 3: Test Locally

**Validate the schema:**

```bash
dossier validate my-workflow.ds.md
```

**Run with Claude Code:**

```bash
dossier run my-workflow.ds.md
```

Or paste the content directly into a Claude Code session.

---

### Step 4: Publish to Registry

**Login (first time only):**

```bash
dossier login
```

This opens a GitHub OAuth flow.

**Publish:**

```bash
dossier publish my-workflow.ds.md --namespace yourorg/development/category
```

### Publishing Best Practices

| Type | Recommended Namespace | Example |
|------|----------------------|---------|
| Skills | `org/skills/name` | `imboard-ai/skills/start-issue` |
| Git workflows | `org/development/git/name` | `imboard-ai/development/git/setup-issue-workflow` |
| Testing | `org/development/testing/name` | `imboard-ai/development/testing/coverage-gap` |
| Security | `org/development/security/name` | `imboard-ai/development/security/vuln-scan` |

**Why namespace skills separately?**

The `dossier install-skill` command works with *any* dossier in the registry. Using a `skills/` namespace helps consumers identify which dossiers are meant to be used as skills vs standalone workflows.

---

### Step 5: Create a Skill (Optional)

If you want natural language triggers, create a skill that calls your dossier.

**Create the skill file:**

```bash
mkdir -p ~/.claude/skills/my-workflow
touch ~/.claude/skills/my-workflow/SKILL.md
```

**Skill structure:**

```yaml
---
name: my-workflow
description: Brief description of what this does.
  Use when user says "trigger phrase", "another trigger", etc.
---

# My Workflow

When the user wants to [do the thing]:

## Prerequisites
Ensure dossier-tools is installed:
```bash
pip install dossier-tools
```

## Steps

1. Extract any parameters from their request
2. Run the workflow:
   ```bash
   dossier run yourorg/development/category/my-workflow
   ```
3. Confirm completion with the user

## What This Creates
- Output 1
- Output 2
```

**Key elements:**
- `name`: Skill identifier
- `description`: Include trigger phrases so Claude knows when to activate
- Body: Instructions for Claude on how to run the workflow

### Two Patterns for Skills

There are two ways to create skills that use dossiers:

| Pattern | How It Works | Best For |
|---------|--------------|----------|
| **Lightweight skill** | Minimal skill file calls `dossier run` | Large workflows, keeps context small |
| **Dossier as skill** | Dossier with full frontmatter installed directly | Small skills you want to version/share |

**Pattern 1: Lightweight skill calls dossier** (shown above)
- Skill has minimal frontmatter (`name`, `description`)
- Body contains `dossier run yourorg/workflow`
- Workflow logic lives in the registry, not in the skill

**Pattern 2: Dossier installed as skill**
- Use `dossier install-skill yourorg/skills/my-skill`
- The full dossier becomes the skill
- Get versioning, checksums, signatures

### A Note on Frontmatter Compatibility

You might notice that standard Claude Code skills use minimal frontmatter:

```yaml
---
name: my-skill
description: Trigger phrases here
---
```

While dossiers have richer frontmatter:

```yaml
---
schema_version: "1.0.0"
name: my-workflow
title: My Workflow
version: "1.0.0"
status: stable
objective: What this accomplishes
authors:
  - name: Your Name
checksum:
  algorithm: sha256
  hash: abc123...
---
```

**Here's the good news:** When you run `dossier install-skill`, the full dossier (with all its frontmatter) gets installed as a skill—and Claude Code handles it gracefully. We've tested this extensively.

**Why does this matter?**

| Approach | Frontmatter | Benefits |
|----------|-------------|----------|
| Standard skill | `name`, `description` | Simple, minimal |
| Dossier as skill | Full dossier schema | Versioning, checksums, signatures, registry publishing |

By using dossier frontmatter for your skills, you get the full power of dossier-tools: version pinning, integrity verification, cryptographic signatures, and registry publishing—all while keeping the natural language trigger experience.

> [!TIP]
> If you plan to share your skill via the registry, use dossier frontmatter from the start. You can still use it locally as a skill, and when you're ready to share, just `dossier publish`.

> [!WARNING]
> **Don't install full workflow dossiers as skills.** While `dossier install-skill` technically works with any dossier, we don't recommend installing large workflow dossiers directly as skills. They lack dedicated trigger phrases in the description, and their full content bloats Claude Code's context unnecessarily. Instead, create a lightweight skill that *calls* the dossier via `dossier run`.

---

### Step 6: Install and Share

**For skills:**

```bash
# Install from registry
dossier install-skill yourorg/skills/my-workflow

# Install specific version
dossier install-skill yourorg/skills/my-workflow@1.0.0

# Force reinstall
dossier install-skill yourorg/skills/my-workflow --force
```

After installing, **start a new Claude Code session** for the skill to be discovered.

**For dossiers (no skill):**

```bash
# Run directly from registry
dossier run yourorg/development/category/my-workflow

# Run specific version
dossier run yourorg/development/category/my-workflow@1.0.0

# Pull locally first
dossier pull yourorg/development/category/my-workflow
```

---

## Quick Reference

### Commands

| Command | Purpose |
|---------|---------|
| `dossier new` | Create new dossier interactively |
| `dossier validate FILE` | Validate schema |
| `dossier checksum FILE --update` | Calculate and update checksum |
| `dossier sign FILE --signed-by EMAIL` | Sign with your key |
| `dossier verify FILE` | Verify checksum and signature |
| `dossier login` | Authenticate with registry |
| `dossier publish FILE --namespace NS` | Publish to registry |
| `dossier list` | List available dossiers |
| `dossier search QUERY` | Search registry |
| `dossier get NAME` | View dossier metadata |
| `dossier pull NAME` | Download dossier locally |
| `dossier run NAME` | Execute dossier |
| `dossier install-skill NAME` | Install as Claude Code skill |

### File Locations

| What | Where |
|------|-------|
| Skills | `~/.claude/skills/<name>/SKILL.md` |
| Dossier cache | `~/.dossier/cache/` |
| Auth credentials | `~/.dossier/credentials` |
| Signing keys | `~/.dossier/keys/` |

---

## Example Workflows

Looking for inspiration? Check out these examples:

- **[Streamlining Your Issue Workflow](./streamlining-issue-workflow.md)** — Automate branch creation, worktrees, and planning docs
- **[Finishing What You Started](./finishing-what-you-started.md)** — Pre-PR checks, security scans, and PR creation

Or browse the registry:

```bash
dossier list
dossier search "your keyword"
```

---

## Summary

| Step | Command | Result |
|------|---------|--------|
| Create | `dossier new` | `my-workflow.ds.md` |
| Validate | `dossier validate` | Schema check |
| Checksum | `dossier checksum --update` | Integrity hash |
| Test | `dossier run my-workflow.ds.md` | Local execution |
| Publish | `dossier publish --namespace` | In registry |
| Skill (opt) | Create `~/.claude/skills/*/SKILL.md` | Natural language trigger |
| Share | `dossier install-skill` | Team can use it |

---

## Links

- [dossier-tools on GitHub](https://github.com/liberioai/dossier-tools)
- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [Dossier Registry](https://dossier-registry-mvp.vercel.app)
