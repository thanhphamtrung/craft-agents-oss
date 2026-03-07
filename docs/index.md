# Craft Agents Documentation Index

Welcome to the Craft Agents documentation. Choose your path based on your role and needs.

## Quick Navigation

### For Product & Business
- **[Project Overview & PDR](./project-overview-pdr.md)** — Product vision, features, requirements, success metrics
- **[Project Roadmap](./project-roadmap.md)** — Version history, planned features, contribution opportunities

### For Developers
- **[Codebase Summary](./codebase-summary.md)** — Monorepo structure, packages, dependency graph
- **[Code Standards](./code-standards.md)** — Coding conventions, security patterns, testing
- **[System Architecture](./system-architecture.md)** — High-level design, process model, data flows

### For Operations & DevOps
- **[Deployment Guide](./deployment-guide.md)** — Development setup, production builds, server deployment, monitoring

### For Designers & Frontend
- **[Design Guidelines](./design-guidelines.md)** — Design system, components, accessibility, themes

### For Users & Integrators
- **[CLI Reference](./cli.md)** — Terminal client commands, examples, scripting patterns

---

## Documentation Map

```
docs/
├── index.md (this file)
├── project-overview-pdr.md      ← Start here for product context
├── project-roadmap.md            ← See what's planned
├── codebase-summary.md           ← Understand the structure
├── code-standards.md             ← Learn how to write code
├── system-architecture.md        ← Understand how it works
├── deployment-guide.md           ← Set up & deploy
├── design-guidelines.md          ← Build UI components
└── cli.md                        ← Use the CLI tool
```

---

## Common Scenarios

### "I'm new to Craft Agents — where do I start?"

1. Read **[Project Overview & PDR](./project-overview-pdr.md)** for vision and features
2. Watch the demo video in README.md
3. Follow **[Deployment Guide](./deployment-guide.md)** local dev setup
4. Explore **[Codebase Summary](./codebase-summary.md)** to understand structure

**Time:** 30 minutes

### "I need to contribute code"

1. Read **[Code Standards](./code-standards.md)** for conventions
2. Review **[Codebase Summary](./codebase-summary.md)** for file organization
3. Check **[System Architecture](./system-architecture.md)** to understand data flow
4. Follow build/test commands in **[Deployment Guide](./deployment-guide.md)**

**Time:** 1 hour (first time only)

### "I need to deploy to production"

1. Review **[System Architecture](./system-architecture.md)** — understand deployment scenarios
2. Follow **[Deployment Guide](./deployment-guide.md)** — server setup, TLS, Docker/Kubernetes
3. Check security checklist in **[Deployment Guide](./deployment-guide.md)**

**Time:** 2-4 hours depending on platform

### "I need to implement a feature"

1. Check **[Project Roadmap](./project-roadmap.md)** — is it planned?
2. Review **[System Architecture](./system-architecture.md)** — where does it fit?
3. Read **[Code Standards](./code-standards.md)** — implementation patterns
4. Consult **[Codebase Summary](./codebase-summary.md)** — related files to modify

**Time:** Depends on feature complexity

### "I need to build a custom UI component"

1. Review **[Design Guidelines](./design-guidelines.md)** — design system
2. Check component examples in same file
3. Follow **[Code Standards](./code-standards.md)** — React patterns
4. Test dark mode & accessibility

**Time:** 30 minutes

### "I need to integrate an external service"

1. Check **[System Architecture](./system-architecture.md)** — Sources & MCP section
2. Review **[Codebase Summary](./codebase-summary.md)** — packages/shared structure
3. Look for examples in packages/shared/src/sources/
4. Read MCP spec at https://modelcontextprotocol.io

**Time:** 1-3 hours depending on service

### "I need to write a CLI script"

1. Review **[CLI Reference](./cli.md)** — available commands
2. Check examples section in **[CLI Reference](./cli.md)**
3. Use `--json` flag for machine-readable output in scripts

**Time:** 30 minutes

---

## Documentation by Topic

### Product & Vision
- [x] Product vision & goals (project-overview-pdr.md)
- [x] Feature matrix (project-overview-pdr.md)
- [x] Success metrics (project-overview-pdr.md, project-roadmap.md)
- [x] Roadmap & planned features (project-roadmap.md)
- [x] Release history (project-roadmap.md)

### Architecture & Design
- [x] System architecture (system-architecture.md)
- [x] Process model (system-architecture.md)
- [x] Data flow (system-architecture.md)
- [x] Security (system-architecture.md, code-standards.md)
- [x] Design system (design-guidelines.md)
- [x] Component library (design-guidelines.md)
- [x] Accessibility (design-guidelines.md)

### Code & Development
- [x] Codebase structure (codebase-summary.md)
- [x] TypeScript conventions (code-standards.md)
- [x] React patterns (code-standards.md)
- [x] File organization (code-standards.md, codebase-summary.md)
- [x] Error handling (code-standards.md)
- [x] Testing (code-standards.md)
- [x] Security patterns (code-standards.md)
- [x] Performance patterns (code-standards.md)

### Deployment & Operations
- [x] Local dev setup (deployment-guide.md)
- [x] Building from source (deployment-guide.md)
- [x] Production packaging (deployment-guide.md)
- [x] Headless server (deployment-guide.md)
- [x] Docker deployment (deployment-guide.md)
- [x] Kubernetes deployment (deployment-guide.md)
- [x] TLS & security (deployment-guide.md)
- [x] Monitoring & troubleshooting (deployment-guide.md)
- [x] CLI usage (cli.md)

### Missing / Future Documentation
- [ ] API reference (RPC channels)
- [ ] MCP integration guide
- [ ] Skill development guide
- [ ] Automation examples
- [ ] Migration guides
- [ ] Performance benchmarks
- [ ] Video tutorials

---

## File Statistics

| Document | LOC | Size | Focus |
|----------|-----|------|-------|
| project-overview-pdr.md | 232 | 8.7 KB | Product & requirements |
| codebase-summary.md | 439 | 16 KB | Monorepo structure |
| code-standards.md | 674 | 17 KB | Coding conventions |
| system-architecture.md | 612 | 23 KB | System design |
| project-roadmap.md | 224 | 7.3 KB | Features & timeline |
| deployment-guide.md | 581 | 13 KB | Setup & operations |
| design-guidelines.md | 635 | 15 KB | Design system |
| cli.md | 240 | 8.2 KB | CLI reference |
| **Total** | **3,637** | **108 KB** | **Complete coverage** |

---

## Search by Keyword

**Architecture & Design:**
- System architecture → system-architecture.md
- Process model → system-architecture.md
- Data flow → system-architecture.md
- Permission system → system-architecture.md
- Theme system → design-guidelines.md
- Accessibility → design-guidelines.md

**Code & Development:**
- TypeScript conventions → code-standards.md
- React patterns → code-standards.md
- Error handling → code-standards.md
- Testing → code-standards.md
- Security → code-standards.md
- File organization → codebase-summary.md, code-standards.md

**Deployment & Operations:**
- Development setup → deployment-guide.md
- Production build → deployment-guide.md
- Docker → deployment-guide.md
- Kubernetes → deployment-guide.md
- TLS → deployment-guide.md
- Monitoring → deployment-guide.md
- Troubleshooting → deployment-guide.md
- CLI → cli.md

**Product & Roadmap:**
- Product vision → project-overview-pdr.md
- Features → project-overview-pdr.md, project-roadmap.md
- Roadmap → project-roadmap.md
- Success metrics → project-overview-pdr.md, project-roadmap.md

---

## Tips for Documentation Maintenance

### Keeping Docs Current
1. Update docs when code changes significantly
2. Run `bun run typecheck:all` to ensure TypeScript examples are valid
3. Verify links quarterly (especially to external resources)
4. Update version numbers when releasing

### Contributing Documentation
1. Follow Markdown style in existing files
2. Keep files under 800 LOC (split if needed)
3. Use clear headers and table of contents
4. Include real code examples, not pseudocode
5. Test all CLI commands before documenting
6. Verify all cross-references are valid

### Feedback & Improvements
- Found an error? → Open a GitHub issue
- Have a suggestion? → GitHub discussions
- Want to contribute? → See CONTRIBUTING.md

---

## External Resources

**Official:**
- [GitHub Repository](https://github.com/lukilabs/craft-agents-oss)
- [Craft.do Website](https://craft.do)
- [Craft Agents Website](https://agents.craft.do)

**Technical Specs:**
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io)
- [Claude Agent SDK](https://www.npmjs.com/package/@anthropic-ai/claude-agent-sdk)
- [Electron Documentation](https://www.electronjs.org/docs)
- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)

**Community:**
- GitHub Issues: [lukilabs/craft-agents-oss/issues](https://github.com/lukilabs/craft-agents-oss/issues)
- GitHub Discussions: [lukilabs/craft-agents-oss/discussions](https://github.com/lukilabs/craft-agents-oss/discussions)

---

## Version History

**v0.7.1** (Current)
- Complete documentation suite
- 6 new documentation files
- ~3,600 lines of technical docs

**v0.7.0 and earlier**
- CLI reference (cli.md)
- README.md with quick start

---

## Document Accessibility

All documentation files are:
- ✓ Plain Markdown (.md format)
- ✓ Readable in any text editor
- ✓ Searchable with standard tools (grep, ripgrep)
- ✓ Linkable with relative paths
- ✓ Versionable in Git

---

**Last Updated:** March 7, 2026

**Maintained By:** Documentation Team

**Next Review:** After v0.8 release or when docs gaps identified
