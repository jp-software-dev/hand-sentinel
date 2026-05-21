# Import OpenCV for video capture and image processing
import cv2

# Import Pygame to handle audio playback
import pygame

# Import the logging module to print status and error messages to the console
import logging

# Import sys to handle system-level exits and closures
import sys

# Import threading to run the camera capture in a separate background process
import threading

# Import custom core modules for hand detection and gesture recognition
from core.detector import HandSentinelDetector
from core.gesture_registry import GestureRegistry, ScubaCatGesture

# Import the user interface module to handle the screen and HUD elements
from ui.display import HandSentinelUI

# Import configuration settings for the detector and the UI
from config.settings import DETECTOR_CFG, UI_CFG

# Import a custom frame buffer to smoothly handle camera frames without lagging
from utils.frame_buffer import FrameBuffer

# Configure the logging system to show timestamps, severity levels, and the message
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# Initialize a logger specifically for this main script
logger = logging.getLogger(__name__)

def capture_thread(cap, buffer, stop_event):
    # Loop continuously until the stop signal event is triggered
    while not stop_event.is_set():
        # Attempt to read the latest frame from the webcam
        success, frame = cap.read()
        
        # If the frame was successfully captured, flip it horizontally (mirror effect) and put it in the buffer
        if success:
            buffer.put(cv2.flip(frame, 1))
            
    # Log a message once the loop breaks and the thread finishes
    logger.info("Capture thread finished.")

def main():
    # Initialize the audio mixer from Pygame to allow sound effects
    pygame.mixer.init()
    
    # Access the default system camera (index 0)
    cap = cv2.VideoCapture(0)

    # Check if the camera was successfully opened; if not, log an error and exit the program
    if not cap.isOpened():
        logger.error("Could not open the camera.")
        return 1

    # Create a thread-safe frame buffer that holds a maximum of 2 frames to avoid processing lag
    buffer = FrameBuffer(maxsize=2)
    
    # Create an event flag to safely signal the background thread when it's time to stop
    stop_evt = threading.Event()
    
    # Set up the background camera thread, passing the camera, buffer, and stop event
    # 'daemon=True' ensures this thread will automatically close if the main program crashes
    cap_thread = threading.Thread(
        target=capture_thread, args=(cap, buffer, stop_evt), daemon=True
    )
    
    # Start the background camera capture thread
    cap_thread.start()

    # Initialize the hand detection module using confidence settings from the configuration file
    detector = HandSentinelDetector(
        max_hands=DETECTOR_CFG.max_hands,
        detection_con=DETECTOR_CFG.detection_confidence,
        track_con=DETECTOR_CFG.tracking_confidence
    )

    # Create a registry to manage and store all active gestures
    registry = GestureRegistry()
    
    # Register the specific 'scuba_cat' gesture to be monitored by the registry
    registry.register("scuba_cat", ScubaCatGesture())

    # Initialize the user interface manager, loading necessary video and audio assets
    ui = HandSentinelUI(
        video_path=UI_CFG.video_path,
        audio_path=UI_CFG.audio_path
    )

    # Log a startup message to let the user know the system is ready
    logger.info("Hand Sentinel started. Press 'q' to quit.")

    try:
        # Start the main execution loop to process frames
        while True:
            try:
                # Attempt to retrieve the latest frame from the background buffer
                frame = buffer.get()
            except Exception:
                # If there's an error getting the frame, break the loop
                break

            # Extract the vertical (height) and horizontal (width) dimensions of the current frame
            height, width = frame.shape[:2]

            # Process the frame to detect hands, returning the drawn frame and a list of hand landmarks
            frame, all_hands = detector.process_frame(frame)

            # Check the current hand positions against all registered gestures
            gestures = registry.detect_all(all_hands, width, height)
            
            # Extract the status of the 'scuba_cat' gesture (True if active, False otherwise)
            combo_active = gestures.get("scuba_cat", False)

            # Draw the Heads-Up Display (HUD) and any visual effects over the frame based on the combo status
            frame = ui.draw_hud(frame, combo_active=combo_active)
            
            # Display the final processed frame in the application window
            ui.show_window(frame)

            # Wait for 1 millisecond and check if the 'q' key is pressed to manually break the loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Handle the case where the user forcefully stops the script (e.g., using Ctrl+C in the terminal)
    except KeyboardInterrupt:
        logger.info("Interrupted by the user.")

    # Ensure all hardware resources and windows are properly released when the script stops
    finally:
        # Trigger the stop event to tell the background thread to halt
        stop_evt.set()
        
        # Wait up to 2 seconds for the capture thread to safely finish closing
        cap_thread.join(timeout=2.0)
        
        # Release the webcam hardware
        cap.release()
        
        # Shut down the Pygame audio mixer
        pygame.mixer.quit()
        
        # Close all active OpenCV GUI windows
        cv2.destroyAllWindows()
        
        # Log a final confirmation message
        logger.info("Hand Sentinel closed successfully.")

    # Return 0 to indicate the program executed without fatal errors
    return 0

# Check if this script is being run directly (not imported as a module)
if __name__ == "__main__":
    # Execute the main function and exit with its return code
    sys.exit(main())