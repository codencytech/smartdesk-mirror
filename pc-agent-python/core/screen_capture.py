# File: core/screen_capture.py
import base64
import io
from PIL import ImageGrab
import numpy as np

class ScreenCapture:
    def __init__(self):
        # Balanced quality and speed (perfect for WiFi/mobile data)
        self.target_width = 1280
        self.target_height = 720
        self.quality = 65  # Perfect clarity + low size

    def capture(self):
        try:
            # Capture full PC screen
            screenshot = ImageGrab.grab()

            # --- Resize to EXACT 1280x720 while preserving aspect ratio ---
            original_w, original_h = screenshot.size
            target_w, target_h = self.target_width, self.target_height

            # Compute aspect ratios
            original_ratio = original_w / original_h
            target_ratio = target_w / target_h

            if original_ratio > target_ratio:
                # PC screen is wider → fit width
                new_w = target_w
                new_h = int(target_w / original_ratio)
            else:
                # PC screen is taller → fit height
                new_h = target_h
                new_w = int(target_h * original_ratio)

            # Resize using best fast filter
            screenshot = screenshot.resize((new_w, new_h))

            # --- Convert to JPEG → Base64 ---
            buffer = io.BytesIO()
            screenshot.save(buffer, format="JPEG", quality=self.quality, optimize=True)
            img_bytes = buffer.getvalue()
            img_base64 = base64.b64encode(img_bytes).decode("utf-8")

            # Final Data URL
            data_url = f"data:image/jpeg;base64,{img_base64}"

            # Debug logs
            print("✅ Screen captured")
            print(f"   Original screen: {original_w}x{original_h}")
            print(f"   Sent as: {new_w}x{new_h}")
            print(f"   JPEG Quality: {self.quality}")
            print(f"   Base64 Size: {len(img_base64)} chars")

            return data_url

        except Exception as e:
            print(f"❌ Screen capture error: {e}")
            return None

    # Not used now, but kept for future settings screen
    def set_quality(self, quality):
        self.quality = max(30, min(90, quality))

    def set_scale(self, scale):
        pass  # Disabled (now using fixed HD resolution)
