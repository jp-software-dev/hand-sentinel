import math

class HandSentinelActions:
    def __init__(self):
        self.tip_ids = [4, 8, 12, 16, 20]
        self.tolerancia_combo = 0

    def escanear_dedos_activos(self, lista_puntos):
        dedos_activos = []
        if len(lista_puntos) == 0:
            return dedos_activos
        
        if lista_puntos[self.tip_ids[0]][1] > lista_puntos[self.tip_ids[0] - 1][1]:
            dedos_activos.append(1)
        else:
            dedos_activos.append(0)
            
        for id_dedo in range(1, 5):
            punta_y = lista_puntos[self.tip_ids[id_dedo]][2]
            nudillo_y = lista_puntos[self.tip_ids[id_dedo] - 2][2]
            if punta_y < nudillo_y:
                dedos_activos.append(1)
            else:
                dedos_activos.append(0)
        return dedos_activos
    
    def calcular_distancia(self, p1, p2, lista_puntos):
        if len(lista_puntos) == 0:
            return 0, None
        
        x1, y1 = lista_puntos[p1][1], lista_puntos[p1][2]
        x2, y2 = lista_puntos[p2][1], lista_puntos[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2 

        distancia = math.hypot(x2 - x1, y2 - y1)
        info_espacial = (x1, y1, x2, y2, cx, cy)
        return distancia, info_espacial

    def detectar_combo_gato(self, todas_las_manos, ancho, alto):
        if len(todas_las_manos) == 2:
            zona_cara_y_max = alto * 0.55  
            mano_arriba = False
            manos_abiertas = 0
            manos_cerradas = 0

            for puntos_mano in todas_las_manos:
                cy = puntos_mano[9][2]
                
                if cy < zona_cara_y_max:
                    mano_arriba = True
                
                dedos = self.escanear_dedos_activos(puntos_mano)
                if sum(dedos) >= 4:
                    manos_abiertas += 1
                elif sum(dedos) <= 2:
                    manos_cerradas += 1

            if mano_arriba and manos_abiertas == 1 and manos_cerradas == 1:
                self.tolerancia_combo = 20
                return True

        if self.tolerancia_combo > 0:
            self.tolerancia_combo -= 1
            return True

        return False