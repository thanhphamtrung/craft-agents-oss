# Craft Skill Installer

Install skills from the craft-agents-oss catalog into a Craft Desktop workspace with an interactive selection menu.

## What It Does

Skills in `.claude/skills/` work in Claude Code CLI but NOT in Craft Desktop, which reads from `{workspace.rootPath}/skills/{slug}/SKILL.md`. This installer bridges the gap:

1. Auto-detects your active Craft Desktop workspace
2. Fetches the full skill catalog (60+ skills)
3. Presents an interactive menu grouped by category
4. Installs only the skills you select
5. Skips already-installed skills (unless updating)

## Prerequisites

- **Craft Desktop** installed with at least one workspace configured
- Config file at `~/.craft-agent/config.json`

## Usage

### In Claude Code CLI

```
/craft-skill-installer          # Full install flow
/craft-skill-installer list     # Show installed vs available
/craft-skill-installer update   # Reinstall already-installed skills
```

### In Craft Desktop

Paste this prompt into a Craft Desktop session:

> Install skills from the craft-agents-oss catalog. Read my workspace config from `~/.craft-agent/config.json`, fetch the skill catalog from `https://raw.githubusercontent.com/lukilabs/craft-agents-oss/main/.claude/skills/ck-help/scripts/skills_data.yaml`, show me skills grouped by category, and install the ones I pick to my workspace's `skills/` directory.

Or if you have the skill installed, mention it with `@craft-skill-installer`.

## Installation Sources

| Source | When Used | Notes |
|--------|-----------|-------|
| **Local repo** | CWD contains `.claude/skills/` | Fastest, includes references |
| **GitHub** | No local repo available | Fetches from `lukilabs/craft-agents-oss` main branch |

Local source is preferred — it's faster and includes reference files. GitHub source fetches SKILL.md files only (references can't be enumerated via raw URLs).

## Skill Categories

Skills are grouped by category for easier browsing:

| Category | Examples |
|----------|----------|
| `ai-ml` | ai-artist, ai-multimodal, google-adk-python |
| `backend` | backend-development, better-auth, payment-integration |
| `frontend` | frontend-design, frontend-development, threejs, ui-styling |
| `frameworks` | mobile-development, shopify, web-frameworks |
| `utilities` | debug, fix, cook, code-review, test, plan |
| `dev-tools` | git, docs-seeker, repomix, scout, worktree |
| `infrastructure` | devops |
| `database` | databases |
| `multimedia` | chrome-devtools, media-processing |
| `other` | mermaidjs-v11, sequential-thinking, context-engineering |

## How Selection Works

After the menu is displayed, you can select skills by:

- **Numbers**: `1,4,7` or ranges `1-5`
- **Category name**: `frontend` installs all frontend skills
- **`all`**: Install every skill in the catalog
- **`update`**: Reinstall skills that are already installed

Already-installed skills show a ✓ marker and are skipped unless you choose to update.

## What Gets Installed

| Component | Installed? | Notes |
|-----------|-----------|-------|
| `SKILL.md` | Yes | Core skill prompt — always installed |
| `references/` | Local only | Reference docs copied when using local source |
| `scripts/` | No | Scripts require Claude Code venv, not applicable in Craft |

## Idempotency

- Running the installer multiple times is safe
- Already-installed skills are skipped by default
- Use `update` mode to overwrite existing installations
- No restart needed — Craft Desktop auto-detects new skills
