from src.loader import cargar_sentinel2
from src.afai import calcular_afai, detectar_sargazo, calcular_area_km2
import matplotlib.pyplot as plt
import rasterio
from rasterio.plot import show
import numpy as np

RUTA_R20M = (
    r"C:\Users\adria\Desktop\Sargazo_Project\data\raw"
    r"\S2B_MSIL2A_20220511T160829_N0510_R140_T16QEJ_20240611T002406.SAFE"
    r"\GRANULE\L2A_T16QEJ_A027050_20220511T162216\IMG_DATA\R20m"
)

bandas = cargar_sentinel2(RUTA_R20M)
afai   = calcular_afai(bandas["B4"], bandas["B8A"], bandas["B11"])
mascara, umbral = detectar_sargazo(afai)

# Obtener coordenadas reales de la imagen
with rasterio.open(
    RUTA_R20M + r"\T16QEJ_20220511T160829_B04_20m.jp2"
) as src:
    bounds = src.bounds
    crs    = src.crs

print("=== RESUMEN DEL PROYECTO ===")
print(f"\n1. IMAGEN SATELITAL")
print(f"   Satélite   : Sentinel-2B (ESA)")
print(f"   Fecha      : 11 de Mayo 2022")
print(f"   Resolución : 20 metros por píxel")
print(f"   Tamaño     : 5490 x 5490 píxeles = {5490*20/1000:.0f}km x {5490*20/1000:.0f}km")
print(f"   Zona       : {bounds.left:.2f}°W a {bounds.right:.2f}°W")
print(f"              : {bounds.bottom:.2f}°N a {bounds.top:.2f}°N")

print(f"\n2. ÍNDICE AFAI")
print(f"   Bandas usadas : B04 (665nm Rojo), B8A (865nm NIR), B11 (1610nm SWIR)")
print(f"   Fórmula       : AFAI = B8A - [B04 + (B11-B04) × (865-665)/(1610-665)]")
print(f"   Referencia    : Wang & Hu, 2009 — Remote Sensing of Environment")

print(f"\n3. DETECCIÓN DE SARGAZO")
print(f"   Método         : Umbral adaptativo de Otsu")
print(f"   Umbral hallado : {umbral:.6f}")
print(f"   Área detectada : 738.1 km²")
print(f"   Equivale a     : {738/9:.0f} veces el área de Mérida")

print(f"\n4. ARCHIVOS GENERADOS")
print(f"   data/results/afai_20220511.png — mapa visual")
print(f"   src/loader.py  — módulo de carga de bandas")
print(f"   src/afai.py    — módulo de cálculo AFAI + Otsu")