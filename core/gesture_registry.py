from abc import ABC, abstractmethod
import math

class BaseGesture(ABC):
    @abstractmethod
    def detect(self, all_hands: list, width: int, height: int) -> bool:
        ...

class ScubaCatGesture(BaseGesture):
    def __init__(self):
        self.tip_ids = [4, 8, 12, 16, 20]
        self.combo_tolerance = 0

    def scan_active_fingers(self, landmark_list, is_right_hand=True):
        if len(landmark_list) != 21:
            return [0] * 5

        active = []
        thumb_tip_x = landmark_list[4][1]
        thumb_ip_x = landmark_list[3][1]

        if is_right_hand:
            active.append(1 if thumb_tip_x > thumb_ip_x else 0)
        else:
            active.append(1 if thumb_tip_x < thumb_ip_x else 0)

        for fid in range(1, 5):
            tip_y = landmark_list[self.tip_ids[fid]][2]
            knuckle_y = landmark_list[self.tip_ids[fid] - 2][2]
            active.append(1 if tip_y < knuckle_y else 0)

        return active

    def detect(self, all_hands, width, height) -> bool:
        if len(all_hands) == 2:
            hand1 = all_hands[0]
            hand2 = all_hands[1]
            
            if len(hand1) == 21 and len(hand2) == 21:
                cx1, cy1 = hand1[9][1], hand1[9][2]
                cx2, cy2 = hand2[9][1], hand2[9][2]
                
                distance_between_hands = math.hypot(cx2 - cx1, cy2 - cy1)
                min_distance_required = width * 0.15 
                
                if distance_between_hands > min_distance_required:
                    face_zone_y_max = height * 0.55  
                    
                    if cy1 < face_zone_y_max or cy2 < face_zone_y_max:
                        is_right1 = cx1 > cx2 
                        is_right2 = not is_right1

                        fingers1 = sum(self.scan_active_fingers(hand1, is_right1))
                        fingers2 = sum(self.scan_active_fingers(hand2, is_right2))
                        
                        is_valid_pose = (fingers1 <= 1 and fingers2 >= 4) or (fingers1 >= 4 and fingers2 <= 1)

                        if is_valid_pose:
                            self.combo_tolerance = 20 
                            return True

        if self.combo_tolerance > 0:
            self.combo_tolerance -= 1
            return True

        return False

class GestureRegistry:
    def __init__(self):
        self._gestures = {}

    def register(self, name: str, gesture: BaseGesture):
        self._gestures[name] = gesture

    def detect_all(self, all_hands, width, height) -> dict:
        return {
            name: gesture.detect(all_hands, width, height)
            for name, gesture in self._gestures.items()
        }