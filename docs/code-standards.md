# Code Standards & Conventions

**Version:** 0.7.1 | **Language:** TypeScript/React | **Runtime:** Bun

## Overview

Craft Agents follows TypeScript/React best practices with a focus on readability, maintainability, and type safety. This document describes conventions for writing consistent, self-documenting code.

## File Naming Conventions

### TypeScript/JavaScript
- **Format:** kebab-case with descriptive names (longer is better for LLM discoverability)
- **Examples:**
  - `session-manager.ts` (not `sessionMgr.ts`)
  - `create-mcp-client-pool.ts` (not `mcpPool.ts`)
  - `aes-256-gcm-encryption.ts` (not `crypto.ts`)
- **Rationale:** Self-documenting for tools like Grep/Glob; LLM-friendly

### React Components
- **Format:** PascalCase (standard React convention)
- **Examples:**
  - `SessionViewer.tsx`
  - `MessageCard.tsx`
  - `PermissionModeToggle.tsx`

### Configuration & Data Files
- **Format:** kebab-case or snake_case per context
- **Examples:**
  - `config.json`, `theme.json`, `automations.json`
  - `session-tools-core.ts` (Zod schema)

## TypeScript Conventions

### Type Definitions
```typescript
// Use explicit types for public APIs
export interface AgentEvent {
  type: "text" | "tool_use" | "tool_result" | "error";
  data: unknown;
  timestamp: Date;
}

// Use type for unions and intersections
export type PermissionMode = "safe" | "ask" | "allow-all";

// Use generics for reusable patterns
export interface Response<T> {
  ok: boolean;
  data?: T;
  error?: string;
}
```

### Naming Rules
- **Interfaces:** PascalCase (e.g., `CraftAgent`, `SessionEvent`)
- **Types:** PascalCase (e.g., `PermissionMode`, `ToolResult`)
- **Constants:** UPPER_SNAKE_CASE (e.g., `MAX_MESSAGE_LENGTH`)
- **Variables/Functions:** camelCase (e.g., `createSession`, `toolHandler`)
- **Private methods:** `_methodName` or `#methodName` (prefer latter)

### Exports
```typescript
// Named exports preferred for discoverability
export { createSession } from "./sessions/create-session.ts";
export { CraftAgent } from "./agent/craft-agent.ts";
export type { SessionEvent } from "./types/index.ts";

// Barrel exports (index.ts) organize submodule APIs
// packages/shared/src/agent/index.ts
export { CraftAgent } from "./craft-agent.ts";
export { PermissionChecker } from "./permission-checker.ts";
export type { PermissionMode } from "./mode-types.ts";
```

### Null/Undefined Handling
```typescript
// Prefer optional chaining & nullish coalescing
const name = user?.profile?.name ?? "Anonymous";

// Use non-null assertion sparingly (only after type narrowing)
if (value) {
  const nonNull = value!.property;
}

// Type guards for discriminated unions
function handleEvent(event: AgentEvent) {
  if (event.type === "tool_use") {
    // event is now narrowed to ToolUseEvent
    const tool = event.tool;
  }
}
```

## React Component Conventions

### Component Structure
```typescript
// File: component-name.tsx
import { FC, ReactNode, useCallback } from "react";

interface ComponentNameProps {
  title: string;
  onAction?: (id: string) => void;
  children?: ReactNode;
}

export const ComponentName: FC<ComponentNameProps> = ({
  title,
  onAction,
  children,
}) => {
  const handleClick = useCallback(() => {
    onAction?.("clicked");
  }, [onAction]);

  return (
    <div>
      <h1>{title}</h1>
      {children}
      <button onClick={handleClick}>Action</button>
    </div>
  );
};
```

### Hooks
```typescript
// Custom hook: use{FeatureName}.ts
import { useAtom } from "jotai";
import { useMemo, useCallback } from "react";
import { sessionAtom } from "../atoms/session-atoms.ts";

export function useSessionData(sessionId: string) {
  const [session] = useAtom(useMemo(() => sessionAtom(sessionId), [sessionId]));

  const getMessages = useCallback(() => {
    return session?.messages ?? [];
  }, [session]);

  return { session, getMessages };
}
```

### Jotai Atoms (State Management)
```typescript
// atoms/session-atoms.ts
import { atomFamily } from "jotai";
import type { Session } from "@craft-agent/core";

// Per-session isolation using atomFamily
export const sessionAtom = atomFamily((sessionId: string) =>
  atom<Session | null>(null)
);

export const sessionMessagesAtom = atomFamily((sessionId: string) =>
  atom<Message[]>([])
);

// Usage in component:
const [session, setSession] = useAtom(sessionAtom(sessionId));
```

**Why Jotai atomFamily:**
- Isolates state per session/workspace ID
- Prevents cross-session contamination
- Efficient garbage collection
- Type-safe with generics

### Styling (Tailwind CSS v4)
```typescript
// Use Tailwind utilities directly in className
<div className="flex flex-col gap-4 p-4 bg-white dark:bg-slate-900 rounded-lg shadow-sm hover:shadow-md transition-shadow">
  <h2 className="text-xl font-semibold text-gray-900">Title</h2>
  <p className="text-sm text-gray-500">Description</p>
</div>

// Reusable class combinations via clsx
import clsx from "clsx";

const buttonClasses = clsx(
  "px-4 py-2 rounded-md font-medium",
  "bg-blue-600 hover:bg-blue-700 text-white",
  "disabled:opacity-50 disabled:cursor-not-allowed",
  "transition-colors"
);

// For complex conditions
className={clsx(
  "base-class",
  {
    "active-class": isActive,
    "disabled-class": isDisabled,
  }
)}
```

### Component Composition
```typescript
// Prefer composition over props drilling
interface PageLayoutProps {
  sidebar: ReactNode;
  main: ReactNode;
  footer?: ReactNode;
}

export const PageLayout: FC<PageLayoutProps> = ({
  sidebar,
  main,
  footer,
}) => (
  <div className="flex gap-4">
    <aside className="w-64">{sidebar}</aside>
    <main className="flex-1">{main}</main>
    {footer && <footer>{footer}</footer>}
  </div>
);

// Usage: pass components as props
<PageLayout
  sidebar={<SidebarNav />}
  main={<MainContent />}
  footer={<AppFooter />}
/>
```

## Credential & Security Patterns

### Credential Storage
```typescript
// Encrypt sensitive data with AES-256-GCM
import { encryptCredentials, decryptCredentials } from "@craft-agent/shared/credentials";

// Storage
const encrypted = await encryptCredentials({
  apiKey: "sk-...",
  token: "oauth-...",
});
fs.writeFileSync("~/.craft-agent/credentials.enc", encrypted);

// Retrieval
const buffer = fs.readFileSync("~/.craft-agent/credentials.enc");
const credentials = await decryptCredentials(buffer);
```

### Environment Variable Filtering
```typescript
// Block sensitive env vars from being passed to subprocesses
const BLOCKED_ENV_VARS = [
  "ANTHROPIC_API_KEY",
  "OPENAI_API_KEY",
  "AWS_SECRET_ACCESS_KEY",
  "GITHUB_TOKEN",
];

function sanitizeEnv(env: Record<string, string>) {
  const sanitized = { ...env };
  BLOCKED_ENV_VARS.forEach((key) => {
    delete sanitized[key];
  });
  return sanitized;
}
```

### OAuth Token Management
```typescript
// Store tokens securely
interface OAuthToken {
  accessToken: string;
  refreshToken?: string;
  expiresAt: number;
}

// Encrypt before storage
async function saveOAuthToken(provider: string, token: OAuthToken) {
  const encrypted = await encryptCredentials(token);
  // Store in credentials.enc with provider key
}
```

## Error Handling Patterns

### Try-Catch with Type Safety
```typescript
// Define error types
interface ErrorResponse {
  code: string;
  message: string;
  statusCode?: number;
}

async function fetchSession(id: string): Promise<Session> {
  try {
    const response = await fetch(`/api/sessions/${id}`);
    if (!response.ok) {
      throw new Error(`Session not found: ${response.status}`);
    }
    return response.json();
  } catch (error) {
    if (error instanceof NetworkError) {
      // Handle network error
    } else if (error instanceof TimeoutError) {
      // Handle timeout
    } else {
      // Log unexpected error
      console.error("Unexpected error:", error);
      throw new Error("Failed to fetch session");
    }
  }
}
```

### Result Type Pattern (for business logic)
```typescript
// Use Result<T, E> for operations that can fail
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

async function createSession(name: string): Promise<Result<Session, Error>> {
  if (!name.trim()) {
    return { ok: false, error: new Error("Session name required") };
  }

  try {
    const session = await api.createSession({ name });
    return { ok: true, value: session };
  } catch (error) {
    return { ok: false, error: error as Error };
  }
}

// Usage with pattern matching
const result = await createSession("My Session");
if (result.ok) {
  console.log("Created:", result.value);
} else {
  console.error("Error:", result.error.message);
}
```

## Testing Patterns

### Bun Test (TypeScript)
```typescript
// file.test.ts - co-located with source
import { describe, it, expect, beforeEach, mock } from "bun:test";
import { CraftAgent } from "./craft-agent.ts";

describe("CraftAgent", () => {
  let agent: CraftAgent;

  beforeEach(() => {
    agent = new CraftAgent({
      name: "test-agent",
      model: "claude-opus",
    });
  });

  it("should create a session", async () => {
    const session = await agent.createSession("test");
    expect(session.id).toBeDefined();
    expect(session.title).toBe("test");
  });

  it("should handle tool errors gracefully", async () => {
    const toolError = () => {
      throw new Error("Tool execution failed");
    };

    expect(toolError).toThrow();
  });
});
```

### Vitest (for React components)
```typescript
// component.test.tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { SessionViewer } from "./SessionViewer.tsx";

describe("SessionViewer", () => {
  it("should render messages", () => {
    const messages = [{ id: "1", text: "Hello" }];
    render(<SessionViewer messages={messages} />);

    expect(screen.getByText("Hello")).toBeInTheDocument();
  });

  it("should send message on button click", () => {
    const onSend = vi.fn();
    render(<SessionViewer onSend={onSend} />);

    fireEvent.click(screen.getByText("Send"));
    expect(onSend).toHaveBeenCalled();
  });
});
```

## Import Organization

```typescript
// Order imports: stdlib → external → internal → relative
import fs from "fs";
import path from "path";

import { atomFamily } from "jotai";
import { FC, useCallback } from "react";

import type { Session } from "@craft-agent/core";
import { CraftAgent } from "@craft-agent/shared";

import { sessionAtom } from "../atoms/session-atoms.ts";
import { useSession } from "../hooks/use-session.ts";

// Avoid circular imports:
// ✓ a.ts → b.ts → c.ts (linear)
// ✗ a.ts → b.ts → a.ts (circular)
```

## Code Comments

### When to Comment
```typescript
// Good: Explains *why*, not *what*
// Recursive approach because the tool schema can be arbitrarily nested
function resolveToolSchema(schema: ToolSchema): ResolvedSchema {
  // ...
}

// Poor: States the obvious
// Get the user ID
const userId = user.id;
```

### JSDoc for Public APIs
```typescript
/**
 * Create a new session with optional initialization.
 *
 * @param name - Display name for the session
 * @param options - Additional configuration (workspace ID, provider)
 * @returns Promise resolving to the created Session
 * @throws {ValidationError} If name is empty or too long
 *
 * @example
 * ```ts
 * const session = await createSession("My Project", {
 *   workspaceId: "ws-123",
 *   provider: "claude"
 * });
 * ```
 */
export async function createSession(
  name: string,
  options?: SessionOptions
): Promise<Session> {
  // ...
}
```

### Type Comments for Complex Types
```typescript
// AgentEvent can be one of several event types depending on execution stage
type AgentEvent =
  | { type: "text_delta"; text: string }
  | { type: "tool_use"; tool: ToolCall }
  | { type: "tool_result"; result: ToolResult }
  | { type: "error"; error: Error };
```

## Zod Schema Patterns

```typescript
import { z } from "zod";

// Define validation schemas for external input
export const CreateSessionSchema = z.object({
  name: z.string().min(1).max(100),
  workspaceId: z.string().uuid(),
  permissionMode: z.enum(["safe", "ask", "allow-all"]).default("ask"),
  provider: z.string().optional(),
});

export type CreateSessionInput = z.infer<typeof CreateSessionSchema>;

// Use in functions
async function createSession(input: unknown) {
  const validated = CreateSessionSchema.parse(input);
  // validated is now type-safe
}

// Tool schemas for MCP
export const SendMessageToolSchema = z.object({
  sessionId: z.string().describe("Session ID"),
  message: z.string().describe("User message"),
  sources: z.array(z.string()).optional().describe("@mentions"),
});
```

## Performance Patterns

### Memoization (React)
```typescript
import { useMemo, useCallback } from "react";

function SessionList({ sessions, filter }) {
  // Memoize expensive computation
  const filteredSessions = useMemo(
    () => sessions.filter((s) => s.title.includes(filter)),
    [sessions, filter]
  );

  // Memoize callback to prevent child re-renders
  const handleSelect = useCallback(
    (id: string) => {
      onSelectSession(id);
    },
    [onSelectSession]
  );

  return (
    // Pass memoized callback to prevent SessionItem re-renders
    <SessionItem key={s.id} session={s} onSelect={handleSelect} />
  );
}
```

### Connection Pooling (MCP)
```typescript
// Reuse MCP connections instead of creating per-request
class MCPClientPool {
  private clients = new Map<string, MCPClient>();

  async getClient(serverId: string): Promise<MCPClient> {
    if (!this.clients.has(serverId)) {
      this.clients.set(serverId, await MCPClient.connect(serverId));
    }
    return this.clients.get(serverId)!;
  }

  async cleanup() {
    for (const client of this.clients.values()) {
      await client.disconnect();
    }
    this.clients.clear();
  }
}
```

## Module Pattern (Server-Side)

```typescript
// modules/sessions.ts - Encapsulate business logic
import type { Session } from "@craft-agent/core";

export class SessionRepository {
  constructor(private dataDir: string) {}

  async create(name: string): Promise<Session> {
    const id = generateId();
    const session = { id, name, createdAt: new Date() };
    await this.save(session);
    return session;
  }

  async getById(id: string): Promise<Session | null> {
    // Load from disk
  }

  async delete(id: string): Promise<void> {
    // Delete from disk
  }

  private async save(session: Session): Promise<void> {
    // Append to JSONL
  }
}

// Export factory
export function createSessionRepository(dataDir: string) {
  return new SessionRepository(dataDir);
}
```

## Linting & Formatting

### ESLint (Shared & UI)
```bash
bun run lint:shared          # Check packages/shared
bun run lint:ui              # Check packages/ui
bun run lint                 # Check all
```

**Enforced Rules:**
- No `var` declarations (use `const`/`let`)
- No direct file opens (use IPC in Electron)
- No hardcoded paths (use path utilities)
- No localStorage (use config storage)
- No direct platform checks (use abstraction layer)
- React hooks dependencies correct

### Custom ESLint Rules (Electron)
- `no-direct-file-open` — Prevent Electron main/preload from accessing files directly
- `no-direct-navigation-state` — Use Redux/Jotai instead of direct state
- `no-direct-platform-check` — Use platform utility instead of process.platform

## Type Checking

```bash
bun run typecheck             # Check one package
bun run typecheck:all        # Check all packages
bun run typecheck:electron   # Check electron specifically
```

**Strategy:** Strict TypeScript (no `any`, enable strict mode)

## Version Control

### Commit Messages
- Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Example: `feat: add permission mode cycling with SHIFT+TAB`
- No AI references in messages

### Branch Naming
- Feature: `feature/descriptive-name`
- Bug: `fix/descriptive-issue`
- Docs: `docs/descriptive-change`

## Accessibility Standards

### React Components
- Use semantic HTML (`<button>`, `<input>`, `<nav>`)
- Provide `aria-label` for icon-only buttons
- Use `role` attributes for custom widgets
- Keyboard navigation support

```typescript
<button
  aria-label="Delete session"
  onClick={handleDelete}
  onKeyDown={(e) => {
    if (e.key === "Enter" || e.key === " ") {
      handleDelete();
    }
  }}
>
  <TrashIcon />
</button>
```

## Deprecation

When deprecating code:

```typescript
/**
 * @deprecated Use `createNewSession` instead.
 * This function will be removed in v1.0.0.
 */
export function createSession_old(name: string): Session {
  // Keep implementation but mark as deprecated
}
```

## Summary

**Key Principles:**
1. Self-documenting code (clear naming)
2. Type safety (strict TypeScript)
3. Readable over clever (prefer simple)
4. Security first (credential encryption, env filtering)
5. Performance conscious (memoization, pooling)
6. Well-tested (unit + integration tests)
7. Accessible (keyboard + screen readers)

Follow the style guides in ESLint configs and existing code. When in doubt, prioritize clarity over cleverness.
