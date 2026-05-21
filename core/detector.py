import cv2
import mediapipe as mp
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class HandLandmark:
    id: int
    x: int
    y: int

class HandSentinelDetector:
    def __init__(self, mode=False, max_hands=2, detection_con=0.5, track_con=0.5):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=mode,
            max_num_hands=max_hands,
            model_complexity=0,
            min_detection_confidence=float(detection_con),
            min_tracking_confidence=float(track_con)
        )
        self._results = None

    def process_frame(self, img, draw=True):
        height, width = img.shape[:2]

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_rgb.flags.writeable = False
        self._results = self.hands.process(img_rgb)
        img_rgb.flags.writeable = True

        all_hands = []

        if not self._results.multi_hand_landmarks:
            return img, all_hands

        for hand_lms in self._results.multi_hand_landmarks:
            if draw:
                self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)

            hand_data = [
                [pid, int(lm.x * width), int(lm.y * height)]
                for pid, lm in enumerate(hand_lms.landmark)
            ]
            all_hands.append(hand_data)

        return img, all_hands