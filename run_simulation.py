from config import HORAS_SIMULACION, NUM_REPLICAS
from harbor import ejecutar_simulacion
from statistics import resumen_estadistico, imprimir_resumen


def ejecutar_replicas(num_replicas, duracion_horas, semilla_base=42):
    resultados = []
    
    print(f"Iniciando {num_replicas} réplicas de simulación...")
    print(f"Duración de cada simulación: {duracion_horas} horas")
    print("-" * 50)
    
    for i in range(num_replicas):
        # Usar semilla diferente para cada réplica
        semilla = semilla_base + i
        print(f"Ejecutando réplica {i+1}/{num_replicas} (semilla={semilla})...")
        
        try:
            estadisticas = ejecutar_simulacion(duracion_horas, semilla)
            resultados.append(estadisticas)
            
            # Reporte breve de esta réplica
            if estadisticas.tiempos_espera:
                print(f"  ✅ Completada: {estadisticas.total_barcos_atendidos} barcos, "
                      f"espera promedio={estadisticas.tiempo_promedio_espera:.2f}h")
            else:
                print(f"  ⚠️  Réplica sin barcos atendidos")
                
        except Exception as e:
            print(f"  ❌ Error en réplica {i+1}: {e}")
            continue
    
    print("-" * 50)
    print(f"Simulaciones completadas: {len(resultados)} réplicas exitosas")
    
    return resultados


def main():
    print("=" * 70)
    print("SIMULACIÓN DE EVENTOS DISCRETOS - PUERTO SOBRECARGADO")
    print("=" * 70)
    print(f"\nConfiguración:")
    print(f"  - Muelles: 3")
    print(f"  - Remolcadores: 1")
    print(f"  - Tasa de llegada: 1 barco cada {1/0.125:.0f} horas")
    print(f"  - Duración por simulación: {HORAS_SIMULACION} horas ({HORAS_SIMULACION/24:.1f} días)")
    print(f"  - Número de réplicas: {NUM_REPLICAS}")
    
    # Ejecutar réplicas
    resultados = ejecutar_replicas(NUM_REPLICAS, HORAS_SIMULACION)
    
    if not resultados:
        print("\n❌ No se obtuvieron resultados válidos.")
        return
    
    # Generar resumen estadístico
    resumen = resumen_estadistico(resultados)
    imprimir_resumen(resumen)
    
    # Guardar resultados en archivo (opcional)
    guardar_resultados(resumen, "resultados_simulacion.txt")
    
    print("\n✨ Simulación completada exitosamente.")


def guardar_resultados(resumen, archivo):
    """
    Guarda los resultados en un archivo de texto.
    """
    try:
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("RESULTADOS DE SIMULACIÓN - PUERTO SOBRECARGADO\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"Número de réplicas: {resumen['num_replicas']}\n\n")
            
            # Tiempo de espera
            media, error, inf, sup = resumen['tiempo_espera']
            f.write("TIEMPO PROMEDIO DE ESPERA:\n")
            f.write(f"  Media: {media:.4f} horas\n")
            f.write(f"  Intervalo 95%: [{inf:.4f}, {sup:.4f}]\n\n")
            
            # Tiempo en sistema
            media, error, inf, sup = resumen['tiempo_sistema']
            f.write("TIEMPO PROMEDIO EN SISTEMA:\n")
            f.write(f"  Media: {media:.4f} horas\n")
            f.write(f"  Intervalo 95%: [{inf:.4f}, {sup:.4f}]\n\n")
            
            # Barcos atendidos
            media, error, inf, sup = resumen['barcos_atendidos']
            f.write("BARCOS ATENDIDOS:\n")
            f.write(f"  Media: {media:.1f}\n")
            f.write(f"  Intervalo 95%: [{inf:.1f}, {sup:.1f}]\n\n")
            
            # Datos brutos
            f.write("DATOS BRUTOS POR RÉPLICA:\n")
            f.write("Réplica, Tiempo Espera Prom, Barcos Atendidos\n")
            for i, (te, ba) in enumerate(zip(resumen['raw_tiempos_espera'], resumen['raw_barcos_atendidos'])):
                f.write(f"{i+1}, {te:.4f}, {ba}\n")
        
        print(f"\n📄 Resultados guardados en '{archivo}'")
    except Exception as e:
        print(f"\n⚠️  No se pudo guardar el archivo: {e}")


if __name__ == "__main__":
    main()