import cv2
import mediapipe as mp
import pyautogui
import time
import math
import json
import os
from collections import deque
from enum import Enum

class GestureType(Enum):
    NONE = 0
    SCROLL_DOWN = 1
    SCROLL_UP = 2
    PLAY_PAUSE = 3
    PINCH = 4
    PEACE_SIGN = 5
    FIST = 6
    THUMBS_UP = 7
    POINTING = 8
    SWIPE_LEFT = 9
    SWIPE_RIGHT = 10
    OPEN_HAND = 11

class GestureRecognizer:
    """Advanced gesture recognition system"""
    
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.hand_positions = deque(maxlen=10)  # Track hand positions for smoothing
        self.last_action_time = 0
        self.cooldown = 0.8
        self.prev_hand_x = 0
        self.prev_hand_y = 0
        
    def distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
    
    def count_extended_fingers(self, hand_landmarks):
        """Count extended fingers (more accurate)"""
        fingers = []
        
        # Thumb
        if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
            fingers.append(1)
        else:
            fingers.append(0)
        
        # Other fingers
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        
        for tip, pip in zip(tips, pips):
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
                fingers.append(1)
            else:
                fingers.append(0)
        
        return fingers
    

    
    def detect_gesture(self, hand_landmarks):
        """Detect the current gesture based on finger count or pinch"""
        fingers = self.count_extended_fingers(hand_landmarks)
        finger_count = sum(fingers)
        thumb_index_dist = self.get_pinch_distance(hand_landmarks)
        thumb_middle_dist = self.get_thumb_middle_distance(hand_landmarks)
        pinch_threshold = 0.12
        strict_pinch_threshold = 0.08

        # Thumbs up should display as no gesture
        is_thumbs_up = fingers[0] == 1 and sum(fingers[1:]) == 0
        if is_thumbs_up:
            return GestureType.NONE

        # Preserve 1-finger scroll unless the pinch is very tight
        if finger_count == 1 and fingers[1] == 1:
            if thumb_index_dist < strict_pinch_threshold:
                return GestureType.PINCH
            return GestureType.SCROLL_DOWN

        # Preserve 2-finger scroll unless a tight pinch is detected
        if finger_count == 2 and fingers[1] == 1 and fingers[2] == 1:
            if min(thumb_index_dist, thumb_middle_dist) < strict_pinch_threshold:
                if thumb_index_dist <= thumb_middle_dist:
                    return GestureType.PINCH
                return GestureType.PEACE_SIGN
            return GestureType.SCROLL_UP

        # Check for thumb-index pinch (volume down)
        if thumb_index_dist < pinch_threshold and thumb_index_dist <= thumb_middle_dist:
            return GestureType.PINCH
        
        # Check for thumb-middle pinch (volume up)
        if thumb_middle_dist < pinch_threshold:
            return GestureType.PEACE_SIGN
        
        if finger_count == 4:
            return GestureType.OPEN_HAND
        elif finger_count == 5:
            return GestureType.PLAY_PAUSE
        
        return GestureType.NONE
    
    def get_hand_position(self, hand_landmarks, frame_width, frame_height):
        """Get normalized hand position"""
        middle_finger_tip = hand_landmarks.landmark[9]
        x = middle_finger_tip.x * frame_width
        y = middle_finger_tip.y * frame_height
        return int(x), int(y)
    
    def get_hand_distance(self, hand_landmarks):
        """Get approximate hand span distance"""
        thumb = hand_landmarks.landmark[4]
        pinky = hand_landmarks.landmark[20]
        return self.distance(thumb, pinky)
    
    def get_pinch_distance(self, hand_landmarks):
        """Get distance between thumb and index finger"""
        thumb = hand_landmarks.landmark[4]
        index = hand_landmarks.landmark[8]
        return self.distance(thumb, index)
    
    def get_thumb_middle_distance(self, hand_landmarks):
        """Get distance between thumb and middle finger"""
        thumb = hand_landmarks.landmark[4]
        middle = hand_landmarks.landmark[12]
        return self.distance(thumb, middle)
    
    def detect_thumb_index_pinch(self, hand_landmarks, threshold=0.12):
        """Detect if thumb is pinched with index finger"""
        return self.get_pinch_distance(hand_landmarks) < threshold
    
    def detect_thumb_middle_pinch(self, hand_landmarks, threshold=0.12):
        """Detect if thumb is pinched with middle finger"""
        return self.get_thumb_middle_distance(hand_landmarks) < threshold
    
    def detect_pinch(self, hand_landmarks, threshold=0.1):
        """Detect if pinch gesture is being made"""
        pinch_dist = self.get_pinch_distance(hand_landmarks)
        return pinch_dist < threshold
    
    def process_frame(self, frame):
        """Process frame and return hand landmarks and RGB frame"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        return results

class ActionController:
    """Handles gesture-to-action mapping"""
    
    def __init__(self, config_path="config.json"):
        self.config = self._load_config(config_path)
        self.last_action_time = 0
        self.gesture_history = deque(maxlen=20)
        
    def _load_config(self, config_path):
        """Load configuration from file"""
        default_config = {
            "scroll_speed": 200,
            "scroll_cooldown": 0.8,
            "mouse_speed": 1.5,
            "enable_mouse_control": True,
            "enable_volume_control": True,
            "enable_app_shortcuts": True,
            "gesture_timeout": 2.0
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except:
                return default_config
        
        return default_config
    
    def execute_action(self, gesture, hand_pos=None, hand_distance=None, screen_width=1920, screen_height=1080, pinch_distance=None):
        """Execute action based on gesture"""
        current_time = time.time()
        
        if current_time - self.last_action_time < self.config["scroll_cooldown"]:
            return
        
        action_performed = False
        
        if gesture == GestureType.SCROLL_DOWN:
            pyautogui.scroll(-self.config["scroll_speed"])
            action_performed = True
            self.gesture_history.append(("SCROLL_DOWN", current_time))
        
        elif gesture == GestureType.SCROLL_UP:
            pyautogui.scroll(self.config["scroll_speed"])
            action_performed = True
            self.gesture_history.append(("SCROLL_UP", current_time))
        
        elif gesture == GestureType.PLAY_PAUSE:
            pyautogui.press('space')
            action_performed = True
            self.gesture_history.append(("PLAY_PAUSE", current_time))
        
        elif gesture == GestureType.PINCH:
            pyautogui.press('volumedown')
            action_performed = True
            self.gesture_history.append(("VOLUME_DOWN", current_time))
        
        elif gesture == GestureType.PEACE_SIGN:
            pyautogui.press('volumeup')
            action_performed = True
            self.gesture_history.append(("VOLUME_UP", current_time))
        
        elif gesture == GestureType.OPEN_HAND:
            pyautogui.press('f')
            action_performed = True
            self.gesture_history.append(("FULLSCREEN", current_time))
        
        if action_performed:
            self.last_action_time = current_time

class GestureControlUI:
    """Handles on-screen UI and feedback"""
    
    def __init__(self):
        self.gesture_display_time = 0
        self.current_gesture = "None"
        self.fps = 0
        self.last_time = time.time()
        
    def update_fps(self):
        """Update FPS calculation"""
        current_time = time.time()
        dt = current_time - self.last_time
        if dt > 0:
            self.fps = int(1 / dt)
        self.last_time = current_time
    
    def draw_info(self, frame, gesture, hand_landmarks=None):
        """Draw gesture info and UI on frame"""
        height, width = frame.shape[:2]
        
        # FPS
        cv2.putText(frame, f"FPS: {self.fps}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Current Gesture
        display_names = {
            GestureType.PINCH: "VOLUME_DOWN",
            GestureType.PEACE_SIGN: "VOLUME_UP",
            GestureType.OPEN_HAND: "FULLSCREEN",
            GestureType.NONE: "NO_GESTURE"
        }
        if gesture is None:
            gesture_text = "None"
        else:
            gesture_text = display_names.get(gesture, gesture.name)
        cv2.putText(frame, f"Gesture: {gesture_text}", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
        
        # Zone indicators
        cv2.putText(frame, "LEFT", (20, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 255), 1)
        cv2.putText(frame, "CENTER", (width // 2 - 40, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 255), 1)
        cv2.putText(frame, "RIGHT", (width - 100, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 255), 1)
        
        # Instructions
        instructions = [
            "1 Finger: Scroll Down | 2 Fingers: Scroll Up | 4 Fingers: Fullscreen | 5 Fingers: Play/Pause",
            "Thumbs Up: No Gesture | Thumb+Index Pinch: Volume Down | Thumb+Middle Pinch: Volume Up | Q: Quit"
        ]
        
        for i, text in enumerate(instructions):
            cv2.putText(frame, text, (10, height - 60 + i * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Draw hand landmarks if available
        if hand_landmarks:
            mp_hands = mp.solutions.hands
            mp_draw = mp.solutions.drawing_utils
            for landmarks in hand_landmarks:
                mp_draw.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS,
                                      mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2))

def main():
    """Main application loop"""
    recognizer = GestureRecognizer()
    controller = ActionController()
    ui = GestureControlUI()
    
    cap = cv2.VideoCapture(0)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print("Gesture Control System Started!")
    print("Press 'q' to quit\n")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        ui.update_fps()
        
        results = recognizer.process_frame(frame)
        current_gesture = None
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                current_gesture = recognizer.detect_gesture(hand_landmarks)
                hand_pos = recognizer.get_hand_position(hand_landmarks, frame_width, frame_height)
                hand_distance = recognizer.get_hand_distance(hand_landmarks)
                
                # Execute action
                controller.execute_action(current_gesture, hand_pos, hand_distance, frame_width, frame_height)
        
        # Draw UI
        ui.draw_info(frame, current_gesture, results.multi_hand_landmarks)
        
        cv2.imshow("Advanced Gesture Control System", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\nShutting down...")
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()