"""
afai.py — Cálculo del índice AFAI y detección de sargazo
Referencia: Wang & Hu, 2009 — Remote Sensing of Environment
            doi: 10.1016/j.rse.2009.02.003
Autor: Alexander Gallegos — UADY FC 2026
"""
import numpy as np
from skimage.filters import threshold_otsu


# Longitudes de onda centrales de Sentinel-2 (nanómetros)
LAMBDA_RED  = 665   # B04
LAMBDA_NIR  = 865   # B8A
LAMBDA_SWIR = 1610  # B11

# Clases SCL (Scene Classification Layer) de Sentinel-2
SCL_AGUA = 6   # Agua superficial
SCL_NUBES_ALTAS   = 9
SCL_NUBES_MEDIAS  = 8
SCL_NUBES_BAJAS   = 7
SCL_SOMBRA_NUBES  = 3


def calcular_afai(B4: np.ndarray,
                  B8A: np.ndarray,
                  B11: np.ndarray) -> np.ndarray:
    """
    Calcula el Alternative Floating Algae Index (AFAI).

    Fórmula:
        B8A* = B4 + (B11 - B4) * (λNIR - λRed) / (λSWIR - λRed)
        AFAI = B8A - B8A*

    Args:
        B4:  Banda roja normalizada  [0, 1]
        B8A: Banda NIR normalizada   [0, 1]
        B11: Banda SWIR normalizada  [0, 1]
    Returns:
        Array 2D con valores AFAI (positivo = posible sargazo)
    """
    factor   = (LAMBDA_NIR - LAMBDA_RED) / (LAMBDA_SWIR - LAMBDA_RED)
    B8A_prima = B4 + (B11 - B4) * factor
    return B8A - B8A_prima


def aplicar_mascara_agua(afai: np.ndarray,
                          SCL:  np.ndarray) -> np.ndarray:
    """
    Filtra el AFAI dejando SOLO píxeles clasificados como agua.
    Elimina tierra, vegetación terrestre, nubes y sombras.

    La banda SCL de Sentinel-2 L2A asigna clase 6 al agua superficial.
    Sin este filtro, la vegetación terrestre (NIR alto) genera
    falsos positivos que contaminan la detección de sargazo.

    Args:
        afai: Array AFAI sin filtrar
        SCL:  Banda de clasificación de escena (enteros)
    Returns:
        AFAI con NaN en todo lo que no sea agua
    """
    mascara_agua = SCL == SCL_AGUA
    return np.where(mascara_agua, afai, np.nan)


def aplicar_mascara_nubes(afai: np.ndarray,
                           SCL:  np.ndarray) -> np.ndarray:
    """
    Adicional: elimina también los píxeles afectados por nubes y sombras.
    Se puede encadenar con aplicar_mascara_agua.
    """
    nubes = np.isin(SCL, [SCL_NUBES_ALTAS, SCL_NUBES_MEDIAS,
                           SCL_NUBES_BAJAS, SCL_SOMBRA_NUBES])
    return np.where(nubes, np.nan, afai)


def detectar_sargazo(afai: np.ndarray,
                     percentil: float = 95.0) -> tuple[np.ndarray, float]:
    """
    Detecta sargazo usando percentil alto sobre píxeles de agua.
    El sargazo ocupa una fracción pequeña del océano — los valores
    más altos de AFAI corresponden a concentraciones reales de alga.

    Args:
        afai:      Array AFAI filtrado (solo agua)
        percentil: Porcentaje de píxeles considerados sargazo (default 95)
    Returns:
        mascara: Array booleano (True = sargazo)
        umbral:  Valor de corte utilizado
    """
    datos_validos = afai[~np.isnan(afai)]

    if datos_validos.size == 0:
        raise ValueError("No hay píxeles válidos de agua.")

    # Solo el X% superior de AFAI en zona marina = sargazo
    umbral = float(np.percentile(datos_validos, percentil))

    # Además exigimos que sea positivo (condición física del sargazo)
    umbral = max(umbral, 0.0)

    mascara = (afai > umbral) & (~np.isnan(afai))
    return mascara, umbral


def calcular_area_km2(mascara: np.ndarray,
                       resolucion_m: float = 20.0) -> float:
    """
    Estima el área de sargazo detectado en km².

    Args:
        mascara:      Array booleano de sargazo
        resolucion_m: Resolución espacial en metros (20m para B11 Sentinel-2)
    Returns:
        Área en km²
    """
    pixeles  = int(np.sum(mascara))
    area_m2  = pixeles * (resolucion_m ** 2)
    area_km2 = area_m2 / 1_000_000
    return round(area_km2, 2)


def resumen_deteccion(afai_filtrado: np.ndarray,
                       mascara: np.ndarray,
                       umbral: float) -> dict:
    """
    Genera un resumen estadístico de la detección para reportes.

    Returns:
        dict con métricas clave
    """
    datos = afai_filtrado[~np.isnan(afai_filtrado)]
    return {
        "umbral_otsu":       round(umbral, 6),
        "afai_min":          round(float(np.nanmin(afai_filtrado)), 6),
        "afai_max":          round(float(np.nanmax(afai_filtrado)), 6),
        "afai_media":        round(float(np.nanmean(afai_filtrado)), 6),
        "pixeles_agua":      int(datos.size),
        "pixeles_sargazo":   int(np.sum(mascara)),
        "area_km2":          calcular_area_km2(mascara),
        "cobertura_pct":     round(np.sum(mascara) / datos.size * 100, 2),
    }