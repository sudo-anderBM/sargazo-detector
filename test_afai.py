"""
test_afai.py — Detección completa de sargazo con filtro SCL
Ejecutar: python test_afai.py
"""
from src.loader    import cargar_sentinel2
from src.afai      import (calcular_afai, aplicar_mascara_agua,
                            aplicar_mascara_nubes, detectar_sargazo,
                            resumen_deteccion)
from src.visualize import mapa_afai, mapa_comparacion
from src.utils     import imprimir_resumen

RUTA_R20M = (
    r"C:\Users\adria\Desktop\Sargazo_Project\data\raw"
    r"\S2B_MSIL2A_20220511T160829_N0510_R140_T16QEJ_20240611T002406.SAFE"
    r"\GRANULE\L2A_T16QEJ_A027050_20220511T162216\IMG_DATA\R20m"
)
FECHA = "2022-05-11"

print("=" * 48)
print("  SARGAZO DETECTOR v1.0")
print("  Alexander Gallegos — UADY FC 2026")
print("=" * 48)

# 1. Cargar bandas
print("\n[1/5] Cargando bandas Sentinel-2...")
bandas = cargar_sentinel2(RUTA_R20M)

# 2. Calcular AFAI
print("\n[2/5] Calculando índice AFAI...")
afai_raw = calcular_afai(bandas["B4"], bandas["B8A"], bandas["B11"])

# 3. Aplicar filtros SCL (agua + nubes)
print("\n[3/5] Aplicando filtros SCL...")
afai_agua   = aplicar_mascara_agua(afai_raw, bandas["SCL"])
afai_limpio = aplicar_mascara_nubes(afai_agua, bandas["SCL"])
print("  ✓ Tierra y vegetación eliminadas")
print("  ✓ Nubes y sombras eliminadas")

# 4. Detectar sargazo con Otsu
print("\n[4/5] Detectando sargazo con umbral Otsu...")
mascara, umbral = detectar_sargazo(afai_limpio, percentil=95.0)
info = resumen_deteccion(afai_limpio, mascara, umbral)
imprimir_resumen(info, FECHA)

# 5. Visualizar
print("[5/5] Generando mapas...")
mapa_comparacion(
    afai_raw, afai_limpio,
    fecha=FECHA,
    guardar_en="data/results/comparacion_scl.png"
)
mapa_afai(
    afai_limpio, mascara,
    area_km2=info["area_km2"],
    fecha=FECHA,
    guardar_en="data/results/sargazo_20220511.png"
)