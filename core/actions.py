# Import the math module to calculate the distance between points
import math

class HandSentinelActions:
    def __init__(self):
        # Define a list of point IDs corresponding to the fingertips (Thumb, Index, Middle, Ring, Pinky)
        self.tip_ids = [4, 8, 12, 16, 20]
        
        # Define the amount of tolerance frames before turning off the combo
        self.combo_tolerance = 0

    def scan_active_fingers(self, landmark_list):
        # Create an empty list to store which fingers are open (1) or closed (0)
        active_fingers = []
        
        # Check if the hand has no landmarks, and return the empty list if so
        if len(landmark_list) == 0:
            return active_fingers
        
        # Check the thumb: verify if its x-coordinate is further than the lower joint
        if landmark_list[self.tip_ids[0]][1] > landmark_list[self.tip_ids[0] - 1][1]:
            active_fingers.append(1)
        else:
            active_fingers.append(0)
            
        # Start a loop to check the remaining 4 fingers (Index to Pinky)
        for finger_id in range(1, 5):
            # Get the y-coordinate of the current fingertip
            tip_y = landmark_list[self.tip_ids[finger_id]][2]
            
            # Get the y-coordinate of the knuckle for the same finger
            knuckle_y = landmark_list[self.tip_ids[finger_id] - 2][2]
            
            # Check if the tip is higher up on the screen (lower y-value) than the knuckle
            if tip_y < knuckle_y:
                active_fingers.append(1)
            else:
                active_fingers.append(0)
                
        # Return the final list of active and inactive fingers
        return active_fingers
    
    def calculate_distance(self, p1, p2, landmark_list):
        # Return 0 if the landmark list is empty
        if len(landmark_list) == 0:
            return 0, None
        
        # Extract the X and Y coordinates for both requested points
        x1, y1 = landmark_list[p1][1], landmark_list[p1][2]
        x2, y2 = landmark_list[p2][1], landmark_list[p2][2]
        
        # Calculate the exact center point between the two landmarks
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2 

        # Calculate the Euclidean distance using the math library
        distance = math.hypot(x2 - x1, y2 - y1)
        
        # Group the spatial information into a single tuple
        spatial_info = (x1, y1, x2, y2, cx, cy)
        
        return distance, spatial_info

    def detect_cat_combo(self, all_hands, width, height):
        # Verify that exactly two hands are detected in the frame
        if len(all_hands) == 2:
            hand1 = all_hands[0]
            hand2 = all_hands[1]
            
            # IMPROVEMENT 1: Ensure both hands are fully visible (21 points) to avoid "ghost hands"
            if len(hand1) == 21 and len(hand2) == 21:
                
                # Get the center point (Middle finger lower joint, ID 9) for both hands
                cx1, cy1 = hand1[9][1], hand1[9][2]
                cx2, cy2 = hand2[9][1], hand2[9][2]
                
                # IMPROVEMENT 2: Ensure hands are physically separated to avoid overlapping confusion
                distance_between_hands = math.hypot(cx2 - cx1, cy2 - cy1)
                min_distance_required = width * 0.15 # Hands must be separated by at least 15% of screen width
                
                if distance_between_hands > min_distance_required:
                    
                    # Set a boundary limit for the upper face zone (upper 55% of the screen)
                    face_zone_y_max = height * 0.55  
                    
                    # Check if at least one hand is in the upper part of the screen
                    if cy1 < face_zone_y_max or cy2 < face_zone_y_max:
                        
                        # Count active fingers for both hands
                        fingers1 = sum(self.scan_active_fingers(hand1))
                        fingers2 = sum(self.scan_active_fingers(hand2))
                        
                        # IMPROVEMENT 3: Stricter roles. One strictly closed (0-1), one strictly open (4-5)
                        is_valid_pose = (fingers1 <= 1 and fingers2 >= 4) or (fingers1 >= 4 and fingers2 <= 1)

                        if is_valid_pose:
                            # Refill the tolerance buffer to 20 frames
                            self.combo_tolerance = 20 
                            return True

        # If the combo breaks, check if we still have tolerance frames left
        if self.combo_tolerance > 0:
            # Subtract one tolerance frame
            self.combo_tolerance -= 1
            return True

        # Return False if the combo is not active and no tolerance is left
        return False