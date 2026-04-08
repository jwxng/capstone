const { app, BrowserWindow, ipcMain } = require('electron');
const fs = require('fs');
const path = require('path');

let mainWindow = null;
let gamePopup = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1300,
    height: 1000,
    icon: path.join(__dirname, 'assets/clock-circle.svg'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
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
    console.log('Error reading settings file:', error);
  }

  if (termsAgreed) {
    mainWindow.loadURL('http://localhost:8000/index.html');
  } else {
    mainWindow.loadURL('http://localhost:8000/pages/welcome/welcome.html');
  }
}

function openGamePopup(gameUrl) {
  if (gamePopup && !gamePopup.isDestroyed()) {
    gamePopup.loadURL(gameUrl);
    gamePopup.focus();
    return;
  }

  gamePopup = new BrowserWindow({
    width: 500,
    height: 650,
    alwaysOnTop: true,           // Ensuring that it stays on top always
    resizable: false,
    minimizable: false,          // prevent user from minimizing it away
    fullscreenable: false,
    frame: false,                // borderless — your game HTML has its own close button
    transparent: false,
    backgroundColor: '#ffffff',
    show: false,                 // don't flash — show after content loads
    webPreferences: {
      preload: path.join(__dirname, 'preload-game.js'),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: false
    }
  });

  gamePopup.loadURL(gameUrl);

  gamePopup.once('ready-to-show', () => {
    gamePopup.show();
    gamePopup.focus();

    // On macOS, this extra call ensures focus even when user is in another app
    if (process.platform === 'darwin') {
      app.dock.bounce('critical');   // bounces dock icon to grab attention
      app.focus({ steal: true });    // brings Electron to foreground
      gamePopup.focus();
    }
  });

  gamePopup.on('closed', () => {
    gamePopup = null;
    // Notify the main renderer so it can call eel.close_exercise()
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('game-popup-closed');
    }
  });
}

function closeGamePopup() {
  if (gamePopup && !gamePopup.isDestroyed()) {
    gamePopup.close();
  }
}

// ── IPC Handlers ───────────────────────────────────────────────────
ipcMain.on('open-game-popup', (event, gameUrl) => {
  openGamePopup(gameUrl);
});

ipcMain.on('close-game-popup', () => {
  closeGamePopup();
});

ipcMain.on('update-points', (event, total) => {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send('points-updated', total);
  }
});

// ── App Lifecycle ──────────────────────────────────────────────────
app.whenReady().then(createWindow);