# VIGIL LABS - Free Production Deployment Guide

> **Important:** VIGIL LABS installs and runs real CLI security tools. So it needs a
> **persistent Linux environment** where those tools can be installed. Stateless
> serverless platforms (like Cloud Run) are NOT suitable — they wipe installed
> tools and the database on every restart.
>
> **Only run scans/tools against systems you own or are explicitly authorized to test.**

---

## Which option should I pick?

| Option | Cost | Tools run? | Phone access | Difficulty |
|--------|------|-----------|--------------|-----------|
| **A. Oracle Cloud Always Free VM** | Free forever | ✅ Yes | ✅ Yes | Medium |
| **B. Your own PC + Cloudflare Tunnel** | Free | ✅ Yes | ✅ Yes | Easy |

Recommended: **Option A** for a always-on server, **Option B** if you just want to
test quickly from your phone.

---

# Option A — Oracle Cloud Always Free VM (Recommended)

Oracle gives a genuinely free-forever VM (ARM Ampere: up to 4 cores + 24 GB RAM).
Perfect for a Linux security box.

## Step 1: Create the account + VM

1. Sign up at https://www.oracle.com/cloud/free/ (needs a card for verification, but
   Always Free resources are never charged).
2. In the console: **Menu -> Compute -> Instances -> Create Instance**
3. Settings:
   - **Image:** Ubuntu 22.04 (or 24.04)
   - **Shape:** `VM.Standard.A1.Flex` (Ampere ARM) — set **2 OCPU / 12 GB RAM**
     (stays inside Always Free)
   - **SSH keys:** Download the private key (you'll need it to connect)
4. Under **Networking**, make sure "Assign a public IPv4 address" is on.
5. Click **Create**. Note the **public IP** once it's running.

## Step 2: Open firewall ports

In Oracle console: **Networking -> Virtual Cloud Networks -> your VCN -> Security Lists
-> Default Security List -> Add Ingress Rules**:

| Source CIDR | Protocol | Dest Port |
|-------------|----------|-----------|
| 0.0.0.0/0 | TCP | 80 |
| 0.0.0.0/0 | TCP | 443 |

## Step 3: Connect via SSH

```bash
# From your PC (use the key you downloaded)
chmod 600 ~/Downloads/ssh-key.key
ssh -i ~/Downloads/ssh-key.key ubuntu@<YOUR_PUBLIC_IP>
```

## Step 4: Install Docker

```bash
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
# Ubuntu firewall (in addition to Oracle's)
sudo iptables -I INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save 2>/dev/null || true
# Log out and back in so docker group applies
exit
```

Reconnect (ssh again), then verify: `docker --version`

## Step 5: Deploy VIGIL LABS

```bash
# Clone your repo
git clone https://github.com/RishiPlaysCodes/Hacomb.git
cd Hacomb/vigil-labs

# Create the env file
cp .env.example .env
nano .env
```

In `.env`, set a strong secret (generate on the VM):
```bash
# Run this and paste the output into SECRET_KEY=
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

Then start it:
```bash
docker compose up -d --build
```

## Step 6: Access it

Open on your phone/PC: `http://<YOUR_PUBLIC_IP>`

Register the first account (that becomes admin). Done — it's live 24/7, free forever.

## Step 7 (optional): Free domain + HTTPS

1. Get a free domain (e.g., from https://www.duckdns.org — `yourname.duckdns.org`)
   and point it to your VM's public IP.
2. Add Caddy for automatic HTTPS (edit `docker-compose.yml` to add a Caddy service),
   or run:
   ```bash
   sudo apt install -y caddy
   sudo caddy reverse-proxy --from yourname.duckdns.org --to localhost:80
   ```

---

# Option B — Your Own PC + Cloudflare Tunnel (Easiest)

Run VIGIL LABS on your laptop (where tools are already/easily installed) and expose it
to your phone through a free Cloudflare Tunnel. Nothing to pay, no VM.

## Step 1: Run the app locally

```bash
cd Hacomb/vigil-labs

# Option 1: Docker (simplest)
cp .env.example .env
# set SECRET_KEY in .env (python -c "import secrets; print(secrets.token_urlsafe(64))")
docker compose up -d --build
# App now on http://localhost

# Option 2: Without Docker (two terminals)
# Terminal 1 - backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && cp .env.example .env && python start.py
# Terminal 2 - frontend
cd frontend && npm install && npm run dev
```

## Step 2: Install cloudflared

```bash
# Linux
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared && sudo mv cloudflared /usr/local/bin/

# macOS
brew install cloudflared

# Windows: download cloudflared.exe from
# https://github.com/cloudflare/cloudflared/releases/latest
```

## Step 3: Start the tunnel

```bash
# Point it at your running app (port 80 if Docker, 5173 if npm dev)
cloudflared tunnel --url http://localhost:80
```

Cloudflare prints a public URL like:
```
https://random-words-here.trycloudflare.com
```

Open that URL on your **phone** — done! Works from anywhere, free, no signup needed
for quick tunnels.

> Note: quick-tunnel URLs change each run. For a permanent URL, create a free
> Cloudflare account and a named tunnel (`cloudflared tunnel login`).

---

# Updating the app (either option)

```bash
cd Hacomb/vigil-labs
git pull
docker compose up -d --build   # Docker
# or restart your python/npm processes
```

---

# Quick decision

- **Want it always online, free forever, real server?** -> Option A (Oracle Cloud)
- **Just want to use it from your phone right now?** -> Option B (Cloudflare Tunnel)

Both are 100% free. Neither needs a credit-card charge.
