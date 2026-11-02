# Hand Sentinel: Computer Vision Engine ✋🤖

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" />
  <img src="https://img.shields.io/badge/MediaPipe-00C0A8?style=for-the-badge&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/Pygame-Audio-FF6F00?style=for-the-badge" />
</p>

**Hand Sentinel** is a real-time computer vision engine written in Python. It uses Google's **MediaPipe Hands** neural network to track 21 landmarks on each hand (up to 2 hands, 42 points) from a regular webcam. A geometric gesture classifier reads those landmarks and, when it recognizes the "Scuba" pose, plays a green-screen video overlay with audio, without touching the keyboard or mouse.

## ✨ Core Features

* **Bilateral hand tracking:** 21 landmarks per hand, both hands at once, powered by MediaPipe's pretrained neural network.
* **Rotation-invariant finger detection:** a finger counts as open when its tip is farther from the wrist than its middle joint, so detection works with tilted or horizontal hands, palm or back facing the camera, and either hand.
* **Gesture-triggered media:** the recognized pose starts a chroma-keyed video overlay (played at its native FPS) and a looping sound; both stop when the pose ends.
* **Smooth activation:** a short, time-based grace period keeps the effect from flickering when tracking drops for a moment.
* **Low-latency pipeline:** the camera is read in a background thread into a 2-frame buffer, so processing always uses the most recent frame.
* **Extensible gestures:** new gestures subclass `BaseGesture` and are added to the `GestureRegistry`.
* **Centralized configuration:** every threshold, path and UI size lives in `config/settings.py`.

## ⚙️ How It Works

```text
Webcam ──► capture thread ──► FrameBuffer (2 frames)
                                   │
                                   ▼
             HandSentinelDetector (MediaPipe Hands, 21 landmarks/hand)
                                   │
                                   ▼
             GestureRegistry ──► ScubaCatGesture (geometric rules)
                                   │ combo active?
                                   ▼
             HandSentinelUI ──► video overlay + audio + HUD (FPS, status)
```

1. **Capture:** a daemon thread reads the webcam, mirrors the image and pushes it into a small thread-safe buffer.
2. **Detection:** MediaPipe returns the landmarks of each detected hand, converted to pixel coordinates.
3. **Classification:** each registered gesture evaluates the landmarks and returns `True`/`False`.
4. **Rendering:** the UI draws the HUD and, while the combo is active, overlays the video and plays the audio.

## 🗂️ Project Structure

```text
hand-sentinel/
├── assets/
│   ├── Scuba_Cat.mp4        # Green-screen overlay video
│   └── audio.mp3            # Sound played while the combo is active
├── config/
│   └── settings.py          # DetectorConfig, GestureConfig and UIConfig
├── core/
│   ├── detector.py          # MediaPipe hand tracking wrapper
│   └── gesture_registry.py  # BaseGesture, ScubaCatGesture and GestureRegistry
├── ui/
│   └── display.py           # Chroma-key video overlay, audio and HUD
├── utils/
│   ├── fps_counter.py       # Rolling-average FPS counter
│   └── frame_buffer.py      # Thread-safe buffer that keeps only the latest frames
├── main.py                  # Entry point and main loop
└── requirements.txt
```

## 🛠 Technologies Used

* **Language:** Python 3.9 – 3.12 (MediaPipe 0.10.14 does not support newer versions)
* **Computer vision:** OpenCV
* **Hand tracking (neural network):** MediaPipe Hands
* **Gesture classification:** rule-based geometry over the landmarks
* **Audio:** Pygame mixer
* **Math / arrays:** NumPy

## 🚀 Installation & Setup

1. Clone the repository:

```bash
git clone https://github.com/jp-software-dev/hand-sentinel.git
```

2. Navigate into the project directory:

```bash
cd hand-sentinel
```

3. (Recommended) Create and activate a virtual environment:

```bash
python -m venv venv
```

```bash
venv\Scripts\activate
```

On Linux/macOS use `source venv/bin/activate` instead.

4. Install the dependencies:

```bash
pip install -r requirements.txt
```

5. Run the engine:

```bash
python main.py
```

## 🎮 Usage: The "Scuba" Trigger

With the webcam active, Hand Sentinel draws the landmarks of your hands in real time. The combo is detected when **all** of these are true:

* **Both hands** are fully visible in the frame.
* The hands are **separated** by at least 15% of the frame width.
* At least **one hand is in the upper part of the frame** (top 55%, around the face).
* **One hand is closed** (0–1 fingers open) and **the other is open** (4–5 fingers open).

A natural way to do it: make a fist in front of your mouth (the "regulator") and raise the other hand open, like a scuba diver. The detector does not track your face, so only the conditions above matter.

While the combo is active, the Scuba Cat video appears in the top-right corner, the audio loops and the HUD shows `COMBO DETECTED`. The effect stays on for 0.7 s after the pose breaks to avoid flickering.

### Controls

* Press **`q`** or close the window to exit.

## 🔧 Configuration

All tunable values are in [`config/settings.py`](config/settings.py):

| Setting | Default | Description |
| --- | --- | --- |
| `DetectorConfig.max_hands` | `2` | Maximum hands tracked |
| `DetectorConfig.detection_confidence` | `0.5` | Minimum confidence to detect a hand |
| `DetectorConfig.tracking_confidence` | `0.5` | Minimum confidence to keep tracking a hand |
| `GestureConfig.combo_grace_seconds` | `0.7` | Seconds the combo stays active after the pose breaks |
| `GestureConfig.min_hand_separation_ratio` | `0.15` | Minimum distance between hands (ratio of frame width) |
| `GestureConfig.face_zone_ratio` | `0.55` | Upper portion of the frame considered the face zone |
| `GestureConfig.max_fingers_closed` | `1` | Maximum open fingers for the "closed" hand |
| `GestureConfig.min_fingers_open` | `4` | Minimum open fingers for the "open" hand |
| `UIConfig.video_path` / `audio_path` | `assets/...` | Media files used by the effect |
| `UIConfig.cat_overlay_size` | `(180, 180)` | Box the overlay video is fitted into (aspect ratio is kept) |
| `UIConfig.window_name` | `Hand Sentinel - Scuba Mode` | Window title |
| `UIConfig.fps_history_size` | `30` | Frames averaged for the FPS counter |

## 🧩 Adding a New Gesture

1. Create a class in `core/gesture_registry.py` that inherits from `BaseGesture` and implements `detect(all_hands, width, height) -> bool`.
2. Register it in `main.py`:

```python
registry.register("my_gesture", MyGesture())
```

3. Read its state from the dictionary returned by `registry.detect_all(...)`.

## 🩺 Troubleshooting

* **`Could not open the camera.`** Another app may be using the webcam, or camera access is blocked in your OS privacy settings.
* **`Overlay video not found or empty`** Check that `assets/Scuba_Cat.mp4` exists. The file name is case-sensitive on Linux/macOS.
* **`Audio not found`** Check that `assets/audio.mp3` exists.
* **`No frame received from the camera`** The webcam stalled; the app retries and closes only after several consecutive failures.
