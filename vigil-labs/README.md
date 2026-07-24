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

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Copy environment file
cp .env.example .env

# Generate a secret key
python -c "import secrets; print(secrets.token_urlsafe(64))"
# Add the output to SECRET_KEY in .env

# Start all services
docker compose up -d

# Access at http://localhost
```

### Option 2: Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings

python start.py
# API available at http://localhost:8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev              # Web development (http://localhost:5173)
npm run electron:dev     # Electron development
```

### Option 3: Electron Desktop App

```bash
cd frontend
npm install
npm run electron:build   # Builds packaged desktop app
```

---

## Production Deployment

### Using Docker Compose

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env - set SECRET_KEY, DATABASE_URL, etc.

# 2. Build and start
docker compose up -d --build

# 3. Check health
curl http://localhost/health

# 4. View logs
docker compose logs -f backend
```

### With PostgreSQL

Uncomment the PostgreSQL service in `docker-compose.yml` and update `DATABASE_URL`:

```env
DATABASE_URL=postgresql+asyncpg://vigil:yourpassword@postgres:5432/vigil_labs
DB_PASSWORD=yourpassword
```

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

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
