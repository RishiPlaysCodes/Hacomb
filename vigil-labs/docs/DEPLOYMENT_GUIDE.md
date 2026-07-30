# VIGIL LABS - Deployment Guide

## Table of Contents
1. [Local Testing (VS Code)](#local-testing-vs-code)
2. [Google Cloud Free Deployment](#google-cloud-free-deployment)
3. [Accessing on Phone](#accessing-on-phone)

---

## Local Testing (VS Code)

### Prerequisites
- Python 3.11+ installed
- Node.js 18+ installed  
- VS Code with Python & ESLint extensions

---

### Step 1: Clone the Repo

```bash
git clone https://github.com/RishiPlaysCodes/Hacomb.git
cd Hacomb/vigil-labs
```

---

### Step 2: Backend Setup

Open **Terminal 1** in VS Code (`Ctrl + ~`):

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Generate a secret key and add to .env
python -c "import secrets; print(secrets.token_urlsafe(64))"
# Copy the output and paste as SECRET_KEY value in .env

# Start the server
python start.py
```

You should see:
```
============================================================
  VIGIL LABS v1.0.0
  Environment: development
  Host: 127.0.0.1:8000
  Workers: 1
  Debug: True
============================================================
```

**Test it:** Open browser → http://localhost:8000/docs (Swagger UI)

---

### Step 3: Frontend Setup

Open **Terminal 2** in VS Code (`Ctrl + Shift + ~`):

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

You should see:
```
VITE v5.x.x ready in XXXms
➜ Local: http://localhost:5173/
```

**Test it:** Open browser → http://localhost:5173

---

### Step 4: Test the Full App

1. Go to http://localhost:5173
2. Click **Register** → Create first account (this gets admin role)
3. You're in! Explore Dashboard, Tools, Store, etc.
4. Try adding a tool (e.g., `nmap` if installed on your system)

---

### Quick Commands Reference

| Action | Command |
|--------|---------|
| Start Backend | `cd backend && python start.py` |
| Start Frontend | `cd frontend && npm run dev` |
| Build Frontend | `cd frontend && npm run build` |
| Build Electron App | `cd frontend && npm run electron:build` |
| Run DB Migration | `cd backend && alembic upgrade head` |
| Create Migration | `cd backend && alembic revision --autogenerate -m "description"` |

---

### VS Code Recommended Extensions
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- ESLint (dbaeumer.vscode-eslint)
- Tailwind CSS IntelliSense (bradlc.vscode-tailwindcss)
- Thunder Client (for API testing)

---

## Google Cloud Free Deployment

### What You Get Free

Google Cloud offers:
- **$300 free credits** for 90 days (new accounts)
- **Cloud Run Always Free tier**: 2 million requests/month, 360,000 GB-seconds of memory
- **Artifact Registry**: 500 MB storage free
- **Cloud SQL**: Not free, but we'll use SQLite or free alternatives

**Best strategy for FREE deployment:** Use **Cloud Run** (serverless containers) — it's within always-free limits for personal projects.

---

### Step 0: Check Your Google Developer Account

Tu ne bola tha Google Developer Student Club me enroll kiya tha. Yeh check kar:

1. Go to → https://developers.google.com/profile
2. Sign in with your Google account
3. Check if you have any credits or tier benefits
4. Also go to → https://console.cloud.google.com/billing
   - If you see a billing account with credits → you're good!
   - If not → Sign up for free trial at https://cloud.google.com/free

**Google Cloud Free Trial:**
- $300 credit, 90 days
- No auto-charge (they ask before billing starts)
- Credit card required for verification only (they won't charge)

---

### Step 1: Install Google Cloud CLI

```bash
# Windows (PowerShell as Admin):
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:temp\GoogleCloudSDKInstaller.exe")
& $env:temp\GoogleCloudSDKInstaller.exe

# Linux:
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

After install:
```bash
# Login
gcloud auth login

# Set project (create one if needed)
gcloud projects create vigil-labs-app --name="VIGIL LABS"
gcloud config set project vigil-labs-app

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

---

### Step 2: Create Artifact Registry (Docker Repo)

```bash
# Create a Docker repository
gcloud artifacts repositories create vigil-labs \
  --repository-format=docker \
  --location=asia-south1 \
  --description="VIGIL LABS Docker images"

# Configure Docker to use it
gcloud auth configure-docker asia-south1-docker.pkg.dev
```

> **Note:** Use `asia-south1` (Mumbai) for lowest latency from India.

---

### Step 3: Build & Push Backend Image

From the `vigil-labs/` directory:

```bash
# Build backend image
docker build -t asia-south1-docker.pkg.dev/vigil-labs-app/vigil-labs/backend:latest ./backend

# Push to Google Artifact Registry
docker push asia-south1-docker.pkg.dev/vigil-labs-app/vigil-labs/backend:latest
```

**No Docker on your machine?** Use Cloud Build instead:
```bash
cd backend
gcloud builds submit --tag asia-south1-docker.pkg.dev/vigil-labs-app/vigil-labs/backend:latest .
```

---

### Step 4: Deploy Backend to Cloud Run

```bash
gcloud run deploy vigil-labs-backend \
  --image=asia-south1-docker.pkg.dev/vigil-labs-app/vigil-labs/backend:latest \
  --region=asia-south1 \
  --platform=managed \
  --allow-unauthenticated \
  --port=8000 \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=1 \
  --set-env-vars="ENVIRONMENT=production,SECRET_KEY=YOUR-SECRET-KEY-HERE,DATABASE_URL=sqlite+aiosqlite:///./data/vigil_labs.db,DEBUG=false,LOG_LEVEL=INFO,LOG_FORMAT=json,CORS_ORIGINS=[\"https://vigil-labs-frontend-XXXXX.run.app\"],REGISTRATION_ENABLED=true,FIRST_USER_IS_ADMIN=true"
```

> Replace `YOUR-SECRET-KEY-HERE` with a real key:
> ```bash
> python -c "import secrets; print(secrets.token_urlsafe(64))"
> ```

After deploy, you'll get a URL like:
```
https://vigil-labs-backend-xxxxx-el.a.run.app
```

**Save this URL! You need it for frontend.**

---

### Step 5: Build & Deploy Frontend

First, update the API URL for production:

```bash
cd frontend

# Build with the backend URL
VITE_API_URL=https://vigil-labs-backend-xxxxx-el.a.run.app npm run build
```

Or if you can't set env vars inline (Windows):
1. Create `frontend/.env.production`:
```
VITE_API_URL=https://vigil-labs-backend-xxxxx-el.a.run.app
```
2. Then: `npm run build`

Now deploy the frontend:

```bash
# Build frontend Docker image
docker build -t asia-south1-docker.pkg.dev/vigil-labs-app/vigil-labs/frontend:latest ./frontend

# Push
docker push asia-south1-docker.pkg.dev/vigil-labs-app/vigil-labs/frontend:latest

# Deploy to Cloud Run
gcloud run deploy vigil-labs-frontend \
  --image=asia-south1-docker.pkg.dev/vigil-labs-app/vigil-labs/frontend:latest \
  --region=asia-south1 \
  --platform=managed \
  --allow-unauthenticated \
  --port=80 \
  --memory=256Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=1
```

---

### Step 6: Update CORS

After frontend deploys, you'll get its URL (e.g., `https://vigil-labs-frontend-xxxxx.run.app`).

Update the backend CORS:
```bash
gcloud run services update vigil-labs-backend \
  --region=asia-south1 \
  --update-env-vars="CORS_ORIGINS=[\"https://vigil-labs-frontend-xxxxx.run.app\"]"
```

---

### Step 7: Test It!

1. Open the frontend URL on your phone: `https://vigil-labs-frontend-xxxxx.run.app`
2. Register your admin account
3. Done! It's live on the internet!

---

### Free Tier Limits (So You Don't Get Charged)

| Resource | Free Limit | VIGIL LABS Usage |
|----------|-----------|------------------|
| Cloud Run Requests | 2 million/month | ~100-1000 (personal use) |
| Cloud Run CPU | 180,000 vCPU-seconds | Minimal (serverless) |
| Cloud Run Memory | 360,000 GB-seconds | ~512MB per request |
| Artifact Registry | 500 MB | ~200MB (our images) |
| Cloud Build | 120 build-minutes/day | 2-3 builds max |

**You will NOT be charged** for personal use within these limits.

---

### Cost-Saving Tips

1. **Set `min-instances=0`** — Container scales to zero when not in use (no cost when idle)
2. **Use `asia-south1`** — Mumbai region, low latency from India
3. **SQLite is fine** for personal use — no need for Cloud SQL ($$$)
4. **Set budget alerts**: Console → Billing → Budgets → Create budget → Set $0 alert

---

### Set Budget Alert (Important!)

```bash
# Go to: https://console.cloud.google.com/billing/budgets
# OR via CLI:
gcloud billing budgets create \
  --billing-account=YOUR-BILLING-ACCOUNT-ID \
  --display-name="VIGIL LABS Budget" \
  --budget-amount=0 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

---

## Accessing on Phone

Once deployed on Google Cloud Run:

1. Just open the frontend URL in your phone browser
2. Add to Home Screen (Chrome → 3 dots → "Add to Home screen")
3. It works like an app!

The frontend is fully responsive (Tailwind CSS) so it works great on mobile.

---

## Updating the App

When you make changes:

```bash
# Rebuild and redeploy backend
cd backend
gcloud builds submit --tag asia-south1-docker.pkg.dev/vigil-labs-app/vigil-labs/backend:latest .
gcloud run deploy vigil-labs-backend \
  --image=asia-south1-docker.pkg.dev/vigil-labs-app/vigil-labs/backend:latest \
  --region=asia-south1

# Rebuild and redeploy frontend
cd ../frontend
npm run build
docker build -t asia-south1-docker.pkg.dev/vigil-labs-app/vigil-labs/frontend:latest .
docker push asia-south1-docker.pkg.dev/vigil-labs-app/vigil-labs/frontend:latest
gcloud run deploy vigil-labs-frontend \
  --image=asia-south1-docker.pkg.dev/vigil-labs-app/vigil-labs/frontend:latest \
  --region=asia-south1
```

---

## Troubleshooting

### "Permission Denied" errors
```bash
gcloud auth login
gcloud config set project vigil-labs-app
```

### Backend not starting on Cloud Run
Check logs:
```bash
gcloud run services logs read vigil-labs-backend --region=asia-south1 --limit=50
```

### CORS errors in browser
Make sure the frontend URL is in `CORS_ORIGINS` env var on backend.

### Frontend showing "Cannot connect to server"
- Check backend is running: `curl https://your-backend-url.run.app/health`
- Check VITE_API_URL was set correctly during build

---

## Summary of Commands (Quick Reference)

```bash
# ═══ LOCAL TESTING ═══
cd backend && python start.py          # Start backend
cd frontend && npm run dev             # Start frontend

# ═══ GOOGLE CLOUD SETUP (One-time) ═══
gcloud auth login
gcloud projects create vigil-labs-app
gcloud config set project vigil-labs-app
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
gcloud artifacts repositories create vigil-labs --repository-format=docker --location=asia-south1

# ═══ DEPLOY ═══
cd backend && gcloud builds submit --tag asia-south1-docker.pkg.dev/vigil-labs-app/vigil-labs/backend:latest .
gcloud run deploy vigil-labs-backend --image=asia-south1-docker.pkg.dev/vigil-labs-app/vigil-labs/backend:latest --region=asia-south1 --allow-unauthenticated --port=8000 --memory=512Mi --min-instances=0 --max-instances=1

cd frontend && npm run build
gcloud builds submit --tag asia-south1-docker.pkg.dev/vigil-labs-app/vigil-labs/frontend:latest .
gcloud run deploy vigil-labs-frontend --image=asia-south1-docker.pkg.dev/vigil-labs-app/vigil-labs/frontend:latest --region=asia-south1 --allow-unauthenticated --port=80 --memory=256Mi --min-instances=0 --max-instances=1
```
