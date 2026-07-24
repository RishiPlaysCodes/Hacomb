/**
 * VIGIL LABS - Electron Preload Script
 * Exposes a minimal, safe API to the renderer process.
 * Only whitelisted IPC channels are exposed.
 */
const { contextBridge, ipcRenderer } = require('electron');

// Whitelist of allowed IPC channels
const ALLOWED_INVOKE_CHANNELS = ['get-platform', 'get-version'];
const ALLOWED_RECEIVE_CHANNELS = ['notification', 'update-available'];

contextBridge.exposeInMainWorld('vigilAPI', {
  getPlatform: () => ipcRenderer.invoke('get-platform'),
  getVersion: () => ipcRenderer.invoke('get-version'),
  
  // Safe listener registration (prevents arbitrary channel listening)
  onNotification: (callback) => {
    const handler = (_event, ...args) => callback(...args);
    ipcRenderer.on('notification', handler);
    // Return cleanup function
    return () => ipcRenderer.removeListener('notification', handler);
  },
  
  onUpdateAvailable: (callback) => {
    const handler = (_event, ...args) => callback(...args);
    ipcRenderer.on('update-available', handler);
    return () => ipcRenderer.removeListener('update-available', handler);
  },
});
