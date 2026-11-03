# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Factory Inventory Management System Demo with GitHub integration - Full-stack application with Vue 3 frontend, Python FastAPI backend, and in-memory mock data (no database).

> ⚠️ **This repository and any fork you create are PUBLIC.** Do not commit credentials, internal hostnames, or private registry URLs. `client/.npmrc` pins the public npm registry and `client/package-lock.json` is gitignored to prevent locally-configured registries from leaking into commits — leave both in place.

## Critical Tool Usage Rules

### Subagents
Use the Task tool with these specialized subagents for appropriate tasks:

- **vue-expert**: Use for Vue 3 frontend features, UI components, styling, and client-side functionality
  - Examples: Creating components, fixing reactivity issues, performance optimization, complex state management
  - **MANDATORY RULE: ANY time you need to create or significantly modify a .vue file, you MUST delegate to vue-expert**
- **code-reviewer**: Use after writing significant code to review quality and best practices
- **Explore**: Use for understanding codebase structure, searching for patterns, or answering questions about how components work
- **general-purpose**: Use for complex multi-step tasks or when other agents don't fit

### Skills
- **backend-api-test** skill: Use when writing or modifying tests in `tests/backend` directory with pytest and FastAPI TestClient

### MCP Tools
- **ALWAYS use GitHub MCP tools** (`mcp__github__*`) for ALL GitHub operations
  - Exception: Local branches only - use `git checkout -b` instead of `mcp__github__create_branch`
- **ALWAYS use Playwright MCP tools** (`mcp__playwright__*`) for browser testing
  - Test against: `http://localhost:3000` (frontend), `http://localhost:8001` (API)

## Stack
- **Frontend**: Vue 3 + Composition API + Vite (port 3000)
- **Backend**: Python FastAPI (port 8001)
- **Data**: JSON files in `server/data/` loaded via `server/mock_data.py`

## Commands

```bash
# Start / stop both servers (or use the /start and /stop skills)
./scripts/start.sh
./scripts/stop.sh

# Backend only (port 8001, API docs at /docs)
cd server && uv sync && uv run python main.py

# Frontend only (port 3000) - run `npm install` first, otherwise `vite: command not found`
cd client && npm install && npm run dev
cd client && npm run build        # production build -> client/dist/

# Backend tests (pytest config lives in tests/, so run from there)
cd tests && uv run --project ../server pytest
cd tests && uv run --project ../server pytest backend/test_inventory.py::TestName::test_name   # single test
cd tests && uv run --project ../server pytest --cov=../server                                  # coverage

# Regenerate JSON mock data
cd server && uv run python generate_data.py
```

There is no frontend test suite and no linter configured.

## Architecture

- **No database.** `server/mock_data.py` loads every `server/data/*.json` file into module-level lists at import time. `server/main.py` imports them directly and filters in memory (`apply_filters`, `filter_by_month`). Changes are never persisted; restart the server to reload edited JSON.
- **Backend** is a single file, `server/main.py`: Pydantic models, CORS (`*`), and all routes. Most list endpoints use `response_model`, so JSON fields not declared in the model are silently dropped. Dashboard summary and reports endpoints compute aggregates on the fly.
- **Frontend API base URL is hardcoded** to `http://localhost:8001/api` in `client/src/api.js` (no Vite proxy). Each method there maps filter objects to query params and skips values equal to `'all'`.
- **Shared filter state** is a module-level singleton in `client/src/composables/useFilters.js` (4 refs). `getCurrentFilters()` converts it to API params (period becomes `month`). Views and `FilterBar.vue` share the same refs, so changing a filter anywhere affects every view.
- **i18n**: `composables/useI18n.js` with `locales/en.js` and `locales/ja.js` (`t('a.b.c')`, falls back to English). Locale is stored in `localStorage` and drives the currency (en -> USD, ja -> JPY, see `utils/currency.js`). New UI strings need keys in both locale files.
- **Routing** is in `client/src/main.js`. `Backlog.vue` exists in `views/` but has no route registered.
- **Tests** (`tests/backend/`) use FastAPI `TestClient` through the `client` fixture in `conftest.py`, which puts `server/` on `sys.path`. Tests run against the real JSON data.
- `.claude/` holds project subagents, slash commands and the `backend-api-test` skill used by the rules above.

## Key Patterns

**Filter System**: 4 filters (Time Period, Warehouse, Category, Order Status) apply to all data via query params
**Data Flow**: Vue filters → `client/src/api.js` → FastAPI → In-memory filtering → Pydantic validation → Computed properties
**Reactivity**: Raw data in refs (`allOrders`, `inventoryItems`), derived data in computed properties

## API Endpoints
- `GET /api/inventory` - Filters: warehouse, category
- `GET /api/orders` - Filters: warehouse, category, status, month
- `GET /api/dashboard/summary` - All filters
- `GET /api/demand`, `/api/backlog` - No filters
- `GET /api/spending/*` - Summary, monthly, categories, transactions

## Common Issues
1. Use unique keys in v-for (not `index`) - use `sku`, `month`, etc.
2. Validate dates before `.getMonth()` calls
3. Update Pydantic models when changing JSON data structure
4. Inventory filters don't support month (no time dimension)
5. Revenue goals: $800K/month single, $9.6M YTD all months

## File Locations
- Views: `client/src/views/*.vue`
- API Client: `client/src/api.js`
- Backend: `server/main.py`, `server/mock_data.py`
- Data: `server/data/*.json`
- Styles: `client/src/App.vue`

## Design System
- Colors: Slate/gray (#0f172a, #64748b, #e2e8f0)
- Status: green/blue/yellow/red
- Charts: Custom SVG, CSS Grid for layouts
- No emojis in UI
