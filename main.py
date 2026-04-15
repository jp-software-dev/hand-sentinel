import cv2
import pygame
from core.detector import HandSentinelDetector    
from core.actions import HandSentinelActions
from ui.display import HandSentinelUI

def main():

    pygame.mixer.init()
    cap = cv2.VideoCapture(0)
    detector = HandSentinelDetector()
    acciones = HandSentinelActions()
    interfaz = HandSentinelUI()

    while True:
        exito, frame = cap.read()
        if not exito:
            break

        frame = cv2.flip(frame, 1)
        frame = detector.encontrar_manos(frame)
        
        alto, ancho, _ = frame.shape
        todas_las_manos = detector.encontrar_todas_las_manos(frame)
        
        combo_activado = acciones.detectar_combo_gato(todas_las_manos, ancho, alto)
        frame = interfaz.dibujar_hud(frame, combo_activado=combo_activado)
        
        interfaz.mostrar_ventana(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    pygame.mixer.quit()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()