const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  closeGamePopup: () => ipcRenderer.send('close-game-popup'),
  updatePoints: (total) => ipcRenderer.send('update-points', total)
});