import os
import subprocess
import psutil
import platform

class CommandExecutor:
    def __init__(self):
        self.system = platform.system()
    
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
            else:
                return {"success": False, "error": f"Unknown command type: {command_type}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
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
            import pyautogui
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