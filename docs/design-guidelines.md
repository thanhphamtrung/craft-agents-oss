# Design Guidelines

**Version:** 0.7.1 | **Design System:** shadcn/ui + Tailwind CSS v4

## Design Philosophy

Craft Agents prioritizes:
- **Clarity over decoration** — Minimize visual noise
- **Consistency** — Predictable patterns across UI
- **Accessibility** — Keyboard-navigable, screen-reader friendly
- **Responsiveness** — Works on different screen sizes
- **Dark mode first** — Beautiful in both light and dark themes

## Theme System

### Theme Structure

Themes are JSON files stored at:
- **App-level:** `~/.craft-agent/theme.json`
- **Workspace-level:** `~/.craft-agent/workspaces/{id}/theme.json`

**Theme JSON Schema:**
```json
{
  "colors": {
    "primary": "#2563eb",
    "secondary": "#7c3aed",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "background": "#ffffff",
    "surface": "#f9fafb",
    "text": "#111827",
    "textSecondary": "#6b7280",
    "border": "#e5e7eb"
  },
  "fonts": {
    "body": "system-ui, -apple-system, sans-serif",
    "mono": "Menlo, Monaco, 'Courier New', monospace"
  },
  "spacing": {
    "xs": "0.25rem",
    "sm": "0.5rem",
    "md": "1rem",
    "lg": "1.5rem",
    "xl": "2rem"
  },
  "radius": {
    "sm": "0.375rem",
    "md": "0.5rem",
    "lg": "0.75rem",
    "full": "9999px"
  }
}
```

### Built-in Themes

**Light Mode:**
- Colors: Neutral grays, blue accent
- Background: `#ffffff`
- Text: `#111827` (dark gray)

**Dark Mode:**
- Colors: Slate/gray-9xxx, blue accent
- Background: `#0f172a` (dark slate)
- Text: `#f1f5f9` (light slate)

**High Contrast (Accessibility):**
- Increased contrast ratios (WCAG AAA)
- Simplified color palette
- No color-only signaling

### Cascading Theme Application

```
Default Theme (bundled)
    ↓
App Theme Override (~/.craft-agent/theme.json)
    ↓
Workspace Theme Override (~/.craft-agent/workspaces/{id}/theme.json)
    ↓
Final Theme (merged)
```

**Usage in React:**
```typescript
import { useTheme } from "./hooks/useTheme";

export function MyComponent() {
  const theme = useTheme();

  return (
    <div
      style={{
        backgroundColor: theme.colors.background,
        color: theme.colors.text,
      }}
    >
      ...
    </div>
  );
}
```

## Component Library (shadcn/ui)

All UI components extend shadcn/ui base components with custom styling.

### Core Components

**Typography:**
```typescript
// Heading styles
<h1 className="text-3xl font-bold">Page Title</h1>
<h2 className="text-2xl font-semibold">Section Title</h2>
<h3 className="text-xl font-semibold">Subsection</h3>
<p className="text-sm text-gray-600">Body text</p>
<p className="text-xs text-gray-500">Small text (captions)</p>
```

**Buttons:**
```typescript
// Primary action
<button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
  Primary
</button>

// Secondary action
<button className="bg-gray-200 hover:bg-gray-300 text-gray-900 px-4 py-2 rounded">
  Secondary
</button>

// Danger action
<button className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded">
  Delete
</button>

// Icon button (no text)
<button
  aria-label="Close"
  className="p-2 hover:bg-gray-100 rounded transition"
>
  <XIcon size={20} />
</button>
```

**Cards:**
```typescript
<div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-800">
  <h3 className="text-lg font-semibold mb-2">Card Title</h3>
  <p className="text-gray-600 dark:text-gray-400">Content here</p>
</div>
```

**Inputs:**
```typescript
<input
  type="text"
  placeholder="Enter text..."
  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
/>

<textarea
  placeholder="Enter message..."
  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
/>
```

**Badges & Tags:**
```typescript
// Status badge
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
  Active
</span>

// Label badge
<span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200">
  <TagIcon size={12} />
  Important
</span>
```

## Layout Patterns

### Sidebar + Main Content

```typescript
<div className="flex h-screen">
  <aside className="w-64 border-r border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 overflow-y-auto">
    {/* Sidebar content */}
  </aside>
  <main className="flex-1 flex flex-col">
    <header className="border-b border-gray-200 dark:border-gray-800 p-4">
      {/* Header */}
    </header>
    <div className="flex-1 overflow-y-auto">
      {/* Main content */}
    </div>
  </main>
</div>
```

### Panel System (Resizable)

```typescript
import { PanelGroup, Panel, PanelResizeHandle } from "react-resizable-panels";

<PanelGroup direction="horizontal">
  <Panel defaultSize={25} minSize={20}>
    {/* Left panel */}
  </Panel>
  <PanelResizeHandle className="w-1 bg-gray-300 dark:bg-gray-700 hover:bg-blue-500" />
  <Panel defaultSize={75} minSize={50}>
    {/* Right panel */}
  </Panel>
</PanelGroup>
```

### Modal / Overlay

```typescript
<div className="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center z-50">
  <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg p-6 max-w-md w-full mx-4">
    <h2 className="text-xl font-semibold mb-4">Dialog Title</h2>
    <p className="text-gray-600 dark:text-gray-400 mb-6">Dialog content</p>
    <div className="flex gap-3 justify-end">
      <button className="px-4 py-2 rounded bg-gray-200 dark:bg-gray-700 hover:bg-gray-300">
        Cancel
      </button>
      <button className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white">
        Confirm
      </button>
    </div>
  </div>
</div>
```

## Chat UI Patterns

### Message Bubble (User)

```typescript
<div className="flex justify-end">
  <div className="max-w-2xl bg-blue-600 text-white rounded-lg rounded-tr-none px-4 py-3">
    <p className="text-sm">{message.text}</p>
    <span className="text-xs text-blue-200 mt-1 block">
      {new Date(message.timestamp).toLocaleTimeString()}
    </span>
  </div>
</div>
```

### Message Bubble (Assistant)

```typescript
<div className="flex justify-start">
  <div className="max-w-2xl bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg rounded-tl-none px-4 py-3">
    <p className="text-sm">{message.text}</p>
    <span className="text-xs text-gray-500 dark:text-gray-400 mt-1 block">
      {new Date(message.timestamp).toLocaleTimeString()}
    </span>
  </div>
</div>
```

### Tool Result Display

```typescript
<div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded p-3 my-3">
  <div className="flex items-center gap-2 mb-2">
    <WrenchIcon size={16} className="text-orange-600" />
    <span className="text-sm font-medium">Tool: send_email</span>
  </div>
  <pre className="text-xs bg-gray-900 dark:bg-black text-green-400 p-2 rounded overflow-x-auto">
    {toolResult}
  </pre>
</div>
```

## Color Palette

### Primary Colors
| Use | Light | Dark |
|-----|-------|------|
| Primary action | `#2563eb` (blue-600) | `#3b82f6` (blue-500) |
| Primary hover | `#1d4ed8` (blue-700) | `#60a5fa` (blue-400) |
| Secondary | `#7c3aed` (violet-600) | `#a78bfa` (violet-400) |

### Semantic Colors
| Use | Light | Dark |
|-----|-------|------|
| Success | `#10b981` (emerald-600) | `#34d399` (emerald-400) |
| Warning | `#f59e0b` (amber-600) | `#fbbf24` (amber-400) |
| Danger | `#ef4444` (red-600) | `#f87171` (red-400) |
| Info | `#0ea5e9` (sky-500) | `#0284c7` (sky-600) |

### Neutral Colors
| Use | Light | Dark |
|-----|-------|------|
| Background | `#ffffff` (white) | `#0f172a` (slate-950) |
| Surface | `#f9fafb` (gray-50) | `#1e293b` (slate-900) |
| Border | `#e5e7eb` (gray-200) | `#334155` (slate-700) |
| Text | `#111827` (gray-900) | `#f1f5f9` (slate-100) |
| Text secondary | `#6b7280` (gray-500) | `#94a3b8` (slate-400) |

## Spacing System

**Tailwind Spacing Scale (rem → px):**
```
xs: 0.25rem (4px)
sm: 0.5rem (8px)
md: 1rem (16px)
lg: 1.5rem (24px)
xl: 2rem (32px)
2xl: 2.5rem (40px)
3xl: 3rem (48px)
```

**Usage:**
```typescript
// Padding
className="p-4"      // All sides
className="px-4"     // Horizontal
className="py-2"     // Vertical
className="pt-4"     // Top
className="pb-4"     // Bottom

// Margin
className="m-4"      // All sides
className="mx-auto"  // Center horizontally
className="mb-2"     // Bottom

// Gap (flexbox)
className="gap-4"    // Between flex items
className="gap-x-2"  // Horizontal
className="gap-y-4"  // Vertical
```

## Typography Scale

```
Display: text-5xl font-bold        (3rem, 48px)
Heading 1: text-4xl font-bold      (2.25rem, 36px)
Heading 2: text-3xl font-semibold  (1.875rem, 30px)
Heading 3: text-2xl font-semibold  (1.5rem, 24px)
Heading 4: text-xl font-semibold   (1.25rem, 20px)
Body: text-base                    (1rem, 16px)
Small: text-sm                     (0.875rem, 14px)
Caption: text-xs                   (0.75rem, 12px)
```

**Font Families:**
- **Body:** `system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- **Monospace:** `'Menlo', 'Monaco', 'Courier New', monospace`

## Iconography

**Icon Source:** Lucide React (consistent, modern icons)

**Icon Sizes:**
```typescript
<IconComponent size={16} />  // xs (compact)
<IconComponent size={20} />  // sm (default)
<IconComponent size={24} />  // md (prominent)
<IconComponent size={32} />  // lg (large)
<IconComponent size={40} />  // xl (very large)
```

**Usage in Buttons:**
```typescript
// Icon only
<button aria-label="Delete">
  <TrashIcon size={20} />
</button>

// Icon + text
<button className="flex items-center gap-2">
  <CheckIcon size={20} />
  Save
</button>

// Text + icon
<button className="flex items-center gap-2">
  Send
  <SendIcon size={20} />
</button>
```

## Accessibility

### Keyboard Navigation

- **Tab:** Navigate between focusable elements
- **Shift+Tab:** Navigate backwards
- **Enter:** Activate button/link
- **Space:** Toggle checkbox/radio
- **Arrow keys:** Navigate select/radio options
- **Escape:** Close modal/popover

### Semantic HTML

```typescript
// Good: Semantic elements
<button>Click me</button>
<a href="/page">Link</a>
<nav>Navigation</nav>
<main>Main content</main>
<section>Section</section>

// Avoid: Non-semantic
<div onClick={handleClick}>Click me</div>
<div role="button">Click me</div>
```

### ARIA Labels

```typescript
// Icon-only buttons
<button aria-label="Close dialog">
  <XIcon size={20} />
</button>

// Screen reader only text
<span className="sr-only">Loading...</span>

// Descriptions
<input aria-describedby="password-hint" type="password" />
<p id="password-hint">Must be 8+ characters</p>

// Live regions
<div aria-live="polite" aria-atomic="true">
  {notification}
</div>
```

### Color Contrast

- **Text on background:** Minimum WCAG AA (4.5:1 for normal text, 3:1 for large text)
- **Interactive elements:** Minimum 3:1 contrast
- **No color-only signaling:** Use icons, text, patterns

**Test with:** WebAIM Contrast Checker

## Animation & Transitions

**Prefer subtle, purpose-driven animations:**

```typescript
// Fade in
className="animate-fade-in"

// Smooth transition
className="transition-all duration-200"

// Hover effect
className="hover:opacity-80 transition-opacity"

// Loading spinner
<Loader className="animate-spin" size={24} />

// Skeleton (placeholder)
<div className="bg-gray-200 dark:bg-gray-700 animate-pulse rounded h-10 w-full" />
```

**Avoid:**
- Auto-playing videos
- Flashing/strobing effects
- Motion that lasts >3s without pause

## Dark Mode

### Implementation

```typescript
// Tailwind dark mode (class strategy)
<html className="dark">
  <body className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
    ...
  </body>
</html>
```

### Color Mapping

```typescript
// Light → Dark
className="bg-white dark:bg-gray-900"
className="text-gray-900 dark:text-white"
className="border-gray-200 dark:border-gray-800"
className="bg-blue-600 dark:bg-blue-500"  // Adjust for dark
```

### Testing Dark Mode

Press `Cmd+Shift+D` in Electron dev tools to toggle dark mode.

## Responsive Design

### Breakpoints (Tailwind)
```
sm: 640px   (tablets)
md: 768px   (tablets+)
lg: 1024px  (desktops)
xl: 1280px  (large desktops)
2xl: 1536px (ultra-wide)
```

### Mobile-First Approach

```typescript
// Default (mobile)
className="w-full p-2"
// Tablet up
className="sm:w-1/2 sm:p-4"
// Desktop up
className="lg:w-1/3 lg:p-6"
```

### Common Patterns

```typescript
// Stack on mobile, flex on desktop
className="flex flex-col lg:flex-row gap-4"

// Hide on small screens
className="hidden lg:block"

// Text size responsive
className="text-sm sm:text-base lg:text-lg"

// Grid responsive
className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4"
```

## Form Design

### Input Field

```typescript
<div className="space-y-2">
  <label className="block text-sm font-medium">Email</label>
  <input
    type="email"
    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
    placeholder="user@example.com"
  />
  <p className="text-xs text-gray-500">We'll never share your email.</p>
</div>
```

### Checkbox

```typescript
<label className="flex items-center gap-2 cursor-pointer">
  <input type="checkbox" className="rounded" />
  <span className="text-sm">I agree to the terms</span>
</label>
```

### Select / Dropdown

```typescript
<select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
  <option>Choose an option</option>
  <option value="1">Option 1</option>
  <option value="2">Option 2</option>
</select>
```

### Form Validation

```typescript
<div className="space-y-2">
  <input
    type="text"
    className={clsx(
      "w-full px-3 py-2 border rounded-md",
      error
        ? "border-red-500 focus:ring-red-500"
        : "border-gray-300 focus:ring-blue-500"
    )}
  />
  {error && <p className="text-xs text-red-600">{error}</p>}
</div>
```

## Motion & Micro-interactions

### Loading State

```typescript
<button disabled className="opacity-50 cursor-not-allowed flex items-center gap-2">
  <Loader size={16} className="animate-spin" />
  Loading...
</button>
```

### Success Feedback

```typescript
<div className="flex items-center gap-2 text-green-600">
  <CheckCircleIcon size={20} />
  <span>Saved successfully</span>
</div>
```

### Error State

```typescript
<div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded p-3 text-red-800 dark:text-red-100">
  <div className="flex items-center gap-2">
    <AlertCircleIcon size={20} />
    <span className="font-medium">Error message here</span>
  </div>
</div>
```

## Summary

**Design Principles:**
1. Use Tailwind CSS for all styling
2. Follow shadcn/ui component patterns
3. Support both light and dark modes
4. Ensure keyboard navigation
5. Maintain consistent spacing & typography
6. Use color semantically (not just aesthetically)
7. Keep animations subtle and purposeful
8. Test on mobile, tablet, and desktop

**Resources:**
- [Tailwind CSS v4 Docs](https://tailwindcss.com/docs)
- [shadcn/ui Components](https://ui.shadcn.com/)
- [Lucide Icons](https://lucide.dev/)
- [WCAG Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
