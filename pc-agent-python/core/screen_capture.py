# File: core/screen_capture.py
import base64
import io
from PIL import ImageGrab
import numpy as np

class ScreenCapture:
    def __init__(self):
        self.quality = 50  # JPEG quality (1-100)
        self.scale_factor = 0.5  # Scale down for mobile

    def capture(self):
        try:
            # Capture the screen
            screenshot = ImageGrab.grab()
            
            # Resize for mobile optimization
            width, height = screenshot.size
            new_width = int(width * self.scale_factor)
            new_height = int(height * self.scale_factor)
            screenshot = screenshot.resize((new_width, new_height))
            
            # Convert to JPEG and then to base64
            buffer = io.BytesIO()
            screenshot.save(buffer, format='JPEG', quality=self.quality)
            img_bytes = buffer.getvalue()
            
            # Convert to base64 string
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            # Return as data URL for direct image display
            return f"data:image/jpeg;base64,{img_base64}"
            
        except Exception as e:
            print(f"Screen capture error: {e}")
            return None

    def set_quality(self, quality):
        self.quality = max(1, min(100, quality))

    def set_scale(self, scale):
        self.scale_factor = max(0.1, min(1.0, scale))

# In screen_capture.py - Add debug logging
def capture(self):
    try:
        # Capture the screen
        screenshot = ImageGrab.grab()
        
        # Resize for mobile optimization
        width, height = screenshot.size
        new_width = int(width * self.scale_factor)
        new_height = int(height * self.scale_factor)
        screenshot = screenshot.resize((new_width, new_height))
        
        # Convert to JPEG and then to base64
        buffer = io.BytesIO()
        screenshot.save(buffer, format='JPEG', quality=self.quality)
        img_bytes = buffer.getvalue()
        
        # Convert to base64 string
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        # Create data URL
        data_url = f"data:image/jpeg;base64,{img_base64}"
        
        print(f"✅ Screen captured successfully")
        print(f"   Original size: {width}x{height}")
        print(f"   Scaled size: {new_width}x{new_height}")
        print(f"   JPEG quality: {self.quality}")
        print(f"   Base64 length: {len(img_base64)}")
        print(f"   Data URL length: {len(data_url)}")
        
        return data_url
        
    except Exception as e:
        print(f"❌ Screen capture error: {e}")
        import traceback
        traceback.print_exc()
        return None