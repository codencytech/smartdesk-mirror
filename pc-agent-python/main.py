from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.screen_capture import ScreenCapture
from core.system_monitor import system_monitor
from core.command_executor import command_executor
from core.connection_manager import connection_manager
import time
import socket
from fastapi.responses import Response
import json

app = FastAPI(title="SmartDesk Mirror - PC Agent")

screen = ScreenCapture()

# ---------------- CORS FIX ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ------------------------------------------

@app.get("/")
def home():
    return {"status": "PC Agent Running"}

# FIXED: Allow desktop app to access these without authentication
@app.get("/system-metrics")
def get_system_metrics():
    """Get real-time system metrics (CPU, RAM, Network) - No auth for desktop app"""
    try:
        metrics = system_monitor.get_all_metrics()
        return metrics
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get metrics: {str(e)}"}
        )

@app.get("/connection/generate-code")
def generate_connection_code():
    """Generate a new connection code and QR code - No auth for desktop app"""
    try:
        code = connection_manager.generate_connection_code()
        qr_code = connection_manager.generate_qr_code(code)
        
        print(f"🔑 Generated new connection code: {code}")
        
        return {
            "code": code,
            "qr_code": qr_code,
            "valid_for_minutes": connection_manager.code_validity_minutes,
            "expires_at": time.time() + (connection_manager.code_validity_minutes * 60)
        }
    except Exception as e:
        print(f"❌ Error generating code: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to generate code: {str(e)}"}
        )

@app.get("/connection/pending-requests")
def get_pending_requests():
    """Get all pending connection requests - No auth for desktop app"""
    try:
        return connection_manager.get_pending_requests()
    except Exception as e:
        print(f"Error getting pending requests: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/connection/active")
def get_active_connections():
    """Get all active connections - No auth for desktop app"""
    try:
        return connection_manager.get_active_connections()
    except Exception as e:
        print(f"Error getting active connections: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/connection/respond")
async def connection_respond(request: Request):
    """Desktop app responds to connection request - No auth for desktop app"""
    try:
        body = await request.json()
        request_id = body.get("request_id")
        accepted = body.get("accepted", False)
        
        print(f"💬 Connection response: request_id={request_id}, accepted={accepted}")
        
        connection_manager.handle_connection_response(request_id, accepted)
        
        return {
            "success": True,
            "message": "Connection response processed"
        }
    except Exception as e:
        print(f"❌ Connection response error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

# Mobile endpoints - These require connection code authentication
@app.post("/connection/request")
async def connection_request(request: Request):
    """Mobile device requests connection using code"""
    try:
        body = await request.json()
        code = body.get("code")
        device_info = body.get("device_info", "Unknown Mobile Device")
        
        # Enhanced device detection
        user_agent = request.headers.get("user-agent", "").lower()
        device_type = "Mobile Device"
        
        if "android" in user_agent:
            device_type = "Android Phone"
        elif "iphone" in user_agent or "ipad" in user_agent:
            device_type = "Apple Device"
        elif "windows" in user_agent:
            device_type = "Windows Device"
        elif "mac" in user_agent:
            device_type = "Mac Device"
        elif "linux" in user_agent:
            device_type = "Linux Device"
        
        enhanced_device_info = f"{device_type} ({device_info})"
        
        print(f"📱 Connection request received:")
        print(f"   Code: {code}")
        print(f"   Device: {enhanced_device_info}")
        print(f"   User Agent: {user_agent}")
        
        if not code:
            return JSONResponse(
                status_code=400, 
                content={"success": False, "message": "Code is required"}
            )
        
        if not connection_manager.validate_code(code):
            print(f"❌ Invalid code: {code}")
            return {
                "success": False,
                "message": "Invalid or expired code"
            }
        
        # Add connection request with enhanced info
        request_id = connection_manager.add_connection_request(code, enhanced_device_info)
        print(f"✅ Connection request added: request_id={request_id}")
        
        return {
            "success": True,
            "request_id": request_id,
            "message": "Connection request sent. Waiting for approval."
        }
            
    except Exception as e:
        print(f"❌ Connection request error: {e}")
        return JSONResponse(
            status_code=500, 
            content={"success": False, "message": str(e)}
        )

@app.get("/connection/status/{code}")
def get_connection_status(code: str):
    """Check if connection is active for a code"""
    try:
        print(f"🔍 Status check for code: {code}")
        is_active = connection_manager.is_connection_active(code)
        
        return {
            "active": is_active,
            "message": "Connection active" if is_active else "Connection not active or pending"
        }
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return JSONResponse(
            status_code=500, 
            content={"active": False, "message": str(e)}
        )


@app.get("/mobile/screen")
def get_mobile_screen(request: Request):
    """Get screen capture for mobile app"""
    # Check if connection is active
    code = request.headers.get("x-connection-code")
    if not code or not connection_manager.is_connection_active(code):
        return JSONResponse(
            status_code=401, 
            content={"error": "No active connection or connection not approved"}
        )
    
    try:
        frame = screen.capture()
        if frame:
            print(f"✅ Screen captured, returning direct data URL (length: {len(frame)})")
            # Return as plain text with the data URL directly
            return Response(
                content=frame,
                media_type="text/plain"
            )
        else:
            print("❌ Screen capture returned None")
            return JSONResponse(
                status_code=500,
                content={"error": "Screen capture failed"}
            )
    except Exception as e:
        print(f"❌ Screen capture error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Screen capture failed: {str(e)}"}
        )

@app.post("/mobile/execute-command")
async def execute_mobile_command(request: Request):
    """Execute commands sent from mobile app"""
    # Check if connection is active
    code = request.headers.get("x-connection-code")
    if not code or not connection_manager.is_connection_active(code):
        return JSONResponse(
            status_code=401, 
            content={"error": "No active connection or connection not approved"}
        )
    
    try:
        body = await request.json()
        command_type = body.get("type")
        command_data = body.get("data", {})
        
        result = command_executor.execute_command(command_type, command_data)
        return result
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Command execution failed: {str(e)}"}
        )

@app.get("/mobile/system-info")
def get_mobile_system_info(request: Request):
    """Get system info for mobile app"""
    # Check if connection is active
    code = request.headers.get("x-connection-code")
    if not code or not connection_manager.is_connection_active(code):
        return JSONResponse(
            status_code=401, 
            content={"error": "No active connection or connection not approved"}
        )
    
    try:
        result = command_executor.get_system_info()
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

# Add this debug endpoint to test basic functionality
@app.get("/debug/test")
def debug_test():
    """Debug endpoint to test basic functionality"""
    try:
        # Test QR code generation
        test_code = "123456"
        qr_code = connection_manager.generate_qr_code(test_code)
        
        return {
            "status": "ok",
            "message": "Debug test successful",
            "test_code": test_code,
            "qr_code_length": len(qr_code) if qr_code else 0
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Debug test failed: {str(e)}"}
        )

# Also add this to test the connection manager directly
@app.get("/debug/generate-simple-code")
def generate_simple_code():
    """Generate a simple connection code without QR for testing"""
    try:
        code = connection_manager.generate_connection_code()
        return {
            "code": code,
            "status": "success"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to generate code: {str(e)}"}
        )

@app.get("/debug/local-ip")
def get_local_ip():
    """Get the local IP address of the PC"""
    try:
        # Method 1: Use socket to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        return {
            "ip": local_ip,
            "hostname": socket.gethostname(),
            "method": "socket"
        }
    except Exception as e:
        # Method 2: Try getting from network interfaces
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return {
                "ip": local_ip,
                "hostname": hostname,
                "method": "hostname"
            }
        except:
            return {
                "ip": "127.0.0.1",
                "error": "Could not determine local IP",
                "method": "fallback"
            }

# In main.py - Add debug endpoint
@app.get("/debug/screen-test")
def debug_screen_test():
    """Debug endpoint to test screen capture"""
    try:
        frame = screen.capture()
        if frame:
            return {
                "status": "success",
                "frame_length": len(frame),
                "has_data": True
            }
        else:
            return {
                "status": "error", 
                "message": "Screen capture returned None"
            }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e)
        }

# In main.py - Add direct screen test endpoint
@app.get("/debug/screen-direct")
def debug_screen_direct():
    """Debug endpoint to return screen capture directly"""
    try:
        frame = screen.capture()
        if frame:
            # Return as plain text with image content type
            from fastapi.responses import Response
            return Response(
                content=frame,
                media_type="text/plain"
            )
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "Screen capture failed"}
            )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Screen capture failed: {str(e)}"}
        )

# In main.py - Add this debug endpoint
@app.get("/debug/screen-raw")
def debug_screen_raw():
    """Debug endpoint to see raw screen response"""
    try:
        frame = screen.capture()
        if frame:
            return {
                "raw_response": frame[:200] + "..." if len(frame) > 200 else frame,
                "is_data_url": frame.startswith("data:image"),
                "length": len(frame)
            }
        else:
            return {"error": "Screen capture returned None"}
    except Exception as e:
        return {"error": str(e)}

# In main.py - Add a simple test endpoint
@app.get("/debug/simple-test")
def debug_simple_test():
    """Simple test endpoint that returns plain text"""
    return "Hello from PC - This is plain text response"

if __name__ == "__main__":
    print("🚀 Starting PC Agent...")
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)