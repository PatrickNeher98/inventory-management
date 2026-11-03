# Design Tokens and CSS Skeleton

Put the tokens on `:root` in the global stylesheet (**This repo**: the global `<style>` in `client/src/App.vue`).

```css
:root {
  /* Spacing (4/8px grid) */
  --space-1: 4px;  --space-2: 8px;  --space-3: 12px;
  --space-4: 16px; --space-6: 24px; --space-8: 32px; --space-12: 48px;

  /* Radius */
  --radius-sm: 6px; --radius-md: 8px; --radius-lg: 12px; --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.06);
  --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.08);
  --shadow-lg: 0 12px 32px rgba(15, 23, 42, 0.16);

  /* Slate palette */
  --color-slate-900: #0f172a;  /* primary text, sidebar background */
  --color-slate-700: #334155;
  --color-slate-500: #64748b;  /* muted text */
  --color-slate-300: #cbd5e1;  /* muted text on dark sidebar (contrast) */
  --color-slate-200: #e2e8f0;  /* borders */
  --color-slate-50:  #f8fafc;  /* app background */
  --color-surface:   #ffffff;
  --color-accent:    #3b82f6;

  /* Status */
  --color-green:  #16a34a; --color-green-soft:  #dcfce7;
  --color-blue:   #2563eb; --color-blue-soft:   #dbeafe;
  --color-yellow: #ca8a04; --color-yellow-soft: #fef9c3;
  --color-red:    #dc2626; --color-red-soft:    #fee2e2;

  /* Typography */
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans JP", sans-serif;
  --text-xs: 12px; --text-sm: 13px; --text-base: 14px;
  --text-md: 16px; --text-lg: 20px; --text-xl: 24px;
  --weight-regular: 400; --weight-medium: 500; --weight-semibold: 600;

  /* Layout */
  --sidebar-width: 240px;
  --sidebar-width-collapsed: 72px;
  --topbar-height: 60px;
  --content-max-width: 1360px;

  /* Layers */
  --z-topbar: 20; --z-backdrop: 40; --z-sidebar: 50;
}
```

## Shell skeleton

```css
.app-shell { display: flex; min-height: 100vh; background: var(--color-slate-50); font-family: var(--font-sans); color: var(--color-slate-900); }

.sidebar {
  position: fixed; inset: 0 auto 0 0; z-index: var(--z-sidebar);
  width: var(--sidebar-width); display: flex; flex-direction: column;
  background: var(--color-slate-900); color: var(--color-slate-300);
  transition: width 0.2s ease, transform 0.2s ease;
}
.collapsed .sidebar { width: var(--sidebar-width-collapsed); }

.app-main {
  flex: 1; min-width: 0; margin-left: var(--sidebar-width);
  display: flex; flex-direction: column; height: 100vh;
  transition: margin-left 0.2s ease;
}
.collapsed .app-main { margin-left: var(--sidebar-width-collapsed); }

.topbar {
  position: sticky; top: 0; z-index: var(--z-topbar); height: var(--topbar-height);
  display: flex; align-items: center; gap: var(--space-4); padding: 0 var(--space-6);
  background: var(--color-surface); border-bottom: 1px solid var(--color-slate-200);
}
.content { flex: 1; overflow-y: auto; padding: var(--space-6); }
.content > * { max-width: var(--content-max-width); margin-inline: auto; }

.nav-link {
  display: flex; align-items: center; gap: var(--space-3); min-height: 40px;
  padding: 0 var(--space-3); border-radius: var(--radius-md);
  color: inherit; text-decoration: none; font-size: var(--text-base); font-weight: var(--weight-medium);
}
.nav-link:hover { background: rgba(255, 255, 255, 0.06); color: #fff; }
.nav-link.router-link-active { background: rgba(255, 255, 255, 0.12); color: #fff; }
:focus-visible { outline: 2px solid var(--color-accent); outline-offset: 2px; }

@media (max-width: 767px) {
  .sidebar { transform: translateX(-100%); width: var(--sidebar-width); }
  .drawer-open .sidebar { transform: none; box-shadow: var(--shadow-lg); }
  .app-main, .collapsed .app-main { margin-left: 0; }
  .content { padding: var(--space-4); }
}
@media (prefers-reduced-motion: reduce) { .sidebar, .app-main { transition: none; } }
```

Notes: use `.router-link-exact-active` for the `/` route to avoid it matching everywhere. Collapsed rail hides label text with a visually-hidden pattern (not `display: none` on the element carrying `aria-label`).
