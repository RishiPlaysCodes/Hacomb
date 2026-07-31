/**
 * VIGIL LABS - Electron Main Process
 * Production-hardened window management, backend lifecycle, and security.
 */
const { app, BrowserWindow, ipcMain, shell, session } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow = null;
let backendProcess = null;

const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

// ─── Security: Disable remote module and restrict navigation ─────────────────

app.on('web-contents-created', (_event, contents) => {
  // Prevent navigation to unknown origins
  contents.on('will-navigate', (event, navigationUrl) => {
    const parsedUrl = new URL(navigationUrl);
    const allowedOrigins = ['http://localhost:5173', 'http://localhost:8000'];
    
    if (!allowedOrigins.includes(parsedUrl.origin) && parsedUrl.protocol !== 'file:') {
      event.preventDefault();
      shell.openExternal(navigationUrl);
    }
  });

  // Block new window creation (popup blockers)
  contents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
});

// ─── Window Creation ─────────────────────────────────────────────────────────

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    title: 'VIGIL LABS',
    icon: path.join(__dirname, '../public/vigil-icon.png'),
    frame: false,
    titleBarStyle: 'hidden',
    titleBarOverlay: {
      color: '#0a0a0f',
      symbolColor: '#e2e8f0',
      height: 36,
    },
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,       // CRITICAL: Isolate renderer from Node.js
      nodeIntegration: false,        // CRITICAL: No Node.js in renderer
      sandbox: true,                 // Additional sandboxing
      webSecurity: true,             // Enforce same-origin policy
      allowRunningInsecureContent: false,
    },
    backgroundColor: '#0a0a0f',
    show: false,
  });

  // Load app
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  // Show when ready (prevents visual flash)
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// ─── Content Security Policy ─────────────────────────────────────────────────

function setCSP() {
  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': [
          isDev
            ? "default-src 'self' http://localhost:*; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; connect-src 'self' http://localhost:* ws://localhost:*;"
            : "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self' http://127.0.0.1:8000 ws://127.0.0.1:8000;",
        ],
      },
    });
  });
}

// ─── Backend Process Management ──────────────────────────────────────────────

function startBackend() {
  if (isDev) return; // In dev, backend runs separately

  // Resolve backend directory - works both in dev and packaged
  let backendDir;
  if (app.isPackaged) {
    // In packaged app, backend should be next to the .exe
    backendDir = path.join(path.dirname(app.getPath('exe')), 'backend');
  } else {
    backendDir = path.join(__dirname, '../../backend');
  }

  // Check if backend directory exists
  const fs = require('fs');
  if (!fs.existsSync(backendDir)) {
    console.error(`[Backend] Directory not found: ${backendDir}`);
    console.error('[Backend] Please ensure the backend folder is next to the app.');
    // Don't crash - just show the app without backend
    // User can start backend manually
    return;
  }

  const pythonPath = process.platform === 'win32' ? 'python' : 'python3';

  backendProcess = spawn(
    pythonPath,
    ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'],
    {
      cwd: backendDir,
      env: { ...process.env, PYTHONPATH: backendDir, ENVIRONMENT: 'production' },
      stdio: ['ignore', 'pipe', 'pipe'],
      shell: true, // Use shell on Windows to find python in PATH
    }
  );

  backendProcess.stdout.on('data', (data) => {
    console.log(`[Backend] ${data.toString().trim()}`);
  });

  backendProcess.stderr.on('data', (data) => {
    console.error(`[Backend] ${data.toString().trim()}`);
  });

  backendProcess.on('exit', (code) => {
    console.log(`[Backend] Process exited with code ${code}`);
    if (code !== 0 && mainWindow) {
      mainWindow.webContents.send('notification', {
        type: 'error',
        title: 'Backend Error',
        message: 'The backend process has crashed. Please restart the application.',
      });
    }
  });
}

// ─── IPC Handlers ────────────────────────────────────────────────────────────

ipcMain.handle('get-platform', () => process.platform);
ipcMain.handle('get-version', () => app.getVersion());

// ─── App Lifecycle ───────────────────────────────────────────────────────────

app.whenReady().then(() => {
  setCSP();
  startBackend();
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on('before-quit', () => {
  if (backendProcess && !backendProcess.killed) {
    backendProcess.kill('SIGTERM');
    // Force kill after 5 seconds
    setTimeout(() => {
      if (backendProcess && !backendProcess.killed) {
        backendProcess.kill('SIGKILL');
      }
    }, 5000);
  }
});
