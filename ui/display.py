# Import OpenCV for image manipulation and video processing
import cv2

# Import NumPy to handle matrix operations and color arrays efficiently
import numpy as np

# Import Pygame to manage and play audio files
import pygame

# Import logging to output warnings or errors to the console
import logging

# Import time to play the overlay video at its own speed, independent of the camera FPS
import time

# Import the custom FPSCounter to track and display the application's performance
from utils.fps_counter import FPSCounter

# Initialize the logger for this specific module
logger = logging.getLogger(__name__)

class CatVideoProcessor:
    def __init__(self, path: str, target_size: tuple = (180, 180)):
        # Create an empty list to store all the processed frames of the video in memory
        self.frames = []

        # Native frame rate of the video (read in _preprocess, 30 FPS if the file does not report it)
        self.fps = 30.0

        # Pre-process the video immediately upon initialization to avoid lag later
        self._preprocess(path, target_size)

        # Moment the playback started; the current frame is derived from the elapsed time
        self._start_time = time.perf_counter()

    def _preprocess(self, path: str, size: tuple):
        # Open the video file from the provided path
        cap = cv2.VideoCapture(path)

        # Store the video's own frame rate so playback speed does not depend on the camera
        native_fps = cap.get(cv2.CAP_PROP_FPS)
        if native_fps and native_fps > 0:
            self.fps = native_fps
        
        # Define the lower and upper bounds for the green screen color in HSV format
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])

        # Final (width, height) of each frame, computed from the first frame to keep the aspect ratio
        fit_size = None

        # Loop through every frame in the video until it ends
        while True:
            ret, frame = cap.read()
            if not ret:
                # Break the loop if there are no more frames to read
                break

            # Scale the video to fit inside the target box without stretching it (e.g. a vertical video stays vertical)
            if fit_size is None:
                src_h, src_w = frame.shape[:2]
                scale = min(size[0] / src_w, size[1] / src_h)
                fit_size = (max(1, int(src_w * scale)), max(1, int(src_h * scale)))
            frame = cv2.resize(frame, fit_size, interpolation=cv2.INTER_AREA)
            
            # Convert the frame from standard BGR color space to HSV for easier color filtering
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Create a mask that isolates the green background (white where green is, black elsewhere)
            mask = cv2.inRange(hsv, lower_green, upper_green)
            
            # Invert the mask so the subject (e.g., the cat) is white and the background is black
            mask_inv = cv2.bitwise_not(mask)
            
            # Extract the foreground (the subject) by applying the inverted mask to the original frame
            fg = cv2.bitwise_and(frame, frame, mask=mask_inv)
            
            # Save the processed foreground and the original green mask into our memory list
            self.frames.append((fg, mask))

        # Release the video file from memory once all frames are processed
        cap.release()

        # Without frames the overlay silently never appears, so make the problem visible in the console
        if not self.frames:
            logger.warning("Overlay video not found or empty: %s", path)

    def restart(self):
        # Rewind the playback so the video starts from its first frame
        self._start_time = time.perf_counter()

    def next_frame(self) -> tuple:
        # If the video failed to load or has no frames, return nothing
        if not self.frames:
            return None, None

        # Pick the frame that matches the elapsed time. Use modulo (%) to loop back to 0 when reaching the end
        elapsed = time.perf_counter() - self._start_time
        index = int(elapsed * self.fps) % len(self.frames)

        # Return the requested frame data
        return self.frames[index]

class HandSentinelUI:
    def __init__(self, video_path: str = "assets/Scuba_Cat.mp4", audio_path: str = "assets/audio.mp3"):
        # Initialize the FPS counter to monitor screen performance
        self.fps_counter = FPSCounter()
        
        # Initialize the video processor to preload the green-screen asset
        self.cat_processor = CatVideoProcessor(video_path)
        
        # Create a flag to track whether the sound effect is currently playing
        self._is_audio_playing = False

        # Remember the combo state of the previous frame to detect when it turns on
        self._was_active = False
        
        # Load the audio file into memory
        self._audio = self._load_audio(audio_path)

    def _load_audio(self, path: str):
        # Attempt to load the audio file using Pygame
        try:
            return pygame.mixer.Sound(path)
        except pygame.error:
            # If the file is missing or corrupted, log a warning and return None
            logger.warning("Audio not found: %s", path)
            return None

    def _handle_audio(self, combo_active: bool):
        # If the combo is active, audio isn't playing yet, and the audio file loaded successfully
        if combo_active and not self._is_audio_playing and self._audio:
            # Start playing the audio on an infinite loop (loops=-1)
            self._audio.play(loops=-1)
            self._is_audio_playing = True
            
        # If the combo stops but audio is still playing
        elif not combo_active and self._is_audio_playing and self._audio:
            # Stop the audio playback
            self._audio.stop()
            self._is_audio_playing = False

    def _overlay_cat(self, frame: np.ndarray) -> np.ndarray:
        # Get the next frame (foreground and background mask) from the preloaded video
        fg, mask = self.cat_processor.next_frame()
        
        # If there is no video data available, just return the untouched camera frame
        if fg is None:
            return frame
            
        # Extract the height and width of the overlay video
        h, w = fg.shape[:2]
        
        # Define the Y coordinates (top to bottom) for placing the video in the top-right corner
        y1, y2 = 20, 20 + h
        
        # Define the X coordinates (left to right) for placing the video
        x1, x2 = frame.shape[1] - w - 20, frame.shape[1] - 20

        # Skip the overlay if the camera frame is too small to hold it (slicing would produce a mismatched ROI)
        if x1 < 0 or y2 > frame.shape[0]:
            return frame

        # Select the Region of Interest (ROI) on the main camera frame where the video will go
        roi = frame[y1:y2, x1:x2]
        
        # Black out the area in the ROI where our subject (the cat) will be placed
        bg = cv2.bitwise_and(roi, roi, mask=mask)
        
        # Combine the blacked-out background with our subject foreground and place it back on the camera frame
        frame[y1:y2, x1:x2] = cv2.add(bg, fg)
        
        # Draw a green rectangular border around the overlaid video
        cv2.rectangle(frame, (x1-5, y1-5), (x2+5, y2+5), (0,255,0), 2)
        
        # Add text directly below the video indicating the mode is active
        cv2.putText(frame, 'SCUBA MODE: ACTIVE', (x1, y2+25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
                    
        return frame

    def draw_hud(self, frame: np.ndarray, combo_active: bool = False) -> np.ndarray:
        # Check if we need to start or stop the audio based on the combo status
        self._handle_audio(combo_active)
        
        # Restart the video from the beginning each time the combo turns on
        if combo_active and not self._was_active:
            self.cat_processor.restart()
        self._was_active = combo_active

        # If the correct hand gesture combo is detected, overlay the video onto the screen
        if combo_active:
            frame = self._overlay_cat(frame)
            
        # Update the FPS counter and get the current frames per second
        fps = self.fps_counter.tick()
        
        # Set the text color: Green if the combo is active, Red if it is waiting
        color = (0,255,0) if combo_active else (0,0,255)
        
        # Set the status text based on whether the user is performing the gesture
        status = 'COMBO DETECTED' if combo_active else 'WAITING FOR GESTURE...'
        
        # Draw the current FPS on the top left of the screen in cyan
        cv2.putText(frame, f'FPS: {fps:.0f}', (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
                    
        # Draw the current detection status just below the FPS counter
        cv2.putText(frame, status, (10,70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    
        return frame

    def show_window(self, frame: np.ndarray, name: str = "Hand Sentinel - Scuba Mode"):
        # Display the final composed frame in a desktop window with the given title
        cv2.imshow(name, frame)