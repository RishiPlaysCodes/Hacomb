# VIGIL LABS — Complete Code Documentation

## Ye Kya Hai? (The Idea)

**VIGIL LABS** ek desktop application hai jo **CLI (Command Line) tools ko GUI (Graphical Interface) me convert** karta hai.

### Problem jo solve karta hai:
Cybersecurity me 200+ tools hain (nmap, sqlmap, hydra, etc.) jinke liye terminal me complicated commands yaad karni padti hain. Jaise:
```
nmap -sV -sC -p 1-1000 -oN scan.txt 192.168.1.1
```
Ye command yaad rakhna mushkil hai. VIGIL LABS iska solution hai — **form bharo, button dabao, tool chal jaaye.**

### Kaise kaam karta hai (Simple):
1. Tool register karo (naam, path, flags batao)
2. App automatically ek form bana deta hai (text fields, checkboxes, dropdowns)
3. User form bhare → app command generate kare → execute kare → output dikhaye
4. AI help kare — tool samjhaye, errors fix kare, workflow suggest kare

---

## Tech Stack (Kaunsi technology, kyon)

| Technology | Kahan use | Kyon |
|-----------|-----------|------|
| **Python + FastAPI** | Backend (server) | Fast, async, automatic API docs |
| **SQLite** | Database | File-based, zero setup, portable |
| **SQLAlchemy** | Database ORM | Python objects ↔ database tables (SQL likhne ki zaroorat nahi) |
| **React + TypeScript** | Frontend (UI) | Component-based, type-safe, fast |
| **Tailwind CSS** | Styling | Utility classes, no custom CSS needed |
| **Zustand** | State management | Simple global state (login status, settings) |
| **Electron** | Desktop app | Web app ko .exe me convert karta hai |
| **Vite** | Build tool | Super fast development server + bundler |
| **JWT (JSON Web Tokens)** | Authentication | Secure login tokens |
| **bcrypt** | Password hashing | One-way encryption (password safe store) |
| **WebSocket** | Live terminal | Real-time output streaming |
| **Google Gemini** | AI Assistant | Free AI for tool help, error analysis |

---

## Project Structure (Folder Guide)

```
vigil-labs/
├── backend/                    ← SERVER (Python FastAPI)
│   ├── app/
│   │   ├── api/routes/         ← API endpoints (URLs jo data dete hain)
│   │   │   ├── auth.py         ← Login/Register/Logout
│   │   │   ├── tools.py        ← Tool CRUD (create/read/update/delete)
│   │   │   ├── execution.py    ← Tool run karna + history
│   │   │   ├── store.py        ← Tool Store (browse/install/uninstall)
│   │   │   ├── workflows.py    ← Multi-tool pipelines
│   │   │   └── system.py       ← Health check + AI endpoints
│   │   ├── core/               ← Core utilities
│   │   │   ├── config.py       ← All settings (.env se load)
│   │   │   ├── database.py     ← Database connection
│   │   │   ├── security.py     ← Password hash + JWT + rate limit
│   │   │   ├── middleware.py   ← Error handling (catch all errors)
│   │   │   ├── validators.py   ← Input validation (security)
│   │   │   └── exceptions.py   ← Custom error types
│   │   ├── models/             ← Database table definitions
│   │   │   ├── user.py         ← Users table
│   │   │   ├── tool.py         ← Tools + Arguments tables
│   │   │   ├── execution.py    ← Execution history table
│   │   │   ├── workflow.py     ← Workflows table
│   │   │   ├── preset.py       ← Saved configurations
│   │   │   └── store.py        ← Store tools table
│   │   ├── schemas/            ← Request/Response format definitions
│   │   │   ├── auth.py         ← Login/Register data format
│   │   │   ├── tool.py         ← Tool data format
│   │   │   └── execution.py    ← Execution data format
│   │   ├── services/           ← Business logic
│   │   │   ├── execution_engine.py  ← CORE: builds + runs commands safely
│   │   │   ├── workflow_engine.py   ← Runs multi-tool pipelines
│   │   │   ├── tool_store.py        ← Install/uninstall tools
│   │   │   ├── store_catalog.py     ← 141 pre-configured tools list
│   │   │   ├── ai_agent.py          ← Rule-based AI (local, no API)
│   │   │   ├── ai_assistant.py      ← Help output parser
│   │   │   └── gemini_ai.py         ← Google Gemini AI integration
│   │   └── main.py            ← App entry point (starts everything)
│   ├── .env                    ← SECRET settings (not in git)
│   ├── .env.example            ← Template for .env
│   ├── requirements.txt        ← Python packages needed
│   ├── start.py                ← Production startup script
│   └── alembic/                ← Database migrations
│
├── frontend/                   ← USER INTERFACE (React)
│   ├── src/
│   │   ├── App.tsx             ← Route definitions (which page shows where)
│   │   ├── main.tsx            ← Entry point (renders React app)
│   │   ├── pages/              ← Each page of the app
│   │   │   ├── LoginPage.tsx       ← Login/Register screen
│   │   │   ├── DashboardPage.tsx   ← Main dashboard with stats
│   │   │   ├── ToolsPage.tsx       ← List of registered tools
│   │   │   ├── StorePage.tsx       ← Tool store (browse/install)
│   │   │   ├── ToolBuilderPage.tsx ← Create/edit tool GUI
│   │   │   ├── ExecutionPage.tsx   ← Run a tool with form
│   │   │   ├── HistoryPage.tsx     ← Past executions
│   │   │   ├── WorkflowsPage.tsx   ← Multi-tool workflows
│   │   │   ├── AIAssistantPage.tsx ← Gemini AI chat
│   │   │   └── SettingsPage.tsx    ← App settings
│   │   ├── components/         ← Reusable UI pieces
│   │   │   ├── layout/        ← Page layout (sidebar, topbar)
│   │   │   └── common/        ← Shared components (buttons, cards)
│   │   ├── store/              ← Global state
│   │   │   ├── authStore.ts    ← Login state (who is logged in)
│   │   │   └── appStore.ts     ← UI state (sidebar open, terminal)
│   │   ├── utils/              ← Helper functions
│   │   │   ├── api.ts          ← HTTP client (talks to backend)
│   │   │   └── cn.ts          ← CSS class merger utility
│   │   └── styles/
│   │       └── index.css       ← Global styles + Tailwind
│   ├── electron/               ← Desktop app wrapper
│   │   ├── main.js            ← Electron main process
│   │   └── preload.js         ← Security bridge
│   ├── package.json            ← Node.js dependencies
│   ├── vite.config.ts          ← Build configuration
│   ├── tailwind.config.js      ← Design system (colors, fonts)
│   └── tsconfig.json           ← TypeScript settings
│
├── START.bat                   ← ONE-CLICK LAUNCHER (Windows)
├── docker-compose.yml          ← Docker deployment
└── SECURITY.md                 ← Security documentation
```

---

## BACKEND EXPLAINED (Line by Line)

---

### `backend/app/core/config.py` — Settings

**Kya karta hai:** App ki saari settings ek jagah define karta hai. `.env` file se values load karta hai.

```python
class Settings(BaseSettings):
    APP_NAME: str = "VIGIL LABS"          # App ka naam
    SECRET_KEY: str = "..."               # JWT tokens sign karne ke liye (PRIVATE!)
    DATABASE_URL: str = "sqlite..."       # Database ka address
    MAX_CONCURRENT_PROCESSES: int = 10    # Ek saath kitne tools chal sakte hain
    GEMINI_API_KEY: str = ""              # AI ke liye Google API key
```

**Kyon:** Hardcoded values bad practice hai. Settings ek jagah hon to change karna easy hai. `.env` file se load hoti hain taki different environments (dev/prod) me alag values ho.

---

### `backend/app/core/security.py` — Security

**Kya karta hai:** Password hash karna, JWT tokens banana, rate limiting.

```python
def hash_password(password: str) -> str:
    """Password ko encrypt karta hai (one-way — wapas nahi aa sakta)"""
    pwd_bytes = password.encode("utf-8")[:72]  # bcrypt ki 72-byte limit
    salt = _bcrypt.gensalt(rounds=12)          # Random salt (har password alag)
    return _bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")
```

**Simple explanation:**
- User ne password diya "Test1234"
- `hash_password("Test1234")` → `$2b$12$xYzAbC...` (kuch random string)
- Database me ye random string store hoti hai, asli password KABHI nahi
- Login pe dobara hash karke compare karte hain

```python
def create_access_token(data: dict) -> str:
    """JWT token banata hai — ye user ko "pass" deta hai server access ka"""
```

**JWT kya hai:** Ek encoded string jo batati hai "ye user X hai, Y time tak valid hai." Jaise entry pass — dikhao aur andar jao, baar baar login nahi karna padta.

---

### `backend/app/core/database.py` — Database

**Kya karta hai:** Database se connect karta hai, tables banata hai.

```python
engine = create_async_engine(settings.DATABASE_URL)  # Connection banao
AsyncSessionLocal = async_sessionmaker(engine)       # "Session" factory

async def get_db():
    """Har API request ko ek database session deta hai"""
    async with AsyncSessionLocal() as session:
        yield session  # Use karo
        # Automatically band ho jaayega
```

**Kyon async:** Multiple users ek saath use kar sakte hain bina ek doosre ko block kiye.

---

### `backend/app/models/user.py` — User Table

**Kya karta hai:** Database me "users" table define karta hai.

```python
class User(Base):
    __tablename__ = "users"              # Table ka naam

    id = Column(String(36), primary_key=True)  # Unique ID (UUID)
    username = Column(String(50), unique=True)  # Username (duplicate nahi ho sakta)
    hashed_password = Column(String(255))       # Encrypted password
    role = Column(String(20), default="user")   # "admin" ya "user"
    is_active = Column(Boolean, default=True)   # Account active hai ya banned
```

**Kaise kaam karta hai:** Jab koi register karta hai → ek naya row ban jaata hai is table me.

---

### `backend/app/models/tool.py` — Tool Table

**Kya karta hai:** Registered tools store karta hai.

```python
class Tool(Base):
    __tablename__ = "tools"

    name = Column(String(100))               # Tool ka naam (jaise "Nmap")
    executable_path = Column(String(500))    # Path (jaise "nmap" ya "/usr/bin/nmap")
    command_template = Column(Text)          # Template: "{executable} {args}"
    risk_level = Column(String(20))          # "low", "medium", "high", "critical"
    execution_timeout = Column(Integer)      # Kitni der me timeout (seconds)
```

```python
class ToolArgument(Base):
    __tablename__ = "tool_arguments"

    name = Column(String(100))         # Argument naam (jaise "target")
    flag = Column(String(50))          # CLI flag (jaise "-p" ya "--port")
    field_type = Column(String(50))    # Form me kya dikhega: "text", "number", "select", "toggle"
    is_required = Column(Boolean)      # Zaruri hai ya optional
```

**Ye combined kaise kaam karta hai:**
1. Tool = "Nmap", template = `nmap {args}`
2. Arguments = [{name: "target", flag: "", type: "ip"}, {name: "ports", flag: "-p", type: "text"}]
3. User form bhare: target=192.168.1.1, ports=1-1000
4. App command banaye: `nmap -p 1-1000 192.168.1.1`
5. Execute kare → output dikhaye

---

### `backend/app/services/execution_engine.py` — CORE (Command Runner)

**Ye sabse important file hai.** Ye actually tools chalata hai.

```python
def build_command(self, template, executable, arguments, tool_args):
    """User ke form input se final command banata hai"""
    # Template: "nmap {args}"
    # Arguments: {target: "192.168.1.1", ports: "80,443"}
    # Tool args definitions: [{name: "ports", flag: "-p"}, ...]
    # Result: "nmap -p '80,443' '192.168.1.1'"
```

```python
async def execute(self, command, execution_id, ...):
    """Command ko actually run karta hai (subprocess)"""
    # 1. Security check — dangerous command to nahi?
    is_safe, reason = validate_command_safety(command)
    if not is_safe:
        raise RuntimeError(f"Blocked: {reason}")

    # 2. Process start karo
    process = await asyncio.create_subprocess_shell(command, ...)

    # 3. Output stream karo (real-time WebSocket se)
    # 4. Timeout handle karo
    # 5. Complete hone pe status update karo
```

**Security kaise kaam karti hai:**
- `rm -rf /` type commands BLOCKED hain
- Shell operators (`&&`, `|`, `;`) by default BLOCKED (injection prevention)
- Har input `shlex.quote()` se escaped hota hai
- Ek saath max 10 processes (DoS prevention)

---

### `backend/app/services/gemini_ai.py` — AI Integration

```python
async def chat(message: str, context: Optional[str] = None) -> str:
    """Gemini AI ko message bhejta hai, response wapas laata hai"""
    model = _get_model()  # Lazy load (pehli baar pe hi initialize)
    response = model.generate_content(prompt)
    return response.text
```

**System prompt** (AI ko bataya gaya hai wo kya hai):
> "You are VIGIL LABS AI — a cybersecurity expert assistant. Help users configure tools, understand outputs, fix errors. Never refuse legitimate tool usage."

---

### `backend/app/api/routes/auth.py` — Login/Register API

```python
@router.post("/register")
async def register(request: RegisterRequest, db: AsyncSession):
    """Naya user account banata hai"""
    # 1. Password strong hai? (8+ chars, uppercase+lowercase+number)
    # 2. Username already taken?
    # 3. Pehla user hai? → Admin role do
    # 4. Password hash karo
    # 5. Database me save karo
    # 6. JWT token generate karo
    # 7. Token + user info return karo
```

```python
@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession):
    """Existing user login"""
    # 1. Username se user dhundho
    # 2. Password verify karo (hash compare)
    # 3. Account active hai?
    # 4. JWT token generate karo
    # 5. Return karo
```

---

### `backend/app/services/store_catalog.py` — Tool Catalog (141 Tools)

```python
TOOL_CATALOG = [
    {
        "name": "Nmap",                              # Display name
        "slug": "nmap",                              # URL-friendly ID
        "category": "Recon / Scanning",              # Category
        "description": "Network discovery tool",     # What it does
        "executable_name": "nmap",                   # Binary name
        "install_method": "apt",                     # How to install
        "install_command_linux": "sudo apt install -y nmap",
        "install_command_windows": "choco install nmap -y",
        "install_command_macos": "brew install nmap",
        "risk_level": "medium",                      # How dangerous
        "supports_linux": True,                      # Platform support
        "supports_windows": True,
        "supports_macos": True,
        "tags": ["network", "scanner", "ports"],     # Search tags
    },
    # ... 140 more tools
]
```

---

## FRONTEND EXPLAINED

---

### `frontend/src/utils/api.ts` — HTTP Client

**Kya karta hai:** Backend se baat karta hai. Har request me automatically JWT token lagata hai.

```typescript
export const api = axios.create({
  baseURL: 'http://localhost:8000',  // Backend ka address
  timeout: 30000,                    // 30 sec timeout
});

// Har request me token daal
api.interceptors.request.use((config) => {
  const token = getStoredToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// 401 aaye to token refresh karo
api.interceptors.response.use(response => response, async (error) => {
  if (error.response?.status === 401) {
    // Refresh token se naya access token lo
    // Fail ho to login page pe bhej do
  }
});
```

---

### `frontend/src/store/authStore.ts` — Login State

```typescript
export const useAuthStore = create((set) => ({
  user: null,           // Logged in user info
  accessToken: null,    // JWT access token
  isAuthenticated: false,

  login: async (username, password) => {
    const res = await api.post('/api/auth/login', { username, password });
    set({ user: res.data.user, accessToken: res.data.access_token, isAuthenticated: true });
  },

  logout: () => {
    set({ user: null, accessToken: null, isAuthenticated: false });
  },
}));
```

**Zustand kya hai:** Global state management. Koi bhi component `useAuthStore()` call karke user info access kar sakta hai.

---

### `frontend/src/App.tsx` — Routing

```typescript
<Routes>
  <Route path="/login" element={<LoginPage />} />
  <Route path="/*" element={
    <ProtectedRoute>  {/* Logged in nahi? → Login pe bhej do */}
      <MainLayout>    {/* Sidebar + TopBar wrapper */}
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/tools" element={<ToolsPage />} />
        <Route path="/store" element={<StorePage />} />
        <Route path="/execute/:toolId" element={<ExecutionPage />} />
        {/* ... baaki pages */}
      </MainLayout>
    </ProtectedRoute>
  } />
</Routes>
```

---

### `frontend/tailwind.config.js` — Design System

```javascript
colors: {
  vigil: {
    bg: '#f6f7fb',        // Page background (light gray)
    card: '#ffffff',       // Cards (white)
    primary: '#6366f1',   // Main accent (indigo/purple)
    success: '#059669',   // Green (success)
    danger: '#dc2626',    // Red (error)
    text: '#0f172a',      // Main text (dark)
  }
}
```

**Kyon custom colors:** Poori app me consistent look chahiye. `bg-vigil-primary` likhte hain, color ek jagah se change hota hai.

---

## KEY FLOWS (How Things Work End-to-End)

---

### Flow 1: User Register karta hai

```
Browser → POST /api/auth/register {username, password}
   ↓
auth.py: validate password strength
   ↓
security.py: hash_password("Test1234") → "$2b$12$..."
   ↓
database: INSERT INTO users (id, username, hashed_password, role="admin")
   ↓
security.py: create_access_token({sub: user_id, role: "admin"})
   ↓
Response: {access_token: "eyJ...", user: {...}}
   ↓
Frontend: authStore saves token → redirects to /dashboard
```

---

### Flow 2: Tool Execute karta hai

```
User fills form → clicks "Execute"
   ↓
Frontend: POST /api/executions/run {tool_id, arguments: {target: "x.x.x.x", ports: "80"}}
   ↓
execution.py: load tool from DB → load tool_arguments
   ↓
execution_engine.build_command("nmap {args}", "nmap", {target: "x.x.x.x"}, [...])
   → Result: "nmap -p '80' 'x.x.x.x'"
   ↓
execution_engine.validate_command_safety("nmap -p '80' 'x.x.x.x'")
   → OK (no dangerous patterns)
   ↓
execution_engine.execute(command, ...) → subprocess starts
   ↓
WebSocket streams output line-by-line to browser
   ↓
Process completes → status="completed", exit_code=0
   ↓
Frontend shows green "Completed!" with full output
```

---

### Flow 3: Tool Install karta hai

```
User clicks "Install" on Nmap in Store
   ↓
Frontend: POST /api/store/install/{tool_id}
   ↓
store.py: load StoreTool from DB
   ↓
tool_store.py: check if already installed (shutil.which("nmap"))
   → If yes: return {success: true, already_installed: true}
   ↓
tool_store.py: get_install_command(tool_data)
   → Windows: "choco install nmap -y"
   → Linux: "sudo apt install -y nmap"
   → macOS: "brew install nmap"
   ↓
tool_store.py: run command (subprocess)
   ↓
Verify: shutil.which("nmap") → found at "C:\Program Files\Nmap\nmap.exe"
   ↓
Response: {success: true, path: "C:\..."}
   ↓
Frontend: shows "Installed ✓"
```

---

## SECURITY EXPLAINED

| Protection | Kya karta hai | Kyon |
|-----------|---------------|------|
| Password hashing (bcrypt) | Password encrypt (one-way) | Database leak hone pe bhi password safe |
| JWT tokens | Har request verify | Session hijacking prevent |
| Rate limiting | 5 login attempts/5 min | Brute force attack prevent |
| Command sanitization | Shell operators block | Command injection prevent |
| Input validation | Max length, format check | Buffer overflow/SQL injection prevent |
| CORS | Sirf allowed origins | Cross-site attacks prevent |
| Security headers | X-Frame-Options etc. | Clickjacking prevent |

---

## HOW TO ADD A NEW TOOL (User Guide)

1. **Store se install karo** (agar available hai)
2. **Ya manually Tool Builder me:**
   - Name: "My Tool"
   - Executable: `mytool` (ya full path)
   - Command Template: `{executable} {args}`
   - Add Arguments:
     - Name: "target", Flag: "-t", Type: "text", Required: yes
     - Name: "verbose", Flag: "-v", Type: "toggle"
   - Save
3. **Execute:** Tools page → click Run → form bharo → Execute!

---

## COMMON ERRORS & FIXES

| Error | Cause | Fix |
|-------|-------|-----|
| "Registration failed" | Password weak | 8+ chars, A-Z + a-z + 0-9 |
| "Failed to load tool store" | Backend not running | Start backend first |
| "Not supported on your OS" | Linux-only tool on Windows | Use WSL or Kali |
| "AI quota exceeded" | 15 req/min Gemini limit | Wait 1 min or regenerate key |
| "Install failed: permission" | Needs admin | Run as Administrator |

---

## GLOSSARY (Technical Terms Explained)

| Term | Meaning |
|------|---------|
| **API** | Application Programming Interface — backend ke URLs jo data dete hain |
| **JWT** | JSON Web Token — encoded "pass" for authentication |
| **Hash** | One-way encryption (can't be reversed) |
| **ORM** | Object-Relational Mapping — Python objects = database tables |
| **CORS** | Cross-Origin Resource Sharing — which websites can talk to backend |
| **WebSocket** | Two-way real-time connection (for live terminal output) |
| **Middleware** | Code that runs on EVERY request (logging, security headers) |
| **Schema** | Data format definition (what fields a request must have) |
| **Migration** | Database structure change (add/remove columns safely) |
| **Singleton** | Only one instance of a class exists (shared globally) |
| **Async** | Code that doesn't block — multiple things happen simultaneously |
| **subprocess** | Running another program from within your program |
| **Rate Limiting** | Restricting how many requests someone can make (anti-abuse) |

---

*This documentation was written for VIGIL LABS v1.0.0*
*If you read this far, you now understand the entire codebase. 🎉*
