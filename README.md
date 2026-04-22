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
- Optional voice control for common actions

## Requirements

- Python 3.7+
- Webcam
- Windows/Mac/Linux

## Installation

### Easy Setup (Windows recommended)

1. Install Python 3.10 or newer.
   - Download it from python.org or use:
   ```powershell
   winget install -e --id Python.Python.3.10 --accept-package-agreements --accept-source-agreements
   ```

2. Open PowerShell in the project folder and create a virtual environment.
   ```powershell
   C:\Users\<YourUser>\AppData\Local\Programs\Python\Python310\python.exe -m venv .venv
   ```

3. Activate the virtual environment.
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

4. Install the dependencies.
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

   Voice commands now use `SpeechRecognition` plus `sounddevice` for microphone capture on Windows, so the default install should be enough.

5. Install the Microsoft Visual C++ runtime if MediaPipe needs it.
   ```powershell
   winget install -e --id Microsoft.VCRedist.2015+.x64 --accept-package-agreements --accept-source-agreements
   ```

6. Run the app.
   ```powershell
   python main.py
   ```

### Linux/macOS Quick Setup

1. Create and activate a virtual environment.
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies and run.
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
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

### Voice Commands
- "scroll down"
- "scroll up"
- "volume down"
- "volume up"
- "play" or "pause"
- "fullscreen"

Voice commands are tuned for lower latency by default. You can reduce `voice_cooldown` or `voice_chunk_seconds` in `config.json` if you want them even faster.

### Ignored Gestures
- Thumbs up: No gesture
- 3 fingers: No gesture

## Configuration

Edit `config.json` to customize behavior used by the current app:

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
- Fullscreen uses the "f" key and depends on the active app.
- Volume uses system volume keys.
- Pinch thresholds are currently defined in code in main.py.
- Voice commands are customizable via `voice_commands` in config.json.

## Optional Extensions

See advanced_examples.py for optional extensions (app launching, two-hand zoom, logging). These are examples and are not active in main.py by default.

## Troubleshooting

**Installation fails or Python command not found on Windows?**
- The Microsoft Store alias may shadow Python.
- Use the full interpreter path once to create the venv:
   - `C:\Users\<YourUser>\AppData\Local\Programs\Python\Python310\python.exe -m venv .venv`
- Then run using `.venv\Scripts\python.exe`.

**Virtual environment exists but packages fail to install/run?**
- Your `.venv` may be tied to an old Python path.
- Delete and recreate it:
   - `Remove-Item -Recurse -Force .venv`
   - `C:\Users\<YourUser>\AppData\Local\Programs\Python\Python310\python.exe -m venv .venv`

**Voice commands are disabled?**
- Confirm the app prints `Voice control enabled` at startup.
- If the primary microphone path fails, the app falls back to `sounddevice` automatically.
- Check Windows microphone privacy settings if neither backend can access audio.

**`python main.py` still says `No module named 'cv2'`?**
- You are probably using a different Python interpreter than the one in `.venv`.
- Activate the virtual environment first, or run the app with `.\.venv\Scripts\python.exe main.py`.
- If you want to use system Python instead, install the requirements into that interpreter with `python -m pip install -r requirements.txt`.

**ImportError: DLL load failed while importing MediaPipe bindings**
- Install Microsoft Visual C++ Redistributable (2015+ x64):
   - `winget install -e --id Microsoft.VCRedist.2015+.x64 --accept-package-agreements --accept-source-agreements`

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
