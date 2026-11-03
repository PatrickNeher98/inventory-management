---
name: saas-redesign
description: Redesign a Vue 3 application's UI into a modern SaaS-style interface with a vertical left navigation sidebar (instead of a top nav bar), design tokens, consistent spacing and a polished professional look. Use when asked to modernize the layout, add a sidebar, or apply a SaaS/dashboard redesign.
---

# SaaS Redesign (Left Sidebar Layout)

Turns a Vue 3 app with a top nav bar into a SaaS-style shell: left sidebar, slim top bar, scrollable content. Generic for any Vue 3 + vue-router app; repo-specific notes are marked **This repo**.

Token values and CSS skeleton: `references/tokens.md`.

## 0. Process rules (read first)

- **ANY .vue creation or significant change MUST be delegated to the `vue-expert` subagent.** The orchestrating session only coordinates. Give vue-expert this skill's path plus the discovery results.
- Before touching anything run `git status` / `git diff` on `App.vue`, the router file, locale files and views. If they have uncommitted changes, another session may be editing them: stop and coordinate (ask the user) before editing `App.vue` or `main.js`. Never overwrite or revert others' edits; build on top of them.
- Use `code-reviewer` after the work for a quality pass.

## 1. Discovery (no editing)

1. Read `App.vue` (current top nav, global styles, layout wrappers).
2. Read the router definition (**This repo**: `client/src/main.js`; `Backlog.vue` has no route, do not add one).
3. Read global styles (**This repo**: styles live in `client/src/App.vue`) and any CSS variables already present.
4. Read the i18n setup (**This repo**: `composables/useI18n.js`, `locales/en.js`, `locales/ja.js`, `t('a.b.c')`).
5. Identify existing shell components to keep (**This repo**: `FilterBar`, `ProfileMenu`, `LanguageSwitcher`) and where they are mounted.
6. **Map route -> i18n key (explicit step).** Labels cannot be derived generically from the router. Take the nav entries from the existing `App.vue` markup instead of inventing them, and cross-check against the router so no route is missed or invented. Produce a table: route path, current label, `nav.*` key. **This repo**: `App.vue` uses `t('nav.*')` keys, but "Reports" is hardcoded English. Migrate every hardcoded label to a `nav.*` key (e.g. `nav.reports`) in both `en.js` and `ja.js`. Another session may be adding `/restocking` with `nav.restocking`: include it if present in `App.vue`/`main.js` at apply time, and never duplicate or redefine the key. Iterate with `v-for` keyed by route `path`.
7. **Active state**: this repo marks active links with `:class="{ active: $route.path === '...' }"`. Keep supporting that class: style `.nav-link.active, .nav-link.router-link-active` together (or keep the existing binding when using `<router-link>`). Do not remove either mechanism.
8. **Before applying**, run `git status` and `git diff` on `App.vue`, `main.js` and `client/src/locales/*`; re-read them immediately before editing, since other sessions are changing them.

## 2. Design tokens

Define all tokens as CSS custom properties on `:root` (see `references/tokens.md`):

- Spacing scale on a 4/8px grid: 4, 8, 12, 16, 24, 32, 48.
- Radius (sm 6, md 8, lg 12), shadows (sm, md, lg), z-index layers.
- Slate palette: `#0f172a` (text/sidebar dark), `#64748b` (muted), `#e2e8f0` (borders), plus a light background (`#f8fafc`) and white surfaces.
- Status colors: green, blue, yellow, red (each with a base and soft background variant).
- Typography scale: 12/13/14/16/20/24px, weights 400/500/600, system font stack.
- Replace hardcoded colors/paddings in the shell with tokens. Do not mass-rewrite view styles unless asked; map existing values to tokens opportunistically.

## 3. Layout

Structure in `App.vue`:

```
<div class="app-shell" :class="{ collapsed, 'drawer-open': drawerOpen }">
  <aside class="sidebar">  brand / <nav aria-label="Main"> items / footer </aside>
  <div class="app-main">
    <header class="topbar"> hamburger, page title, filters </header>
    <main class="content"> <router-view/> </main>
  </div>
</div>
```

- **Sidebar**: fixed, full height, ~240px wide; collapsible to an icon rail ~72px (labels hidden visually, kept in `title`/`aria-label`). Collapse state persisted in `localStorage` (guard reads with try/catch, default expanded).
- **Brand** at top (logo mark as inline SVG + app name from i18n).
- **Nav items**: icon + label, 40px min height, active state styled via `.router-link-active` / `.router-link-exact-active` (use exact for the root `/` route).
- **Footer**: profile menu and language switcher (reuse existing components; restyle for the dark/light sidebar, do not rewrite their logic). Collapse toggle button lives here or in the brand row.
- **Top bar**: slim (56-64px), sticky; shows current page title (from route meta or the nav label via `t()`), and hosts the filter bar (**This repo**: `FilterBar` stays as is and shares the singleton refs).
- **Main content**: the only scrolling region (`overflow-y: auto`), `max-width` ~1280-1440px, centered, padding `var(--space-6)` (24px), `var(--space-4)` on mobile.
- **Responsive (< 768px)**: sidebar becomes an off-canvas drawer (`transform: translateX(-100%)`), opened by a hamburger button in the top bar, with a backdrop. Close on backdrop click, Escape, and route change. Rail collapse is ignored on mobile. Respect `prefers-reduced-motion`.

## 4. Accessibility

- `<aside>` plus `<nav aria-label="...">` landmark (label via i18n); `<main>` landmark; `<header>` for the top bar.
- Active link gets `aria-current="page"` (router-link does this automatically for exact-active; verify in the DOM).
- Visible `:focus-visible` outline (2px, offset 2px, high-contrast color) on every interactive element; never `outline: none` without a replacement.
- Everything keyboard operable: hamburger and collapse buttons are real `<button>` with `aria-label`, `aria-expanded`, `aria-controls`. Drawer: Escape closes, return focus to hamburger.
- Text contrast at least 4.5:1 (muted `#64748b` on white passes; check it on dark sidebar backgrounds and use a lighter slate there). Icons are decorative: `aria-hidden="true"`.

## 5. Repo rules

- **No emojis in UI.** Use inline SVG icons (stroke `currentColor`, 20px, `stroke-width` 1.75). No icon library needed.
- **New UI strings need keys in both `client/src/locales/en.js` and `ja.js`** (e.g. `nav.collapse`, `nav.openMenu`, `nav.main`). Locale files may be edited by others: re-read right before editing and add only your keys.
- Unique `v-for` keys (route path, `sku`, `month`), never the index.
- Keep `FilterBar`, `ProfileMenu`, `LanguageSwitcher` working with their current props/events.
- **Do not modify the shared filter singleton** (`client/src/composables/useFilters.js`).
- Currency/locale behavior is unchanged. Do not touch the backend. Do not commit a lockfile or private registry URLs (repo is public).

## 6. Verification

1. Ensure servers are running (`/start` skill or `./scripts/start.sh`).
2. Use Playwright MCP (`mcp__playwright__*`) at `http://localhost:3000`:
   - Desktop (e.g. 1440x900): screenshot every route; check active state, collapse/expand, reload persists collapse.
   - Mobile (e.g. 390x844): screenshot closed and open drawer; check hamburger, backdrop, close on navigation.
   - Check the console for errors; tab through the sidebar to confirm focus rings.
   - Switch to `ja` and confirm labels fit and nothing overflows.
3. Run `cd client && npm run build` and confirm it succeeds.

## 7. Final checklist

- [ ] Uncommitted changes in `App.vue`/router/locales checked; no clash with another session
- [ ] Nav items taken from existing App.vue, route -> `nav.*` key table done, hardcoded labels (e.g. Reports) migrated to both locales, `/restocking` included if present
- [ ] Active state works via `.active` and/or `.router-link-active`
- [ ] Tokens defined as CSS custom properties (spacing, radius, shadow, slate, status, type)
- [ ] Left sidebar 240px, collapses to 72px rail, state in `localStorage`
- [ ] Brand top, footer with profile + language switcher, slim top bar with title + filters
- [ ] Main content scrolls, max-width and consistent padding
- [ ] Drawer + hamburger under 768px; closes on Escape, backdrop, route change
- [ ] `nav` landmark, `aria-current`, `:focus-visible`, keyboard operable, contrast OK
- [ ] No emojis; inline SVG icons only
- [ ] New strings in both `en.js` and `ja.js`
- [ ] Unique `v-for` keys; `useFilters.js` untouched; existing components still work
- [ ] .vue work done by `vue-expert`; `code-reviewer` run
- [ ] Playwright desktop + mobile screenshots reviewed; `npm run build` passes
