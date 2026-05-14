# Parámetros del puerto
NUM_MUELLES = 3
NUM_REMOLCADORES = 1

# Llegada de barcos (exponencial, λ = 8 horas → media 8 horas)
MEDIA_LLEGADA_HORAS = 8  # 1/λ = 8 horas
TASA_LLEGADA = 1 / MEDIA_LLEGADA_HORAS  # λ = 0.125 barcos/hora

# Tamaños de barcos
TAMAÑOS = ['pequeño', 'mediano', 'grande']
PROBABILIDADES_TAMAÑO = [0.25, 0.25, 0.5]

# Tiempo de carga (distribución normal)
MEDIA_CARGA = {
    'pequeño': 9,
    'mediano': 12,
    'grande': 18
}
VARIANZA_CARGA = {
    'pequeño': 1,
    'mediano': 2,
    'grande': 3
}

# Asistencia del remolcador (exponencial)
# - Aproximar barco al muelle: λ = 2 horas → media = 0.5 horas (30 min)
MEDIA_ASISTENCIA_LLEGADA_HORAS = 0.5
TASA_ASISTENCIA_LLEGADA = 1 / MEDIA_ASISTENCIA_LLEGADA_HORAS

# - Retirar barco del muelle: λ = 1 hora → media = 1 hora
MEDIA_ASISTENCIA_SALIDA_HORAS = 1
TASA_ASISTENCIA_SALIDA = 1 / MEDIA_ASISTENCIA_SALIDA_HORAS

# - Traslado vacío del remolcador: λ = 15 minutos = 0.25 horas
MEDIA_TRASLADO_VACIO_HORAS = 0.25
TASA_TRASLADO_VACIO = 1 / MEDIA_TRASLADO_VACIO_HORAS

# Duración de la simulación (en horas)
HORAS_SIMULACION = 8760  # 1 año

# Número de réplicas para obtener resultados estadísticos
NUM_REPLICAS = 30
