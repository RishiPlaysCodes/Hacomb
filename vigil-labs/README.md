# VIGIL LABS

**Professional Cross-Platform CLI Tool Management Platform**

A production-grade desktop application for managing, configuring, running, and monitoring any CLI-based tool through a premium graphical interface. Built for cybersecurity professionals, system administrators, DevOps engineers, and power users.

---

## Features

- **Custom Tool Builder** - Register ANY CLI tool with 30+ configurable field types
- **Dynamic Form Generation** - Auto-creates GUI forms from tool configurations
- **Live Terminal Streaming** - Real-time WebSocket-based output
- **AI Assistant** - Intelligent help for configuration, error analysis, and tool understanding
- **Tool Store** - 80+ pre-configured cybersecurity tools (Nmap, Nuclei, ffuf, etc.)
- **Multi-Tool Workflows** - Chain tools together with output piping
- **Cross-Platform** - Works on Kali Linux and Windows
- **Authentication System** - JWT-based with session management, rate limiting, and inactivity lock
- **Execution History** - Full logging, search, and export (HTML/JSON/TXT)
- **Dashboard Analytics** - System monitoring, process status, usage stats
- **Presets & Templates** - Save and reuse tool configurations
- **Process Management** - Start, stop, monitor with timeout handling
- **Report Generation** - Export execution results in multiple formats

---

## Architecture

```
vigil-labs/
├── frontend/              # Electron + React + Vite + Tailwind
│   ├── electron/          # Electron main process (hardened)
│   ├── src/               # React application
│   │   ├── components/    # Layout, common UI
│   │   ├── pages/         # Route pages
│   │   ├── store/         # Zustand state management
│   │   └── utils/         # API client, helpers
│   ├── Dockerfile         # Nginx production image
│   └── nginx.conf         # Reverse proxy config
├── backend/               # Python FastAPI
│   ├── app/
│   │   ├── api/           # REST routes + WebSocket
│   │   ├── core/          # Config, DB, Security, Middleware
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas (validated)
│   │   └── services/      # Execution engine, AI, Workflows
│   ├── alembic/           # Database migrations
│   ├── Dockerfile         # Production image (non-root)
│   └── start.py           # Production startup script
├── docker-compose.yml     # Production deployment
├── docker-compose.dev.yml # Development with hot-reload
└── SECURITY.md            # Security documentation
```

---

## Quick Start (One-Shot Commands)

### Windows — First Time Setup
Open PowerShell and paste this entire block:
```powershell
cd C:\Users\gurud\Hacomb\vigil-labs\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Then create `.env`:
```powershell
copy .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(64))"
```
Copy the output, open `.env` in notepad, paste after `SECRET_KEY=`, also set `AI_MODEL=gemini` and `GEMINI_API_KEY=your_key`. Save.

### Daily Use (Every Time You Want to Run)
**Terminal 1 — Backend:**
```powershell
cd C:\Users\gurud\Hacomb\vigil-labs\backend
venv\Scripts\activate
python start.py
```

**Terminal 2 — Frontend:**
```powershell
cd C:\Users\gurud\Hacomb\vigil-labs\frontend
npm run dev
```

**Open:** http://localhost:5173

**First time:** Register with username `admin`, password `Test1234` (8+ chars, uppercase+lowercase+number).

### OR — One Double-Click (START.bat)
Just double-click: `C:\Users\gurud\Hacomb\vigil-labs\START.bat`
It does everything automatically.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Desktop | Electron 28 (sandboxed, CSP-hardened) |
| Frontend | React 18, TypeScript (strict), Vite 5 |
| Styling | Tailwind CSS, Framer Motion |
| State | Zustand, React Query |
| Backend | Python FastAPI, WebSockets |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Auth | JWT + bcrypt + rate limiting |
| Process | asyncio subprocess, psutil |
| Deploy | Docker, Nginx, multi-stage builds |
| Migrations | Alembic (async) |

---

## Security

See [SECURITY.md](./SECURITY.md) for comprehensive security documentation.

Key security features:
- Command injection prevention (blocked operators, input sanitization)
- Rate limiting on all endpoints
- Security headers on all responses
- Non-root Docker containers
- Strict input validation
- SQL injection prevention
- JWT with proper token lifecycle

---

## API Documentation

When running in development mode (`DEBUG=true`):
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

API docs are disabled in production for security.

---

## Environment Variables

See `backend/.env.example` for all available configuration options.

Critical production settings:
- `SECRET_KEY` - Must be a strong random value (64+ chars)
- `ENVIRONMENT=production`
- `DEBUG=false`
- `DATABASE_URL` - PostgreSQL recommended
- `CORS_ORIGINS` - Restrict to your domain

---

## License

MIT

---

Built with precision. Designed for professionals.
