import cv2
import numpy as np
import pygame
import logging
from utils.fps_counter import FPSCounter

logger = logging.getLogger(__name__)

class CatVideoProcessor:
    def __init__(self, path: str, target_size: tuple = (180, 180)):
        self.frames = []
        self._preprocess(path, target_size)
        self._index = 0

    def _preprocess(self, path: str, size: tuple):
        cap = cv2.VideoCapture(path)
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.resize(frame, size)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, lower_green, upper_green)
            mask_inv = cv2.bitwise_not(mask)
            fg = cv2.bitwise_and(frame, frame, mask=mask_inv)
            self.frames.append((fg, mask))

        cap.release()

    def next_frame(self) -> tuple:
        if not self.frames:
            return None, None
        item = self.frames[self._index]
        self._index = (self._index + 1) % len(self.frames)
        return item

class HandSentinelUI:
    def __init__(self, video_path: str = "assets/scuba_cat.mp4", audio_path: str = "assets/audio.mp3"):
        self.fps_counter = FPSCounter()
        self.cat_processor = CatVideoProcessor(video_path)
        self._is_audio_playing = False
        self._audio = self._load_audio(audio_path)

    def _load_audio(self, path: str):
        try:
            return pygame.mixer.Sound(path)
        except pygame.error:
            logger.warning("Audio no encontrado: %s", path)
            return None

    def _handle_audio(self, combo_active: bool):
        if combo_active and not self._is_audio_playing and self._audio:
            self._audio.play(loops=-1)
            self._is_audio_playing = True
        elif not combo_active and self._is_audio_playing and self._audio:
            self._audio.stop()
            self._is_audio_playing = False

    def _overlay_cat(self, frame: np.ndarray) -> np.ndarray:
        fg, mask = self.cat_processor.next_frame()
        if fg is None:
            return frame
        h, w = fg.shape[:2]
        y1, y2 = 20, 20 + h
        x1, x2 = frame.shape[1] - w - 20, frame.shape[1] - 20
        roi = frame[y1:y2, x1:x2]
        bg = cv2.bitwise_and(roi, roi, mask=mask)
        frame[y1:y2, x1:x2] = cv2.add(bg, fg)
        cv2.rectangle(frame, (x1-5, y1-5), (x2+5, y2+5), (0,255,0), 2)
        cv2.putText(frame, 'SCUBA MODE: ACTIVE', (x1, y2+25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
        return frame

    def draw_hud(self, frame: np.ndarray, combo_active: bool = False) -> np.ndarray:
        self._handle_audio(combo_active)
        if combo_active:
            frame = self._overlay_cat(frame)
        fps = self.fps_counter.tick()
        color = (0,255,0) if combo_active else (0,0,255)
        status = 'COMBO DETECTADO' if combo_active else 'ESPERANDO GESTO...'
        cv2.putText(frame, f'FPS: {fps:.0f}', (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
        cv2.putText(frame, status, (10,70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        return frame

    def show_window(self, frame: np.ndarray, name: str = "Hand Sentinel - Scuba Mode"):
        cv2.imshow(name, frame)