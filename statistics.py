import math
import numpy as np
from config import NUM_REPLICAS


def calcular_intervalo_confianza(datos, confianza=0.95):
    n = len(datos)
    if n == 0:
        return (0, 0, 0, 0)
    
    media = np.mean(datos)
    desviacion = np.std(datos, ddof=1)  # ddof=1 para desviación muestral
    
    # Valor crítico de t-student para n-1 grados de libertad
    from scipy import stats
    t_critico = stats.t.ppf((1 + confianza) / 2, n - 1)
    
    margen_error = t_critico * (desviacion / math.sqrt(n))
    
    return (media, margen_error, media - margen_error, media + margen_error)


def resumen_estadistico(resultados_replicas):
    tiempos_espera_promedio = [r.tiempo_promedio_espera for r in resultados_replicas if r.tiempos_espera]
    tiempos_sistema_promedio = [r.tiempo_promedio_sistema for r in resultados_replicas if r.tiempos_sistema]
    barcos_atendidos = [r.total_barcos_atendidos for r in resultados_replicas]
    utilizacion_muelles = [r.utilizacion_muelles for r in resultados_replicas if r.utilizacion_muelles is not None]
    utilizacion_remolcador = [r.utilizacion_remolcador for r in resultados_replicas if r.utilizacion_remolcador is not None]
    
    resumen = {
        'num_replicas': len(resultados_replicas),
        'tiempo_espera': calcular_intervalo_confianza(tiempos_espera_promedio),
        'tiempo_sistema': calcular_intervalo_confianza(tiempos_sistema_promedio),
        'barcos_atendidos': calcular_intervalo_confianza(barcos_atendidos),
        'utilizacion_muelles': calcular_intervalo_confianza(utilizacion_muelles),
        'utilizacion_remolcador': calcular_intervalo_confianza(utilizacion_remolcador),
    }
    
    # Datos brutos para análisis adicional
    resumen['raw_tiempos_espera'] = tiempos_espera_promedio
    resumen['raw_barcos_atendidos'] = barcos_atendidos
    
    return resumen


def imprimir_resumen(resumen):
    print("\n" + "=" * 70)
    print("RESUMEN DE SIMULACIÓN - PUERTO SOBRECARGADO")
    print("=" * 70)
    
    print(f"\n📊 Réplicas ejecutadas: {resumen['num_replicas']}")
    
    # Tiempo de espera
    media, error, inf, sup = resumen['tiempo_espera']
    print(f"\n⏱️  Tiempo promedio de ESPERA (llegada → inicio carga):")
    print(f"   Media: {media:.4f} horas ({media*60:.2f} minutos)")
    print(f"   Intervalo 95%: [{inf:.4f}, {sup:.4f}] horas")
    print(f"   Margen de error: ±{error:.4f} horas")
    
    # Tiempo en sistema
    media, error, inf, sup = resumen['tiempo_sistema']
    print(f"\n⏱️  Tiempo promedio en SISTEMA:")
    print(f"   Media: {media:.4f} horas ({media*60:.2f} minutos)")
    print(f"   Intervalo 95%: [{inf:.4f}, {sup:.4f}] horas")
    
    # Barcos atendidos
    media, error, inf, sup = resumen['barcos_atendidos']
    print(f"\n🚢 Barcos atendidos (promedio por simulación):")
    print(f"   Media: {media:.1f}")
    print(f"   Intervalo 95%: [{inf:.1f}, {sup:.1f}]")
    
    # Utilización de muelles
    if resumen['utilizacion_muelles'][0] is not None:
        media, error, inf, sup = resumen['utilizacion_muelles']
        print(f"\n⚓ Utilización promedio de muelles:")
        print(f"   Media: {media:.2%}")
        print(f"   Intervalo 95%: [{inf:.2%}, {sup:.2%}]")
    
    # Utilización de remolcador
    if resumen['utilizacion_remolcador'][0] is not None:
        media, error, inf, sup = resumen['utilizacion_remolcador']
        print(f"\n🛥️  Utilización promedio del remolcador:")
        print(f"   Media: {media:.2%}")
        print(f"   Intervalo 95%: [{inf:.2%}, {sup:.2%}]")
    
    print("\n" + "=" * 70)