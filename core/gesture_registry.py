# Import the ABC (Abstract Base Class) module to create a template for all gestures
from abc import ABC, abstractmethod

# Import math to calculate distances between coordinates
import math

# Import the gesture thresholds so they can be tuned from a single place
from config.settings import GESTURE_CFG

class BaseGesture(ABC):
    # Enforce that any class inheriting from BaseGesture MUST have a 'detect' method
    @abstractmethod
    def detect(self, all_hands: list, width: int, height: int) -> bool:
        ...

class ScubaCatGesture(BaseGesture):
    def __init__(self, cfg=GESTURE_CFG):
        # Store the thresholds that define a valid pose
        self.cfg = cfg
        # Define the point IDs corresponding to the tips of the 5 fingers
        self.tip_ids = [4, 8, 12, 16, 20]
        # Initialize the tolerance counter to 0
        self.combo_tolerance = 0

    @staticmethod
    def _dist(landmark_list, a, b):
        # Return the Euclidean distance in pixels between two landmarks of the same hand
        return math.hypot(landmark_list[a][1] - landmark_list[b][1],
                          landmark_list[a][2] - landmark_list[b][2])

    def scan_active_fingers(self, landmark_list):
        # If the hand doesn't have all 21 points, return an array indicating 5 closed fingers
        if len(landmark_list) != 21:
            return [0] * 5

        active = []

        # Thumb: it is open when its tip is farther from the pinky base (17) than its inner joint (3).
        # Comparing distances instead of X coordinates works for both hands, palm or back facing the camera
        active.append(1 if self._dist(landmark_list, 4, 17) > self._dist(landmark_list, 3, 17) else 0)

        # Loop through the remaining 4 fingers
        for fid in range(1, 5):
            tip = self.tip_ids[fid]
            pip = tip - 2

            # A finger is open when its tip is farther from the wrist (0) than its middle joint (PIP).
            # Unlike comparing Y coordinates, this still works when the hand is tilted or horizontal
            active.append(1 if self._dist(landmark_list, tip, 0) > self._dist(landmark_list, pip, 0) else 0)

        return active

    def detect(self, all_hands, width, height) -> bool:
        # Check if exactly two hands are on the screen
        if len(all_hands) == 2:
            hand1 = all_hands[0]
            hand2 = all_hands[1]
            
            # Ensure both hands are fully mapped (no ghosting/glitches)
            if len(hand1) == 21 and len(hand2) == 21:
                
                # Extract the center coordinates (lower middle finger joint) of both hands
                cx1, cy1 = hand1[9][1], hand1[9][2]
                cx2, cy2 = hand2[9][1], hand2[9][2]
                
                # Calculate the exact distance between the centers of both hands
                distance_between_hands = math.hypot(cx2 - cx1, cy2 - cy1)
                
                # Define the minimum distance they must be apart (a ratio of the screen width)
                min_distance_required = width * self.cfg.min_hand_separation_ratio
                
                # Proceed only if the hands are safely separated from each other
                if distance_between_hands > min_distance_required:
                    
                    # Define the limit for the upper area of the screen (the "face zone")
                    face_zone_y_max = height * self.cfg.face_zone_ratio
                    
                    # Check if at least one of the hands is raised into the "face zone"
                    if cy1 < face_zone_y_max or cy2 < face_zone_y_max:
                        
                        # Count the open fingers on both hands (independent of which hand is left or right)
                        fingers1 = sum(self.scan_active_fingers(hand1))
                        fingers2 = sum(self.scan_active_fingers(hand2))
                        
                        # Validate the pose: One hand must be closed and the other open
                        closed, opened = self.cfg.max_fingers_closed, self.cfg.min_fingers_open
                        is_valid_pose = (fingers1 <= closed and fingers2 >= opened) or (fingers1 >= opened and fingers2 <= closed)

                        # If the pose is completely valid, activate the combo and reset the tolerance timer
                        if is_valid_pose:
                            self.combo_tolerance = self.cfg.combo_tolerance_frames
                            return True

        # If the combo is broken, check if we still have "grace period" frames left
        if self.combo_tolerance > 0:
            # Consume one tolerance frame and pretend the combo is still active
            self.combo_tolerance -= 1
            return True

        # Return False if the gesture is not detected and the tolerance has run out
        return False

class GestureRegistry:
    def __init__(self):
        # Create an empty dictionary to store multiple different gestures
        self._gestures = {}

    def register(self, name: str, gesture: BaseGesture):
        # Add a new gesture object to the registry under a specific string name
        self._gestures[name] = gesture

    def detect_all(self, all_hands, width, height) -> dict:
        # Loop through all registered gestures, run their detect() method, 
        # and return a dictionary of their True/False statuses
        return {
            name: gesture.detect(all_hands, width, height)
            for name, gesture in self._gestures.items()
        }