import cv2
import mediapipe as mp

class HandSentinelDetector:
    def __init__(self, mode=False, max_hands=2, detection_con=0.5, track_con=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = float(detection_con)
        self.track_con = float(track_con)    
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode = self.mode,
            max_num_hands = self.max_hands,
            min_detection_confidence = self.detection_con,
            min_tracking_confidence = self.track_con
        )
        self.mp_draw = mp.solutions.drawing_utils

    def encontrar_manos(self, img, dibujar=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.resultados = self.hands.process(img_rgb)
        if self.resultados.multi_hand_landmarks:
            for hand_lms in self.resultados.multi_hand_landmarks:
                if dibujar:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return img
    
    def encontrar_posicion(self, img, num_mano=0):
        lista_puntos =[]
        if self.resultados.multi_hand_landmarks and len(self.resultados.multi_hand_landmarks) > num_mano:
            mi_mano = self.resultados.multi_hand_landmarks[num_mano]
            for id_punto, lm in enumerate(mi_mano.landmark):
                alto, ancho, canales = img.shape
                cx, cy = int(lm.x * ancho), int(lm.y * alto)
                lista_puntos.append([id_punto, cx, cy])
        return lista_puntos

    def encontrar_todas_las_manos(self, img):
        todas_las_manos = []
        if self.resultados.multi_hand_landmarks:
            for mi_mano in self.resultados.multi_hand_landmarks:
                lista_puntos = []
                for id_punto, lm in enumerate(mi_mano.landmark):
                    alto, ancho, canales = img.shape
                    cx, cy = int(lm.x * ancho), int(lm.y * alto)
                    lista_puntos.append([id_punto, cx, cy])
                todas_las_manos.append(lista_puntos)
        return todas_las_manos