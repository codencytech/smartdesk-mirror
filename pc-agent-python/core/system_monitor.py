import psutil
import time

class SystemMonitor:
    def __init__(self):
        self.last_net_io = psutil.net_io_counters()
        self.last_time = time.time()
    
    def get_cpu_usage(self):
        """Get current CPU usage percentage"""
        return psutil.cpu_percent(interval=0.1)
    
    def get_ram_usage(self):
        """Get current RAM usage percentage"""
        memory = psutil.virtual_memory()
        return memory.percent
    
    def get_network_usage(self):
        """Get network usage in KB/s"""
        current_net_io = psutil.net_io_counters()
        current_time = time.time()
        
        time_diff = current_time - self.last_time
        bytes_sent = current_net_io.bytes_sent - self.last_net_io.bytes_sent
        bytes_recv = current_net_io.bytes_recv - self.last_net_io.bytes_recv
        
        # Convert to KB/s
        upload_speed = (bytes_sent / time_diff) / 1024
        download_speed = (bytes_recv / time_diff) / 1024
        
        # Update last values
        self.last_net_io = current_net_io
        self.last_time = current_time
        
        return round(upload_speed + download_speed, 1)
    
    def get_all_metrics(self):
        """Get all system metrics"""
        return {
            "cpu": f"{self.get_cpu_usage():.1f}%",
            "ram": f"{self.get_ram_usage():.1f}%",
            "net": f"{self.get_network_usage()} KB/s"
        }

# Global instance
system_monitor = SystemMonitor()