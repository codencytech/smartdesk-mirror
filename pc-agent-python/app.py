# smartdesk-mirror/pc-agent-python/app.py
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse

app = FastAPI(title="SmartDesk Mirror - PC Agent")

@app.get("/")
async def root():
    return JSONResponse(content={"message": "Hello from SmartDesk Mirror PC Agent"})

# Simple websocket endpoint for later signaling/control tests
@app.websocket("/ws/test")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    await ws.send_text("pc-agent: websocket connected")
    try:
        while True:
            data = await ws.receive_text()
            # echo for now
            await ws.send_text(f"pc-agent echo: {data}")
    except Exception:
        await ws.close()
