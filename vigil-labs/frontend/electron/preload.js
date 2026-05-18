const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('vigilAPI', {
  getPlatform: () => ipcRenderer.invoke('get-platform'),
  getVersion: () => ipcRenderer.invoke('get-version'),
  onNotification: (callback) => ipcRenderer.on('notification', callback),
});
