# Quick Start Guide

## Installation and Setup

### Step 1: Install dependencies
```bash
pip install -r requirements.txt
```

If you encounter issues, install individually:
```bash
pip install opencv-python
pip install mediapipe
pip install pyautogui
pip install SpeechRecognition
```

If microphone input is unavailable, also install:
```bash
pip install pyaudio
```

The app now prefers `sounddevice` for microphone capture when available, so the default dependency install should usually be enough on Windows.

### Step 2: Run the application
```bash
python main.py
```

Press "q" to quit at any time.

---

## Basic Gestures to Try

### 1) Scroll (1 and 2 fingers)
- 1 finger: Scroll Down
- 2 fingers: Scroll Up

### 2) Fullscreen and Play/Pause
- 4 fingers: Fullscreen (sends "f")
- 5 fingers: Play/Pause (sends Space)

### 3) Pinch for Volume
- Thumb + index pinch: Volume Down
- Thumb + middle pinch: Volume Up

### 4) Ignored Gestures
- Thumbs up: No gesture
- 3 fingers: No gesture

### 5) Voice Commands
- "scroll down"
- "scroll up"
- "volume down"
- "volume up"
- "play" or "pause"
- "fullscreen"

Voice commands now use shorter capture windows, so they should feel faster. Lower `voice_chunk_seconds` in `config.json` if you want even less delay.

---

## Real-World Use Cases

### Scenario 1: Watching videos
```
1 finger    → Scroll through comments
2 fingers   → Scroll back up
4 fingers   → Fullscreen ("f")
5 fingers   → Play/Pause (Space)
Pinch       → Adjust volume
```

### Scenario 2: Browsing documents
```
1 finger → Scroll Down
2 fingers → Scroll Up
```

---

## Customization

### Change scroll speed
Edit `config.json`:
```json
{
  "scroll_speed": 200,
  "scroll_cooldown": 0.8,
  "enable_voice_control": true,
  "voice_cooldown": 1.2,
  "voice_phrase_time_limit": 3
}
```

Notes:
- Pinch thresholds are currently set in code in main.py.
- Fullscreen uses the "f" key and depends on the active app.

---

## Advanced Examples

See advanced_examples.py for optional extensions (app launcher, two-hand zoom, logging). These are examples and are not active in main.py by default.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Gestures not detected | Better lighting, move closer to camera |
| False triggers | Increase `scroll_cooldown` in config.json |
| Low FPS | Close other apps, reduce camera resolution |

---

## File Structure

```
gesture-control/
├── main.py               # Core application
├── utils.py              # Helper functions and utilities
├── advanced_examples.py  # Optional extension examples
├── config.json           # Configuration settings
├── requirements.txt      # Python dependencies
├── README.md             # Full documentation
└── QUICKSTART.md         # This file
```
