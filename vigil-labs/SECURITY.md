# VIGIL LABS - Security Documentation

## Overview

VIGIL LABS is a CLI tool management platform that executes system commands. Security is critical. This document outlines the security measures implemented and deployment guidelines.

---

## Authentication & Authorization

### JWT Token System
- **Access tokens**: Short-lived (default 30 minutes), used for API authentication
- **Refresh tokens**: Long-lived (7 days), used to obtain new access tokens
- **Algorithm**: HS256 with configurable secret key
- **Token validation**: Proper claims verification (sub, exp, type, iat)

### Password Security
- **Hashing**: bcrypt with 12 rounds
- **Minimum requirements**: 8 characters, uppercase, lowercase, and numeric
- **Rate limiting**: 5 login attempts per 5 minutes per IP

### Role-Based Access
- **admin**: Full access, first registered user only
- **user**: Standard access, can manage own tools and executions
- **viewer**: Read-only access (future)

---

## Command Execution Security

### Input Sanitization
- All user inputs are sanitized before command construction
- `shlex.quote()` used for shell argument escaping
- Null bytes stripped from all inputs

### Blocked Patterns
The following are blocked by default:
- Dangerous commands: `rm -rf /`, `mkfs`, `dd if=/dev/zero`, fork bombs, etc.
- Shell operators: `&&`, `||`, `;`, `|`, backticks, `$(`, `${`

### Configurable Safety
- `ALLOW_SHELL_OPERATORS=false` (default) - prevents shell injection
- Set to `true` only in fully trusted environments with authenticated users

### Execution Limits
- Maximum concurrent processes (default: 10)
- Per-process timeout enforcement (max: 1 hour)
- Output size limits (10MB per process)
- Duplicate execution prevention per user/tool

---

## API Security

### Rate Limiting
- General: 100 requests per 60 seconds per IP
- Authentication: 5 requests per 5 minutes per IP
- Account lockout after repeated failures

### Input Validation
- All API inputs validated via Pydantic models with strict field validators
- UUID format enforcement for resource IDs
- Path traversal prevention for file/directory inputs
- SQL injection prevention via parameterized queries and LIKE sanitization
- Maximum field lengths enforced

### CORS Policy
- Restricted to configured origins only
- Credentials mode enabled
- Limited HTTP methods and headers

### Security Headers
All responses include:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`
- `Strict-Transport-Security` (production only)

---

## Electron Security

### Process Isolation
- `contextIsolation: true` - renderer cannot access Node.js
- `nodeIntegration: false` - no require() in renderer
- `sandbox: true` - additional OS-level sandboxing
- `webSecurity: true` - enforce same-origin policy

### Content Security Policy
- Strict CSP enforced via session headers
- Only allowed origins for scripts, styles, and connections

### Navigation Restrictions
- Blocked navigation to unknown origins
- External links opened in system browser
- No popup window creation allowed

---

## Database Security

### Connection Management
- Async connection pooling (PostgreSQL)
- Connection recycling every hour
- Pre-ping validation before use
- Proper session cleanup on errors

### Data Protection
- Passwords never stored in plaintext (bcrypt)
- Sensitive tokens not logged
- SQL injection prevented via SQLAlchemy ORM

---

## Deployment Security Checklist

### Before Going Live

- [ ] Set `SECRET_KEY` to a strong random value (64+ characters)
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Configure `CORS_ORIGINS` to your actual domain only
- [ ] Use PostgreSQL instead of SQLite for production
- [ ] Enable HTTPS via reverse proxy (nginx/Caddy)
- [ ] Set `REGISTRATION_ENABLED=false` after creating admin account
- [ ] Review `ALLOW_SHELL_OPERATORS` setting
- [ ] Configure proper log rotation
- [ ] Set up monitoring and alerting
- [ ] Run behind a firewall with restricted network access
- [ ] Keep Python dependencies updated (check for CVEs)

### Docker Deployment

- [ ] Never run containers as root (our Dockerfile uses non-root)
- [ ] Use named volumes for persistent data
- [ ] Set resource limits on containers
- [ ] Use Docker secrets for sensitive values
- [ ] Keep base images updated

---

## Reporting Security Issues

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** create a public GitHub issue
2. Email the maintainers with details
3. Allow reasonable time for a fix before disclosure

---

## Dependency Security

Run regular dependency audits:

```bash
# Backend
pip audit

# Frontend
npm audit
```

Keep dependencies updated and monitor for CVEs in:
- `python-jose` (JWT)
- `passlib`/`bcrypt` (password hashing)
- `sqlalchemy` (database)
- `fastapi`/`uvicorn` (server)
