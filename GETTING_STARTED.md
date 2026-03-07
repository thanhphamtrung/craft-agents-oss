# Getting Started

Step-by-step guide to run Craft Agents from source.

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| **Bun** | Latest | `curl -fsSL https://bun.sh/install \| bash` |
| **Node.js** | 18+ | Required by Electron |
| **Git** | Any | For cloning the repo |
| **Python 3** | 3.9+ | For document conversion tools (optional) |

## 1. Clone & Install

```bash
git clone https://github.com/lukilabs/craft-agents-oss.git
cd craft-agents-oss
bun install
```

This installs all dependencies across the monorepo (3 apps + 8 packages).

## 2. Environment Setup (Optional)

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
```

| Variable | Required | Purpose |
|----------|----------|---------|
| `ANTHROPIC_API_KEY` | For Claude | Your Anthropic API key |
| `CRAFT_MCP_URL` | For Craft docs | Craft MCP server URL |
| `CRAFT_MCP_TOKEN` | For Craft docs | Bearer token for MCP auth |
| `SLACK_OAUTH_CLIENT_ID` | For Slack | Slack app OAuth client ID |
| `SLACK_OAUTH_CLIENT_SECRET` | For Slack | Slack app OAuth secret |
| `MICROSOFT_OAUTH_CLIENT_ID` | For Microsoft | Azure app registration client ID |
| `SENTRY_ELECTRON_INGEST_URL` | For error tracking | Sentry DSN URL |

> **Note:** You don't need all of these to get started. The app will prompt you for an API key on first launch. You can also configure providers (Google AI Studio, ChatGPT Plus, GitHub Copilot) directly in the UI.

## 3. Run the Desktop App

### Option A: Dev Mode (recommended for development)

```bash
bun run electron:dev
```

This starts Vite dev server with hot module replacement (HMR) for the renderer process. Changes to React components reflect instantly.

### Option B: Build & Run

```bash
bun run electron:start
```

Builds the full app (main + preload + renderer + resources), then launches Electron.

### Option C: Build Distributable

```bash
# macOS
bun run electron:dist:mac

# Windows
bun run electron:dist:win

# Linux
bun run electron:dist:linux
```

## 4. Run the Headless Server (No GUI)

Run Craft Agents as a headless server and connect via CLI or the desktop app as a thin client:

```bash
# Generate a token and start the server
CRAFT_SERVER_TOKEN=$(openssl rand -hex 32) bun run server:start
```

The server prints connection details on startup:

```
CRAFT_SERVER_URL=ws://127.0.0.1:9100
CRAFT_SERVER_TOKEN=<your-token>
```

### Dev mode (with debug logging):

```bash
CRAFT_SERVER_TOKEN=mysecret bun run server:dev
```

### Connect the desktop app as thin client:

```bash
CRAFT_SERVER_URL=ws://127.0.0.1:9100 CRAFT_SERVER_TOKEN=mysecret bun run electron:start
```

## 5. Run the CLI Client

The CLI connects to a running headless server:

```bash
# Set connection details
export CRAFT_SERVER_URL=ws://127.0.0.1:9100
export CRAFT_SERVER_TOKEN=mysecret

# Run CLI commands
bun run apps/cli/src/index.ts ping
bun run apps/cli/src/index.ts sessions
bun run apps/cli/src/index.ts send <session-id> "Hello!"
```

### Self-contained mode (no separate server needed):

```bash
ANTHROPIC_API_KEY=sk-... bun run apps/cli/src/index.ts run "Summarize the README"
```

## 6. Run the Session Viewer

A web app for viewing shared session transcripts:

```bash
bun run viewer:dev
# Opens at http://localhost:5174/s/
```

## Common Commands

### Type Checking

```bash
# Check all packages
bun run typecheck:all

# Check only shared package
bun run typecheck

# Check only Electron app
bun run typecheck:electron
```

### Testing

```bash
# Run all tests
bun test

# Run shared package tests
bun run test:shared:all

# Run document tool tests (requires Python 3)
bun run test:doc-tools
```

### Linting

```bash
# Lint everything
bun run lint

# Lint specific packages
bun run lint:electron
bun run lint:shared
bun run lint:ui
```

### Full Validation (CI equivalent)

```bash
bun run validate:dev
```

This runs typecheck + tests + doc-tool tests — same as CI.

### Other Useful Commands

```bash
# View debug logs (macOS, opens in new Terminal window)
bun run electron:dev:logs

# Clean build artifacts
bun run electron:clean

# Reset to fresh state
bun run fresh-start

# Print the system prompt used by agents
bun run print:system-prompt
```

## Project Structure

```
craft-agents-oss/
├── apps/
│   ├── electron/          # Desktop app (Electron + React)
│   ├── cli/               # Terminal client
│   └── viewer/            # Web session viewer
├── packages/
│   ├── core/              # Shared TypeScript types
│   ├── shared/            # Business logic (agents, auth, config, MCP)
│   ├── ui/                # Shared React components
│   ├── server-core/       # Server transport & RPC handlers
│   ├── server/            # Headless server entry point
│   ├── session-tools-core/# Session-scoped tool definitions
│   ├── session-mcp-server/# MCP server for Codex sessions
│   └── pi-agent-server/   # Pi agent subprocess
├── scripts/               # Build & utility scripts
├── .env.example           # Environment variable template
└── package.json           # Monorepo root (Bun workspaces)
```

## Troubleshooting

### `bun install` fails

Make sure you have the latest Bun: `bun upgrade`

### Electron doesn't launch

1. Check Node.js is installed: `node --version` (need 18+)
2. Try a clean build: `bun run electron:clean && bun run electron:start`

### Port already in use

```bash
# Kill process on port 5173 (Vite dev server)
lsof -ti:5173 | xargs kill -9

# Kill process on port 9100 (headless server)
lsof -ti:9100 | xargs kill -9
```

### Debug logging

Logs are written to:
- **macOS:** `~/Library/Logs/@craft-agent/electron/main.log`
- **Windows:** `%APPDATA%\@craft-agent\electron\logs\main.log`
- **Linux:** `~/.config/@craft-agent/electron/logs/main.log`

Launch with debug mode:
```bash
# Packaged app (macOS)
/Applications/Craft\ Agents.app/Contents/MacOS/Craft\ Agents -- --debug
```

### Config location

All user data lives at `~/.craft-agent/`:
```
~/.craft-agent/
├── config.json           # Main config
├── credentials.enc       # Encrypted credentials
├── preferences.json      # User preferences
└── workspaces/           # Workspace data, sessions, sources
```

To reset everything: `bun run fresh-start`
