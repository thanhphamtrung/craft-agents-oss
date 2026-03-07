# Project Roadmap

**Current Version:** 0.7.1 | **Release Date:** March 2025 | **License:** Apache 2.0

## Version History

| Version | Release Date | Focus |
|---------|--------------|-------|
| 0.5.0 | ~Nov 2024 | Initial release (MVP) |
| 0.5.1 | ~Dec 2024 | Stability fixes |
| 0.6.0 | ~Jan 2025 | Permission system, Automations |
| 0.7.0 | ~Feb 2025 | Multi-provider support, Headless server |
| 0.7.1 | Mar 2025 | Bug fixes, performance |

## Completed Features (v0.7.1)

### Core Chat Engine
- [x] Multi-session inbox with workflow status
- [x] Real-time streaming (text_delta, tool_use, tool_result)
- [x] Message history persistence (JSONL format)
- [x] Session search & filtering
- [x] Session flagging & archiving
- [x] Session labeling (auto + manual)

### LLM Connectivity
- [x] Claude Agent SDK integration
- [x] Pi SDK integration (Google AI Studio, ChatGPT Plus, GitHub Copilot)
- [x] Custom endpoints (OpenRouter, Vercel AI Gateway, Ollama, self-hosted)
- [x] API key & OAuth token management
- [x] Per-workspace default provider selection
- [x] Connection health checks

### Tool Integration
- [x] MCP server support (stdio + network)
- [x] MCP client pooling (connection reuse)
- [x] Session-scoped tool definitions (session-tools-core)
- [x] Tool response streaming
- [x] Large response auto-summarization (>60KB)
- [x] Tool error handling & graceful degradation

### Sources (Data Integration)
- [x] MCP servers (Craft, Linear, GitHub, Notion, custom)
- [x] REST APIs (Google OAuth: Gmail, Calendar, Drive)
- [x] REST APIs (Slack, Microsoft)
- [x] Local filesystem & Obsidian vaults
- [x] Custom API setup (OpenAPI specs)
- [x] Source credentials (encrypted storage)

### Permission System
- [x] Three-level mode: safe (read-only), ask (prompt), allow-all (auto)
- [x] Per-tool permission rules
- [x] SHIFT+TAB permission mode cycling
- [x] Approval prompts for sensitive tools
- [x] Permission persistence per session

### Advanced Features
- [x] Skills (workspace-scoped agent instructions)
- [x] Automations (event-driven with cron triggers)
- [x] Deep linking (craftagents:// URL scheme)
- [x] Multi-file diff viewer
- [x] File attachments (images, PDFs, Office docs)
- [x] Cascading theme system (app + workspace level)
- [x] Background tasks with progress tracking
- [x] Markdown rendering (Shiki, Mermaid, LaTeX, PDF)
- [x] Terminal output (ANSI color parsing)

### Server & Deployment
- [x] Headless server mode (WebSocket RPC)
- [x] CLI client (craft-cli)
- [x] TLS support (wss://)
- [x] Docker deployment
- [x] Multi-user sessions
- [x] Remote server + thin client mode

## In Progress / Next (v0.8)

### Performance & UX
- [ ] Optimize session list rendering (1000+ sessions)
- [ ] Improve tool response latency (p99 <5s target)
- [ ] Keyboard shortcuts improvements
- [ ] Session preview (hover tooltip)
- [ ] Inline help & tooltips

### Developer Experience
- [ ] Plugin API for custom tools
- [ ] Skill marketplace / sharing
- [ ] CLI tool improvements (better error messages)
- [ ] Better debug logging

### UI Refinements
- [ ] Dark mode improvements
- [ ] Session grouping by workspace
- [ ] Customizable status workflow
- [ ] Accessibility audit (WCAG AA)

## Planned Features (v0.9+)

### Enterprise Features
- [ ] Team workspaces (shared sessions)
- [ ] Permission delegation (admin roles)
- [ ] Audit logging (action history)
- [ ] SSO integration (SAML, OAuth 2.0)
- [ ] Custom branding (logo, colors)

### Extended Sources
- [ ] Database connections (Postgres, MySQL, SQLite)
- [ ] Custom API template system
- [ ] Webhook support (receive → create session)
- [ ] S3 integration
- [ ] Cloud storage (OneDrive, iCloud)

### Advanced Agent Features
- [ ] Agent-to-agent communication
- [ ] Multi-agent orchestration
- [ ] Custom instruction templates
- [ ] Context window optimization
- [ ] Thinking level control (extended thinking)

### Content & Knowledge
- [ ] Session transcript search (full-text + semantic)
- [ ] Knowledge base ingestion
- [ ] Session summarization
- [ ] Auto-tagging / categorization
- [ ] Content federation (multi-workspace search)

### Mobile & Web
- [ ] Web app version (PWA)
- [ ] iOS / Android companion apps
- [ ] Session sync across devices
- [ ] Responsive design improvements

## Known Limitations & Workarounds

| Issue | Status | Workaround |
|-------|--------|-----------|
| Large file attachments (>100MB) | Known | Split files or use cloud storage + links |
| Real-time collab. (multi-user editing) | Not planned | Use turn-based workflow |
| Offline mode (no server) | Partial | Desktop app works offline, server requires connection |
| GPU acceleration (local models) | Future | Use OpenRouter with local model providers |
| Native mobile apps | Future | Web PWA available |

## Release Criteria

A release is ready when:
- [x] All planned features implemented
- [x] Type checking passes (`tsc --noEmit`)
- [x] Tests pass (unit + integration)
- [x] Security review complete (credentials, OAuth, env vars)
- [x] No regressions in existing features
- [x] Documentation updated
- [x] Performance benchmarks met
- [x] Cross-platform tested (macOS, Windows, Linux)

## Success Metrics (2025)

| Metric | Target | Current |
|--------|--------|---------|
| GitHub stars | 3K+ | ~1.5K |
| Monthly active users | 5K+ | Growing |
| Community extensions | 10+ | 3-5 |
| Enterprise deployments | 20+ | <5 |
| Docs coverage | 90%+ | 75% |
| Test coverage | 80%+ | 70% |
| Crash-free rate | 99.9%+ | 99%+ |

## Roadmap Priorities

### Q1 2025 (v0.8)
1. Performance optimization (session list, tool latency)
2. UX refinements (keyboard shortcuts, preview, help)
3. Developer experience (better debugging, examples)
4. Documentation improvements

### Q2 2025 (v0.9)
1. Enterprise features (teams, audit logs, SSO)
2. Extended sources (databases, webhooks)
3. Knowledge management (search, summarization)
4. Accessibility audit & fixes

### Q3 2025 (v1.0)
1. Mobile/web companion apps
2. Advanced agent features (multi-agent, thinking levels)
3. Marketplace / plugin system
4. Performance targets (p99 latency <2s)

## Contribution Opportunities

For community contributors:

**Help Wanted:**
- [ ] Additional source integrations (Jira, Asana, etc.)
- [ ] Language translations
- [ ] Documentation improvements
- [ ] Bug fixes & performance optimizations
- [ ] Custom MCP server examples
- [ ] UI/UX improvements

**Good First Issues:**
- [ ] Error message improvements
- [ ] Documentation typos
- [ ] Test coverage for edge cases
- [ ] Accessibility enhancements

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## Feedback & Feature Requests

- **GitHub Issues:** [Feature requests tagged `enhancement`](https://github.com/lukilabs/craft-agents-oss/issues?q=label%3Aenhancement)
- **Discussions:** [Community discussions](https://github.com/lukilabs/craft-agents-oss/discussions)
- **Craft Agents Sessions:** Share feedback via Craft Agents itself

## Long-Term Vision (2026+)

**Craft Agents aims to become:**
- The de-facto standard for human-AI agent collaboration
- A platform for building complex agent workflows
- A marketplace for AI-powered tools & integrations
- The foundation for agent-native applications

**North Star Metrics:**
- Trusted by 100K+ developers & knowledge workers
- Enabling billions in value creation through automation
- Open-source ecosystem with 50+ community integrations
- Enterprise standard for AI workflow orchestration
