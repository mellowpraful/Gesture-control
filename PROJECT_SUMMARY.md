# Project Summary: Advanced Gesture Control System

## Current Gesture Mapping

- 1 finger (index): Scroll Down
- 2 fingers (index + middle): Scroll Up
- 4 fingers: Fullscreen (sends "f")
- 5 fingers: Play/Pause (sends Space)
- Thumb + index pinch: Volume Down
- Thumb + middle pinch: Volume Up
- Thumbs up: No gesture (ignored)
- 3 fingers: No gesture (reserved)

## Voice Command Mapping

- "scroll down": Scroll Down
- "scroll up": Scroll Up
- "volume down": Volume Down
- "volume up": Volume Up
- "play" / "pause": Play/Pause
- "fullscreen": Fullscreen (sends "f")

## Project Structure

```
gesture-control/
├── main.py               # Core application
├── utils.py              # Helper functions and utilities
├── advanced_examples.py  # Optional extension examples
├── config.json           # Configuration settings
├── requirements.txt      # Dependencies
├── README.md             # Full documentation
├── QUICKSTART.md         # Getting started guide
└── PROJECT_SUMMARY.md    # This file
```

## Notes

- Additional gesture types exist in `GestureType`, but only the mapping above is active in main.py.
- Pinch thresholds are currently set in code in main.py.
- Zone guides are visual only; no zone-based actions are active by default.

## How to Run

```bash
pip install -r requirements.txt
python main.py
```
