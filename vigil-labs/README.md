# VIGIL LABS

**Professional Cross-Platform CLI Tool Management Platform**

A production-level desktop application for managing, configuring, running, and monitoring any CLI-based tool through a premium graphical interface. Built for cybersecurity professionals, system administrators, DevOps engineers, and power users.

## Features

- **Custom Tool Builder** - Register ANY CLI tool with 30+ configurable field types
- **Dynamic Form Generation** - Auto-creates GUI forms from tool configurations
- **Live Terminal Streaming** - Real-time WebSocket-based output
- **AI Assistant** - Intelligent help for configuration, error analysis, and tool understanding
- **Cross-Platform** - Works on Kali Linux and Windows
- **Authentication System** - JWT-based with session management and inactivity lock
- **Execution History** - Full logging, search, and export (HTML/JSON/TXT)
- **Dashboard Analytics** - System monitoring, process status, usage stats
- **Presets & Templates** - Save and reuse tool configurations
- **Process Management** - Start, stop, monitor with timeout handling
- **Report Generation** - Export execution results in multiple formats

## Architecture

```
vigil-labs/
├── frontend/          # Electron + React + Vite + Tailwind
│   ├── electron/      # Electron main process
│   ├── src/           # React application
│   │   ├── components/  # Layout, common UI
│   │   ├── pages/       # Route pages
│   │   ├── store/       # Zustand state management
│   │   └── utils/       # API client, helpers
│   └── public/        # Static assets
├── backend/           # Python FastAPI
│   └── app/
│       ├── api/       # REST routes + WebSocket
│       ├── core/      # Config, DB, Security
│       ├── models/    # SQLAlchemy models
│       ├── schemas/   # Pydantic schemas
│       └── services/  # Execution engine, AI assistant
└── shared/            # Shared configurations
```

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev            # Web development
npm run electron:dev   # Electron development
```

### Production Build
```bash
cd frontend
npm run electron:build
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Desktop | Electron 28 |
| Frontend | React 18, TypeScript, Vite 5 |
| Styling | Tailwind CSS, Framer Motion |
| State | Zustand, React Query |
| Backend | Python FastAPI, WebSockets |
| Database | SQLite (async), PostgreSQL-ready |
| Auth | JWT (python-jose), bcrypt |
| Process | asyncio subprocess, psutil |

## License

MIT

---

Built with precision. Designed for professionals.
