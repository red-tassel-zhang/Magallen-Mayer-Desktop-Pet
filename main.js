const { app, BrowserWindow, screen, ipcMain, Tray, Menu } = require('electron');
const path = require('path');

let mainWindow = null;
let tray = null;

function createWindow() {
  const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize;

  mainWindow = new BrowserWindow({
    width: 500,
    height: 650,
    x: screenWidth - 520,
    y: screenHeight - 680,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    hasShadow: false,
    resizable: false,
    skipTaskbar: true,
    type: 'toolwindow',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));
  mainWindow.setVisibleOnAllWorkspaces(true);
  mainWindow.setAlwaysOnTop(true, 'floating');

  // IPC handlers
  ipcMain.on('move-window', (_, { dx, dy }) => {
    const [x, y] = mainWindow.getPosition();
    mainWindow.setPosition(x + dx, y + dy);
  });

  ipcMain.on('set-window-position', (_, { x, y }) => {
    mainWindow.setPosition(Math.round(x), Math.round(y));
  });

  ipcMain.on('close-app', () => {
    app.quit();
  });

  ipcMain.on('minimize-app', () => {
    if (mainWindow) mainWindow.hide();
  });

  ipcMain.handle('get-window-bounds', () => {
    if (!mainWindow) return null;
    const bounds = mainWindow.getBounds();
    const display = screen.getPrimaryDisplay().workArea;
    return {
      x: bounds.x, y: bounds.y,
      width: bounds.width, height: bounds.height,
      screenWidth: display.width, screenHeight: display.height,
    };
  });
}

function createTray() {
  // Simple tray for restoring window
  tray = new Tray(path.join(__dirname, 'renderer', 'icon.png'));
  const contextMenu = Menu.buildFromTemplate([
    {
      label: '显示/隐藏',
      click: () => {
        if (mainWindow) {
          mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
        }
      },
    },
    { type: 'separator' },
    { label: '退出', click: () => app.quit() },
  ]);
  tray.setToolTip('麦哲伦桌面宠物');
  tray.setContextMenu(contextMenu);
  tray.on('double-click', () => {
    if (mainWindow) {
      mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
    }
  });
}

app.whenReady().then(() => {
  createWindow();
  // Skip tray if icon doesn't exist
  try {
    createTray();
  } catch (_) {
    // icon.png not found, skip tray
  }
});

app.on('window-all-closed', () => {
  app.quit();
});
