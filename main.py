import os
import sys


def _ensure_project_venv():
    """Re-launch the script with the project virtual environment when needed."""
    workspace_root = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(workspace_root, ".venv", "Scripts", "python.exe")

    if not os.path.exists(venv_python):
        return

    current_exe = os.path.normcase(os.path.abspath(sys.executable))
    target_exe = os.path.normcase(os.path.abspath(venv_python))

    if current_exe == target_exe:
        return

    os.execv(venv_python, [venv_python] + sys.argv)


_ensure_project_venv()

import cv2
import mediapipe as mp
import pyautogui
import time
import math
import json
import threading
import importlib
from collections import deque
from enum import Enum

try:
    sr = importlib.import_module("speech_recognition")
except ImportError:
    sr = None

try:
    sd = importlib.import_module("sounddevice")
except ImportError:
    sd = None

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
            "gesture_timeout": 2.0,
            "enable_voice_control": True,
            "voice_cooldown": 0.5,
            "voice_phrase_time_limit": 2,
            "voice_listen_timeout": 0.5,
            "voice_chunk_seconds": 0.75,
            "voice_commands": {
                "scroll down": "scroll_down",
                "scroll up": "scroll_up",
                "volume down": "volume_down",
                "volume up": "volume_up",
                "play": "play_pause",
                "pause": "play_pause",
                "play pause": "play_pause",
                "fullscreen": "fullscreen"
            }
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        merged = default_config.copy()
                        for key, value in loaded.items():
                            if isinstance(merged.get(key), dict) and isinstance(value, dict):
                                nested = merged[key].copy()
                                nested.update(value)
                                merged[key] = nested
                            else:
                                merged[key] = value
                        return merged
            except:
                return default_config
        
        return default_config

    def _perform_action_by_name(self, action_name, current_time):
        """Run a named action and append history when successful."""
        action_performed = False

        if action_name == "scroll_down":
            pyautogui.scroll(-self.config["scroll_speed"])
            action_performed = True
            self.gesture_history.append(("SCROLL_DOWN", current_time))

        elif action_name == "scroll_up":
            pyautogui.scroll(self.config["scroll_speed"])
            action_performed = True
            self.gesture_history.append(("SCROLL_UP", current_time))

        elif action_name == "play_pause":
            pyautogui.press('space')
            action_performed = True
            self.gesture_history.append(("PLAY_PAUSE", current_time))

        elif action_name == "volume_down":
            pyautogui.press('volumedown')
            action_performed = True
            self.gesture_history.append(("VOLUME_DOWN", current_time))

        elif action_name == "volume_up":
            pyautogui.press('volumeup')
            action_performed = True
            self.gesture_history.append(("VOLUME_UP", current_time))

        elif action_name == "fullscreen":
            pyautogui.press('f')
            action_performed = True
            self.gesture_history.append(("FULLSCREEN", current_time))

        if action_performed:
            self.last_action_time = current_time

        return action_performed

    def execute_voice_action(self, action_name):
        """Execute action requested by the voice controller."""
        current_time = time.time()
        if current_time - self.last_action_time < self.config.get("voice_cooldown", 0.5):
            return False
        return self._perform_action_by_name(action_name, current_time)
    
    def execute_action(self, gesture, hand_pos=None, hand_distance=None, screen_width=1920, screen_height=1080, pinch_distance=None):
        """Execute action based on gesture"""
        current_time = time.time()
        
        if current_time - self.last_action_time < self.config["scroll_cooldown"]:
            return
        
        action_name = None

        if gesture == GestureType.SCROLL_DOWN:
            action_name = "scroll_down"

        elif gesture == GestureType.SCROLL_UP:
            action_name = "scroll_up"

        elif gesture == GestureType.PLAY_PAUSE:
            action_name = "play_pause"

        elif gesture == GestureType.PINCH:
            action_name = "volume_down"

        elif gesture == GestureType.PEACE_SIGN:
            action_name = "volume_up"

        elif gesture == GestureType.OPEN_HAND:
            action_name = "fullscreen"

        if action_name:
            self._perform_action_by_name(action_name, current_time)


class VoiceController:
    """Background microphone listener for voice commands."""

    def __init__(self, action_controller, ui=None):
        self.action_controller = action_controller
        self.ui = ui
        self.config = action_controller.config
        self.enabled = bool(self.config.get("enable_voice_control", True) and sr is not None)
        self.voice_commands = self.config.get("voice_commands", {})
        self.voice_cooldown = float(self.config.get("voice_cooldown", 0.5))
        self.phrase_time_limit = float(self.config.get("voice_phrase_time_limit", 2))
        self.listen_timeout = float(self.config.get("voice_listen_timeout", 0.5))
        self.chunk_seconds = float(self.config.get("voice_chunk_seconds", 0.75))
        self.last_voice_action_time = 0
        self._stop_event = threading.Event()
        self._thread = None
        self.backend = None

        self.recognizer = None
        self.microphone = None

        if self.enabled:
            self.recognizer = sr.Recognizer()
            self._initialize_backend()

    def _initialize_backend(self):
        """Pick a working audio backend for voice recognition."""
        if sr is None:
            self.enabled = False
            return

        try:
            self.microphone = sr.Microphone()
            self.backend = "speech_recognition"
            return
        except Exception:
            self.microphone = None

        if sd is not None:
            self.backend = "sounddevice"
            return

        self.enabled = False

    def start(self):
        """Start listening thread if voice control is available."""
        if not self.enabled or self._thread is not None:
            return
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def is_listening(self):
        """Return whether the background listener thread is running."""
        return self._thread is not None and self._thread.is_alive()

    def stop(self):
        """Stop listening thread."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)

    def _set_ui_voice_text(self, text):
        if self.ui:
            self.ui.last_voice_text = text
            self.ui.last_voice_time = time.time()

    def _resolve_voice_action(self, spoken_text):
        lower = spoken_text.lower().strip()

        if lower in self.voice_commands:
            return self.voice_commands[lower]

        for phrase, action in self.voice_commands.items():
            if phrase in lower:
                return action

        return None

    def _handle_spoken_text(self, spoken_text):
        action_name = self._resolve_voice_action(spoken_text)
        if not action_name:
            return

        now = time.time()
        if now - self.last_voice_action_time < self.voice_cooldown:
            return

        if self.action_controller.execute_voice_action(action_name):
            self.last_voice_action_time = now
            self._set_ui_voice_text(f"Voice: {spoken_text}")

    def _transcribe_audio(self, audio_data):
        try:
            spoken_text = self.recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            return
        except sr.RequestError:
            self._set_ui_voice_text("Voice service unavailable")
            time.sleep(1.0)
            return
        except Exception:
            return

        self._handle_spoken_text(spoken_text.lower().strip())

    def _listen_loop(self):
        """Continuously listen for voice commands."""
        if self.backend == "speech_recognition" and self.microphone is not None:
            with self.microphone as source:
                try:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                except Exception:
                    pass

            while not self._stop_event.is_set():
                try:
                    with self.microphone as source:
                        audio = self.recognizer.listen(source, timeout=self.listen_timeout, phrase_time_limit=self.phrase_time_limit)
                    self._transcribe_audio(audio)
                except sr.WaitTimeoutError:
                    continue
                except Exception:
                    continue
            return

        if self.backend == "sounddevice" and sd is not None:
            sample_rate = 16000

            while not self._stop_event.is_set():
                try:
                    audio_buffer = sd.rec(
                        int(sample_rate * self.chunk_seconds),
                        samplerate=sample_rate,
                        channels=1,
                        dtype="int16",
                    )
                    sd.wait()
                    if self._stop_event.is_set():
                        break

                    if not audio_buffer.any():
                        continue

                    audio = sr.AudioData(audio_buffer.tobytes(), sample_rate, 2)
                    self._transcribe_audio(audio)
                except Exception:
                    continue

            return

        self.enabled = False

class GestureControlUI:
    """Handles on-screen UI and feedback"""
    
    def __init__(self):
        self.gesture_display_time = 0
        self.current_gesture = "None"
        self.fps = 0
        self.last_time = time.time()
        self.voice_enabled = False
        self.voice_listening = False
        self.last_voice_text = ""
        self.last_voice_time = 0
        
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

        if self.voice_enabled and self.voice_listening:
            voice_status = "LISTENING"
            voice_color = (0, 255, 0)
        elif self.voice_enabled:
            voice_status = "READY"
            voice_color = (0, 255, 255)
        else:
            voice_status = "OFF"
            voice_color = (0, 0, 255)

        cv2.putText(frame, f"Voice: {voice_status}", (10, 105),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, voice_color, 2)

        if self.last_voice_text and (time.time() - self.last_voice_time) < 3.0:
            cv2.putText(frame, self.last_voice_text, (10, 135),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Zone indicators
        cv2.putText(frame, "LEFT", (20, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 255), 1)
        cv2.putText(frame, "CENTER", (width // 2 - 40, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 255), 1)
        cv2.putText(frame, "RIGHT", (width - 100, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 255), 1)
        
        # Instructions
        instructions = [
            "1 Finger: Scroll Down | 2 Fingers: Scroll Up | 4 Fingers: Fullscreen | 5 Fingers: Play/Pause",
            "Thumbs Up: No Gesture | Thumb+Index Pinch: Volume Down | Thumb+Middle Pinch: Volume Up",
            "Voice: say scroll up/down, volume up/down, play/pause, fullscreen | Q: Quit"
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
    voice = VoiceController(controller, ui)
    ui.voice_enabled = voice.enabled
    
    cap = cv2.VideoCapture(0)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print("Gesture Control System Started!")
    if voice.enabled:
        print("Voice control enabled")
    else:
        print("Voice control disabled (install SpeechRecognition and microphone support to enable)")
    print("Press 'q' to quit\n")

    voice.start()
    ui.voice_listening = voice.is_listening()
    
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
        ui.voice_listening = voice.is_listening()
        ui.draw_info(frame, current_gesture, results.multi_hand_landmarks)
        
        cv2.imshow("Advanced Gesture Control System", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\nShutting down...")
            break
    
    voice.stop()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()