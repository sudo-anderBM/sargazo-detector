"""
test_visualizaciones.py — Prueba de las visualizaciones mejoradas
Carga datos del pipeline y genera mapas profesionales
"""
import json
import numpy as np
from pathlib import Path
from datetime import datetime

# Importar módulos del proyecto
from src.loader import cargar_sentinel2
from src.afai import (calcular_afai, aplicar_mascara_agua,
                     aplicar_mascara_nubes, detectar_sargazo)
from src.visualize import (mapa_afai_profesional, mapa_comparacion_mejorado,
                          crear_visualizacion_completa)


def cargar_datos_pipeline():
    """Carga datos usando el mismo pipeline que funciona"""
    RUTA_R20M = (
        r"C:\Users\adria\Desktop\Sargazo_Project\data\raw"
        r"\S2B_MSIL2A_20220511T160829_N0510_R140_T16QEJ_20240611T002406.SAFE"
        r"\GRANULE\L2A_T16QEJ_A027050_20220511T162216\IMG_DATA\R20m"
    )

    print("Cargando datos del pipeline...")

    # 1. Cargar bandas
    bandas = cargar_sentinel2(RUTA_R20M)

    # 2. Calcular AFAI sin filtro
    afai_sin_filtro = calcular_afai(bandas["B4"], bandas["B8A"], bandas["B11"])

    # 3. Aplicar filtros
    afai_filtrado = aplicar_mascara_agua(afai_sin_filtro, bandas["SCL"])
    afai_filtrado = aplicar_mascara_nubes(afai_filtrado, bandas["SCL"])

    # 4. Detectar sargazo
    mascara, umbral = detectar_sargazo(afai_filtrado, percentil=95.0)

    # 5. Calcular área
    pixeles_sargazo = np.sum(mascara)
    area_km2 = pixeles_sargazo * (20 * 20) / 1_000_000  # 20m resolución

    print(f"   Área detectada: {area_km2:.2f} km²")
    print(f"   Umbral usado: {umbral:.6f}")
    return afai_sin_filtro, afai_filtrado, mascara, area_km2


def probar_visualizaciones():
    """Prueba todas las visualizaciones mejoradas con submuestreo para velocidad"""
    print("\n=== PRUEBA DE VISUALIZACIONES MEJORADAS ===\n")

    # Cargar datos
    afai_sin_filtro, afai_filtrado, mascara, area_km2 = cargar_datos_pipeline()

    # Submuestreo para pruebas rápidas (cada 10 píxeles)
    factor = 10
    afai_sin_filtro_small = afai_sin_filtro[::factor, ::factor]
    afai_filtrado_small = afai_filtrado[::factor, ::factor]
    mascara_small = mascara[::factor, ::factor]

    # Ajustar área proporcionalmente
    area_km2_small = area_km2 / (factor ** 2)

    fecha = "2022-05-11"

    print(f"Usando submuestreo {factor}x{factor} para pruebas rápidas")
    print(f"Área ajustada: {area_km2_small:.2f} km²")

    # 1. Mapa de detección profesional
    print("\n1. Generando mapa de detección profesional...")
    mapa_afai_profesional(afai_filtrado_small, mascara_small, area_km2_small, fecha,
                         guardar_en="resultados/deteccion_profesional.png")

    # 2. Mapa de comparación mejorado
    print("2. Generando comparación antes/después...")
    mapa_comparacion_mejorado(afai_sin_filtro_small, afai_filtrado_small, fecha,
                             guardar_en="resultados/comparacion_mejorada.png")

    # 3. Suite completa de visualizaciones
    print("3. Generando suite completa...")
    crear_visualizacion_completa(afai_sin_filtro_small, afai_filtrado_small, mascara_small,
                                area_km2_small, fecha, "resultados")

    print("\n✅ Todas las visualizaciones generadas exitosamente!")
    print("📁 Revisa la carpeta 'resultados/' para ver los mapas")


if __name__ == "__main__":
    probar_visualizaciones()