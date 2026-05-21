# Import OpenCV for image manipulation
import cv2

# Import Google's MediaPipe library for AI hand tracking
import mediapipe as mp

# Import logging to output status messages
import logging

# Import dataclass to define a simple structure for hand landmarks
from dataclasses import dataclass

# Initialize a logger for the detector module
logger = logging.getLogger(__name__)

# Define a simple data structure to represent a single joint/point on the hand
@dataclass
class HandLandmark:
    id: int
    x: int
    y: int

class HandSentinelDetector:
    def __init__(self, mode=False, max_hands=2, detection_con=0.5, track_con=0.5):
        # Load the MediaPipe Hands solution module
        self.mp_hands = mp.solutions.hands
        
        # Load the drawing utilities to visually plot the hand landmarks on the screen
        self.mp_draw = mp.solutions.drawing_utils
        
        # Initialize the AI hand tracking model with the provided parameters
        self.hands = self.mp_hands.Hands(
            static_image_mode=mode,             # False means it treats input as a video stream (faster)
            max_num_hands=max_hands,            # Limit to tracking up to 2 hands
            model_complexity=0,                 # 0 is the fastest model, 1 is more accurate but slower
            min_detection_confidence=float(detection_con),
            min_tracking_confidence=float(track_con)
        )
        
        # Create an internal variable to store the latest raw detection results
        self._results = None

    def process_frame(self, img, draw=True):
        # Get the height and width of the current camera frame
        height, width = img.shape[:2]

        # Convert the image from BGR (OpenCV's default) to RGB (MediaPipe's requirement)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Lock the image memory to improve performance before passing it to the AI
        img_rgb.flags.writeable = False
        
        # Process the image with the AI model to find hands
        self._results = self.hands.process(img_rgb)
        
        # Unlock the image memory again
        img_rgb.flags.writeable = True

        # Initialize an empty list to store the processed coordinates of all detected hands
        all_hands = []

        # If no hands were found in this frame, return the untouched image and the empty list
        if not self._results.multi_hand_landmarks:
            return img, all_hands

        # Loop through each individual hand detected by the AI
        for hand_lms in self._results.multi_hand_landmarks:
            # If the draw flag is True, draw the skeleton lines and red dots on the original image
            if draw:
                self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)

            # Create a structured list of landmarks for this specific hand
            # Convert the AI's normalized coordinates (0.0 to 1.0) into actual screen pixels by multiplying by width and height
            hand_data = [
                [pid, int(lm.x * width), int(lm.y * height)]
                for pid, lm in enumerate(hand_lms.landmark)
            ]
            
            # Add this fully processed hand to our master list
            all_hands.append(hand_data)

        # Return the modified image (with drawings) and the organized list of hand coordinates
        return img, all_hands