# Import OpenCV to handle the video reading and image display
import cv2
# Import time to help calculate the Frames Per Second
import time
# Import NumPy to create color arrays for the green screen mask
import numpy as np
# Import Pygame to handle the background music/audio
import pygame

class HandSentinelUI:
    def __init__(self, video_path="assets/Scuba Cat..mp4", audio_path="assets/audio.mp3"):
        # Initialize a variable to track time for FPS calculation
        self.previous_time = 0
        
        # Load the cat video file using OpenCV
        self.cat_cap = cv2.VideoCapture(video_path)

        # Use a try-except block to safely load the audio file
        try:
            # Load the sound into Pygame
            self.cat_sound = pygame.mixer.Sound(audio_path)
        except pygame.error:
            # Print a warning if the file is missing instead of crashing
            print(f"Warning: Audio file not found at {audio_path}")
            self.cat_sound = None
            
        # Initialize a flag to know if the audio is currently playing
        self.is_playing_audio = False

    def draw_hud(self, frame, active_fingers=None, combo_active=False):
        # Get the current system time
        current_time = time.time()
        
        # Calculate the FPS based on the time difference between frames
        fps = 1 / (current_time - self.previous_time) if (current_time - self.previous_time) > 0 else 0
        
        # Update the previous time for the next cycle
        self.previous_time = current_time

        # Check if the combo gesture is successfully detected
        if combo_active:
            # If the audio is not playing and the file exists, start playing it
            if not self.is_playing_audio and self.cat_sound:
                self.cat_sound.play(loops=-1)
                self.is_playing_audio = True
        else:
            # If the combo stops and audio is playing, stop the audio
            if self.is_playing_audio and self.cat_sound:
                 self.cat_sound.stop()
                 self.is_playing_audio = False

        # Start the Green Screen effect if the combo is active
        if combo_active and self.cat_cap.isOpened():
            # Read the next frame from the cat video
            ret, frame_cat = self.cat_cap.read()
            
            # If the video reached the end, reset it to frame 0
            if not ret:
                self.cat_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame_cat = self.cat_cap.read()

            # If a video frame was successfully read
            if ret:
                # Resize the cat video to fit the corner of the screen
                frame_cat = cv2.resize(frame_cat, (180, 180))
                
                # Convert the video frame colors to HSV (Hue, Saturation, Value)
                hsv = cv2.cvtColor(frame_cat, cv2.COLOR_BGR2HSV)
                
                # Set the lowest and highest boundaries for the green color
                lower_green = np.array([35, 40, 40])
                upper_green = np.array([85, 255, 255])
                
                # Create a mask that isolates the green background
                mask = cv2.inRange(hsv, lower_green, upper_green)
                
                # Invert the mask to isolate the cat itself
                mask_inv = cv2.bitwise_not(mask)
                
                # Get the dimensions of the resized cat frame
                h, w, _ = frame_cat.shape
                
                # Define the Y coordinates for placing it (top right area)
                y1, y2 = 20, 20 + h
                
                # Define the X coordinates for placing it (aligned to the right border)
                x1, x2 = frame.shape[1] - w - 20, frame.shape[1] - 20
                
                # Select the exact region of interest (ROI) on the main camera frame
                roi = frame[y1:y2, x1:x2]
                
                # Cut out the green background from the cat frame
                fg = cv2.bitwise_and(frame_cat, frame_cat, mask=mask_inv)
                
                # Cut a cat-shaped hole into the camera background
                bg = cv2.bitwise_and(roi, roi, mask=mask)
                
                # Merge the cat into the camera frame hole
                frame[y1:y2, x1:x2] = cv2.add(bg, fg)
                
                # Draw a green rectangle around the area
                cv2.rectangle(frame, (x1-5, y1-5), (x2+5, y2+5), (0, 255, 0), 2)
                
                # Add text indicating the mode is active
                cv2.putText(frame, 'SCUBA MODE: ACTIVE', (x1, y2+25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Print the current FPS counter on the top left
        cv2.putText(frame, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # Display the current status of the detector
        if combo_active:
            cv2.putText(frame, 'TARGET: COMBO DETECTED', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, 'WAITING FOR GESTURE...', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Return the fully drawn frame
        return frame

    def show_window(self, frame, window_name="Hand Sentinel - Scuba Mode"):
        # Display the final image in a window
        cv2.imshow(window_name, frame)