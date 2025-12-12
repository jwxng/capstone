const { app, BrowserWindow } = require('electron');
const path = require("path");

function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    icon: path.join(__dirname, "assets/clock-circle.svg"), 
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
      contextIsolation: true,
      websecurity: false,
      media: true
    }
  });

  win.loadFile('index.html');
}

app.whenReady().then(createWindow);
