from dataclasses import dataclass

@dataclass(frozen=True)
class DetectorConfig:
    max_hands: int = 2
    detection_confidence: float = 0.5
    tracking_confidence: float = 0.5

@dataclass(frozen=True)
class GestureConfig:
    combo_tolerance_frames: int = 20
    min_hand_separation_ratio: float = 0.15
    face_zone_ratio: float = 0.55
    max_fingers_closed: int = 1
    min_fingers_open: int = 4

@dataclass(frozen=True)
class UIConfig:
    video_path: str = "assets/scuba_cat.mp4"
    audio_path: str = "assets/audio.mp3"
    cat_overlay_size: tuple = (180, 180)
    window_name: str = "Hand Sentinel - Scuba Mode"
    fps_history_size: int = 30

DETECTOR_CFG = DetectorConfig()
GESTURE_CFG  = GestureConfig()
UI_CFG       = UIConfig()