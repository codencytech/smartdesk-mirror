const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");
const WebSocket = require("ws");
const crypto = require("crypto");

let mainWindow;

// 👉 Generate API KEY one time
const API_KEY = "sk-" + crypto.randomBytes(16).toString("hex");

// 👉 Create WebSocket Server
const wss = new WebSocket.Server({ port: 8765 });
console.log("WebSocket running at ws://localhost:8765");

// Listen for messages from PC Agent
wss.on("connection", ws => {
    console.log("PC Agent Connected");

    ws.on("message", msg => {
        console.log("Received:", msg);
        mainWindow.webContents.send("agent-status", msg.toString());
    });

    ws.send("connected");
});

// Electron Window
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        webPreferences: {
            preload: path.join(__dirname, "preload.js"),
        }
    });

    mainWindow.loadURL("http://localhost:5173/");
}

app.whenReady().then(() => {
    console.log("API KEY:", API_KEY);
    createWindow();
});
