"""
Advanced Examples and Extensions for Gesture Control System

This file demonstrates advanced features and how to extend the system.
Uncomment and modify examples to add custom functionality.
"""

import pyautogui
import time
from main import GestureType, ActionController
from utils import (
    GestureLogger, AppLauncher, MouseController, 
    ScreenAnalyzer, PerformanceMonitor, load_preset
)

# ============================================================================
# EXAMPLE 1: Custom Gesture Logger
# ============================================================================

def example_with_logging():
    """Example showing how to add logging to gesture events"""
    logger = GestureLogger("gesture_events.log")
    
    # Log some example gestures
    logger.log_event("SCROLL_DOWN", time.time(), hand_count=1)
    logger.log_event("PINCH", time.time(), hand_count=1)
    logger.log_event("PEACE_SIGN", time.time(), hand_count=1)
    
    # Print statistics
    stats = logger.get_statistics()
    print("Gesture Statistics:", stats)


# ============================================================================
# EXAMPLE 2: Application Launcher Based on Gestures
# ============================================================================

class AppLauncherController(ActionController):
    """Extended controller with app launching capability"""
    
    def execute_action(self, gesture, hand_pos=None, hand_distance=None, 
                       screen_width=1920, screen_height=1080):
        """Override execute_action to add app launching"""
        
        # Original actions
        super().execute_action(gesture, hand_pos, hand_distance, screen_width, screen_height)
        
        # NEW: App launching based on gesture + zone
        if gesture == GestureType.FIST and hand_pos:
            zone = ScreenAnalyzer.get_zone(hand_pos[0], hand_pos[1], screen_width, screen_height)
            
            app_map = {
                "left": "chrome",      # Launch Chrome in left zone
                "center": "code",      # Launch VS Code in center zone
                "right": "notepad"     # Launch Notepad in right zone
            }
            
            if zone in app_map:
                print(f"Launching {app_map[zone]} in {zone} zone...")
                AppLauncher.launch_app(app_map[zone])


# ============================================================================
# EXAMPLE 3: Two-Hand Gestures (Advanced)
# ============================================================================

class TwoHandGestureController(ActionController):
    """Controller supporting two-hand gestures"""
    
    def __init__(self, config_path="config.json"):
        super().__init__(config_path)
        self.hand_positions = []  # Track both hands
    
    def detect_two_hand_gesture(self, hand_positions):
        """Detect gestures using two hands"""
        if len(hand_positions) < 2:
            return None
        
        # Calculate distance between hands
        x1, y1 = hand_positions[0]
        x2, y2 = hand_positions[1]
        
        distance = ((x1 - x2)**2 + (y1 - y2)**2) ** 0.5
        
        # Close hands = Zoom in
        if distance < 100:
            return "ZOOM_IN"
        
        # Far hands = Zoom out
        elif distance > 400:
            return "ZOOM_OUT"
        
        # Hands moving towards = Grab
        else:
            return "GRAB"
    
    def execute_two_hand_action(self, action):
        """Execute two-hand gesture action"""
        if action == "ZOOM_IN":
            pyautogui.hotkey('ctrl', 'plus')
            print("Zooming In")
        elif action == "ZOOM_OUT":
            pyautogui.hotkey('ctrl', 'minus')
            print("Zooming Out")
        elif action == "GRAB":
            pyautogui.press('space')
            print("Grab/Select")


# ============================================================================
# EXAMPLE 4: Gesture Presets for Different Use Cases
# ============================================================================

def use_presentation_mode():
    """Use optimized settings for presentation control"""
    preset = load_preset("presentation")
    print("Presentation Mode Settings:", preset)
    # Settings optimized for:
    # - Slide navigation (slower, more accurate)
    # - Video control
    # - Slower gesture recognition


def use_gaming_mode():
    """Use optimized settings for gaming"""
    preset = load_preset("gaming")
    print("Gaming Mode Settings:", preset)
    # Settings optimized for:
    # - Fast gesture recognition
    # - Rapid hand movements
    # - Quick response times


# ============================================================================
# EXAMPLE 5: Extended Gesture Recognition with Custom Gestures
# ============================================================================

class CustomGestureRecognizer:
    """Add your own custom gesture recognition"""
    
    @staticmethod
    def is_heart_shape(hand_landmarks):
        """Detect heart shape gesture"""
        # This is a placeholder - implement your own logic
        # by analyzing hand landmark positions
        pass
    
    @staticmethod
    def is_ok_sign(hand_landmarks):
        """Detect OK sign (thumb + index pinch, other fingers up)"""
        # Analyze thumb-index proximity and other finger positions
        pass
    
    @staticmethod
    def is_rock_sign(hand_landmarks):
        """Detect rock/metal sign"""
        # Index and pinky extended, middle and ring folded
        pass


# ============================================================================
# EXAMPLE 6: Advanced Mouse Control with Gestures
# ============================================================================

class AdvancedMouseController:
    """Advanced mouse interactions based on gestures"""
    
    def __init__(self):
        self.is_drawing = False
        self.prev_pos = None
    
    def start_drawing(self, position):
        """Start drawing mode with gesture"""
        self.is_drawing = True
        self.prev_pos = position
        print("Drawing mode ON")
    
    def stop_drawing(self):
        """Stop drawing mode"""
        self.is_drawing = False
        print("Drawing mode OFF")
    
    def draw_line(self, from_pos, to_pos):
        """Draw a line by moving mouse"""
        MouseController.smooth_move(
            from_pos[0], from_pos[1],
            to_pos[0], to_pos[1],
            duration=0.05
        )
    
    def draw_circle(self, center, radius):
        """Draw a circle"""
        import math
        for angle in range(0, 360, 10):
            x = center[0] + radius * math.cos(math.radians(angle))
            y = center[1] + radius * math.sin(math.radians(angle))
            MouseController.smooth_move(x, y, x, y, duration=0.02)


# ============================================================================
# EXAMPLE 7: Performance Monitoring and Optimization
# ============================================================================

def monitor_performance():
    """Monitor and display performance metrics"""
    monitor = PerformanceMonitor()
    
    # Simulate adding frame times (in real app, measure actual processing time)
    for i in range(100):
        monitor.add_frame_time(1/30)  # Assume 30 FPS
    
    stats = monitor.get_stats()
    print("Performance Stats:", stats)


# ============================================================================
# EXAMPLE 8: Custom Keyboard Shortcuts
# ============================================================================

class CustomShortcutController(ActionController):
    """Add custom keyboard shortcuts for specific gestures"""
    
    CUSTOM_SHORTCUTS = {
        "SCREENSHOT": ["print"],  # Print Screen
        "RECORD": ["win", "g"],   # Windows + G for game bar
        "CALCULATOR": ["win", "semicolon"],  # Open calculator
        "SEARCH": ["win", "s"],   # Windows search
    }
    
    def execute_custom_shortcut(self, shortcut_name):
        """Execute a custom keyboard shortcut"""
        if shortcut_name in self.CUSTOM_SHORTCUTS:
            keys = self.CUSTOM_SHORTCUTS[shortcut_name]
            if len(keys) == 1:
                pyautogui.press(keys[0])
            else:
                pyautogui.hotkey(*keys)
            print(f"Executed: {shortcut_name}")


# ============================================================================
# EXAMPLE 9: Multi-Gesture Combinations
# ============================================================================

class MultiGestureDetector:
    """Detect combinations of gestures"""
    
    def __init__(self):
        self.gesture_sequence = []
        self.sequence_timeout = 2.0
        self.last_gesture_time = 0
    
    def add_gesture(self, gesture, current_time):
        """Add gesture to sequence"""
        # Clear sequence if timeout exceeded
        if current_time - self.last_gesture_time > self.sequence_timeout:
            self.gesture_sequence = []
        
        self.gesture_sequence.append(gesture)
        self.last_gesture_time = current_time
        
        # Check for specific sequences
        self.check_sequences()
    
    def check_sequences(self):
        """Check if sequence matches known patterns"""
        # Example: Scroll down + Scroll up = Pause
        if len(self.gesture_sequence) >= 2:
            last_two = self.gesture_sequence[-2:]
            
            if (last_two[0] == GestureType.SCROLL_DOWN and 
                last_two[1] == GestureType.SCROLL_UP):
                print("SEQUENCE DETECTED: Quick pause!")
                pyautogui.press('space')


# ============================================================================
# EXAMPLE 10: Voice + Gesture Hybrid Control
# ============================================================================

class VoiceGestureHybrid:
    """Combine voice commands with gesture recognition"""
    
    def __init__(self):
        self.voice_command = None
        self.enable_voice = False
    
    def process_voice_command(self, command):
        """Process voice input"""
        self.voice_command = command
        print(f"Voice Command Received: {command}")
    
    def execute_hybrid_action(self, gesture, voice_command=None):
        """Execute action based on gesture + voice combination"""
        if voice_command:
            # Gesture + Voice combination
            if gesture == GestureType.POINTING and voice_command == "click":
                pyautogui.click()
                print("Voice+Gesture: Click executed")
            
            elif gesture == GestureType.PEACE_SIGN and voice_command == "copy":
                pyautogui.hotkey('ctrl', 'c')
                print("Voice+Gesture: Copy executed")


# ============================================================================
# HOW TO USE THESE EXAMPLES:
# ============================================================================

if __name__ == "__main__":
    print("=== Gesture Control Advanced Examples ===\n")
    
    # Uncomment the examples you want to test:
    
    # Example 1: Logging
    # example_with_logging()
    
    # Example 4: Use presentation mode
    # use_presentation_mode()
    
    # Example 7: Monitor performance
    # monitor_performance()
    
    print("\nTo use these examples:")
    print("1. Import the controller or detector class")
    print("2. Replace the original class in main.py")
    print("3. Customize gesture-to-action mappings")
    print("4. Run main.py\n")
    
    print("For more features, combine multiple examples!")
