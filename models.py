import random
import math
from config import TAMAÑOS, PROBABILIDADES_TAMAÑO, MEDIA_CARGA, VARIANZA_CARGA


class Barco:
    _contador_ids = 0
    
    def __init__(self, tiempo_llegada):
        Barco._contador_ids += 1
        self.id = Barco._contador_ids
        self.tiempo_llegada = tiempo_llegada
        
        # Determinar tamaño según probabilidades
        self.tamaño = random.choices(TAMAÑOS, PROBABILIDADES_TAMAÑO)[0]
        
        # Generar tiempo de carga según distribución normal
        media = MEDIA_CARGA[self.tamaño]
        varianza = VARIANZA_CARGA[self.tamaño]
        desviacion = math.sqrt(varianza)
        
        # Aseguramos que el tiempo no sea negativo
        self.tiempo_carga = max(0.1, random.gauss(media, desviacion))
        
        # Variables para seguimiento temporal
        self.tiempo_inicio_carga = None
        self.tiempo_fin_carga = None
        self.tiempo_inicio_asistencia_llegada = None
        self.tiempo_fin_asistencia_llegada = None
        self.tiempo_inicio_asistencia_salida = None
        self.tiempo_fin_asistencia_salida = None
        
        # Estado actual
        self.muelle_asignado = None
        self.estado = "esperando"  # esperando, en_remolcador_entrada, cargando, en_remolcador_salida, completado
    
    @property
    def tiempo_espera(self):
        if self.tiempo_inicio_carga is not None:
            return self.tiempo_inicio_carga - self.tiempo_llegada
        return None
    
    @property
    def tiempo_en_sistema(self):
        """Tiempo total desde llegada hasta fin de asistencia de salida"""
        if self.tiempo_fin_asistencia_salida is not None:
            return self.tiempo_fin_asistencia_salida - self.tiempo_llegada
        return None
    
    def __repr__(self):
        return f"Barco({self.id}, {self.tamaño}, llegó en t={self.tiempo_llegada:.2f})"


class EstadisticasSimulacion:
    def __init__(self):
        self.barcos_atendidos = []
        self.tiempos_espera = []
        self.tiempos_sistema = []
        self.utilizacion_muelles = []
        self.utilizacion_remolcador = None
        self.numero_barcos_en_cola_por_momento = []
        
    def agregar_barco(self, barco):
        self.barcos_atendidos.append(barco)
        if barco.tiempo_espera is not None:
            self.tiempos_espera.append(barco.tiempo_espera)
        if barco.tiempo_en_sistema is not None:
            self.tiempos_sistema.append(barco.tiempo_en_sistema)
    
    @property
    def tiempo_promedio_espera(self):
        if not self.tiempos_espera:
            return 0
        return sum(self.tiempos_espera) / len(self.tiempos_espera)
    
    @property
    def tiempo_promedio_sistema(self):
        if not self.tiempos_sistema:
            return 0
        return sum(self.tiempos_sistema) / len(self.tiempos_sistema)
    
    @property
    def total_barcos_atendidos(self):
        return len(self.barcos_atendidos)