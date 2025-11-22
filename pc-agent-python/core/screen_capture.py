import base64
import cv2
import numpy as np
from mss import mss
import pyautogui

class ScreenCapture:
    def __init__(self):
        try:
            self.sct = mss()
            # Test if we can access monitors
            self.monitors = self.sct.monitors
            print(f"Available monitors: {len(self.monitors)}")
        except Exception as e:
            print(f"MSS initialization failed: {e}")
            self.sct = None

    def capture(self):
        try:
            # Method 1: Try MSS first
            if self.sct and len(self.monitors) > 1:
                screenshot = self.sct.grab(self.monitors[1])
                img = np.array(screenshot)
                # Convert from BGRA to BGR
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            else:
                # Method 2: Fallback to pyautogui
                screenshot = pyautogui.screenshot()
                img = np.array(screenshot)
                # Convert from RGB to BGR for OpenCV
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            # Resize image to reduce bandwidth (optional)
            height, width = img.shape[:2]
            if height > 800 or width > 1200:
                scale = min(800/height, 1200/width)
                new_width = int(width * scale)
                new_height = int(height * scale)
                img = cv2.resize(img, (new_width, new_height))
            
            # Encode to JPEG with quality compression
            _, buffer = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 70])
            encoded = base64.b64encode(buffer).decode("utf-8")
            return encoded
            
        except Exception as e:
            print(f"Screen capture error: {e}")
            return self._get_error_image(str(e))

    def _get_error_image(self, error_msg=""):
        """Return a descriptive error image"""
        img = np.zeros((400, 600, 3), dtype=np.uint8)
        
        # Add error message to image
        lines = [
            "Screen Capture Failed",
            "Common fixes:",
            "1. Run as Administrator",
            "2. Check display permissions",
            "3. Try different capture method"
        ]
        
        if error_msg:
            lines.append(f"Error: {error_msg[:50]}...")
        
        y_pos = 50
        for line in lines:
            cv2.putText(img, line, (20, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            y_pos += 30
        
        _, buffer = cv2.imencode(".jpg", img)
        encoded = base64.b64encode(buffer).decode("utf-8")
        return encoded