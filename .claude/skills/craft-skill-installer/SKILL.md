---
name: ck:craft-skill-installer
description: Install skills from the craft-agents-oss catalog into a Craft Desktop workspace. Use when the user wants to set up skills in Craft Desktop, migrate skills from Claude Code to Craft, or manage installed Craft skills.
argument-hint: "[install|update|list]"
---

# Craft Skill Installer

Install skills from the craft-agents-oss skill catalog into a Craft Desktop workspace.

## How It Works

Follow these steps sequentially. Use `bash` tool for file operations and `WebFetch` for GitHub downloads.

---

### Step 1: Detect Craft Workspace

Read the Craft Desktop config to find the active workspace:

```bash
cat ~/.craft-agent/config.json
```

**Parse the JSON to extract:**
1. `activeWorkspaceId` — the currently active workspace ID
2. Find the matching workspace in the `workspaces` array
3. Get its `rootPath` (expand `~` to the user's home directory)
4. Verify the workspace exists: `ls "{rootPath}"`

**Create the skills directory if missing:**
```bash
mkdir -p "{rootPath}/skills"
```

**If `config.json` doesn't exist or has no workspaces**, ask the user:
- "Craft Desktop config not found at `~/.craft-agent/config.json`. Is Craft installed?"
- "No workspaces found. Please create a workspace in Craft Desktop first."

**If multiple workspaces exist**, list them and ask which one to install to.

---

### Step 2: Fetch Skill Catalog

Try **local first**, then **GitHub fallback**.

**Local (if repo is available):**
```bash
cat .claude/skills/ck-help/scripts/skills_data.yaml
```
Check if this file exists in the current working directory. If it does, use it.

**GitHub fallback:**
Fetch the catalog from:
```
https://raw.githubusercontent.com/lukilabs/craft-agents-oss/main/.claude/skills/ck-help/scripts/skills_data.yaml
```

Parse the YAML into a list of skills. Each skill has:
- `name` — skill slug (e.g., `debug`, `frontend-development`)
- `description` — short description
- `category` — grouping (e.g., `frontend`, `backend`, `utilities`, `ai-ml`)
- `path` — relative path to SKILL.md (e.g., `debug/SKILL.md`)
- `has_references` — whether skill has a `references/` directory
- `has_scripts` — whether skill has a `scripts/` directory

---

### Step 3: Check Already Installed Skills

For each skill in the catalog, check if it's already installed:
```bash
ls "{rootPath}/skills/{name}/SKILL.md" 2>/dev/null
```

Mark each skill as `installed` or `not installed`.

---

### Step 4: Present Interactive Menu

Group skills by category and display a numbered menu.

**Format:**

```
## Craft Skill Installer

Workspace: {workspace name} ({rootPath})
Source: {local repo | GitHub}

### AI/ML (3 skills)
  1. ai-artist — Generate images via Nano Banana with 129 curated prompts
  2. ai-multimodal — Analyze images/audio/video with Gemini API ✓ installed
  3. google-adk-python — Build AI agents with Google ADK Python

### Backend (3 skills)
  4. backend-development — Build backends with Node.js, Python, Go
  5. better-auth — Add authentication with Better Auth
  6. payment-integration — Integrate payments with SePay, Polar, Stripe

### Frontend (7 skills)
  7. frontend-design — Create polished frontend interfaces
  ...

### Utilities (12 skills)
  ...

(... all categories ...)

---
Which skills to install?
- Enter numbers: 1,4,7 or 1-5
- Enter category name: frontend, backend, ai-ml
- Enter 'all' to install everything
- Enter 'update' to reinstall already-installed skills
- Enter 'q' to quit
```

Wait for the user's response before proceeding.

---

### Step 5: Install Selected Skills

For each selected skill:

#### 5a. Skip if already installed
If the skill is already installed and user did NOT say "update" or "reinstall", skip it and note "Already installed" in the summary.

#### 5b. Fetch SKILL.md

**Local source (preferred):**
```bash
mkdir -p "{rootPath}/skills/{name}"
cp .claude/skills/{path} "{rootPath}/skills/{name}/SKILL.md"
```

**GitHub source:**
Fetch from:
```
https://raw.githubusercontent.com/lukilabs/craft-agents-oss/main/.claude/skills/{path}
```
Write the content to `{rootPath}/skills/{name}/SKILL.md`.

#### 5c. Fetch references (if `has_references: true`)

**Local source:**
```bash
cp -r .claude/skills/{name}/references/ "{rootPath}/skills/{name}/references/"
```

**GitHub source:**
References cannot be enumerated via raw GitHub URLs. Instead, inform the user:
> "Skill '{name}' has reference files that can't be auto-fetched from GitHub. Clone the repo locally for full skill content, or the SKILL.md alone will work for most use cases."

#### 5d. Skip scripts
Scripts (`has_scripts: true`) are typically Python/Bash files that require the Claude Code venv. They're not applicable in Craft Desktop. Skip them silently.

---

### Step 6: Show Summary

Display a completion summary:

```
## Installation Complete

Installed {N} skills to {rootPath}/skills/

| # | Skill | Status |
|---|-------|--------|
| 1 | debug | ✓ Installed |
| 2 | frontend-development | ✓ Installed |
| 3 | ai-multimodal | ○ Already existed (skipped) |
| 4 | cook | ✓ Updated |

Skills are now available in Craft Desktop — no restart needed.
Mention a skill with @ in your chat to activate it.
```

---

## Handling Edge Cases

- **Nested skill paths** (e.g., `document-skills/docx`): Create `{rootPath}/skills/document-skills-docx/SKILL.md` (flatten the path with hyphens for Craft compatibility)
- **Network errors on GitHub fetch**: Retry once, then report the error and continue with remaining skills
- **Permission errors**: Ask user to check file permissions on the workspace directory
- **User says "update" or "reinstall"**: Overwrite existing SKILL.md files for selected skills

## Quick Commands

When the user invokes this skill with arguments:
- `install` or no args → Run full flow (Steps 1-6)
- `list` → Run Steps 1-3 only, show installed vs available
- `update` → Run Steps 1-4, pre-select already-installed skills, overwrite them
