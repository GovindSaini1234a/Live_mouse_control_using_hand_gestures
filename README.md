# 🖱️ Live Mouse Control Using Hand Gestures

> Control your computer's mouse entirely through hand gestures captured by your webcam — no physical mouse needed!

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?logo=opencv)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Hands-orange)](https://mediapipe.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Gesture Reference](#gesture-reference)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Hand Landmark Reference](#hand-landmark-reference)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## 📖 About the Project

This project implements a **virtual mouse** using real-time hand gesture recognition. It uses your webcam feed to detect hand landmarks via **MediaPipe**, processes the finger positions and angles to interpret gestures, and translates them into mouse actions using **PyAutoGUI** and **pynput**.

Built as a computer vision project, it demonstrates how 21 hand landmarks detected by MediaPipe can be mapped to meaningful user interactions — all without touching a physical mouse.

---

## ✨ Features

| Feature | Gesture |
|---|---|
| 🖱️ **Mouse Movement** | Close thumb + index & middle fingers upright |
| 👆 **Left Click** | Open thumb + bend index finger (middle straight) |
| 👉 **Right Click** | Open thumb + bend middle finger (index straight) |
| ✌️ **Double Click** | Open thumb + bend both index & middle fingers |
| 📸 **Screenshot** | Close thumb + index + middle fingers simultaneously |
| ⏸️ **Stop Movement** | Open/extend thumb |

---

## 🤌 Gesture Reference

```
MOVEMENT         LEFT CLICK       RIGHT CLICK      DOUBLE CLICK     SCREENSHOT
                                                                     
  👍 closed        👍 open           👍 open           👍 open           👍 closed
  ☝️ up            ☝️ bent ↓         ☝️ up              ☝️ bent ↓         ☝️ closed
  🖕 up            🖕 up             🖕 bent ↓          🖕 bent ↓         🖕 closed
```

> **Tip:** Only the **thumb**, **index finger**, and **middle finger** are actively tracked. The ring and pinky fingers can be in any position.

---

## ⚙️ How It Works

### Architecture Overview

```
Webcam Feed
    │
    ▼
OpenCV (frame capture & BGR→RGB conversion)
    │
    ▼
MediaPipe Hands (21 landmark detection)
    │
    ▼
util.py (angle & distance calculations)
    ├── get_angle(a, b, c)   ─── checks if finger is bent or straight
    └── get_distance(pts)    ─── checks thumb-to-index distance
    │
    ▼
Gesture Detection (detect_gesture)
    ├── is_left_click()
    ├── is_right_click()
    ├── is_double_click()
    └── is_screenshot()
    │
    ▼
Mouse Actions
    ├── PyAutoGUI  ─── mouse movement, double click, screenshot
    └── pynput     ─── left click, right click
```

### Angle & Distance Logic

- **Finger bend detection**: Calculates the angle formed by 3 consecutive landmarks (e.g., landmarks 5→6→8 for the index finger). Angle < 50° → finger is **bent**; angle > 90° → finger is **upright**.
- **Thumb state detection**: Measures the Euclidean distance between landmark **4** (thumb tip) and landmark **5** (index finger base). Distance < 50 → thumb is **closed**; distance > 50 → thumb is **open**.

### Key MediaPipe Landmarks Used

| Landmark | Finger Part |
|---|---|
| `4` | Thumb tip |
| `5` | Index finger base (MCP joint) |
| `6` | Index finger middle joint (PIP) |
| `8` | Index finger tip |
| `9` | Middle finger base (MCP joint) |
| `10` | Middle finger middle joint (PIP) |
| `12` | Middle finger tip |

---

## 📁 Project Structure

```
Live_mouse_control_using_hand_gestures/
│
├── main.py          # Entry point — video capture, landmark detection, gesture dispatch
├── util.py          # Utility functions: get_angle(), get_distance()
└── screenshots/     # Auto-saved screenshots (created at runtime)
```

---

## 🔧 Prerequisites

- Python 3.8 or higher
- A working webcam
- Windows / macOS / Linux

---

## 🚀 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/GovindSaini1234a/Live_mouse_control_using_hand_gestures.git
   cd Live_mouse_control_using_hand_gestures
   ```

2. **Install dependencies**

   ```bash
   pip install opencv-python mediapipe pyautogui pynput numpy
   ```

   | Package | Purpose |
   |---|---|
   | `opencv-python` | Webcam capture & image display |
   | `mediapipe` | Hand landmark detection |
   | `pyautogui` | Mouse movement & double-click |
   | `pynput` | Left & right click |
   | `numpy` | Angle & distance math |

---

## ▶️ Usage

```bash
python main.py
```

- A window named **"frame"** will open showing your webcam feed with hand landmarks drawn.
- Perform gestures in front of the camera to control the mouse.
- Press **`Q`** to quit the application.

> **Note:** If you have multiple cameras, change the index in `cv2.VideoCapture(0)` inside `main.py` — use `1`, `2`, etc. for other cameras.

---

## 🖐️ Hand Landmark Reference

MediaPipe detects **21 landmarks** per hand:

```
                    8   12  16  20
                    |   |   |   |
                    7   11  15  19
                    |   |   |   |
                    6   10  14  18
                    |   |   |   |
              4     5   9   13  17
              |      \ /
              3       |
              |       |
              2       0
               \     /
                1---/
```

- `0` — Wrist  
- `1-4` — Thumb (1=CMC, 2=MCP, 3=IP, 4=Tip)  
- `5-8` — Index finger  
- `9-12` — Middle finger  
- `13-16` — Ring finger  
- `17-20` — Pinky finger  

---

## 🛠️ Troubleshooting

| Issue | Solution |
|---|---|
| **Camera not opening** | Change `cv2.VideoCapture(0)` to `1` or `2` |
| **Mouse moving erratically** | Ensure good lighting and keep hand clearly in frame |
| **`get_distance` argument error** | Pass landmarks as a list: `[landmark_list[4], landmark_list[5]]` |
| **`landmark_list` not defined** | Restart the kernel/runtime after saving changes |
| **Clicks not registering** | Try adjusting angle/distance thresholds in the gesture functions |
| **High CPU usage** | Reduce camera resolution or lower `model_complexity` to `0` |

---

## 🤝 Contributing

Contributions are welcome! Some ideas for improvement:

- [ ] Add scroll gesture (pinch and drag)
- [ ] Add zoom in/out gesture
- [ ] Support two-hand mode for more gestures
- [ ] GUI for configuring gesture thresholds
- [ ] Optimize performance with frame skipping

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

- [MediaPipe by Google](https://mediapipe.dev/) for the blazing-fast hand landmark detection model
- [OpenCV](https://opencv.org/) for video capture and image processing
- Inspired by the **Data Science Marine** YouTube tutorial series on computer vision projects
