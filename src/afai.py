"""
afai.py — Cálculo del índice AFAI para detección de sargazo
Paper original: Wang & Hu, 2009 (Remote Sensing of Environment)
"""
import numpy as np
from skimage.filters import threshold_otsu


def calcular_afai(B4: np.ndarray, B8: np.ndarray, B11: np.ndarray) -> np.ndarray:
    """
    Calcula el Alternative Floating Algae Index (AFAI).
    
    Fórmula: AFAI = B8 - B8* 
    donde B8* = B4 + (B11 - B4) * ((λNIR - λRed) / (λSWIR - λRed))
    
    Longitudes de onda Sentinel-2:
        B4  = 665nm  (Rojo)
        B8  = 833nm  (NIR)
        B11 = 1610nm (SWIR)
    
    Args:
        B4:  Banda roja normalizada
        B8:  Banda NIR normalizada  
        B11: Banda SWIR normalizada
    Returns:
        Array 2D con valores AFAI
    """
    lambda_red  = 665
    lambda_nir  = 833
    lambda_swir = 1610

    B8_prima = B4 + (B11 - B4) * (
        (lambda_nir - lambda_red) / (lambda_swir - lambda_red)
    )

    afai = B8 - B8_prima
    return afai


def detectar_sargazo(afai: np.ndarray) -> tuple[np.ndarray, float]:
    """
    Genera máscara binaria de sargazo usando umbral adaptativo de Otsu.
    Esto es lo que diferencia este proyecto de uno básico.
    
    Args:
        afai: Array 2D con valores AFAI
    Returns:
        mascara: Array booleano (True = sargazo)
        umbral:  Valor de corte encontrado automáticamente
    """
    datos_validos = afai[~np.isnan(afai)]
    umbral = threshold_otsu(datos_validos)
    mascara = afai > umbral
    return mascara, umbral


def calcular_area_km2(mascara: np.ndarray, resolucion_m: float = 20.0) -> float:
    """
    Estima el área de sargazo detectado en km².
    
    Args:
        mascara:      Array booleano de sargazo
        resolucion_m: Resolución espacial en metros (20m para B11 Sentinel-2)
    Returns:
        Área en km²
    """
    pixeles = np.sum(mascara)
    area_m2 = pixeles * (resolucion_m ** 2)
    return area_m2 / 1_000_000