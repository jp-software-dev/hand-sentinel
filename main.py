# Import OpenCV to capture video from the computer's webcam
import cv2
# Import Pygame to manage the audio system
import pygame

# Import the logic, detection, and UI modules from the project folders
from core.detector import HandSentinelDetector    
from core.actions import HandSentinelActions
from ui.display import HandSentinelUI

def main():
    # Initialize the audio mixer module for background music
    pygame.mixer.init()
    
    # Open the default webcam (index 0)
    cap = cv2.VideoCapture(0)
    
    # Create an instance of the Detector module
    detector = HandSentinelDetector()
    
    # Create an instance of the Actions module
    actions = HandSentinelActions()
    
    # Create an instance of the UI module
    ui = HandSentinelUI()

    # Start an infinite loop to process the video frame by frame
    while True:
        # Read the current frame from the webcam
        success, frame = cap.read()
        
        # Break the loop if the camera fails to provide a frame
        if not success:
            break

        # Flip the frame horizontally to act like a mirror
        frame = cv2.flip(frame, 1)
        
        # Send the frame to the detector to process and draw landmarks
        frame = detector.find_hands(frame)
        
        # Extract the current dimensions of the frame
        height, width, _ = frame.shape
        
        # Get the nested list containing data for all hands present
        all_hands = detector.find_all_hands(frame)
        
        # Evaluate if the Scuba Cat gesture is currently being performed
        combo_active = actions.detect_cat_combo(all_hands, width, height)
        
        # Draw the entire HUD (including the green screen and texts)
        frame = ui.draw_hud(frame, combo_active=combo_active)
        
        # Show the processed frame to the user
        ui.show_window(frame)

        # Wait 1 millisecond for user input, break loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam hardware block
    cap.release()
    
    # Shut down the audio engine safely
    pygame.mixer.quit()
    
    # Close all OpenCV windows to prevent crashes
    cv2.destroyAllWindows()

# Entry point of the script: only run main() if executed directly
if __name__ == "__main__":
    main()