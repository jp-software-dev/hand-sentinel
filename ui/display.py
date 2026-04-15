import cv2
import time
import numpy as np
import pygame

class HandSentinelUI:
    def __init__(self, video_path="assets/Scuba Cat..mp4", audio_path="assets/audio.mp3"):
        self.tiempo_anterior = 0
        self.cap_cat = cv2.VideoCapture(video_path)

        try:
            self.sonido_gato = pygame.mixer.Sound(audio_path)
        except pygame.error:
            print(f"Advertencia: No se encontró el audio en {audio_path}")
            self.sonido_gato = None
        self.audio_reproduciendo = False

    def dibujar_hud(self, frame, dedos_activos=None, combo_activado=False):
        tiempo_actual = time.time()
        fps = 1 / (tiempo_actual - self.tiempo_anterior) if (tiempo_actual - self.tiempo_anterior) > 0 else 0
        self.tiempo_anterior = tiempo_actual

        if combo_activado:
            if not self.audio_reproduciendo and self.sonido_gato:
                self.sonido_gato.play(loops=-1)
                self.audio_reproduciendo = True
        else:
            if self.audio_reproduciendo and self.sonido_gato:
                 self.sonido_gato.stop()
                 self.audio_reproduciendo = False

        if combo_activado and self.cap_cat.isOpened():
            ret, frame_cat = self.cap_cat.read()
            if not ret:
                self.cap_cat.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame_cat = self.cap_cat.read()

            if ret:
                frame_cat = cv2.resize(frame_cat, (180, 180))
                hsv = cv2.cvtColor(frame_cat, cv2.COLOR_BGR2HSV)
                lower_green = np.array([35, 40, 40])
                upper_green = np.array([85, 255, 255])
                
                mask = cv2.inRange(hsv, lower_green, upper_green)
                mask_inv = cv2.bitwise_not(mask)
                
                h, w, _ = frame_cat.shape
                y1, y2 = 20, 20 + h
                x1, x2 = frame.shape[1] - w - 20, frame.shape[1] - 20
                
                cat_crop = frame_cat
                roi = frame[y1:y2, x1:x2]
                
                fg = cv2.bitwise_and(cat_crop, cat_crop, mask=mask_inv)
                bg = cv2.bitwise_and(roi, roi, mask=mask)
                
                frame[y1:y2, x1:x2] = cv2.add(bg, fg)
                
                cv2.rectangle(frame, (x1-5, y1-5), (x2+5, y2+5), (0, 255, 0), 2)
                cv2.putText(frame, 'SCUBA MODE: ACTIVE', (x1, y2+25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.putText(frame, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        if combo_activado:
            cv2.putText(frame, 'TARGET: COMBO DETECTED', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, 'WAITING FOR GESTURE...', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return frame

    def mostrar_ventana(self, frame, nombre_ventana="Hand Sentinel - Scuba Mode"):
        cv2.imshow(nombre_ventana, frame)