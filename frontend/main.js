const { app, BrowserWindow } = require('electron');
const fs = require('fs');
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
      webSecurity: false,
      media: true
    }
  });

  const settingsPath = path.join(__dirname, '../settings.json');
  let termsAgreed = false;

  try {
    if (fs.existsSync(settingsPath)) {
      const rawData = fs.readFileSync(settingsPath);
      const settings = JSON.parse(rawData);
      termsAgreed = settings.terms_agreed;
    }
  } catch (error) {
    console.log("Error reading settings file:", error);
  }

  if (termsAgreed) {
    win.loadURL('http://localhost:8000/index.html');
  } else {
    win.loadURL('http://localhost:8000/pages/welcome/welcome.html');
  }
}

app.whenReady().then(createWindow);

