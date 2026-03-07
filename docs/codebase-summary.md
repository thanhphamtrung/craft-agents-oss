# Craft Agents — Codebase Summary

**Version:** 0.7.1 | **Runtime:** Bun | **Monorepo:** Workspace structure

## Monorepo Organization

```
craft-agents-oss/
├── apps/                      # 3 end-user applications
│   ├── cli/                   # Terminal WebSocket client
│   ├── electron/              # Desktop Electron app (main product)
│   └── viewer/                # Web SPA for session transcripts
├── packages/                  # 8 shared libraries
│   ├── core/                  # Shared TypeScript types & utilities
│   ├── shared/                # Core business logic (agent, auth, config)
│   ├── ui/                    # React component library
│   ├── server-core/           # Headless server infrastructure
│   ├── server/                # Server CLI entry point
│   ├── session-tools-core/    # Session-scoped tool definitions
│   ├── session-mcp-server/    # MCP server for Codex
│   └── pi-agent-server/       # Pi agent subprocess
└── scripts/                   # Build & release automation
```

## Apps (3)

### apps/electron (~93K LOC)

**Purpose:** Primary desktop application

**Structure:**
```
apps/electron/
├── src/
│   ├── main/                  # Electron main process (IPC handlers, window mgmt)
│   ├── preload/               # Context bridge (controlled IPC exposure)
│   ├── renderer/              # React UI (Vite-bundled)
│   │   ├── components/        # React components (chat, sessions, settings)
│   │   ├── atoms/             # Jotai state (per-session isolation)
│   │   ├── actions/           # Action handlers & hooks
│   │   ├── pages/             # Page layouts
│   │   ├── assets/            # Icons, themes, images
│   │   └── playground/        # Dev tool for component testing
│   ├── resources/             # Bundled binaries & subprocesses
│   │   ├── bin/               # Doc tools (pdf-tool, xlsx-tool, etc.)
│   │   ├── bridge-mcp-server/ # MCP stdio bridge (JS bundle)
│   │   ├── session-mcp-server/# Session tools MCP server
│   │   └── docs/              # In-app documentation
│   ├── eslint-rules/          # Custom ESLint plugins (no direct-file-open, etc.)
│   ├── electron-builder.yml   # Electron packager config
│   └── vite.config.ts         # Renderer build config (Vite)
└── package.json
```

**Key Dependencies:**
- `@anthropic-ai/claude-agent-sdk`: Claude agent execution
- `@modelcontextprotocol/sdk`: MCP client & tool management
- `@mariozechner/pi-coding-agent`: Pi agent SDK
- `@craft-agent/shared`: Business logic
- `@craft-agent/ui`: React components
- `jotai`: Atomic state management
- `react`: 18.3.1
- `electron`: 39.2.7
- `esbuild`: Main process bundling
- `vite`: Renderer bundling

**Build Scripts:**
- `bun run electron:dev` — Hot reload (Vite + Electron watch)
- `bun run electron:start` — Build & launch
- `bun run electron:dist` — Package for distribution (mac/win/linux)

### apps/cli (~3.3K LOC)

**Purpose:** Terminal WebSocket client for scripting & CI/CD

**Structure:**
```
apps/cli/
├── src/
│   ├── index.ts               # CLI entry point & arg parsing
│   ├── client.ts              # WebSocket RPC client
│   ├── commands.ts            # Command implementations (ping, send, run, etc.)
│   └── server-spawner.ts      # Spawn headless server for `run` command
└── package.json
```

**Commands:** ping, health, versions, workspaces, sessions, sources, connections, send, invoke, listen, run, --validate-server

**Key Dependencies:**
- `ws`: WebSocket
- `@craft-agent/server-core`: Server runtime & RPC
- `@craft-agent/shared`: Business logic

### apps/viewer (~500 LOC)

**Purpose:** Web SPA for viewing/sharing session transcripts

**Structure:**
```
apps/viewer/
├── src/
│   ├── App.tsx                # Main SPA component
│   ├── index.tsx              # Entry point
│   └── assets/
├── vite.config.ts             # Vite config
└── package.json
```

**Usage:** `bun run viewer:dev` (localhost:5174)

## Packages (8)

### packages/core (~200 LOC)

**Purpose:** Shared types and utilities

**Exports:**
- `types/` — Core types: Workspace, Session, Message, AgentEvent
- `utils/` — UUID generation, path utilities

**Dependencies:** None (pure types)

### packages/shared (~10K LOC)

**Purpose:** Core business logic for agent, auth, config, credentials, MCP

**Structure:**
```
packages/shared/src/
├── agent/                     # CraftAgent SDK wrapper, permissions
├── auth/                      # OAuth flows, token mgmt
├── config/                    # Config file storage & migrations
├── credentials/               # AES-256-GCM encrypted storage
├── mcp/                       # MCP client pool, tool invocation
├── sessions/                  # Session persistence (JSONL)
├── sources/                   # API/MCP source definitions
├── workspaces/                # Workspace config
├── labels/                    # Auto-labeling logic
├── automations/               # Event-driven automations
├── validation/                # Zod schemas
├── skills/                    # Skill metadata & storage
├── tools/                     # Tool definitions
└── mentions/                  # @mention parsing
```

**Key Exports:**
- `agent/` — CraftAgent, permissions (safe/ask/allow-all)
- `auth/` — OAuth (Slack, Microsoft), token handlers
- `config/` — Storage, migrations, preferences
- `credentials/` — AES-256-GCM encryption/decryption
- `mcp/` — MCP client pool, tool invocation
- `sessions/` — JSONL reader/writer
- `sources/` — Source definitions & storage
- `automations/` — Event-driven automation config

**Key Dependencies:**
- `@craft-agent/core` — Shared types
- `@craft-agent/session-tools-core` — Tool schemas
- `@anthropic-ai/claude-agent-sdk` — Claude integration
- `@modelcontextprotocol/sdk` — MCP SDK
- `zod` — Schema validation
- `croner` — Cron scheduling (automations)

**Tests:**
- `bun run test` (unit tests in each module)
- `bun test llm-connections.test.ts` (LLM setup)
- `bun test models-pi.test.ts` (Pi SDK models)

### packages/ui (~22.5K LOC)

**Purpose:** React component library (platform-agnostic)

**Structure:**
```
packages/ui/src/
├── components/
│   ├── session-viewer/        # Chat component (messages, tool results)
│   ├── markdown/              # Markdown renderer (Shiki, Mermaid, LaTeX)
│   ├── overlays/              # Modal overlays (code, diff, terminal, image)
│   ├── terminal-ansi/         # ANSI parser for terminal output
│   ├── pdf-viewer/            # PDF rendering
│   ├── json-viewer/           # JSON tree viewer
│   └── common/                # Base components (buttons, cards, etc.)
├── hooks/                     # React hooks (useSession, useMarkdown, etc.)
├── utils/                     # Helpers (markdown parsing, ANSI parsing)
└── types/                     # TypeScript types
```

**Key Dependencies:**
- `react` 18.3.1
- `shiki` — Code syntax highlighting (32+ languages)
- `marked` + `react-markdown` — Markdown rendering
- `katex` + `rehype-katex` — Math rendering
- `beautiful-mermaid` — Diagram rendering
- `@tiptap/react` — Rich text editor
- `@radix-ui` — Headless UI components
- `tailwindcss` v4 — Styling

**Features:**
- Markdown with syntax highlighting (Shiki)
- Math (LaTeX) rendering
- Mermaid diagram rendering
- PDF inline viewing
- JSON tree viewer
- ANSI color parsing (terminal output)
- Diff viewer (side-by-side)
- Code overlay with copy

### packages/server-core (~12.7K LOC)

**Purpose:** Headless server infrastructure (transport, RPC, runtime)

**Structure:**
```
packages/server-core/src/
├── transport/                 # WebSocket RPC server
├── runtime/                   # Server runtime (session mgmt, tool execution)
├── handlers/                  # RPC command handlers
│   ├── rpc/                   # RPC channel implementations
│   ├── credentials.ts
│   ├── sessions.ts
│   ├── workspaces.ts
│   ├── sources.ts
│   ├── skills.ts
│   └── ...
├── bootstrap/                 # Server initialization
├── model-fetchers/            # Model list fetching
├── sessions/                  # SessionManager (execution logic)
└── domain/                    # Domain models
```

**Key Exports:**
- `transport/` — WsRpcServer (WebSocket RPC)
- `runtime/` — Server runtime
- `handlers/rpc/` — Command implementations
- `bootstrap/` — Server initialization
- `sessions/` — SessionManager

**Key Dependencies:**
- `ws` — WebSocket
- `@craft-agent/core` — Types
- `@craft-agent/shared` — Business logic
- `sharp` — Image processing
- `@anthropic-ai/claude-agent-sdk` — Claude execution
- `@modelcontextprotocol/sdk` — MCP

### packages/server (~50 LOC)

**Purpose:** Headless server CLI entry point

**Contents:**
```
packages/server/src/
└── index.ts                   # Server startup script
```

**Usage:**
```bash
CRAFT_SERVER_TOKEN=<token> bun run packages/server/src/index.ts
```

### packages/session-tools-core (~6.3K LOC)

**Purpose:** Session-scoped tool definitions with Zod schema validation

**Structure:**
```
packages/session-tools-core/src/
├── types.ts                   # Tool schema definitions
├── registry.ts                # Tool registry
└── handlers/                  # Tool implementations
```

**Key Concepts:**
- Tools are Zod-validated input/output schemas
- Per-session tool definitions
- Handler functions for tool execution
- Schema-driven validation

### packages/session-mcp-server (~600 LOC)

**Purpose:** MCP server for Codex (session-scoped tools)

**Structure:**
```
packages/session-mcp-server/src/
├── index.ts                   # MCP server entry point
├── handlers.ts                # Tool call handlers
└── schemas.ts                 # Tool schemas (Zod)
```

**Usage:** Runs as stdio MCP server, proxies session-tools to agents

### packages/pi-agent-server (~2K LOC)

**Purpose:** Pi agent subprocess with JSONL protocol

**Structure:**
```
packages/pi-agent-server/src/
├── index.ts                   # Subprocess entry point
├── protocol.ts                # JSONL protocol
└── tools/                     # Tool implementations
```

**Usage:** Spawned as subprocess by server runtime

## Dependency Graph

```
┌─────────────────────────────────────────┐
│ apps/electron (main product)            │
├─────────────────────────────────────────┤
│ @craft-agent/ui (components)            │
│ @craft-agent/shared (business logic)    │
│ @craft-agent/server-core (headless)     │
└─────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ @craft-agent/shared                     │
├─────────────────────────────────────────┤
│ @craft-agent/core (types)               │
│ @craft-agent/session-tools-core (tools) │
│ @anthropic-ai/claude-agent-sdk          │
│ @modelcontextprotocol/sdk               │
│ @mariozechner/pi-coding-agent (Pi)      │
└─────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ @craft-agent/core (shared types)        │
│ @craft-agent/session-tools-core         │
└─────────────────────────────────────────┘
```

## Build & Development Workflow

### Local Development
```bash
bun install                    # Install all workspaces
bun run electron:dev          # Hot reload Electron + Vite
bun run server:dev            # Headless server in dev mode
bun run typecheck:all         # Type checking
bun run test:shared:all       # Run tests
bun run lint                  # ESLint + custom rules
```

### Building
```bash
bun run electron:build        # Build all parts (main, preload, renderer)
bun run electron:start        # Build & launch packaged app
bun run electron:dist:mac     # Package for macOS
bun run electron:dist:win     # Package for Windows
bun run electron:dist:linux   # Package for Linux
bun run server:build          # Build headless server binary
```

### Testing
```bash
bun test                      # All tests
bun run test:shared:llm-connections
bun run test:shared:models-pi
bun run test:doc-tools        # Python doc tool tests
```

## Configuration Files

| File | Purpose |
|------|---------|
| `package.json` | Root workspace config |
| `packages/*/package.json` | Package configs |
| `apps/electron/electron-builder.yml` | Electron packaging |
| `apps/electron/vite.config.ts` | Renderer bundling |
| `.env` | OAuth secrets (build-time) |
| `.env.example` | Env var template |
| `tsconfig.json` | TypeScript config |
| `.eslintrc.cjs` | ESLint rules |

## Entry Points

| App/Tool | Entry | Description |
|----------|-------|-------------|
| Electron (dev) | `apps/electron/src/main/index.ts` | Main process |
| Electron (preload) | `apps/electron/src/preload/index.ts` | IPC bridge |
| Electron (renderer) | `apps/electron/src/renderer/index.tsx` | React UI |
| CLI | `apps/cli/src/index.ts` | Terminal client |
| Viewer | `apps/viewer/src/index.tsx` | Web SPA |
| Server | `packages/server/src/index.ts` | Headless server |
| Session MCP | `packages/session-mcp-server/src/index.ts` | MCP server |

## File Organization Patterns

### TypeScript/JavaScript
- **Main exports:** `src/index.ts`
- **Submodule exports:** `src/{feature}/index.ts`
- **Tests:** Co-located with source or in `src/__tests__/`
- **Naming:** kebab-case for files with long, descriptive names

### React Components
- **Component file:** `src/components/ComponentName.tsx` (PascalCase)
- **Hooks:** `src/hooks/useHookName.ts` (camelCase)
- **Atoms (Jotai):** `src/atoms/sessionAtoms.ts` (camelCase)
- **Styles:** Tailwind CSS utilities (no separate CSS files)

### Configuration
- **Zod schemas:** `src/{feature}/schema.ts` or `src/{feature}/types.ts`
- **Config storage:** `~/.craft-agent/{filename}.json` or `.enc` (encrypted)
- **JSONL data:** Session messages, preferences

## Key Architectural Patterns

1. **Monorepo workspace:** Each package is independently publishable
2. **Type-safe RPC:** Channels are string literals, typed handlers
3. **Per-session state isolation:** Jotai atomFamily for workspace/session IDs
4. **Credential encryption:** AES-256-GCM with key derivation
5. **Event-driven automations:** Event → matcher → actions (cron, prompt, etc.)
6. **Tool pool management:** MCP client pooling, connection reuse
7. **Provider abstraction:** Claude vs Pi SDK behind unified interface
8. **Cascading themes:** App-level + workspace-level override

## Documentation Structure

- `/docs/` — All user & developer documentation
- `README.md` — Quick start & feature overview
- `CONTRIBUTING.md` — Contribution guidelines
- `CLAUDE.md` — Claude Code instructions
- `./.claude/rules/` — Development workflows & standards

## Metrics (as of v0.7.1)

| Metric | Value |
|--------|-------|
| Total LOC | ~143K |
| Electron app | ~93K |
| Packages | ~50K |
| TypeScript | ~95% of codebase |
| Test coverage (shared) | ~70% |
| Supported LLM providers | 8+ |
| Built-in sources | 3+ (Craft, Linear, GitHub, etc.) |
| Release cadence | ~1 minor release/month |
