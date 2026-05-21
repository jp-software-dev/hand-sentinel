import cv2
import pygame
import logging
import sys
import threading

from core.detector import HandSentinelDetector
from core.gesture_registry import GestureRegistry, ScubaCatGesture
from ui.display import HandSentinelUI
from config.settings import DETECTOR_CFG, UI_CFG
from utils.frame_buffer import FrameBuffer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def capture_thread(cap, buffer, stop_event):
    while not stop_event.is_set():
        success, frame = cap.read()
        if success:
            buffer.put(cv2.flip(frame, 1))
    logger.info("Hilo de captura terminado.")

def main():
    pygame.mixer.init()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        logger.error("No se pudo abrir la cámara.")
        return 1

    buffer = FrameBuffer(maxsize=2)
    stop_evt = threading.Event()
    cap_thread = threading.Thread(
        target=capture_thread, args=(cap, buffer, stop_evt), daemon=True
    )
    cap_thread.start()

    detector = HandSentinelDetector(
        max_hands=DETECTOR_CFG.max_hands,
        detection_con=DETECTOR_CFG.detection_confidence,
        track_con=DETECTOR_CFG.tracking_confidence
    )

    registry = GestureRegistry()
    registry.register("scuba_cat", ScubaCatGesture())

    ui = HandSentinelUI(
        video_path=UI_CFG.video_path,
        audio_path=UI_CFG.audio_path
    )

    logger.info("Hand Sentinel iniciado. Presiona 'q' para salir.")

    try:
        while True:
            try:
                frame = buffer.get()
            except Exception:
                break

            height, width = frame.shape[:2]

            frame, all_hands = detector.process_frame(frame)

            gestures = registry.detect_all(all_hands, width, height)
            combo_active = gestures.get("scuba_cat", False)

            frame = ui.draw_hud(frame, combo_active=combo_active)
            ui.show_window(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        logger.info("Interrumpido por el usuario.")

    finally:
        stop_evt.set()
        cap_thread.join(timeout=2.0)
        cap.release()
        pygame.mixer.quit()
        cv2.destroyAllWindows()
        logger.info("Hand Sentinel cerrado correctamente.")

    return 0

if __name__ == "__main__":
    sys.exit(main())