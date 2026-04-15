# Advanced Gesture Control System

A webcam-based hand gesture controller for scrolling, media control, fullscreen, and volume.

## Features (current)

### Core Gesture Recognition
- 1 finger (index): Scroll Down
- 2 fingers (index + middle): Scroll Up
- 4 fingers: Fullscreen (sends "f")
- 5 fingers: Play/Pause (sends Space)
- Thumb + index pinch: Volume Down
- Thumb + middle pinch: Volume Up
- Thumbs up: No gesture (ignored)
- 3 fingers: No gesture (reserved)

### Other Features
- Real-time FPS display
- On-screen gesture label and instructions
- Multi-hand detection (up to 2 hands)
- JSON config for scroll speed and cooldown

## Requirements

- Python 3.7+
- Webcam
- Windows/Mac/Linux

## Installation

1. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application
   ```bash
   python main.py
   ```

Press "q" to quit at any time.

## Gesture Guide

### Scrolling
- Index finger up: Scroll Down
- Index + middle up: Scroll Up

### Media and Fullscreen
- 4 fingers: Fullscreen ("f" key)
- 5 fingers: Play/Pause (Space)

### Volume
- Thumb + index pinch: Volume Down
- Thumb + middle pinch: Volume Up

### Ignored Gestures
- Thumbs up: No gesture
- 3 fingers: No gesture

## Configuration

Edit `config.json` to customize behavior used by the current app:

```json
{
  "scroll_speed": 200,
  "scroll_cooldown": 0.8
}
```

Notes:
- Fullscreen uses the "f" key and depends on the active app.
- Volume uses system volume keys.
- Pinch thresholds are currently defined in code in main.py.

## Optional Extensions

See advanced_examples.py for optional extensions (app launching, two-hand zoom, logging). These are examples and are not active in main.py by default.

## Troubleshooting

**Gestures not detected?**
- Ensure good lighting
- Keep hand in camera frame
- Move closer to the camera

**Lag or low FPS?**
- Reduce camera resolution
- Close other applications

**Actions triggering incorrectly?**
- Increase `scroll_cooldown`
- Reduce hand movement speed

## Code Structure

```
main.py
├── GestureType        # Enum for gesture types
├── GestureRecognizer  # Detects gestures from hand landmarks
├── ActionController   # Maps gestures to actions
└── GestureControlUI   # On-screen display and feedback
```

## Learning Resources

- MediaPipe Hand Detection: https://developers.google.com/mediapipe/solutions/vision/hand_landmarker
- OpenCV Docs: https://docs.opencv.org/
- PyAutoGUI Reference: https://pyautogui.readthedocs.io/
