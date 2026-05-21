# Import the ABC (Abstract Base Class) module to create a template for all gestures
from abc import ABC, abstractmethod

# Import math to calculate distances between coordinates
import math

class BaseGesture(ABC):
    # Enforce that any class inheriting from BaseGesture MUST have a 'detect' method
    @abstractmethod
    def detect(self, all_hands: list, width: int, height: int) -> bool:
        ...

class ScubaCatGesture(BaseGesture):
    def __init__(self):
        # Define the point IDs corresponding to the tips of the 5 fingers
        self.tip_ids = [4, 8, 12, 16, 20]
        # Initialize the tolerance counter to 0
        self.combo_tolerance = 0

    def scan_active_fingers(self, landmark_list, is_right_hand=True):
        # If the hand doesn't have all 21 points, return an array indicating 5 closed fingers
        if len(landmark_list) != 21:
            return [0] * 5

        active = []
        
        # Get the X coordinate of the thumb tip and the thumb inner joint
        thumb_tip_x = landmark_list[4][1]
        thumb_ip_x = landmark_list[3][1]

        # Check if the thumb is open based on whether it is a right or left hand
        # This fixes the bug where thumbs were miscalculated depending on which hand was used
        if is_right_hand:
            active.append(1 if thumb_tip_x > thumb_ip_x else 0)
        else:
            active.append(1 if thumb_tip_x < thumb_ip_x else 0)

        # Loop through the remaining 4 fingers
        for fid in range(1, 5):
            tip_y = landmark_list[self.tip_ids[fid]][2]
            knuckle_y = landmark_list[self.tip_ids[fid] - 2][2]
            
            # If the fingertip is higher on the screen than the knuckle, it's open (1), otherwise closed (0)
            active.append(1 if tip_y < knuckle_y else 0)

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
                
                # Define the minimum distance they must be apart (15% of screen width)
                min_distance_required = width * 0.15 
                
                # Proceed only if the hands are safely separated from each other
                if distance_between_hands > min_distance_required:
                    
                    # Define the limit for the upper area of the screen (top 55%)
                    face_zone_y_max = height * 0.55  
                    
                    # Check if at least one of the hands is raised into the "face zone"
                    if cy1 < face_zone_y_max or cy2 < face_zone_y_max:
                        
                        # Determine logically which hand is on the right and which is on the left
                        is_right1 = cx1 > cx2 
                        is_right2 = not is_right1

                        # Scan the fingers for both hands, passing the left/right context to fix the thumb bug
                        fingers1 = sum(self.scan_active_fingers(hand1, is_right1))
                        fingers2 = sum(self.scan_active_fingers(hand2, is_right2))
                        
                        # Validate the pose: One hand must be closed (0-1 fingers) and the other open (4-5 fingers)
                        is_valid_pose = (fingers1 <= 1 and fingers2 >= 4) or (fingers1 >= 4 and fingers2 <= 1)

                        # If the pose is completely valid, activate the combo and reset the tolerance timer
                        if is_valid_pose:
                            self.combo_tolerance = 20 
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