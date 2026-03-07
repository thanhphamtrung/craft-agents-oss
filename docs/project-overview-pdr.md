# Craft Agents — Product Overview & Development Requirements

**Version:** 0.7.1 | **License:** Apache 2.0 | **Built by:** Craft.do

## Executive Summary

Craft Agents is an open-source desktop application (Electron) that provides an intuitive, agent-native interface for working with AI agents. It combines the power of Claude and Pi agent SDKs with an extensible tool/source ecosystem, enabling seamless integration with APIs, databases, and local tools—all without configuration files.

**Core Value:**
- **Agent-native paradigm:** Describe what you want; the agent figures out how
- **No-fluff integration:** Connect to Linear, Gmail, Slack, Postgres, etc. via agent instructions
- **Multi-provider:** Claude, Google AI Studio, ChatGPT Plus, GitHub Copilot, OpenAI—all in one app
- **Customizable & extensible:** Custom MCP servers, skills, and automations
- **Document-centric workflow:** Beautiful markdown-based chat (not code-editor centric)
- **Shareable sessions:** Export and share session transcripts via web

## Product Vision

Enable knowledge workers and developers to augment their capabilities through intelligent agents, removing friction from tool setup and encouraging exploration through natural language.

## Target Audience

1. **Primary:** Developers, knowledge workers using Claude/Pi agents regularly
2. **Secondary:** Enterprise teams building internal agent workflows
3. **Tertiary:** Anyone wanting an alternative to web-based chat interfaces

## Key Features (v0.7.1)

### Core Chat
- Multi-session inbox with status workflow (Todo, In Progress, Needs Review, Done)
- Real-time streaming responses with tool visualization
- Session flagging, labeling, and search

### Multi-Provider LLM
- **Claude:** Anthropic API key, Claude Max/Pro OAuth, custom endpoints (OpenRouter, Vercel AI Gateway, Ollama, etc.)
- **Pi:** Google AI Studio, ChatGPT Plus (Codex OAuth), GitHub Copilot OAuth, OpenAI API key
- Per-workspace default provider configuration

### Sources (API Integration)
- **MCP Servers:** Craft (32+ doc tools), Linear, GitHub, Notion, custom servers
- **REST APIs:** Gmail, Calendar, Drive (Google OAuth), Slack, Microsoft
- **Local:** Filesystem, Obsidian vaults, Git repos
- **Custom:** Paste OpenAPI specs or endpoint URLs
- Agent-assisted setup (auto-discovers APIs, configures credentials)

### Permissions (3-Level)
| Mode | Display | Behavior |
|------|---------|----------|
| `safe` | Explore | Read-only, blocks all writes |
| `ask` | Ask to Edit | Prompts for approval (default) |
| `allow-all` | Auto | Auto-approves all commands |

### Skills & Automations
- **Skills:** Workspace-scoped agent instructions with Zod schema validation
- **Automations:** Event-driven (LabelAdd, SchedulerTick, ToolUse) with prompt actions and cron triggers
- **Mentions:** `@source-name` and `@skill-name` to reference at runtime

### Advanced Features
- Deep linking (`craftagents://` scheme)
- Large response auto-summarization (Claude Haiku for >60KB)
- Diff viewer (VS Code-style multi-file changes)
- File attachments (images, PDFs, Office docs)
- Cascading theme system (app → workspace level)
- Background tasks with progress tracking
- Remote server mode (headless + thin client via WebSocket)

## Functional Requirements

### FR-1: Session Management
- Create, archive, delete sessions
- Status workflow with customizable states
- Session search by title, labels, content
- Persistence to disk (JSONL format)

### FR-2: LLM Connectivity
- Support Claude Agent SDK (Anthropic + custom endpoints)
- Support Pi SDK (Google, OpenAI, GitHub, ChatGPT Plus)
- Token/credential management (OAuth flows + API keys)
- Connection testing & health checks

### FR-3: Tool Integration
- MCP client pool (reuse connections)
- Tool invocation with Zod-validated inputs
- Session-scoped tool definitions
- Tool response streaming & truncation

### FR-4: Permission Enforcement
- Three-tier permission mode system
- Auto-approvals or approval prompts per tool
- Tool-level permission rules
- Permission mode cycling (SHIFT+TAB)

### FR-5: Multi-Provider Support
- Seamless provider switching
- Per-workspace default
- Provider-specific configuration (API endpoints, OAuth flows)
- Model selection per provider

### FR-6: Extensibility
- Custom MCP server support
- Workspace-scoped skills
- Automation event system
- Source configuration & credential storage

## Non-Functional Requirements

### NFR-1: Security
- Credentials encrypted with AES-256-GCM
- Env var filtering for subprocess spawning
- OAuth token management
- HTTPS/TLS for remote server mode
- Credential store health checks

### NFR-2: Performance
- Session load time <1s (even 1000+ sessions)
- Tool response streaming in real-time
- MCP connection pooling (avoid reconnects)
- Large file handling (auto-summarization >60KB)

### NFR-3: Reliability
- Session persistence (JSONL format)
- Crash recovery (restore session state)
- Network resilience (reconnect on WebSocket drop)
- Graceful degradation (tools fail → agent handles)

### NFR-4: Scalability
- Headless server mode for multi-user deployments
- Session replication via WebSocket (thin client)
- Workspace isolation
- Per-session tool pool isolation

### NFR-5: Usability
- One-click OAuth (no manual token entry for OAuth flows)
- Agent-assisted tool setup (no config files)
- Keyboard shortcuts (Cmd+N, Cmd+/, SHIFT+TAB, etc.)
- Inline help & documentation
- Debug logging (~/Library/Logs/@craft-agent/electron/)

## Architecture Principles

1. **Agent-first:** Tool setup, config, and scripting via natural language
2. **Provider-agnostic:** Swap LLM providers without workflow changes
3. **Zero-config defaults:** Works out-of-the-box; advanced customization via UI
4. **Privacy-first:** Credentials encrypted locally; no telemetry
5. **Composable:** Modular packages (core, shared, ui, server-core)
6. **Extensible:** Custom MCP, skills, automations without forking

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Session creation time | <500ms | From UI interaction to input ready |
| Tool response latency (p99) | <5s | Including network round-trip |
| Credential store load time | <100ms | On app startup |
| Session search (1000 sessions) | <100ms | Query response time |
| Permission prompt show time | <200ms | From action to UI visible |
| MCP connection reuse | >80% | Tool calls using pooled connections |
| Crash recovery rate | 100% | Session restoration after crash |
| Subscription provider uptime | >99.5% | For Claude Agent SDK / Pi SDK |

## Tech Stack Summary

| Layer | Technology |
|-------|------------|
| Runtime | Bun |
| Desktop | Electron + React 18 |
| State | Jotai (per-session atoms) |
| UI | shadcn/ui + Tailwind CSS v4 |
| Build | esbuild (main) + Vite (renderer) |
| Credentials | AES-256-GCM file storage |
| Agent SDKs | Claude Agent SDK + Pi SDK |
| MCP | Model Context Protocol SDK v1.24+ |
| Terminal | Node.js + WebSocket RPC |

## Deployment Scenarios

1. **Desktop (packaged):** DMG (macOS), NSIS (Windows), AppImage (Linux)
2. **Desktop (dev):** Hot-reload via Electron + Vite
3. **Headless server:** Docker container or native binary on Linux
4. **Thin client:** Connect to remote server via WebSocket (TLS recommended)
5. **CLI tool:** Terminal WebSocket client for scripting & CI/CD

## Roadmap Status

**Completed (v0.7.1):**
- Multi-provider LLM support
- MCP server integration
- REST API sources
- Permission system (3-level)
- Workspace isolation
- Deep linking
- Automations
- Session tools & skills
- Headless server mode

**In Progress / Planned:**
- UI/UX refinements
- Additional built-in sources
- Performance optimizations
- Enterprise features (SSO, audit logs)
- Extended MCP compatibility

## Configuration

Configuration stored at `~/.craft-agent/`:
```
~/.craft-agent/
├── config.json              # LLM connections, workspaces
├── credentials.enc          # Encrypted API keys
├── preferences.json         # User settings
├── theme.json               # App-level theme
└── workspaces/{id}/
    ├── config.json          # Workspace settings
    ├── theme.json           # Workspace theme override
    ├── automations.json     # Event-driven automations
    ├── sessions/            # JSONL session data
    ├── sources/             # Connected sources
    ├── skills/              # Custom skills
    └── statuses/            # Status configuration
```

## Acceptance Criteria

Feature is production-ready when:
- [ ] Functionality matches specification
- [ ] Tests pass (unit + integration)
- [ ] Type checking passes (`tsc --noEmit`)
- [ ] Security review complete (credentials, env vars, OAuth)
- [ ] Documentation updated (code comments + `/docs`)
- [ ] UI tested on macOS, Windows, Linux
- [ ] Performance benchmarks met
- [ ] No regressions in existing features
