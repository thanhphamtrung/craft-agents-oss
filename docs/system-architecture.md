# System Architecture

**Version:** 0.7.1 | **Deployment Modes:** Desktop, Headless, CLI

## High-Level Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                      User Facing Layer                          │
├────────────────────────────────────────────────────────────────┤
│  Desktop App (Electron)    │    CLI (WebSocket)    │    Web SPA  │
│  Main + Preload + Renderer │    Terminal Client    │    Viewer   │
└────────────────┬───────────────────────────────────┬────────────┘
                 │                                   │
                 └─────────────────┬─────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │  Transport Layer            │
                    │  WebSocket RPC (IPC/WS)    │
                    └──────────────┬──────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
┌───────▼─────────────┐  ┌────────▼────────┐  ┌─────────────▼────┐
│   Session Manager   │  │ RPC Handlers    │  │  Config & Auth   │
│   (Execution)       │  │  (Command API)  │  │  (State Storage) │
└───────┬─────────────┘  └────────┬────────┘  └─────────┬────────┘
        │                         │                      │
        └─────────────┬───────────┴──────────────────────┘
                      │
        ┌─────────────┴──────────────────┐
        │   Business Logic Layer          │
        ├─────────────────────────────────┤
        │ • Agent (Claude + Pi SDKs)      │
        │ • Tool Invocation               │
        │ • MCP Client Pool               │
        │ • Permission Checking           │
        │ • Session Persistence           │
        │ • OAuth & Credentials           │
        └─────────────┬────────────────────┘
                      │
        ┌─────────────┴──────────────────┐
        │   External Services             │
        ├─────────────────────────────────┤
        │ • Claude Agent SDK              │
        │ • Pi Agent SDK                  │
        │ • MCP Servers (stdio/network)   │
        │ • REST APIs (Gmail, Slack, etc) │
        │ • Databases (local/remote)      │
        └─────────────────────────────────┘
```

## Process Architecture (Desktop Mode)

```
┌─────────────────────────────────────────────────────┐
│                  Electron Main Process               │
├─────────────────────────────────────────────────────┤
│ • Window Management                                 │
│ • IPC Router (send/on)                              │
│ • Preload Context Bridge                            │
│ • Subprocess Management                             │
│   - MCP servers (stdio)                             │
│   - Pi agent server                                 │
│   - Doc tools (pdf-tool, xlsx-tool, etc.)           │
│ • Credential Storage (AES-256-GCM)                  │
│ • File I/O (sessions, config, preferences)          │
└──────────────────────────┬──────────────────────────┘
                           │ IPC
        ┌──────────────────┴──────────────────┐
        │                                     │
┌───────▼──────────────────┐  ┌──────────────▼──────────┐
│  Preload Context Bridge   │  │  Renderer (React UI)    │
├───────────────────────────┤  ├───────────────────────┤
│ • Controlled IPC API      │  │ • Session List        │
│ • Type-Safe Channel Calls │  │ • Chat View           │
│ • No Direct File Access   │  │ • Settings            │
│ • No Direct Node APIs     │  │ • Jotai State (atoms) │
└───────────────────────────┘  └───────────────────────┘
```

**Why Multi-Process:**
- **Security:** Preload isolates main process from renderer
- **Stability:** Renderer crash doesn't kill main process
- **Performance:** UI updates don't block IPC handlers
- **Separation of Concerns:** UI logic vs. runtime logic

## Communication Patterns

### Electron (IPC)
```
Renderer (React)
    ↓
Preload (contextBridge)
    ↓
Main Process (IPC handlers)
    ↓
Business Logic (agent, MCP, credentials)
```

**Example IPC Call:**
```typescript
// Renderer (React component)
const result = await ipc.invoke("sessions:create", { name: "My Session" });

// Preload (contextBridge)
contextBridge.exposeInMainWorld("ipc", {
  invoke: (channel, args) => ipcRenderer.invoke(channel, args),
});

// Main Process (IPC handler)
ipcMain.handle("sessions:create", async (event, { name }) => {
  const session = await sessionManager.create(name);
  return session;
});
```

### Server (WebSocket RPC)
```
CLI / Thin Client
    ↓ WebSocket
Server (WsRpcServer)
    ↓
RPC Handlers
    ↓
Business Logic (agent, MCP, credentials)
```

**RPC Channel Pattern:**
```typescript
// Client sends
ws.send(JSON.stringify({
  id: "123",
  channel: "sessions:create",
  args: { name: "My Session" }
}));

// Server receives, routes to handler
const handler = handlers[channel]; // e.g., handlers["sessions:create"]
const result = await handler(args);

// Server sends response
ws.send(JSON.stringify({
  id: "123",
  result: session,
  error: null
}));
```

## Agent Execution Flow

```
User sends message
        │
        ▼
┌──────────────────────┐
│ Create Message Event │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ Permission Check                     │
│ (safe/ask/allow-all mode)            │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ Invoke Agent (Claude or Pi SDK)       │
│ • Inject system prompt               │
│ • Inject tools (MCP + session-tools) │
│ • Stream response                    │
└──────────┬───────────────────────────┘
           │
       ┌───┴───────────────────────┐
       │                           │
       ▼                           ▼
   Text Event              Tool Use Event
   (text_delta)            (invoke tool)
       │                           │
       ▼                           ▼
  ┌─────────────┐    ┌───────────────────────┐
  │ Append to   │    │ Tool Invocation       │
  │ message     │    │ 1. Validate input     │
  │ history     │    │ 2. Permission check   │
  │             │    │ 3. Invoke (MCP/sess) │
  │             │    │ 4. Stream result      │
  └─────────────┘    └───────────┬───────────┘
       │                         │
       │             ┌───────────▼──────────┐
       │             │ Large Response?      │
       │             │ (>60KB)              │
       │             └───────────┬──────────┘
       │                         │
       │             ┌───────────┴──────────┐
       │             │ Yes: Summarize       │
       │             │ (Claude Haiku)       │
       │             │ No: Pass as-is       │
       │             └───────────┬──────────┘
       │                         │
       ▼                         ▼
   ┌─────────────────────────────┐
   │ Agent Continues Loop        │
   │ (until done)                │
   └─────────────┬───────────────┘
                 │
                 ▼
         ┌──────────────┐
         │ Save Session │
         │ (JSONL)      │
         └──────────────┘
```

## MCP Client Pool Architecture

```
┌─────────────────────────────────────┐
│      MCP Client Pool                │
├─────────────────────────────────────┤
│                                     │
│  Map<serverId, MCPClient>           │
│                                     │
│  "linear" ──▶ MCPClient (connected) │
│  "github" ──▶ MCPClient (connected) │
│  "custom" ──▶ MCPClient (connected) │
│                                     │
└─────────────────────────────────────┘
           │
        ┌──┴──┐
        │     │
    ┌───▼──┐ ┌──▼───┐
    │Stdio │ │Network│
    │MCP   │ │MCP    │
    └───┬──┘ └───┬───┘
        │        │
        ▼        ▼
    Subprocess  URL Connection
    (local)     (remote/craft)
```

**Connection Strategy:**
- Pool reuses connections per server (avoid reconnects)
- Automatic reconnect on failure
- Per-session tool invocation
- Request queuing (prevent concurrent calls to same tool)

## Permission System (3-Level)

```
Request to execute tool
        │
        ▼
┌──────────────────────┐
│ Check Permission Mode│
└──────────┬───────────┘
           │
    ┌──────┼──────┐
    │      │      │
    ▼      ▼      ▼
  safe   ask  allow-all
    │      │      │
    ▼      ▼      ▼
  Block  Prompt  Allow
  All    User    All
    │      │      │
    └──────┼──────┘
           │
           ▼
    ┌─────────────┐
    │ Tool Result │
    └─────────────┘
```

**Tool-Level Rules:**
```typescript
interface ToolPermission {
  tool: string;
  mode: "safe" | "ask" | "allow-all" | "block";
  requiresApproval?: boolean;
}

// E.g., "execute_bash" might be "ask" or "block"
// "send_email" might be "ask"
// "read_file" might be "safe"
```

**SHIFT+TAB Cycling:**
- User presses SHIFT+TAB to cycle: safe → ask → allow-all → safe
- Changes affect current session
- Persisted in session config

## Session Lifecycle

```
CREATE
  │
  ├─ Generate ID (UUID)
  ├─ Create JSONL file
  ├─ Initialize atoms
  └─ Return Session object

ACTIVE (chat loop)
  │
  ├─ User sends message
  ├─ Invoke agent (with MCP tools)
  ├─ Append events to JSONL
  ├─ Update Jotai state (for UI)
  └─ Repeat until user exits

ARCHIVE / RESTORE
  │
  ├─ Move to archive folder
  ├─ Mark as archived in config
  └─ Unarchive by moving back

DELETE
  │
  ├─ Delete JSONL file
  ├─ Delete session atom state
  └─ Remove from session list
```

**JSONL Format (Session Persistence):**
```jsonl
{"type":"message","role":"user","text":"Hello","timestamp":"2024-03-07T10:30:00Z"}
{"type":"message","role":"assistant","text":"Hi there!","timestamp":"2024-03-07T10:30:05Z"}
{"type":"tool_use","tool":"send_email","input":{"to":"user@example.com"},"timestamp":"2024-03-07T10:30:10Z"}
{"type":"tool_result","tool":"send_email","result":"Email sent","timestamp":"2024-03-07T10:30:15Z"}
```

## Data Flow (Example: Send Message with Tool Use)

```
User types "Check my email" in chat
    │
    ▼
MessageInput.tsx (React component)
    │ onSend (callback)
    ▼
useSession hook
    │ sessionAtom (Jotai)
    ▼
ipc.invoke("sessions:sendMessage", { sessionId, text })
    │
    ▼ [Electron IPC]
    │
Main Process (IPC handler)
    │ sessions:sendMessage handler
    ▼
SessionManager.executeMessage(sessionId, text)
    │
    ├─ Retrieve session from JSONL
    ├─ Check permission mode
    ▼
CraftAgent.invoke(tools, systemPrompt, messages)
    │
    ├─ Call Claude Agent SDK
    ├─ Stream events (text_delta, tool_use, etc.)
    │
    └─ For each event:
        │
        ├─ text_delta → Append to session message
        │   │
        │   └─ ipc.send("session:event", event)
        │       │
        │       └─ Renderer receives, updates UI (Jotai)
        │
        └─ tool_use → Invoke tool
            │
            ├─ Check permission (safe/ask/allow-all)
            ├─ Get tool from MCP pool
            ├─ Invoke tool with input
            ├─ Handle large responses (>60KB summarize)
            │
            └─ ipc.send("session:toolResult", { tool, result })
                │
                └─ Renderer receives, updates UI

All events appended to JSONL file on disk
```

## Authentication & Credential Flow

```
User adds LLM connection
    │
    ▼
┌─────────────────────────────┐
│ Credential Input Method     │
├─────────────────────────────┤
│ 1. API Key (form input)     │
│ 2. OAuth (browser redirect) │
│ 3. Token (paste)            │
└─────────┬───────────────────┘
          │
          ▼
┌──────────────────────────────────┐
│ Encrypt with AES-256-GCM         │
│ • Derive key from machine info   │
│ • Generate random nonce          │
│ • Authenticate + encrypt         │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Store in credentials.enc         │
│ (~/.craft-agent/credentials.enc) │
└──────────┬───────────────────────┘
           │
           ▼
At runtime (session execution)
           │
           ▼
┌──────────────────────────────────┐
│ Load credentials.enc             │
│ Decrypt credentials              │
│ Inject into agent SDK            │
└──────────────────────────────────┘
```

**OAuth Flows:**
1. **Anthropic (Claude Max/Pro):** Device code → token
2. **Google (Gmail, Calendar):** Redirect → auth code → access token
3. **Slack:** OAuth redirect → access token
4. **Microsoft:** OAuth redirect → access token
5. **GitHub Copilot:** Device code → access token
6. **ChatGPT Plus (Codex):** OAuth redirect → access token

## Event-Driven Automations

```
Event occurs (LabelAdd, SchedulerTick, etc.)
        │
        ▼
┌──────────────────────────┐
│ Check automations.json   │
│ for matching rules       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Evaluate matcher         │
│ (regex, cron pattern)    │
└────────────┬─────────────┘
             │
        ┌────┴────┐
        │          │
    Match      No Match
        │          │
        ▼          ▼
    Execute    (skip)
    action
        │
        ▼
┌──────────────────────────┐
│ Action types:            │
│ 1. Prompt (create        │
│    agent session)        │
│ 2. Webhook (future)      │
│ 3. Email (future)        │
└────────────┬─────────────┘
             │
             ▼
Create session with prompt
(expand $variables like $CRAFT_LABEL)
```

**Supported Events:**
- `SchedulerTick` — Cron schedule
- `LabelAdd` / `LabelRemove` — Label changes
- `SessionStatusChange` — Status workflow
- `PermissionModeChange` — Permission toggle
- `PreToolUse` / `PostToolUse` — Tool invocation
- `SessionStart` / `SessionEnd` — Session lifecycle
- `FlagChange` — Session flagging

## Headless Server Architecture

```
Headless Server (packages/server)
        │
        ├─ WsRpcServer (WebSocket)
        │   ├─ /sessions/create
        │   ├─ /sessions/list
        │   ├─ /sessions/sendMessage
        │   ├─ /sources/get
        │   ├─ /skills/create
        │   └─ ... (40+ RPC channels)
        │
        ├─ Runtime
        │   ├─ SessionManager (execution)
        │   ├─ CredentialStore (AES encryption)
        │   ├─ MCPClientPool (tool integration)
        │   └─ ConfigStore (workspaces, etc.)
        │
        └─ External
            ├─ Claude Agent SDK
            ├─ Pi SDK
            ├─ MCP servers (stdio/network)
            └─ REST APIs
```

**Thin Client:** Desktop Electron connects to server over WebSocket
- All business logic runs on server
- UI runs on client
- Credentials stored on server

## Theme System (Cascading)

```
Default Theme (bundled)
        │
        ▼
App Theme (~/.craft-agent/theme.json)
        │
        ├─ Override: colors, fonts, spacing
        │
        ▼
Workspace Theme (~/.craft-agent/workspaces/{id}/theme.json)
        │
        └─ Override: colors, fonts, spacing

Final Theme = Merge all levels (workspace > app > default)
```

**Theme JSON:**
```json
{
  "colors": {
    "primary": "#2563eb",
    "background": "#ffffff",
    "text": "#000000"
  },
  "fonts": {
    "body": "system-ui",
    "mono": "Monaco"
  }
}
```

## Deployment Architectures

### Desktop (Packaged)
```
User Machine
    │
    ├─ Craft Agents App (DMG/NSIS/AppImage)
    │   ├─ Electron binary
    │   ├─ bundled assets
    │   └─ bundled tools (pdf-tool, etc.)
    │
    └─ ~/.craft-agent/ (user data)
        ├─ config.json
        ├─ credentials.enc
        ├─ workspaces/
        └─ ...
```

### Headless Server + Thin Client
```
Server Machine (Linux VPS)
    │
    ├─ Server binary (standalone)
    ├─ WebSocket listener (ws://:9100)
    └─ ~/.craft-agent/ (server data)
        ├─ config.json
        ├─ credentials.enc
        └─ workspaces/

                    ↑ WebSocket (TLS optional)
                    │

Client Machine
    │
    └─ Thin Client Mode (Electron)
        └─ CRAFT_SERVER_URL=wss://server:9100
           CRAFT_SERVER_TOKEN=<token>
```

### Docker
```
Docker Container
    │
    ├─ Server binary
    ├─ WebSocket listener
    │
    └─ Volume mounts
        ├─ -v craft-data:/root/.craft-agent (state)
        ├─ -v ./certs:/certs:ro (TLS certs)
        └─ -e CRAFT_SERVER_TOKEN=<token>
```

## Summary

**Key Architectural Decisions:**

1. **Multi-process Electron:** Security (preload isolation) + stability
2. **MCP Client Pool:** Connection reuse + performance
3. **Jotai atomFamily:** Per-session state isolation
4. **AES-256-GCM Credentials:** Local encryption without server secrets
5. **WebSocket RPC:** Unified transport for desktop IPC & remote server
6. **JSONL Session Persistence:** Append-only, human-readable, crash-safe
7. **Dual Agent SDK:** Claude (Anthropic) + Pi (Google/OpenAI) abstraction
8. **3-Level Permissions:** Fine-grained control over tool execution
9. **Event-Driven Automations:** Extensible workflow orchestration
10. **Headless Mode:** Multi-user deployments without UI-specific code

This architecture enables:
- **Offline Capability:** Sessions persist locally
- **Privacy:** Credentials never leave device
- **Scalability:** Headless server for teams
- **Extensibility:** Custom MCP servers & skills
- **Flexibility:** Multiple LLM providers at once
