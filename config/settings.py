# Import the dataclass decorator to easily create classes that just store data
from dataclasses import dataclass

# The @dataclass(frozen=True) decorator makes the class read-only (constants)
@dataclass(frozen=True)
class DetectorConfig:
    # Maximum number of hands the camera should look for
    max_hands: int = 2
    # Minimum confidence threshold (0.0 to 1.0) required to register a hand detection
    detection_confidence: float = 0.5
    # Minimum confidence threshold required to keep tracking a hand across frames
    tracking_confidence: float = 0.5

@dataclass(frozen=True)
class GestureConfig:
    # Number of frames the system will wait before dropping the combo if the gesture breaks
    combo_tolerance_frames: int = 20
    # Minimum physical distance required between the two hands (15% of screen width)
    min_hand_separation_ratio: float = 0.15
    # The upper portion of the screen considered the "face zone" (upper 55%)
    face_zone_ratio: float = 0.55
    # The maximum number of fingers allowed open for the "closed" hand
    max_fingers_closed: int = 1
    # The minimum number of fingers required open for the "open" hand
    min_fingers_open: int = 4

@dataclass(frozen=True)
class UIConfig:
    # File paths for the required multimedia assets
    video_path: str = "assets/scuba_cat.mp4"
    audio_path: str = "assets/audio.mp3"
    # Target resolution for scaling the cat overlay video
    cat_overlay_size: tuple = (180, 180)
    # The text displayed on the title bar of the desktop window
    window_name: str = "Hand Sentinel - Scuba Mode"
    # The amount of frames to track when calculating the average FPS
    fps_history_size: int = 30

# Create global, immutable instances of these configurations to be imported across the app
DETECTOR_CFG = DetectorConfig()
GESTURE_CFG  = GestureConfig()
UI_CFG       = UIConfig()