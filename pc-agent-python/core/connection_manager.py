import random
import string
import time
import qrcode
import io
import base64
import socket
import json
from typing import Dict, Optional, List

class ConnectionManager:
    def __init__(self):
        self.active_codes: Dict[str, dict] = {}
        self.connection_requests: List[dict] = []
        self.active_connections: List[dict] = []
        self.code_validity_minutes = 10
        self.code_length = 6
        self.current_code = None
        
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
        
    def generate_connection_code(self) -> str:
        """Generate a new numeric connection code"""
        try:
            # Generate random numeric code
            code = ''.join(random.choices(string.digits, k=self.code_length))
            self.current_code = code
            
            # Store code with timestamp
            self.active_codes[code] = {
                'created_at': time.time(),
                'used': False,
                'connected_device': None
            }
            
            # Clean up expired codes
            self._cleanup_expired_codes()
            
            print(f"🔑 Generated new connection code: {code}")
            return code
        except Exception as e:
            print(f"❌ Error generating connection code: {e}")
            raise e
    
    def _cleanup_expired_codes(self):
        """Remove expired codes"""
        current_time = time.time()
        expired_codes = []
        
        for code, data in self.active_codes.items():
            if current_time - data['created_at'] > (self.code_validity_minutes * 60):
                expired_codes.append(code)
        
        for code in expired_codes:
            del self.active_codes[code]
            if self.current_code == code:
                self.current_code = None
    
    def validate_code(self, code: str) -> bool:
        """Check if a connection code is valid"""
        if code not in self.active_codes:
            return False
        
        code_data = self.active_codes[code]
        current_time = time.time()
        
        # Check if code expired
        if current_time - code_data['created_at'] > (self.code_validity_minutes * 60):
            del self.active_codes[code]
            if self.current_code == code:
                self.current_code = None
            return False
        
        return True
    
    def add_connection_request(self, code: str, device_info: str) -> int:
        """Add a new connection request and return request ID"""
        request_id = len(self.connection_requests)
        self.connection_requests.append({
            'id': request_id,
            'code': code,
            'device_info': device_info,
            'timestamp': time.time(),
            'status': 'pending'  # pending, accepted, rejected
        })
        return request_id
    
    def get_pending_requests(self) -> List[dict]:
        """Get all pending connection requests"""
        return [req for req in self.connection_requests if req['status'] == 'pending']
    
    def handle_connection_response(self, request_id: int, accepted: bool):
        """Handle user response to connection request"""
        for req in self.connection_requests:
            if req['id'] == request_id:
                if accepted:
                    req['status'] = 'accepted'
                    # Mark code as used
                    if req['code'] in self.active_codes:
                        self.active_codes[req['code']]['used'] = True
                        self.active_codes[req['code']]['connected_device'] = req['device_info']
                    # Add to active connections
                    self.active_connections.append({
                        'device_info': req['device_info'],
                        'connected_at': time.time(),
                        'code': req['code']
                    })
                    print(f"✅ Connection accepted: {req['device_info']}")
                else:
                    req['status'] = 'rejected'
                    print(f"❌ Connection rejected: {req['device_info']}")
                break
    
    def is_connection_active(self, code: str) -> bool:
        """Check if a code has an active connection"""
        for conn in self.active_connections:
            if conn['code'] == code:
                return True
        return False
    
    def get_active_connections(self) -> List[dict]:
        """Get all active connections"""
        return self.active_connections
    
    def generate_qr_code(self, code: str) -> str:
        """Generate QR code as base64 string containing connection info"""
        try:
            local_ip = self.get_local_ip()
            qr_data = json.dumps({
                "type": "smartdesk_connection",
                "code": code,
                "ip": local_ip,
                "port": 8000,
                "hostname": socket.gethostname()
            })
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            print(f"❌ Error generating QR code: {e}")
            # Return a simple placeholder if QR generation fails
            return self._generate_placeholder_qr()
    
    def _generate_placeholder_qr(self) -> str:
        """Generate a simple placeholder QR code"""
        try:
            # Create a simple error image
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (200, 200), color='white')
            d = ImageDraw.Draw(img)
            d.text((10, 90), "QR Error", fill='black')
            
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"
        except:
            # Final fallback
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    def get_code_status(self, code: str) -> Optional[dict]:
        """Get status of a connection code"""
        if code in self.active_codes:
            return self.active_codes[code]
        return None

# Global instance
connection_manager = ConnectionManager()