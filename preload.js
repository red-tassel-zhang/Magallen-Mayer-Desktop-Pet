const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  moveWindow: (dx, dy) => ipcRenderer.send('move-window', { dx, dy }),
  setWindowPosition: (x, y) => ipcRenderer.send('set-window-position', { x, y }),
  closeApp: () => ipcRenderer.send('close-app'),
  minimizeApp: () => ipcRenderer.send('minimize-app'),
  getWindowBounds: () => ipcRenderer.invoke('get-window-bounds'),
});
