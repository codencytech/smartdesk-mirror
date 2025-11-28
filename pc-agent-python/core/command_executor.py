import os
import subprocess
import psutil
import platform
import pyautogui

class CommandExecutor:
    def __init__(self):
        self.system = platform.system()
        # Get screen size for absolute positioning
        self.screen_width, self.screen_height = pyautogui.size()
    
    def execute_command(self, command_type, command_data):
        """Execute different types of commands from mobile"""
        try:
            if command_type == "open_app":
                return self.open_application(command_data)
            elif command_type == "open_file":
                return self.open_file(command_data)
            elif command_type == "system_info":
                return self.get_system_info()
            elif command_type == "keyboard":
                return self.simulate_keyboard(command_data)
            elif command_type == "file_operation":
                return self.file_operation(command_data)
            # MOUSE COMMANDS
            elif command_type == "mouse_click":
                return self.mouse_click(command_data)
            elif command_type == "mouse_move":
                return self.mouse_move(command_data)
            elif command_type == "mouse_move_relative":
                return self.mouse_move_relative(command_data)
            elif command_type == "mouse_scroll":
                return self.mouse_scroll(command_data)
            elif command_type == "mouse_down":
                return self.mouse_down(command_data)
            elif command_type == "mouse_up":
                return self.mouse_up(command_data)
            elif command_type == "mouse_double_click":
                return self.mouse_double_click(command_data)
            else:
                return {"success": False, "error": f"Unknown command type: {command_type}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # MOUSE CONTROL METHODS
    def mouse_click(self, data):
        """Handle mouse clicks with optional coordinates"""
        try:
            button = data.get("button", "left")
            
            # If coordinates provided, move to position first
            if "x" in data and "y" in data:
                x = float(data["x"]) * self.screen_width
                y = float(data["y"]) * self.screen_height
                pyautogui.moveTo(x, y)
            
            pyautogui.click(button=button)
            return {"success": True, "message": f"Mouse {button} click"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def mouse_move(self, data):
        """Move mouse to absolute position (0-1 coordinates)"""
        try:
            x = float(data.get("x", 0)) * self.screen_width
            y = float(data.get("y", 0)) * self.screen_height
            pyautogui.moveTo(x, y)
            return {"success": True, "message": f"Mouse moved to ({x}, {y})"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def mouse_move_relative(self, data):
        """Move mouse relative to current position"""
        try:
            dx = float(data.get("dx", 0))
            dy = float(data.get("dy", 0))
            pyautogui.moveRel(dx, dy)
            return {"success": True, "message": f"Mouse moved relative ({dx}, {dy})"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def mouse_scroll(self, data):
        """Handle mouse scrolling"""
        try:
            dx = float(data.get("dx", 0))
            dy = float(data.get("dy", 0))
            
            # Use vertical scrolling for dy (most common)
            if dy != 0:
                pyautogui.scroll(int(dy))
            
            # Horizontal scrolling if supported
            if dx != 0:
                # pyautogui doesn't support horizontal scroll directly
                # This is a workaround - you might need additional setup
                pass
                
            return {"success": True, "message": f"Scrolled ({dx}, {dy})"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def mouse_down(self, data):
        """Press and hold mouse button"""
        try:
            button = data.get("button", "left")
            pyautogui.mouseDown(button=button)
            return {"success": True, "message": f"Mouse {button} down"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def mouse_up(self, data):
        """Release mouse button"""
        try:
            button = data.get("button", "left")
            pyautogui.mouseUp(button=button)
            return {"success": True, "message": f"Mouse {button} up"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def mouse_double_click(self, data):
        """Double click at position"""
        try:
            if "x" in data and "y" in data:
                x = float(data["x"]) * self.screen_width
                y = float(data["y"]) * self.screen_height
                pyautogui.moveTo(x, y)
            
            pyautogui.doubleClick()
            return {"success": True, "message": "Double click"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # EXISTING METHODS (keep your original code)
    def open_application(self, app_name):
        """Open applications by name"""
        app_commands = {
            "chrome": "chrome.exe",
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "file explorer": "explorer.exe",
            "task manager": "taskmgr.exe",
            "control panel": "control.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe"
        }
        
        app_lower = app_name.lower()
        if app_lower in app_commands:
            subprocess.Popen(app_commands[app_lower])
            return {"success": True, "message": f"Opened {app_name}"}
        else:
            # Try to open with default program
            os.startfile(app_name)
            return {"success": True, "message": f"Opened {app_name}"}
    
    def open_file(self, file_path):
        """Open files or folders"""
        try:
            os.startfile(file_path)
            return {"success": True, "message": f"Opened {file_path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_system_info(self):
        """Get detailed system information"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_used_gb = round(memory.used / (1024**3), 1)
            memory_total_gb = round(memory.total / (1024**3), 1)
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_used_gb = round(disk.used / (1024**3), 1)
            disk_total_gb = round(disk.total / (1024**3), 1)
            disk_percent = disk.percent
            
            # Network
            net_io = psutil.net_io_counters()
            network_sent_mb = round(net_io.bytes_sent / (1024**2), 1)
            network_recv_mb = round(net_io.bytes_recv / (1024**2), 1)
            
            return {
                "success": True,
                "system_info": {
                    "cpu_usage": f"{cpu_percent}%",
                    "memory": f"{memory_used_gb}GB / {memory_total_gb}GB ({memory_percent}%)",
                    "disk": f"{disk_used_gb}GB / {disk_total_gb}GB ({disk_percent}%)",
                    "network_sent": f"{network_sent_mb}MB",
                    "network_received": f"{network_recv_mb}MB",
                    "os": platform.system(),
                    "version": platform.version()
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def simulate_keyboard(self, keys):
        """Simulate keyboard shortcuts"""
        try:
            key_commands = {
                "copy": "ctrl+c",
                "paste": "ctrl+v",
                "cut": "ctrl+x",
                "select all": "ctrl+a",
                "save": "ctrl+s",
                "undo": "ctrl+z",
                "redo": "ctrl+y",
                "close window": "alt+f4",
                "task manager": "ctrl+shift+esc",
                "switch windows": "alt+tab"
            }
            
            if keys.lower() in key_commands:
                pyautogui.hotkey(*key_commands[keys.lower()].split('+'))
                return {"success": True, "message": f"Executed: {keys}"}
            else:
                return {"success": False, "error": f"Unknown keyboard command: {keys}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def file_operation(self, operation):
        """Perform file operations"""
        try:
            op_type = operation.get("type")
            path = operation.get("path")
            
            if op_type == "list_directory":
                files = os.listdir(path)
                return {"success": True, "files": files}
            elif op_type == "delete_file":
                os.remove(path)
                return {"success": True, "message": f"Deleted: {path}"}
            else:
                return {"success": False, "error": f"Unknown file operation: {op_type}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global instance
command_executor = CommandExecutor()