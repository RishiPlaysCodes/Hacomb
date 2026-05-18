# VIGIL LABS - Complete Professional Documentation

> **Version:** 1.0.0  
> **Last Updated:** May 2026  
> **Author:** RishiPlaysCodes  
> **Purpose:** Beginner-to-Advanced learning guide for understanding and rebuilding the entire VIGIL LABS project

---

## TABLE OF CONTENTS

1. [Project Overview](#1-project-overview)
2. [Complete Architecture Explanation](#2-complete-architecture-explanation)
3. [File-by-File Explanation](#3-file-by-file-explanation)
4. [Line-by-Line Code Explanation](#4-line-by-line-code-explanation)
5. [Feature Implementation Explanation](#5-feature-implementation-explanation)
6. [Commands Documentation](#6-commands-documentation)
7. [Git Documentation](#7-git-documentation)
8. [Learning Roadmap](#8-learning-roadmap)
9. [Use Cases](#9-use-cases)
10. [Developer Guide](#10-developer-guide)
11. [Diagrams](#11-diagrams)
12. [Professional README Content](#12-professional-readme-content)

---

# 1. PROJECT OVERVIEW

## 1.1 What This App Does

VIGIL LABS ek **professional desktop application** hai jo CLI (Command Line Interface) tools ko ek premium graphical interface ke through manage, configure, run, aur monitor karta hai. 

Simple words mein: Agar tum normally terminal mein `nmap -sV 192.168.1.1` type karte ho, toh VIGIL LABS mein tum sirf ek form fill karoge (target IP, scan type select karo) aur "Execute" button click karo - command automatically generate hoga aur live output dikhega.

## 1.2 Main Objective

Ek **unified desktop platform** banana jahan:
- Koi bhi CLI tool GUI se run ho sake
- Tools install/uninstall marketplace se ho sake
- Multiple tools ko chain karke workflows bana sake
- AI automatically tools recommend kare, errors fix kare
- Professional reports generate ho sake
- Sab kuch cross-platform (Kali Linux + Windows) pe chale

## 1.3 Real-World Use Cases

| User Type | Use Case |
|-----------|----------|
| Cybersecurity Student | Lab exercises without memorizing commands |
| Penetration Tester | Automated recon workflows with reporting |
| System Administrator | Network monitoring and quick tool access |
| DevOps Engineer | Container security scanning pipelines |
| Bug Bounty Hunter | Subdomain enumeration → scanning → reporting |
| Forensics Analyst | Evidence collection and analysis workflows |

## 1.4 Target Users

- Cybersecurity professionals (beginners to advanced)
- System administrators
- DevOps engineers
- Bug bounty hunters
- Students learning CLI tools
- Anyone who uses command-line tools regularly

## 1.5 Main Problem It Solves

**Problem:** CLI tools require memorizing commands, flags, options. Multiple tools need manual chaining. No unified interface exists.

**Solution:** VIGIL LABS gives every CLI tool a beautiful GUI form, chains them into automated pipelines, and adds AI assistance.

## 1.6 Why Each Major Feature Exists

| Feature | Why It Exists |
|---------|--------------|
| Tool Store | Users shouldn't hunt for tools manually - browse, install, done |
| Custom Tool Builder | Any new tool should be addable without editing code |
| Workflow Orchestration | Real work involves multiple tools in sequence |
| AI Agent | Beginners need guidance, everyone needs error help |
| Live Terminal | Users need real-time feedback like a real terminal |
| Authentication | Security - only authorized users should access tools |
| History & Reports | Professional work needs documentation |
| Cross-platform | Kali for security, Windows for convenience |

---

# 2. COMPLETE ARCHITECTURE EXPLANATION

## 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                    ELECTRON SHELL                      │
│  ┌───────────────────────────────────────────────┐  │
│  │              REACT FRONTEND                     │  │
│  │  ┌─────┐ ┌──────┐ ┌───────┐ ┌──────────┐   │  │
│  │  │Pages│ │Store │ │Layout │ │Components│   │  │
│  │  └──┬──┘ └──┬───┘ └───┬───┘ └────┬─────┘   │  │
│  │     │       │         │           │          │  │
│  │     └───────┴────┬────┴───────────┘          │  │
│  │                   │                           │  │
│  │            ┌──────▼──────┐                    │  │
│  │            │  Zustand    │ (State Management) │  │
│  │            │  + API Utils│                    │  │
│  │            └──────┬──────┘                    │  │
│  └───────────────────┼──────────────────────────┘  │
│                      │ HTTP/WebSocket               │
└──────────────────────┼──────────────────────────────┘
                       │
         ┌─────────────▼─────────────┐
         │     PYTHON FASTAPI        │
         │  ┌──────┐ ┌──────────┐   │
         │  │Routes│ │WebSocket │   │
         │  └──┬───┘ └────┬─────┘   │
         │     │           │         │
         │  ┌──▼───────────▼──┐      │
         │  │    Services     │      │
         │  │ ExecutionEngine │      │
         │  │ AIAgent         │      │
         │  │ ToolStore       │      │
         │  │ WorkflowEngine  │      │
         │  └────────┬────────┘      │
         │           │               │
         │  ┌────────▼────────┐      │
         │  │   SQLAlchemy    │      │
         │  │   (Database)    │      │
         │  └────────┬────────┘      │
         └───────────┼───────────────┘
                     │
           ┌─────────▼─────────┐
           │   SQLite Database  │
           │  (vigil_labs.db)   │
           └───────────────────┘
```

## 2.2 Frontend Architecture

**Tech Stack:** React 18 + TypeScript + Vite 5 + Tailwind CSS + Framer Motion + Electron 28

```
frontend/
├── electron/          → Desktop wrapper (Electron main process)
│   ├── main.js       → Window creation, backend spawning
│   └── preload.js    → Secure bridge between Electron and React
├── src/
│   ├── main.tsx      → React app entry point
│   ├── App.tsx       → Router + protected routes
│   ├── pages/        → Full page components (one per route)
│   ├── components/   → Reusable UI components
│   │   ├── layout/   → Shell components (Sidebar, TopBar, Terminal)
│   │   └── common/   → Shared components (badges, spinners, cards)
│   ├── store/        → Zustand state management
│   ├── utils/        → API client, helper functions
│   └── styles/       → Tailwind CSS + custom styles
├── public/           → Static assets (icons)
├── tailwind.config.js → Design system tokens
├── vite.config.ts    → Build configuration
└── package.json      → Dependencies + scripts
```

**Data Flow (Frontend):**
1. User interacts with a Page component
2. Page calls `api.get()` or `api.post()` (from utils/api.ts)
3. API util automatically attaches JWT token from Zustand store
4. Response updates component state or Zustand global state
5. UI re-renders with new data

## 2.3 Backend Architecture

**Tech Stack:** Python 3.11+ + FastAPI + SQLAlchemy (async) + WebSockets + psutil

```
backend/
├── app/
│   ├── main.py           → FastAPI app, lifespan, CORS, route registration
│   ├── core/
│   │   ├── config.py     → All settings (env vars, paths, timeouts)
│   │   ├── database.py   → SQLAlchemy async engine + session factory
│   │   └── security.py   → JWT creation/validation, password hashing
│   ├── models/           → SQLAlchemy ORM models (database tables)
│   │   ├── user.py       → User accounts
│   │   ├── tool.py       → Tool registry + arguments + categories
│   │   ├── execution.py  → Execution records + logs
│   │   ├── preset.py     → Saved tool configurations
│   │   ├── store.py      → Marketplace tools + installations
│   │   └── workflow.py   → Workflow pipelines + runs
│   ├── schemas/          → Pydantic request/response models
│   ├── services/         → Business logic (the "brain")
│   │   ├── execution_engine.py → Process spawning + management
│   │   ├── ai_agent.py        → Intelligent automation
│   │   ├── ai_assistant.py    → Help text parsing, error analysis
│   │   ├── tool_store.py      → Package installation
│   │   ├── store_catalog.py   → Preconfigured tool definitions
│   │   └── workflow_engine.py  → Pipeline execution
│   └── api/
│       ├── routes/       → HTTP endpoint handlers
│       └── websocket/    → Real-time terminal streaming
├── requirements.txt      → Python dependencies
└── .env.example         → Environment variable template
```

**Data Flow (Backend):**
1. Frontend sends HTTP request to `/api/...`
2. FastAPI routes it to the correct handler function
3. Handler validates input using Pydantic schemas
4. Handler calls service layer for business logic
5. Service interacts with database via SQLAlchemy models
6. Response returned as JSON

## 2.4 Database Architecture

**Engine:** SQLite with aiosqlite (async), designed for PostgreSQL migration

**Tables:**

| Table | Purpose | Key Fields |
|-------|---------|------------|
| users | User accounts | username, hashed_password, role, last_login |
| tools | Registered CLI tools | name, executable_path, command_template, arguments |
| tool_arguments | Form field definitions | tool_id, field_type, flag, validation |
| tool_categories | Tool grouping | name, icon, color |
| executions | Run history | tool_id, command, status, stdout, stderr |
| execution_logs | Detailed step logs | execution_id, level, message |
| presets | Saved configurations | tool_id, arguments JSON |
| store_tools | Marketplace catalog | name, install_method, executable_name |
| installed_store_tools | User installations | store_tool_id, status, path |
| workflows | Tool pipelines | steps JSON, run_count |
| workflow_runs | Pipeline execution records | status, step_results |

## 2.5 API Flow

```
Frontend                    Backend                     Database
   │                          │                           │
   │── POST /api/auth/login ──▶│                           │
   │                          │── Query users table ──────▶│
   │                          │◀── Return user row ────────│
   │                          │── Verify password           │
   │                          │── Generate JWT tokens       │
   │◀── {access_token, user} ─│                           │
   │                          │                           │
   │── GET /api/tools/ ──────▶│ (Bearer token in header)  │
   │                          │── Validate JWT             │
   │                          │── Query tools table ──────▶│
   │                          │◀── Return tools ───────────│
   │◀── [{tool1}, {tool2}] ──│                           │
```

## 2.6 Authentication Flow

```
1. User submits username + password on Login page
2. Frontend POST /api/auth/login
3. Backend checks username exists in DB
4. Backend verifies password hash (bcrypt)
5. Backend creates JWT access_token (60 min) + refresh_token (7 days)
6. Frontend stores tokens in Zustand (persisted to localStorage)
7. Every API request includes "Authorization: Bearer <token>"
8. Backend validates token on every request via get_current_user dependency
9. If token expired → Frontend auto-refreshes via interceptor
10. Inactivity > 30 min → Auto-logout
```

## 2.7 Tool Execution Flow

```
1. User opens /execute/:toolId page
2. Frontend loads tool config + arguments from API
3. Dynamic form rendered based on argument definitions
4. User fills form → clicks "Execute"
5. Frontend POST /api/executions/run with {tool_id, arguments}
6. Backend validates arguments (required, format, paths)
7. Backend builds command from template: "nmap -sV -p 80 192.168.1.1"
8. Backend spawns async subprocess
9. Backend stores Execution record in DB (status: running)
10. Frontend connects WebSocket to /ws/terminal/{execution_id}
11. Backend streams stdout/stderr lines to WebSocket in real-time
12. Process completes → Backend updates status + stores output
13. Frontend shows completion toast + final output
```

## 2.8 AI Automation Flow

```
1. User describes goal: "I want to scan a website for vulnerabilities"
2. Frontend POST /api/system/ai/understand-goal
3. AIAgent detects intents: ["web_recon", "vulnerability_scan"]
4. AIAgent returns:
   - Recommended tools: [Nuclei, Nikto, WhatWeb]
   - Suggested workflow: "Web Recon Pipeline"
   - Safety notes
   - Next steps
5. User can:
   a. Ask AI to generate workflow automatically
   b. Get tool recommendations
   c. Auto-analyze a tool (runs --help, parses output)
   d. Get error fixes when something breaks
```

## 2.9 Complete Folder Structure

```
vigil-labs/
├── .gitignore                          # Git ignore rules
├── README.md                           # Project overview
├── docs/                               # Documentation
│   └── VIGIL_LABS_COMPLETE_DOCUMENTATION.md  # This file
├── shared/                             # Shared configs (future)
│
├── backend/                            # Python FastAPI backend
│   ├── .env.example                    # Environment variable template
│   ├── requirements.txt                # Python packages
│   ├── migrations/                     # DB migrations (Alembic)
│   ├── tests/                          # Test files
│   └── app/
│       ├── __init__.py                 # Package marker
│       ├── main.py                     # ★ App entry point
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py              # ★ Settings management
│       │   ├── database.py            # ★ DB engine + sessions
│       │   └── security.py            # ★ JWT + password utils
│       ├── models/
│       │   ├── __init__.py            # Model exports
│       │   ├── user.py                # User table
│       │   ├── tool.py                # Tool + Arguments + Categories
│       │   ├── execution.py           # Execution + Logs
│       │   ├── preset.py              # Saved configs
│       │   ├── store.py               # Marketplace tables
│       │   └── workflow.py            # Workflow tables
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── auth.py                # Login/Register schemas
│       │   ├── tool.py                # Tool CRUD schemas
│       │   └── execution.py           # Execution schemas
│       ├── services/
│       │   ├── __init__.py
│       │   ├── execution_engine.py    # ★ Command execution core
│       │   ├── ai_agent.py            # ★ AI automation brain
│       │   ├── ai_assistant.py        # Help parsing + analysis
│       │   ├── tool_store.py          # Package installation
│       │   ├── store_catalog.py       # 50+ tool definitions
│       │   └── workflow_engine.py     # Pipeline executor
│       └── api/
│           ├── __init__.py
│           ├── routes/
│           │   ├── __init__.py
│           │   ├── auth.py            # /api/auth/* endpoints
│           │   ├── tools.py           # /api/tools/* endpoints
│           │   ├── execution.py       # /api/executions/* endpoints
│           │   ├── store.py           # /api/store/* endpoints
│           │   ├── workflows.py       # /api/workflows/* endpoints
│           │   └── system.py          # /api/system/* + AI endpoints
│           └── websocket/
│               ├── __init__.py
│               └── terminal.py        # ★ WebSocket connection manager
│
└── frontend/                           # React + Electron frontend
    ├── package.json                    # NPM dependencies + scripts
    ├── index.html                      # HTML entry point
    ├── vite.config.ts                  # Vite build config
    ├── tailwind.config.js             # ★ Design system
    ├── postcss.config.js              # CSS processing
    ├── tsconfig.json                  # TypeScript config
    ├── tsconfig.node.json             # Node TS config
    ├── public/
    │   └── vigil-icon.svg            # App icon
    ├── electron/
    │   ├── main.js                    # ★ Electron main process
    │   └── preload.js                 # ★ Secure API bridge
    └── src/
        ├── main.tsx                   # ★ React bootstrap
        ├── App.tsx                    # ★ Router + layout
        ├── pages/
        │   ├── LoginPage.tsx          # Auth UI
        │   ├── DashboardPage.tsx      # Overview + stats
        │   ├── ToolsPage.tsx          # Tool registry
        │   ├── StorePage.tsx          # Marketplace
        │   ├── ToolBuilderPage.tsx    # Custom tool creation
        │   ├── ExecutionPage.tsx      # ★ Tool runner + terminal
        │   ├── HistoryPage.tsx        # Execution history
        │   ├── AIAssistantPage.tsx    # ★ AI Agent interface
        │   ├── WorkflowsPage.tsx      # Pipeline builder
        │   └── SettingsPage.tsx       # User preferences
        ├── components/
        │   ├── layout/
        │   │   ├── MainLayout.tsx     # ★ App shell
        │   │   ├── Sidebar.tsx        # Navigation
        │   │   ├── TopBar.tsx         # Header + search
        │   │   └── TerminalPanel.tsx  # Bottom terminal
        │   └── common/
        │       ├── AnimatedCounter.tsx
        │       ├── EmptyState.tsx
        │       ├── GlassCard.tsx
        │       ├── LoadingSpinner.tsx
        │       ├── PageTransition.tsx
        │       ├── ProgressBar.tsx
        │       └── StatusBadge.tsx
        ├── store/
        │   ├── authStore.ts           # ★ Auth state + persistence
        │   └── appStore.ts            # UI state (sidebar, terminal)
        ├── utils/
        │   ├── api.ts                 # ★ Axios instance + interceptors
        │   └── cn.ts                  # Tailwind class merger
        └── styles/
            └── index.css              # ★ Global styles + animations
```

## 2.10 How All Modules Connect

```
┌────────────┐     imports      ┌──────────────┐
│ main.py    │─────────────────▶│ routes/*.py  │
└────────────┘                  └──────┬───────┘
      │                                │ calls
      │ creates app                    ▼
      │                         ┌──────────────┐
      │                         │ services/*.py│
      │                         └──────┬───────┘
      │                                │ uses
      │                                ▼
      │                         ┌──────────────┐
      │                         │ models/*.py  │
      │                         └──────┬───────┘
      │                                │ maps to
      │                                ▼
      │                         ┌──────────────┐
      └────────────────────────▶│ database.py  │──▶ SQLite
                                └──────────────┘

Frontend connection:
┌────────────┐  HTTP/WS   ┌──────────────┐
│ api.ts     │────────────▶│ main.py      │
└────────────┘             └──────────────┘
      ▲
      │ used by
┌─────┴──────┐
│ pages/*.tsx │◀──── store/*.ts (global state)
└────────────┘
```




---

# 3. FILE-BY-FILE EXPLANATION

## 3.1 Backend Files

### `backend/app/main.py` — Application Entry Point
- **Purpose:** FastAPI app ko create karta hai, sab routes register karta hai, CORS setup karta hai, database initialize karta hai
- **Why it exists:** Ye poore backend ka "starting point" hai - jab server start hota hai, ye file execute hoti hai
- **Key Logic:**
  - `lifespan()` function: App start hone pe DB tables create karta hai + Tool Store catalog seed karta hai
  - CORS middleware: Frontend (localhost:5173) ko backend se baat karne deta hai
  - Router registration: auth, tools, execution, system, store, workflows routes add karta hai
  - WebSocket endpoint: `/ws/terminal/{execution_id}` pe real-time terminal streaming
- **Dependencies:** config, database, security, all route modules, ws_manager
- **Called by:** `uvicorn app.main:app` command

### `backend/app/core/config.py` — Settings Management
- **Purpose:** Saari app settings ek jagah manage karta hai (ports, secrets, timeouts, paths)
- **Why it exists:** Hardcoded values se avoid karna + environment variables support
- **Key Logic:**
  - `Settings` class: Pydantic BaseSettings se inherit - automatically `.env` file read karta hai
  - Directory creation: tools/, reports/, logs/, exports/ folders auto-create
  - Platform detection: `os.name` se Windows/Linux detect
- **Dependencies:** pydantic-settings, os, pathlib
- **Used by:** Almost every other file imports `settings` from here

### `backend/app/core/database.py` — Database Engine
- **Purpose:** SQLAlchemy async engine create karta hai, sessions manage karta hai
- **Why it exists:** Database connection pooling + async support + clean session lifecycle
- **Key Logic:**
  - `engine`: Async SQLite engine (future: just change URL for PostgreSQL)
  - `AsyncSessionLocal`: Session factory - har request ko fresh session deta hai
  - `get_db()`: FastAPI dependency - route handlers mein DB session inject karta hai
  - `init_db()`: Table creation (CREATE TABLE IF NOT EXISTS)
  - `Base`: All models inherit from this (DeclarativeBase)
- **Used by:** All route handlers via `Depends(get_db)`, main.py for init

### `backend/app/core/security.py` — Authentication Utilities
- **Purpose:** Passwords hash karna, JWT tokens create/validate karna
- **Why it exists:** Security ka core - without this, anyone can access everything
- **Key Logic:**
  - `hash_password()`: Bcrypt se password hash (irreversible)
  - `verify_password()`: Plain password ko stored hash se compare
  - `create_access_token()`: JWT token generate (60 min expiry)
  - `create_refresh_token()`: Long-lived refresh token (7 days)
  - `decode_token()`: Token verify + decode payload
  - `get_current_user()`: FastAPI dependency - har protected route pe user extract
- **Libraries:** python-jose (JWT), passlib (bcrypt)
- **Used by:** auth routes (login/register), all protected routes

### `backend/app/models/tool.py` — Tool Registry Model
- **Purpose:** Tools ka database schema define karta hai
- **Why it exists:** Har registered tool ka complete definition store karna
- **Key Logic:**
  - `ToolCategory`: Categories (Recon, Web, Wireless, etc.)
  - `Tool`: Main tool table - name, executable, template, OS support, risk level, env vars, dependencies
  - `ToolArgument`: Each tool's form fields - 18+ types (text, ip, port, file, select, toggle...)
  - Relationships: Tool has many ToolArguments, belongs to ToolCategory
- **Field Types:** text, textarea, number, select, checkbox, toggle, file, folder, ip, domain, port, interface, password, url, email, port_range, ip_range, wordlist, payload

### `backend/app/models/store.py` — Marketplace Models
- **Purpose:** Tool Store catalog + installation tracking
- **Key Logic:**
  - `StoreTool`: Marketplace entry - name, category, install_method (apt/pip/github/winget/choco), platform support, GitHub URL, binary URLs, command templates
  - `InstalledStoreTool`: Track which user installed which tool, status, paths

### `backend/app/models/workflow.py` — Workflow Models
- **Purpose:** Multi-tool pipeline definitions + run history
- **Key Logic:**
  - `Workflow`: Pipeline definition - steps JSON array, run_count, status
  - `WorkflowRun`: Individual execution record - current_step, step_results, duration

### `backend/app/services/execution_engine.py` — Process Execution Core
- **Purpose:** CLI commands safely execute karna with streaming output
- **Why it exists:** Ye poore app ka "engine" hai - bina iske koi tool run nahi hota
- **Key Logic:**
  - `validate_executable()`: Check if tool exists in PATH or absolute path
  - `validate_arguments()`: Required fields check, IP/port format validation, file existence
  - `build_command()`: Template + arguments → final command string with proper escaping
  - `execute()`: Async subprocess spawn with:
    - Concurrent process limit (max 10)
    - Duplicate execution prevention
    - Process group creation (for clean kill)
    - Windows CREATE_NO_WINDOW flag
  - `_stream_output()`: Read stdout/stderr line-by-line and callback
  - `stop_process()`: SIGTERM → wait 5s → SIGKILL (graceful shutdown)
  - `check_dependencies()`: `shutil.which()` for each dependency
  - `get_system_info()`: CPU, RAM, disk via psutil
  - `_escape_value()`: Safe shell escaping (shlex.quote on Linux, quotes on Windows)
- **Security:** Never raw-executes user input - always template-based with escaping

### `backend/app/services/ai_agent.py` — AI Automation Brain
- **Purpose:** Intelligent agent that understands goals, recommends tools, generates workflows
- **Key Logic:**
  - `understand_goal()`: Natural language → intents detection → tool/workflow recommendations
  - `generate_workflow()`: Goal text → automatic pipeline of matching tools
  - `recommend_tools()`: Keyword scoring against 50+ tool catalog
  - `explain_output()`: Tool output → human-readable analysis
  - `analyze_error_advanced()`: Error text → type detection + auto-fix suggestions
  - `generate_report()`: Execution results → professional Markdown report
  - `auto_analyze_tool()`: Run `--help` → parse flags → generate GUI config automatically
  - `_detect_intents()`: 12 intent categories (port_scan, web_recon, osint, etc.)
  - `_build_workflow_templates()`: 6 pre-built pipeline templates
- **No external API needed:** Works entirely with pattern matching + heuristics

### `backend/app/services/tool_store.py` — Package Installation Service
- **Purpose:** Cross-platform tool installation/uninstallation
- **Key Logic:**
  - `_detect_distro()`: Reads /etc/os-release → kali/debian/arch/fedora
  - `check_installed()`: `shutil.which()` to find executables
  - `get_install_command()`: Maps tool → correct package manager command
  - `install_tool()`: Async subprocess to run install command (with 5 min timeout)
  - `uninstall_tool()`: Reverse of install
  - `get_platform_info()`: Detects available package managers

### `backend/app/services/store_catalog.py` — Tool Definitions
- **Purpose:** 50+ preconfigured cybersecurity tools with metadata
- **Contains:** `TOOL_CATALOG` list with each tool's name, category, executable, install commands, risk level, platform support, GitHub URL, tags
- **Categories:** 12 categories from Recon to Reporting
- **Used by:** main.py (seed on startup), store routes (browsing)

### `backend/app/services/workflow_engine.py` — Pipeline Executor
- **Purpose:** Execute workflow steps sequentially with output piping
- **Key Logic:**
  - `run_workflow()`: Iterates steps, runs each command, pipes stdout to next step
  - Timeout per step (default 300s)
  - `continue_on_error` option per step
  - Callbacks for step start/output/complete/workflow complete

### `backend/app/api/routes/auth.py` — Authentication Endpoints
- **Endpoints:**
  - `POST /api/auth/register` → Create account + return tokens
  - `POST /api/auth/login` → Verify credentials + return tokens
  - `POST /api/auth/refresh` → Get new access token using refresh token
  - `GET /api/auth/me` → Get current user profile
  - `POST /api/auth/logout` → Invalidate session

### `backend/app/api/routes/tools.py` — Tool Management Endpoints
- **Endpoints:**
  - `GET /api/tools/` → List all tools (filter: category, search, favorites, risk)
  - `POST /api/tools/` → Create new tool with arguments
  - `GET /api/tools/{id}` → Get tool details
  - `PUT /api/tools/{id}` → Update tool
  - `DELETE /api/tools/{id}` → Soft delete
  - `POST /api/tools/{id}/favorite` → Toggle favorite
  - `GET /api/tools/{id}/check-dependencies` → Verify tool is installed
  - `GET /api/tools/categories/all` → List categories
  - `POST /api/tools/categories/create` → Create category

### `backend/app/api/routes/execution.py` — Execution Endpoints
- **Endpoints:**
  - `POST /api/executions/run` → Execute a tool
  - `POST /api/executions/stop` → Stop running process
  - `GET /api/executions/running` → List active processes
  - `GET /api/executions/history` → Paginated history with filters
  - `GET /api/executions/{id}` → Execution details
  - `DELETE /api/executions/{id}` → Delete record
  - `GET /api/executions/{id}/export` → Export as JSON/TXT/HTML
  - `GET /api/executions/presets/{tool_id}` → Get saved presets
  - `POST /api/executions/presets/save` → Save preset

### `backend/app/api/routes/store.py` — Tool Store Endpoints
- **Endpoints:**
  - `GET /api/store/catalog` → Browse tools (filter: category, search, installed)
  - `GET /api/store/categories` → Store category metadata
  - `GET /api/store/platform` → Current OS capabilities
  - `POST /api/store/install/{id}` → Install tool
  - `POST /api/store/uninstall/{id}` → Uninstall tool
  - `POST /api/store/toggle/{id}` → Enable/disable
  - `POST /api/store/seed` → Seed catalog (admin)
  - `GET /api/store/check-all` → Check all tools' install status

### `backend/app/api/routes/system.py` — System + AI Endpoints
- **System:**
  - `GET /api/system/health` → Health check
  - `GET /api/system/info` → CPU, RAM, disk, platform
  - `GET /api/system/stats` → Dashboard statistics
- **AI Assistant:**
  - `POST /api/system/ai/analyze-help` → Parse --help output
  - `POST /api/system/ai/analyze-error` → Error analysis
  - `POST /api/system/ai/suggest-config` → Safe defaults
  - `POST /api/system/ai/explain-command` → Command explanation
  - `POST /api/system/ai/check-dependencies` → Missing deps
- **AI Agent:**
  - `POST /api/system/ai/understand-goal` → Goal → recommendations
  - `POST /api/system/ai/generate-workflow` → Auto-generate pipeline
  - `POST /api/system/ai/recommend-tools` → Tool suggestions
  - `POST /api/system/ai/explain-output` → Output analysis
  - `POST /api/system/ai/analyze-error-advanced` → Error + auto-fix
  - `POST /api/system/ai/generate-report` → Professional report
  - `POST /api/system/ai/auto-analyze-tool` → Tool → GUI config

### `backend/app/api/websocket/terminal.py` — WebSocket Manager
- **Purpose:** Real-time output streaming to frontend
- **Key Logic:**
  - `ConnectionManager`: Tracks WebSocket connections per execution and per user
  - `connect()`: Accept + register connection
  - `disconnect()`: Clean up dead connections
  - `send_output()`: Broadcast line to all watchers of an execution
  - `send_status()`: Broadcast completion/failure/timeout
  - `broadcast_to_user()`: Send notifications to all user connections

---

## 3.2 Frontend Files

### `frontend/src/main.tsx` — React Entry Point
- **Purpose:** React app bootstrap with providers
- **Logic:** Creates React root, wraps App with BrowserRouter + QueryClientProvider + StrictMode

### `frontend/src/App.tsx` — Router + Auth Guard
- **Purpose:** All routes define karta hai + ProtectedRoute wrapper
- **Logic:**
  - `ProtectedRoute`: Checks `isAuthenticated` from Zustand → redirects to /login if false
  - Routes: /login (public), all others wrapped in ProtectedRoute + MainLayout

### `frontend/src/store/authStore.ts` — Authentication State
- **Purpose:** User session state with persistence
- **Logic:**
  - Zustand store with `persist` middleware → survives page refresh
  - `login()`: POST /api/auth/login → stores tokens + user
  - `register()`: POST /api/auth/register → same
  - `logout()`: Clears all state
  - `refreshAuth()`: Uses refresh_token to get new access_token
  - `checkInactivity()`: Auto-logout after 30 min idle

### `frontend/src/store/appStore.ts` — UI State
- **Purpose:** Sidebar collapse, terminal panel, active executions, notifications
- **Logic:** Simple Zustand store without persistence - UI-only state

### `frontend/src/utils/api.ts` — HTTP Client
- **Purpose:** Configured Axios instance with auth + refresh interceptors
- **Logic:**
  - Request interceptor: Reads token from localStorage → adds Bearer header
  - Response interceptor: On 401 → tries refresh → retries original request
  - `getWSUrl()`: Constructs WebSocket URL with token param

### `frontend/src/pages/ExecutionPage.tsx` — Tool Runner
- **Purpose:** Dynamic form generation + live terminal output
- **Logic:**
  - Loads tool config from API → generates form fields based on `field_type`
  - `renderField()`: Switch on field_type → renders appropriate input (text, select, toggle, file, ip, port, etc.)
  - `handleExecute()`: Validates required fields → POST /api/executions/run → connects WebSocket
  - WebSocket `onmessage`: Appends output lines to state → auto-scrolls terminal
  - Stop button: POST /api/executions/stop

### `frontend/src/pages/StorePage.tsx` — Tool Marketplace
- **Purpose:** VS Code-style marketplace for browsing/installing tools
- **Logic:**
  - Category pills filter
  - Grid/list view toggle
  - Install/uninstall buttons with loading states
  - Enable/disable toggle per tool
  - Real-time install status detection

### `frontend/src/pages/AIAssistantPage.tsx` — AI Agent Interface
- **Purpose:** Chat-like interface for AI agent interaction
- **Logic:**
  - 6 modes: Goal, Workflow, Recommend, Explain, Error, Analyze
  - Mode selector changes API endpoint + placeholder text
  - Response formatters: Convert JSON responses into readable text
  - Chat history with animated messages

### `frontend/src/pages/WorkflowsPage.tsx` — Pipeline Builder
- **Purpose:** Create and run multi-tool workflows
- **Logic:**
  - Step builder: Add tools in sequence with pipe_output option
  - Visual step display with arrows
  - Run/delete workflow actions
  - Tool selector from registered tools

### `frontend/src/components/layout/Sidebar.tsx` — Navigation
- **Purpose:** App navigation with active route indicator
- **Logic:**
  - 8 nav items with Lucide icons
  - Active indicator with `layoutId` animation (Framer Motion)
  - Collapsible (72px ↔ 240px)
  - Running processes badge

### `frontend/src/styles/index.css` — Global Styles
- **Purpose:** Tailwind layers + custom components + animations
- **Key Classes:**
  - `.glass-panel`: Glassmorphism card
  - `.btn-primary/secondary/danger`: Button variants
  - `.input-field`: Styled input
  - `.badge-*`: Status badges
  - `.shimmer`, `.float`, `.glow-text`: Premium animations




---

# 4. LINE-BY-LINE CODE EXPLANATION (Key Files)

## 4.1 `backend/app/services/execution_engine.py` — The Heart

```python
import shlex  # Shell lexical analysis - safely quote/escape command arguments
import signal  # OS signals (SIGTERM, SIGKILL) for process management
import psutil  # Cross-platform process/system utilities

@dataclass
class ProcessInfo:
    """Track running process information."""
    pid: int                    # Process ID (OS level)
    execution_id: str           # Our internal ID (UUID)
    tool_id: str               # Which tool is running
    user_id: str               # Who started it
    process: asyncio.subprocess.Process  # Actual process handle
    started_at: datetime        # When it started
    status: str = "running"     # Current status
```

**`validate_executable()` explained:**
```python
def validate_executable(self, executable_path: str):
    # Step 1: Try to find in system PATH (like 'nmap', 'python3')
    which_result = shutil.which(executable_path)
    if which_result:
        return {"valid": True, "path": which_result}
    
    # Step 2: Check if it's an absolute path ('/usr/bin/nmap')
    if os.path.isfile(executable_path):
        if os.access(executable_path, os.X_OK):  # Is it executable?
            return {"valid": True}
```

**`build_command()` explained:**
```python
def build_command(self, template, executable, arguments, tool_args):
    # Template example: "{executable} -sV {args}"
    command = template.replace("{executable}", executable)
    # Result so far: "nmap -sV {args}"
    
    for name, value in arguments.items():
        arg_def = arg_defs.get(name)  # Get field definition
        
        if arg_def.field_type in ("checkbox", "toggle"):
            if value:  # Only add flag if enabled
                arg_parts.append(arg_def.flag)  # e.g., "-v"
        elif arg_def.flag:
            safe_value = self._escape_value(str(value))  # Prevent injection
            arg_parts.append(f"{arg_def.flag} {safe_value}")  # "-p 80"
    
    # Replace {args} with all arguments joined
    command = command.replace("{args}", " ".join(arg_parts))
    # Final: "nmap -sV -p 80 -v 192.168.1.1"
```

**`execute()` explained:**
```python
async def execute(self, command, execution_id, ...):
    # Safety check 1: Too many processes?
    if self.running_count >= settings.MAX_CONCURRENT_PROCESSES:
        raise RuntimeError("Maximum concurrent processes reached")
    
    # Safety check 2: Same tool already running for this user?
    for proc_info in self._running_processes.values():
        if proc_info.tool_id == tool_id and proc_info.user_id == user_id:
            raise RuntimeError("Tool is already running")
    
    # Platform-specific execution
    if self._is_windows:
        process = await asyncio.create_subprocess_shell(
            command,
            creationflags=0x08000000,  # Hide console window
        )
    else:
        process = await asyncio.create_subprocess_shell(
            command,
            preexec_fn=os.setsid,  # Create process group (for clean kill)
        )
    
    # Start background task for streaming output
    asyncio.create_task(self._stream_output(...))
```

## 4.2 `backend/app/core/security.py` — Auth System

```python
# bcrypt context - industry standard for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    to_encode = data.copy()  # Don't mutate original
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire, "type": "access"})
    # JWT = Header.Payload.Signature (Base64 encoded)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

async def get_current_user(credentials = Depends(security_scheme)):
    # FastAPI dependency injection - runs before every protected route
    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":  # Prevent using refresh as access
        raise HTTPException(401, "Invalid token type")
    return payload  # Contains {sub: user_id, username, role}
```

## 4.3 `frontend/src/store/authStore.ts` — State Persistence

```typescript
export const useAuthStore = create<AuthState>()(
  persist(  // Zustand middleware - saves to localStorage automatically
    (set, get) => ({
      login: async (username, password) => {
        set({ isLoading: true });
        const res = await api.post('/api/auth/login', { username, password });
        // Destructure response - JWT tokens + user object
        const { access_token, refresh_token, user } = res.data;
        set({
          user,
          accessToken: access_token,    // Used for API requests
          refreshToken: refresh_token,  // Used when access expires
          isAuthenticated: true,
          lastActivity: Date.now(),     // For inactivity tracking
        });
      },
      
      checkInactivity: () => {
        const { lastActivity } = get();
        // 30 minutes = 1800000 milliseconds
        if (Date.now() - lastActivity > 30 * 60 * 1000) {
          get().logout();  // Auto-logout idle users
          return true;
        }
        return false;
      },
    }),
    { name: 'vigil-auth' }  // localStorage key
  )
);
```

## 4.4 `frontend/src/utils/api.ts` — HTTP Interceptors

```typescript
// Response interceptor - handles token refresh transparently
api.interceptors.response.use(
  (response) => response,  // Success: pass through
  async (error) => {
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;  // Prevent infinite loop
      
      // Try to refresh the token
      const res = await axios.post('/api/auth/refresh', {
        refresh_token: state.refreshToken,
      });
      
      // Update stored tokens
      state.accessToken = res.data.access_token;
      localStorage.setItem('vigil-auth', JSON.stringify({ state }));
      
      // Retry the original failed request with new token
      originalRequest.headers.Authorization = `Bearer ${res.data.access_token}`;
      return api(originalRequest);
    }
    return Promise.reject(error);
  }
);
```




---

# 5. FEATURE IMPLEMENTATION EXPLANATION

## 5.1 Login/Authentication

| Aspect | Detail |
|--------|--------|
| **Objective** | Secure user access with JWT tokens |
| **User Flow** | Open app → Login form → Enter credentials → Dashboard |
| **Backend Flow** | Receive creds → Find user in DB → Verify bcrypt hash → Generate JWT → Return tokens |
| **Frontend Flow** | Form submit → API call → Store tokens in Zustand (persisted) → Navigate to dashboard |
| **Models** | `User` (id, username, hashed_password, role, last_login) |
| **APIs** | POST /api/auth/login, POST /api/auth/register, POST /api/auth/refresh, GET /api/auth/me |
| **Files** | security.py, auth.py (route), authStore.ts, LoginPage.tsx, api.ts |
| **Edge Cases** | Wrong password (401), duplicate username (400), expired token (auto-refresh), inactivity timeout (30 min auto-logout) |
| **Security** | bcrypt hash (not reversible), JWT with expiry, refresh token rotation, HTTPS in production |

## 5.2 Tool Store / Marketplace

| Aspect | Detail |
|--------|--------|
| **Objective** | VS Code-style marketplace for tool discovery and installation |
| **User Flow** | Open Store → Browse/search → Click Install → Wait → Tool available |
| **Backend Flow** | Seed 50+ tools on startup → API returns catalog with install status → Install runs system package manager |
| **Frontend Flow** | Fetch catalog → Render grid with cards → Install button → Loading state → Success toast |
| **Models** | `StoreTool`, `InstalledStoreTool` |
| **APIs** | GET /api/store/catalog, POST /api/store/install/{id}, POST /api/store/uninstall/{id} |
| **Files** | store.py (model), store_catalog.py (definitions), tool_store.py (installer), store.py (route), StorePage.tsx |
| **Install Methods** | apt, pacman, winget, choco, pip, npm, github clone, binary download, manual |
| **Edge Cases** | No sudo access, network failure, package not available on platform, already installed |

## 5.3 Custom Tool Builder

| Aspect | Detail |
|--------|--------|
| **Objective** | Register ANY CLI tool without editing code |
| **User Flow** | Open Builder → Fill 4 sections (Basic, Execution, Arguments, Advanced) → Save |
| **Backend Flow** | Receive CreateToolRequest → Validate executable → Store Tool + ToolArguments → Return |
| **Frontend Flow** | Tabbed form → Dynamic argument builder → Save to API → Navigate to tools |
| **Models** | `Tool`, `ToolArgument`, `ToolCategory` |
| **APIs** | POST /api/tools/, PUT /api/tools/{id} |
| **Files** | tool.py (model/schema), tools.py (route), ToolBuilderPage.tsx |
| **Argument Types** | 18 types: text, textarea, number, select, checkbox, toggle, file, folder, ip, domain, port, port_range, interface, password, url, wordlist, payload, ip_range |

## 5.4 Live Terminal Output

| Aspect | Detail |
|--------|--------|
| **Objective** | Real-time command output like a real terminal |
| **Technical Flow** | Process stdout → readline → WebSocket broadcast → Frontend append |
| **WebSocket URL** | `ws://localhost:8000/ws/terminal/{execution_id}?token=JWT` |
| **Message Format** | `{"type": "output", "data": "line text", "stream": "stdout/stderr"}` |
| **Completion** | `{"type": "status", "status": "completed", "exit_code": 0}` |
| **Files** | terminal.py (ws_manager), execution_engine.py (_stream_output), ExecutionPage.tsx (WebSocket client) |

## 5.5 Workflow Orchestration

| Aspect | Detail |
|--------|--------|
| **Objective** | Chain multiple tools into automated pipelines |
| **User Flow** | Create Workflow → Add steps (tool selections) → Enable pipe output → Save → Run |
| **Backend Flow** | Store steps as JSON → On run: execute sequentially → Pipe stdout between steps |
| **Models** | `Workflow`, `WorkflowRun` |
| **APIs** | GET/POST /api/workflows/, POST /api/workflows/{id}/run |
| **Example Pipeline** | Subfinder → Httpx → Nuclei → Report |

## 5.6 AI Agent

| Aspect | Detail |
|--------|--------|
| **Objective** | Intelligent automation without external API keys |
| **Capabilities** | Goal understanding, workflow generation, tool recommendation, output explanation, error analysis, auto-fix, report generation, tool auto-analysis |
| **How It Works** | Pattern matching + keyword scoring + rule-based heuristics (no LLM needed) |
| **Auto-Analyze** | Runs `tool --help` → Parses flags with regex → Generates GUI field definitions |
| **Files** | ai_agent.py, ai_assistant.py, system.py (routes), AIAssistantPage.tsx |

## 5.7 Dynamic Form Generation

| Aspect | Detail |
|--------|--------|
| **Objective** | Automatically create GUI forms from tool argument definitions |
| **How** | ToolArgument defines field_type → ExecutionPage.tsx `renderField()` switches on type → Renders appropriate React component |
| **Example** | `field_type: "ip"` → `<input type="text" placeholder="192.168.1.1" className="font-mono">` |
| **Validation** | is_required check, regex validation, min/max length, real-time feedback |

## 5.8 Cross-Platform Compatibility

| Feature | Linux/Kali | Windows |
|---------|-----------|---------|
| Process creation | `preexec_fn=os.setsid` | `creationflags=CREATE_NO_WINDOW` |
| Process kill | `os.killpg(SIGTERM/SIGKILL)` | `process.terminate()` |
| Path escaping | `shlex.quote()` | Double quotes wrapping |
| Install commands | apt/pacman/pip | winget/choco/pip |
| Distro detection | `/etc/os-release` parsing | `platform.system()` check |

---

# 6. COMMANDS DOCUMENTATION

## 6.1 Backend Setup

```bash
# Navigate to backend
cd vigil-labs/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env (change SECRET_KEY!)
nano .env

# Run development server
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Run with debug logging
python -m uvicorn app.main:app --reload --log-level debug
```

## 6.2 Frontend Setup

```bash
# Navigate to frontend
cd vigil-labs/frontend

# Install Node.js dependencies
npm install

# Run web development server (React only, no Electron)
npm run dev

# Run Electron development mode (full desktop app)
npm run electron:dev

# Build for production (web assets only)
npm run build

# Build Electron app (creates installer)
npm run electron:build

# Lint code
npm run lint
```

## 6.3 Full Stack Development

```bash
# Terminal 1: Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev

# Open browser: http://localhost:5173
```

## 6.4 Database Commands

```bash
# Database is auto-created on first run (vigil_labs.db)
# To reset database:
rm vigil_labs.db && python -m uvicorn app.main:app  # Recreates fresh

# To inspect database:
sqlite3 vigil_labs.db
.tables              # List all tables
.schema tools        # Show table structure
SELECT * FROM users; # Query data
.quit
```

## 6.5 Electron Build Commands

```bash
# Linux AppImage + .deb
npm run electron:build  # Creates dist-electron/

# Windows .exe (NSIS installer)
# (Run on Windows or use wine)
npx electron-builder --win

# Linux only
npx electron-builder --linux
```

## 6.6 Environment Variables

```env
# .env file in backend/
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=true
DATABASE_URL=sqlite+aiosqlite:///./vigil_labs.db
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
MAX_CONCURRENT_PROCESSES=10
HOST=127.0.0.1
PORT=8000
```

## 6.7 Troubleshooting Commands

```bash
# Check Python version (need 3.10+)
python3 --version

# Check Node version (need 18+)
node --version

# Check if backend is running
curl http://localhost:8000/api/system/health

# Check if a tool is in PATH
which nmap

# Kill stuck backend process
lsof -i :8000
kill -9 <PID>

# Clear frontend cache
cd frontend && rm -rf node_modules/.vite && npm run dev

# Reset everything
rm backend/vigil_labs.db
rm -rf frontend/node_modules
npm install && npm run dev
```




---

# 7. GIT DOCUMENTATION

## 7.1 Repository Structure

```
RishiPlaysCodes/Hacomb (GitHub)
└── vigil-labs/          ← Main project directory
    ├── backend/
    ├── frontend/
    └── docs/
```

## 7.2 Essential Git Commands

```bash
# Clone repository
git clone https://github.com/RishiPlaysCodes/Hacomb.git
cd Hacomb

# Check current status
git status

# Create feature branch (ALWAYS work on branches, never main)
git checkout -b feature/my-new-feature

# Stage changes
git add vigil-labs/backend/app/services/new_service.py  # Specific file
git add -A                                               # All changes

# Commit with descriptive message
git commit -m "feat: Add tool import/export functionality

- Added export endpoint for JSON/YAML formats
- Added import with validation and conflict resolution
- Updated settings page with import/export buttons"

# Push to remote
git push origin feature/my-new-feature

# Create Pull Request on GitHub (or use gh CLI)
gh pr create --title "feat: Tool Import/Export" --body "Description here"

# Pull latest changes from main
git checkout main
git pull origin main

# Merge main into your branch (keep updated)
git checkout feature/my-new-feature
git merge main

# Resolve conflicts (if any)
# Edit conflicted files, then:
git add .
git commit -m "resolve: Merge conflict in tools.py"
```

## 7.3 Commit Message Convention

```
Format: <type>: <short description>

Types:
- feat:     New feature
- fix:      Bug fix
- refactor: Code restructuring (no new feature)
- style:    CSS/formatting changes
- docs:     Documentation only
- chore:    Build/config changes
- perf:     Performance improvement
- test:     Adding tests

Examples:
- feat: Add workflow drag-and-drop builder
- fix: Resolve WebSocket disconnect on timeout
- refactor: Split execution_engine into modules
- docs: Add API documentation for store endpoints
```

## 7.4 .gitignore Explanation

```gitignore
node_modules/       # NPM packages (reinstall with npm install)
__pycache__/        # Python bytecode cache
*.pyc               # Compiled Python files
.venv/              # Python virtual environment
dist/               # Built frontend assets
*.db                # SQLite database (contains user data)
.env                # Secrets (never commit!)
logs/               # Runtime logs
reports/            # Generated reports
```

## 7.5 Branch Strategy

```
main                    ← Production-ready code
├── feature/tool-store  ← New feature development
├── feature/ai-agent    ← Another feature
├── fix/websocket-leak  ← Bug fix
└── release/v1.1.0      ← Release preparation
```

---

# 8. LEARNING ROADMAP

## 8.1 HTML/CSS/JavaScript Basics

**Why needed:** Frontend UI ke liye
**Where used:** React components, Tailwind classes, event handlers

| Topic | Subtopics | Priority |
|-------|-----------|----------|
| HTML5 | Semantic elements, forms, attributes | Essential |
| CSS3 | Flexbox, Grid, animations, transitions | Essential |
| JavaScript ES6+ | Arrow functions, destructuring, async/await, modules | Essential |
| DOM manipulation | Events, querySelector (for understanding React) | Good to know |

**Practice:** Create a simple login form with CSS animations

## 8.2 React

**Why needed:** Entire frontend is React
**Where used:** Every .tsx file

| Topic | Subtopics | Order |
|-------|-----------|-------|
| JSX syntax | Components, props, rendering | 1st |
| Hooks | useState, useEffect, useRef, useCallback | 2nd |
| Routing | react-router-dom, params, navigation | 3rd |
| State management | Zustand (simpler than Redux) | 4th |
| Data fetching | Axios, React Query | 5th |
| Forms | Controlled inputs, validation | 6th |
| Animation | Framer Motion basics | 7th |

**Practice:** Build a TODO app → then a tool card component → then a form builder

## 8.3 TypeScript

**Why needed:** Type safety, better DX
**Where used:** All .tsx/.ts files

| Topic | Priority |
|-------|----------|
| Basic types (string, number, boolean) | Essential |
| Interfaces and types | Essential |
| Generics | Important |
| Union types | Important |
| Type inference | Good to know |

## 8.4 Electron

**Why needed:** Desktop app wrapper
**Where used:** electron/main.js, electron/preload.js

| Topic | Subtopics |
|-------|-----------|
| Main process | Window creation, app lifecycle |
| Renderer process | Web content (our React app) |
| Preload scripts | Secure IPC bridge |
| Packaging | electron-builder for installers |

## 8.5 Python

**Why needed:** Entire backend
**Where used:** All backend files

| Topic | Order |
|-------|-------|
| Variables, data types, functions | 1st |
| Classes, OOP | 2nd |
| Async/await (asyncio) | 3rd |
| File I/O, subprocess | 4th |
| Decorators, context managers | 5th |
| Type hints | 6th |

## 8.6 FastAPI

**Why needed:** Backend framework
**Where used:** routes, main.py, dependency injection

| Topic | Order |
|-------|-------|
| Path operations (GET, POST, PUT, DELETE) | 1st |
| Request/Response models (Pydantic) | 2nd |
| Dependency injection (Depends) | 3rd |
| Middleware (CORS) | 4th |
| WebSocket support | 5th |
| Lifespan events | 6th |

**Practice:** Build a simple REST API → Add auth → Add WebSocket

## 8.7 SQLAlchemy + Databases

**Why needed:** Data persistence
**Where used:** models/, database.py

| Topic | Order |
|-------|-------|
| SQL basics (SELECT, INSERT, UPDATE) | 1st |
| SQLAlchemy ORM (models, queries) | 2nd |
| Async sessions | 3rd |
| Relationships (one-to-many) | 4th |
| Migrations (Alembic) | 5th |

## 8.8 WebSockets

**Why needed:** Live terminal streaming
**Where used:** terminal.py, ExecutionPage.tsx

| Topic |
|-------|
| HTTP vs WebSocket (persistent connection) |
| FastAPI WebSocket endpoints |
| Browser WebSocket API |
| Message handling (JSON) |
| Connection lifecycle (open, message, close, error) |

## 8.9 Process Management

**Why needed:** Running CLI tools safely
**Where used:** execution_engine.py

| Topic |
|-------|
| subprocess module (Popen, PIPE) |
| asyncio.create_subprocess_shell |
| Process groups (os.setsid, os.killpg) |
| Signals (SIGTERM, SIGKILL) |
| Non-blocking I/O |

## 8.10 Cybersecurity Basics

**Why needed:** Understanding what tools do
**Topics:** Network scanning (nmap), web testing (nikto), OSINT, password hashing, wireless, forensics

## 8.11 Tailwind CSS

**Why needed:** Styling system
**Where used:** Every component's className

| Topic |
|-------|
| Utility-first approach |
| Responsive design (sm:, md:, lg:) |
| Custom theme (tailwind.config.js) |
| @apply directive |
| Dark mode |

---

# 9. USE CASES

## 9.1 Beginner Running Nmap

1. User opens VIGIL LABS → Dashboard appears
2. Navigates to Tool Store → Searches "nmap"
3. Sees Nmap card → Clicks "Install" (runs `sudo apt install -y nmap`)
4. After install → Goes to "My Tools" → Finds Nmap
5. Clicks "Run" → ExecutionPage opens with form:
   - Target IP field: enters `192.168.1.1`
   - Port Range: enters `1-1000`
   - Scan Type: selects `-sV` from dropdown
6. Clicks "Execute" → Terminal shows live output
7. Scan completes → Can export report as HTML

## 9.2 User Creating Custom Tool

1. User has a script: `/home/user/tools/my_scanner.sh`
2. Opens "AI Tool Builder" → Section: Basic Info
   - Name: "My Custom Scanner"
   - Executable: `/home/user/tools/my_scanner.sh`
   - Command Template: `{executable} --target {{target}} --output {{output}}`
3. Section: Arguments
   - Adds "target" (type: ip, required: true, flag: --target)
   - Adds "output" (type: folder, flag: --output)
4. Saves → Tool appears in "My Tools"
5. Can now run it with a GUI form instead of typing commands

## 9.3 AI Generating Workflow

1. User opens "AI Agent" → Mode: "Generate Workflow"
2. Types: "I want to do full recon on example.com"
3. AI responds:
   - Generated workflow: "Full Web Recon Pipeline"
   - Steps: Subfinder → Httpx → WhatWeb → Nuclei
   - Estimated time: 4-12 minutes
   - Safety notes
4. User can save this as a reusable workflow
5. Next time: one-click to run entire pipeline

## 9.4 Cross-Platform Usage

**On Kali Linux:**
- Tools install via `apt` (nmap, nikto, hydra come pre-installed)
- Process management uses POSIX signals
- Tool Store detects Kali → shows apt commands

**On Windows:**
- Tools install via `winget` or `choco`
- Process management uses `process.terminate()`
- Path separators handled automatically
- CREATE_NO_WINDOW flag hides console popups

---

# 10. DEVELOPER GUIDE

## 10.1 How to Add a New API Endpoint

```python
# 1. Create route file: backend/app/api/routes/my_feature.py
from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter(prefix="/api/my-feature", tags=["My Feature"])

@router.get("/")
async def list_items(current_user: dict = Depends(get_current_user)):
    return {"items": []}

# 2. Register in main.py:
from app.api.routes import my_feature
app.include_router(my_feature.router)
```

## 10.2 How to Add a New Database Model

```python
# 1. Create: backend/app/models/my_model.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from app.core.database import Base

class MyModel(Base):
    __tablename__ = "my_table"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# 2. Import in models/__init__.py:
from app.models.my_model import MyModel

# 3. Restart server → Table auto-creates
```

## 10.3 How to Add a New Frontend Page

```typescript
// 1. Create: frontend/src/pages/MyPage.tsx
export default function MyPage() {
  return <div className="space-y-6"><h1>My Page</h1></div>;
}

// 2. Add route in App.tsx:
import MyPage from './pages/MyPage';
// Inside Routes:
<Route path="/my-page" element={<MyPage />} />

// 3. Add to Sidebar.tsx navItems array:
{ path: '/my-page', icon: MyIcon, label: 'My Page', color: 'text-vigil-primary' },
```

## 10.4 How to Add a New Tool to Store Catalog

```python
# Edit: backend/app/services/store_catalog.py
# Add to TOOL_CATALOG list:
{
    "name": "MyTool",
    "slug": "mytool",
    "category": "Recon / Scanning",
    "description": "What it does",
    "executable_name": "mytool",
    "install_method": "apt",
    "install_command_linux": "sudo apt install -y mytool",
    "risk_level": "medium",
    "supports_linux": True,
    "supports_windows": False,
    "tags": ["recon", "scanner"],
}
# Delete vigil_labs.db and restart to re-seed
```

## 10.5 How to Debug

```bash
# Backend errors: Check terminal running uvicorn
# Add print() statements or use:
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Variable value: %s", my_var)

# Frontend errors: Browser DevTools (F12)
# Console tab for errors
# Network tab for API calls
# React DevTools extension for component state

# Electron errors: DevTools opens automatically in dev mode
# Check electron/main.js console output
```

---

# 11. DIAGRAMS

## 11.1 Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                       USER (Desktop)                       │
└───────────────────────────┬──────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────┐
│                    ELECTRON SHELL                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │                 REACT APP (Vite)                     │  │
│  │                                                     │  │
│  │  ┌──────┐ ┌──────┐ ┌───────┐ ┌────────────────┐  │  │
│  │  │Login │ │Dash- │ │Tools/ │ │   Execution    │  │  │
│  │  │Page  │ │board │ │Store  │ │   Page+Term    │  │  │
│  │  └──────┘ └──────┘ └───────┘ └────────────────┘  │  │
│  │       │        │         │            │           │  │
│  │       └────────┴─────────┴────────────┘           │  │
│  │                       │                            │  │
│  │              ┌────────▼────────┐                   │  │
│  │              │  Zustand Store  │                   │  │
│  │              │  + Axios API    │                   │  │
│  │              └────────┬────────┘                   │  │
│  └───────────────────────┼────────────────────────────┘  │
└──────────────────────────┼───────────────────────────────┘
                           │ REST API + WebSocket
┌──────────────────────────▼───────────────────────────────┐
│                    FASTAPI SERVER                          │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                    API LAYER                          │ │
│  │  /auth  /tools  /executions  /store  /workflows     │ │
│  │  /system/ai/*                                        │ │
│  └─────────────────────────┬───────────────────────────┘ │
│                            │                              │
│  ┌─────────────────────────▼───────────────────────────┐ │
│  │                 SERVICE LAYER                         │ │
│  │  ExecutionEngine | AIAgent | ToolStore | Workflows   │ │
│  └─────────────────────────┬───────────────────────────┘ │
│                            │                              │
│  ┌─────────────────────────▼───────────────────────────┐ │
│  │              DATABASE LAYER (SQLAlchemy)              │ │
│  │  Users | Tools | Executions | Store | Workflows      │ │
│  └─────────────────────────┬───────────────────────────┘ │
└────────────────────────────┼─────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   SQLite DB     │
                    │ vigil_labs.db   │
                    └─────────────────┘
```

## 11.2 Tool Execution Flow

```
User clicks "Execute"
        │
        ▼
┌─────────────────┐     POST /api/executions/run
│  ExecutionPage  │────────────────────────────────┐
└────────┬────────┘                                │
         │                                         ▼
         │                              ┌────────────────────┐
         │                              │  execution route   │
         │                              │  validate_arguments│
         │                              │  build_command     │
         │                              │  create DB record  │
         │                              └────────┬───────────┘
         │                                       │
         │                              ┌────────▼───────────┐
         │                              │ ExecutionEngine    │
         │                              │ spawn subprocess   │
         │                              │ start streaming    │
         │                              └────────┬───────────┘
         │                                       │
         │  WebSocket /ws/terminal/{id}          │ stdout lines
         │◀──────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Terminal shows  │
│  live output    │
└─────────────────┘
```

## 11.3 Authentication Flow

```
┌────────┐          ┌──────────┐          ┌────────┐
│  User  │          │ Frontend │          │Backend │
└───┬────┘          └────┬─────┘          └───┬────┘
    │ Enter creds        │                     │
    │───────────────────▶│                     │
    │                    │ POST /auth/login    │
    │                    │────────────────────▶│
    │                    │                     │ bcrypt verify
    │                    │                     │ generate JWT
    │                    │ {access_token,user} │
    │                    │◀────────────────────│
    │                    │ Store in Zustand    │
    │                    │ + localStorage      │
    │   Dashboard loads  │                     │
    │◀───────────────────│                     │
    │                    │                     │
    │ Click "Tools"      │                     │
    │───────────────────▶│                     │
    │                    │ GET /tools          │
    │                    │ Auth: Bearer <token>│
    │                    │────────────────────▶│
    │                    │                     │ validate JWT
    │                    │   [{tool1,tool2}]   │
    │                    │◀────────────────────│
    │   Tools displayed  │                     │
    │◀───────────────────│                     │
```

---

# 12. PROFESSIONAL README CONTENT

## Project Title

# VIGIL LABS

**AI-Powered Cross-Platform Desktop Cyber/Lab Operating Platform**

## Description

VIGIL LABS is a production-level desktop application that transforms CLI-based tool management into a premium graphical experience. Install tools from a built-in marketplace, create custom GUIs for any command-line tool, chain tools into automated workflows, and let AI assist with configuration, execution, and troubleshooting — all through one unified cross-platform interface.

## Key Features

- **Tool Store Marketplace** — Browse and install 50+ cybersecurity tools (apt, pip, winget, choco, GitHub)
- **AI Tool Builder** — Register any CLI tool, AI auto-generates GUI forms from `--help` output
- **Workflow Orchestration** — Chain tools into automated pipelines with output piping
- **AI Automation Agent** — Goal understanding, workflow generation, error fixing, report creation
- **Live Terminal Streaming** — Real-time WebSocket output like a real terminal
- **Dynamic Form Generation** — 18+ field types auto-rendered from tool configurations
- **Execution History** — Full logging, search, export (JSON/HTML/TXT)
- **Process Management** — Start, stop, timeout, concurrent limit, crash recovery
- **Cross-Platform** — Kali Linux, Ubuntu, Windows (Electron desktop app)
- **Professional Auth** — JWT, bcrypt, session management, inactivity lock
- **Premium UX** — Dark glassmorphism, Framer Motion animations, responsive layouts

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Desktop Shell | Electron 28 |
| Frontend | React 18, TypeScript, Vite 5 |
| Styling | Tailwind CSS, Framer Motion |
| State | Zustand (persistent), React Query |
| Backend | Python FastAPI, async WebSockets |
| Database | SQLite (async), PostgreSQL-ready |
| Auth | JWT (python-jose), bcrypt |
| AI | Rule-based agent (no API key required) |
| Process | asyncio subprocess, psutil |

## Installation

```bash
# Clone
git clone https://github.com/RishiPlaysCodes/Hacomb.git
cd Hacomb/vigil-labs

# Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

## Screenshots

> [Dashboard] [Tool Store] [Execution Page] [AI Agent] [Workflows]
> *(Screenshots placeholder - add actual screenshots here)*

## Roadmap

- [ ] Drag-and-drop workflow builder with visual nodes
- [ ] PDF report generation (WeasyPrint)
- [ ] Tool Store community submissions
- [ ] LLM integration (Ollama/OpenAI) for enhanced AI
- [ ] Plugin system for custom extensions
- [ ] Multi-user collaboration
- [ ] Scheduled workflow execution (cron-style)
- [ ] Mobile companion app

## Disclaimer

> **IMPORTANT:** This platform is designed exclusively for **authorized security testing**, **educational purposes**, and **personal lab environments**. Users are responsible for ensuring they have proper authorization before using any tools against systems they do not own. Unauthorized access to computer systems is illegal. Use responsibly.

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m "feat: Add amazing feature"`
4. Push: `git push origin feature/amazing-feature`
5. Open Pull Request

## License

MIT

---

*Built with precision. Designed for professionals. Powered by AI.*

---

# END OF DOCUMENTATION

**Total Files in Project:** 70+  
**Total Lines of Code:** ~10,000+  
**Backend Services:** 6 (execution, AI agent, AI assistant, tool store, store catalog, workflow engine)  
**Frontend Pages:** 10  
**API Endpoints:** 35+  
**Database Tables:** 11  
**Supported Tools:** 50+ preconfigured  

---

*This documentation was created to help you understand, maintain, and rebuild VIGIL LABS from scratch. Study each section systematically, practice the learning roadmap topics, and you'll be able to recreate the entire platform independently.*
