import socket
import threading
import time
import json
from typing import List, Dict

class NetworkDiscovery:
    def __init__(self, port=8000):
        self.port = port
        self.discovery_port = 8001  # Separate port for discovery
        self.running = False
        self.server_socket = None
        
    def get_local_ip(self):
        """Get the local IP address of this machine"""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
    
    def start_discovery_server(self, connection_code: str):
        """Start UDP broadcast server for auto-discovery"""
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.server_socket.settimeout(1.0)
        
        def discovery_handler():
            while self.running:
                try:
                    data, addr = self.server_socket.recvfrom(1024)
                    if data.decode('utf-8') == 'SMARTDESK_DISCOVERY':
                        # Send back discovery response with connection info
                        response = {
                            "type": "smartdesk_pc",
                            "ip": self.get_local_ip(),
                            "port": self.port,
                            "code": connection_code,
                            "name": socket.gethostname()
                        }
                        self.server_socket.sendto(
                            json.dumps(response).encode('utf-8'), 
                            addr
                        )
                        print(f"Discovery request from {addr}")
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Discovery error: {e}")
        
        thread = threading.Thread(target=discovery_handler, daemon=True)
        thread.start()
        print(f"Discovery server started on port {self.discovery_port}")
    
    def stop_discovery_server(self):
        """Stop the discovery server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
    
    def discover_pcs(self, timeout=3) -> List[Dict]:
        """Discover PCs on the network"""
        discovered_pcs = []
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(1.0)
        
        # Send discovery broadcast
        try:
            sock.sendto(b'SMARTDESK_DISCOVERY', ('<broadcast>', self.discovery_port))
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    data, addr = sock.recvfrom(1024)
                    response = json.loads(data.decode('utf-8'))
                    if response.get("type") == "smartdesk_pc":
                        discovered_pcs.append(response)
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Discovery receive error: {e}")
        except Exception as e:
            print(f"Discovery send error: {e}")
        finally:
            sock.close()
        
        return discovered_pcs

# Global instance
network_discovery = NetworkDiscovery()