import simpy
import random
from config import (
    TASA_LLEGADA, TASA_ASISTENCIA_LLEGADA, TASA_ASISTENCIA_SALIDA,
    NUM_MUELLES, NUM_REMOLCADORES
)
from models import Barco, EstadisticasSimulacion


class Puerto:
    """Representa el puerto con sus muelles y remolcador"""
    
    def __init__(self, env):
        self.env = env
        self.muelles = simpy.Resource(env, capacity=NUM_MUELLES)
        self.remolcador = simpy.Resource(env, capacity=NUM_REMOLCADORES)
        
        # Estadísticas
        self.estadisticas = EstadisticasSimulacion()
        
        # Monitoreo de utilización
        self.tiempo_muelles_ocupados = 0
        self.tiempo_remolcador_ocupado = 0
        self.ultima_medicion = 0
    
    def actualizar_utilizacion(self, tiempo_actual):
        """Actualiza los contadores de utilización"""
        delta = tiempo_actual - self.ultima_medicion
        if delta > 0:
            self.tiempo_muelles_ocupados += self.muelles.count * delta
            self.tiempo_remolcador_ocupado += self.remolcador.count * delta
        self.ultima_medicion = tiempo_actual


def proceso_barco(env, puerto, barco):
    """
    Proceso CORREGIDO que maneja el ciclo completo del barco.
    El remolcador se libera después de CADA asistencia.
    """
    
    print(f"[{env.now:.2f}] 🚢 LLEGÓ {barco}")
    
    # ========== PASO 1: Solicitar muelle ==========
    with puerto.muelles.request() as req_muelle:
        # Esperar hasta que haya un muelle disponible
        yield req_muelle
        
        puerto.actualizar_utilizacion(env.now)
        print(f"[{env.now:.2f}] ⚓ {barco} obtuvo un muelle")
        
        # ========== PASO 2: Solicitar remolcador para ASISTENCIA DE LLEGADA ==========
        with puerto.remolcador.request() as req_rem_entrada:
            yield req_rem_entrada
            
            puerto.actualizar_utilizacion(env.now)
            barco.tiempo_inicio_asistencia_llegada = env.now
            
            # Calcular tiempo de espera (desde llegada hasta obtener remolcador)
            tiempo_espera = env.now - barco.tiempo_llegada
            barco.tiempo_inicio_carga = env.now  # La carga empieza después de la asistencia
            
            print(f"[{env.now:.2f}] 🛥️ {barco} OBTUVO REMOLCADOR (entrada) - Esperó {tiempo_espera:.2f}h")
            
            # Asistencia de llegada (remolcador lleva barco al muelle)
            tiempo_asistencia = random.expovariate(TASA_ASISTENCIA_LLEGADA)
            yield env.timeout(tiempo_asistencia)
            
            barco.tiempo_fin_asistencia_llegada = env.now
            print(f"[{env.now:.2f}] 🛥️ {barco} REMOLCADOR ENTRADA COMPLETADA ({tiempo_asistencia:.2f}h)")
        
        # El remolcador se LIBERA automáticamente al salir del with
        print(f"[{env.now:.2f}] 🔓 {barco} REMOLCADOR LIBERADO (entrada completada)")
        
        # ========== PASO 3: CARGA (el barco está solo en el muelle, sin remolcador) ==========
        barco.estado = "cargando"
        print(f"[{env.now:.2f}] 📦 {barco} INICIA CARGA ({barco.tiempo_carga:.2f}h)")
        
        yield env.timeout(barco.tiempo_carga)
        
        barco.tiempo_fin_carga = env.now
        barco.estado = "carga_completada"
        print(f"[{env.now:.2f}] ✅ {barco} TERMINÓ CARGA")
        
        # ========== PASO 4: Solicitar remolcador para ASISTENCIA DE SALIDA ==========
        with puerto.remolcador.request() as req_rem_salida:
            yield req_rem_salida
            
            puerto.actualizar_utilizacion(env.now)
            barco.tiempo_inicio_asistencia_salida = env.now
            
            tiempo_espera_salida = env.now - barco.tiempo_fin_carga
            print(f"[{env.now:.2f}] 🛥️ {barco} OBTUVO REMOLCADOR (salida) - Esperó {tiempo_espera_salida:.2f}h para salir")
            
            # Asistencia de salida
            tiempo_asistencia_salida = random.expovariate(TASA_ASISTENCIA_SALIDA)
            yield env.timeout(tiempo_asistencia_salida)
            
            barco.tiempo_fin_asistencia_salida = env.now
            print(f"[{env.now:.2f}] 🛥️ {barco} REMOLCADOR SALIDA COMPLETADA ({tiempo_asistencia_salida:.2f}h)")
        
        # El remolcador se LIBERA nuevamente
        print(f"[{env.now:.2f}] 🔓 {barco} REMOLCADOR LIBERADO (salida completada)")
        
        # El muelle se libera automáticamente al salir del with externo
        print(f"[{env.now:.2f}] 🔓 {barco} MUELLE LIBERADO")
    
    # ========== REGISTRAR ESTADÍSTICAS ==========
    barco.estado = "completado"
    puerto.estadisticas.agregar_barco(barco)
    
    print(f"[{env.now:.2f}] 📊 {barco} - ESPERA: {barco.tiempo_espera:.2f}h, SISTEMA: {barco.tiempo_en_sistema:.2f}h")
    print("-" * 70)


def generador_barcos(env, puerto):
    """Genera barcos según distribución exponencial"""
    while True:
        tiempo_entre_llegadas = random.expovariate(TASA_LLEGADA)
        yield env.timeout(tiempo_entre_llegadas)
        
        barco = Barco(env.now)
        env.process(proceso_barco(env, puerto, barco))


def ejecutar_simulacion(duracion_horas, semilla=None):
    """
    Ejecuta una simulación completa del puerto.
    
    Args:
        duracion_horas: Duración de la simulación en horas
        semilla: Semilla para el generador aleatorio (opcional)
    
    Returns:
        EstadisticasSimulacion: Objeto con todas las estadísticas
    """
    if semilla is not None:
        random.seed(semilla)
    
    # Crear entorno y puerto
    env = simpy.Environment()
    puerto = Puerto(env)
    
    # Iniciar generador de barcos
    env.process(generador_barcos(env, puerto))
    
    # Ejecutar simulación
    env.run(until=duracion_horas)
    
    # Registrar utilización final
    puerto.actualizar_utilizacion(duracion_horas)
    
    # Calcular utilizaciones promedio
    if duracion_horas > 0:
        puerto.estadisticas.utilizacion_muelles = puerto.tiempo_muelles_ocupados / (NUM_MUELLES * duracion_horas)
        puerto.estadisticas.utilizacion_remolcador = puerto.tiempo_remolcador_ocupado / duracion_horas
    
    return puerto.estadisticas