"""
loader.py — Carga y prepara las bandas de Sentinel-2
"""
import rasterio
import numpy as np
from pathlib import Path


def cargar_banda(ruta: str) -> tuple[np.ndarray, dict]:
    """Lee una banda .jp2 y devuelve array y metadata."""
    with rasterio.open(ruta) as src:
        array = src.read(1).astype(np.float32)
        meta = src.meta
    return array, meta


def normalizar(banda: np.ndarray) -> np.ndarray:
    """Convierte de reflectancia x10000 a 0-1, marca nodata como nan."""
    banda = np.where(banda <= 0, np.nan, banda)
    return banda / 10000.0


def cargar_sentinel2(carpeta_r20m: str) -> dict:
    """
    Carga B04, B8A, B11 y SCL desde la carpeta R20m de Sentinel-2 L2A.

    Args:
        carpeta_r20m: Ruta a la carpeta R20m dentro del .SAFE
    Returns:
        dict con B4, B8A, B11, SCL normalizadas y metadata
    """
    carpeta = Path(carpeta_r20m)

    nombres = {
        "B4":  "B04",
        "B8A": "B8A",
        "B11": "B11",
        "SCL": "SCL",
    }

    bandas = {}
    for clave, codigo in nombres.items():
        archivos = list(carpeta.glob(f"*_{codigo}_20m.jp2"))
        if not archivos:
            raise FileNotFoundError(f"No se encontró banda {codigo} en {carpeta}")
        array, meta = cargar_banda(str(archivos[0]))
        if clave != "SCL":
            bandas[clave] = normalizar(array)
        else:
            bandas[clave] = array  # SCL no se normaliza
        print(f"  ✓ {clave} cargada — shape: {array.shape}")

    bandas["meta"] = meta
    return bandas