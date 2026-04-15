"""
Utility functions and helper classes for gesture control system
"""

import subprocess
import platform
import os
from datetime import datetime
from pathlib import Path

class GestureLogger:
    """Log gesture events for debugging and analytics"""
    
    def __init__(self, log_file="gesture_log.txt"):
        self.log_file = log_file
        self.events = []
    
    def log_event(self, gesture_type, timestamp, hand_count=1):
        """Log a gesture event"""
        event = {
            "timestamp": timestamp,
            "gesture": gesture_type,
            "hand_count": hand_count
        }
        self.events.append(event)
        
        # Write to file
        with open(self.log_file, 'a') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {gesture_type} (Hands: {hand_count})\n")
    
    def get_statistics(self):
        """Get gesture usage statistics"""
        stats = {}
        for event in self.events:
            gesture = event['gesture']
            stats[gesture] = stats.get(gesture, 0) + 1
        return stats

class AppLauncher:
    """Launch applications based on gestures"""
    
    @staticmethod
    def launch_app(app_name):
        """Launch an application"""
        try:
            system = platform.system()
            
            if system == "Windows":
                os.startfile(app_name)
            elif system == "Darwin":  # macOS
                subprocess.Popen(['open', '-a', app_name])
            elif system == "Linux":
                subprocess.Popen([app_name])
                
            return True
        except Exception as e:
            print(f"Error launching {app_name}: {e}")
            return False
    
    @staticmethod
    def get_common_apps():
        """Get list of common applications"""
        system = platform.system()
        
        apps = {
            "Windows": {
                "Chrome": "chrome",
                "Firefox": "firefox",
                "VS Code": "code",
                "Notepad": "notepad",
                "Paint": "mspaint",
                "Calc": "calc",
                "PowerPoint": "powerpnt"
            },
            "Darwin": {
                "Chrome": "Google Chrome",
                "Safari": "Safari",
                "VS Code": "Visual Studio Code",
                "Notes": "Notes",
                "Finder": "Finder"
            },
            "Linux": {
                "Firefox": "firefox",
                "VS Code": "code",
                "Text Editor": "gedit"
            }
        }
        
        return apps.get(system, {})

class MouseController:
    """Enhanced mouse control features"""
    
    @staticmethod
    def smooth_move(start_x, start_y, end_x, end_y, duration=0.25):
        """Move mouse smoothly from start to end position"""
        import pyautogui
        pyautogui.moveTo(end_x, end_y, duration=duration)
    
    @staticmethod
    def click_at_position(x, y, button='left'):
        """Click at specific position"""
        import pyautogui
        pyautogui.click(x, y, button=button)
    
    @staticmethod
    def double_click_at_position(x, y):
        """Double click at position"""
        import pyautogui
        pyautogui.doubleClick(x, y)

class ScreenAnalyzer:
    """Analyze screen for gesture zones"""
    
    @staticmethod
    def get_screen_zones(screen_width, screen_height):
        """Divide screen into zones"""
        return {
            "left": (0, screen_width // 3),
            "center": (screen_width // 3, 2 * screen_width // 3),
            "right": (2 * screen_width // 3, screen_width),
            "top": (0, screen_height // 3),
            "middle": (screen_height // 3, 2 * screen_height // 3),
            "bottom": (2 * screen_height // 3, screen_height)
        }
    
    @staticmethod
    def get_zone(x, y, screen_width, screen_height):
        """Get zone for given coordinates"""
        zones = ScreenAnalyzer.get_screen_zones(screen_width, screen_height)
        
        if x < zones["left"][1]:
            return "left"
        elif x < zones["center"][1]:
            return "center"
        else:
            return "right"

class PerformanceMonitor:
    """Monitor system performance"""
    
    def __init__(self):
        self.frame_times = []
        self.max_readings = 100
    
    def add_frame_time(self, frame_time):
        """Add frame processing time"""
        self.frame_times.append(frame_time)
        if len(self.frame_times) > self.max_readings:
            self.frame_times.pop(0)
    
    def get_average_fps(self):
        """Get average FPS"""
        if not self.frame_times:
            return 0
        avg_time = sum(self.frame_times) / len(self.frame_times)
        return int(1 / avg_time) if avg_time > 0 else 0
    
    def get_stats(self):
        """Get performance statistics"""
        if not self.frame_times:
            return {"avg_fps": 0, "min_fps": 0, "max_fps": 0}
        
        avg_time = sum(self.frame_times) / len(self.frame_times)
        return {
            "avg_fps": int(1 / avg_time) if avg_time > 0 else 0,
            "min_fps": int(1 / max(self.frame_times)) if self.frame_times else 0,
            "max_fps": int(1 / min(self.frame_times)) if self.frame_times else 0
        }

# Gesture preset configurations
GESTURE_PRESETS = {
    "presentation": {
        "scroll_speed": 150,
        "scroll_cooldown": 0.6,
        "enable_volume_control": False,
        "gesture_timeout": 3.0
    },
    "video_editing": {
        "scroll_speed": 100,
        "scroll_cooldown": 0.4,
        "enable_volume_control": True,
        "gesture_timeout": 2.0
    },
    "gaming": {
        "scroll_speed": 50,
        "scroll_cooldown": 0.2,
        "enable_volume_control": False,
        "gesture_timeout": 1.0
    },
    "accessibility": {
        "scroll_speed": 300,
        "scroll_cooldown": 1.0,
        "enable_volume_control": True,
        "gesture_timeout": 3.0
    }
}

def load_preset(preset_name):
    """Load a gesture preset"""
    return GESTURE_PRESETS.get(preset_name, {})
