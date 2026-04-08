const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  openGamePopup: (gameUrl) => ipcRenderer.send('open-game-popup', gameUrl),
  closeGamePopup: () => ipcRenderer.send('close-game-popup'),
  onGameClosed: (callback) => ipcRenderer.on('game-popup-closed', callback),
  onPointsUpdated: (callback) => ipcRenderer.on('points-updated', (event, total) => callback(total))
});
