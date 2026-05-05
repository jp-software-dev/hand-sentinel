# Import the OpenCV library for computer vision tasks
import cv2
# Import the MediaPipe library for AI hand tracking
import mediapipe as mp

class HandSentinelDetector:
    def __init__(self, mode=False, max_hands=2, detection_con=0.5, track_con=0.5):
        # Save the initialization parameters into class variables
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = float(detection_con)
        self.track_con = float(track_con)    
        
        # Load the MediaPipe Hands solution module
        self.mp_hands = mp.solutions.hands
        
        # Initialize the Hands object with our specific confidence parameters
        self.hands = self.mp_hands.Hands(
            static_image_mode = self.mode,
            max_num_hands = self.max_hands,
            min_detection_confidence = self.detection_con,
            min_tracking_confidence = self.track_con
        )
        
        # Load the MediaPipe drawing utilities to draw lines and landmarks on screen
        self.mp_draw = mp.solutions.drawing_utils

    def find_hands(self, img, draw=True):
        # Convert the image from BGR format (OpenCV) to RGB format (MediaPipe)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Process the image to find hand landmarks
        self.results = self.hands.process(img_rgb)
        
        # Verify if any hands were detected in the frame
        if self.results.multi_hand_landmarks:
            # Loop through each detected hand
            for hand_lms in self.results.multi_hand_landmarks:
                # Draw the landmarks and connections if the draw parameter is True
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
                    
        # Return the original image (with drawings if applied)
        return img
    
    def find_position(self, img, hand_num=0):
        # Create an empty list to store the position of each point
        landmark_list = []
        
        # Verify if hands exist and if the requested hand number is available
        if self.results.multi_hand_landmarks and len(self.results.multi_hand_landmarks) > hand_num:
            # Select the specific hand requested
            target_hand = self.results.multi_hand_landmarks[hand_num]
            
            # Loop through all 21 landmarks of the selected hand
            for point_id, lm in enumerate(target_hand.landmark):
                # Get the height, width, and channels of the image
                height, width, channels = img.shape
                
                # Convert the relative coordinates (0 to 1) into pixel coordinates
                cx, cy = int(lm.x * width), int(lm.y * height)
                
                # Append the ID and coordinates to the list
                landmark_list.append([point_id, cx, cy])
                
        # Return the list containing the hand's positions
        return landmark_list

    def find_all_hands(self, img):
        # Create an empty main list to store the data of all hands
        all_hands = []
        
        # Check if any hands were detected
        if self.results.multi_hand_landmarks:
            # Loop through every hand detected in the frame
            for hand in self.results.multi_hand_landmarks:
                # Create a specific list for the current hand
                landmark_list = []
                
                # Loop through all 21 landmarks of the current hand
                for point_id, lm in enumerate(hand.landmark):
                    # Get the dimensions of the image
                    height, width, channels = img.shape
                    
                    # Convert the coordinates into pixel values
                    cx, cy = int(lm.x * width), int(lm.y * height)
                    
                    # Add the point to the current hand's list
                    landmark_list.append([point_id, cx, cy])
                    
                # Append the fully mapped hand into the main list
                all_hands.append(landmark_list)
                
        # Return the nested list with all hands data
        return all_hands