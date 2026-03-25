"""
loader.py — Carga y prepara bandas espectrales de Sentinel-2 L2A
Autor: Alexander Gallegos — UADY FC 2026
"""
import rasterio
import numpy as np
from pathlib import Path


def cargar_banda(ruta: str) -> tuple[np.ndarray, dict]:
    """
    Lee una banda satelital .jp2 y devuelve el array y metadata.

    Args:
        ruta: Ruta al archivo .jp2
    Returns:
        array: Datos como numpy float32
        meta:  Metadata geoespacial (CRS, transform, bounds)
    """
    with rasterio.open(ruta) as src:
        array = src.read(1).astype(np.float32)
        meta  = src.meta.copy()
    return array, meta


def normalizar(banda: np.ndarray) -> np.ndarray:
    """
    Convierte reflectancia x10000 (enteros Sentinel-2) a [0, 1].
    Marca píxeles sin dato (<=0) como NaN para excluirlos del análisis.
    """
    banda = np.where(banda <= 0, np.nan, banda)
    return banda / 10_000.0


def cargar_sentinel2(carpeta_r20m: str) -> dict:
    """
    Carga B04, B8A, B11 y SCL desde la carpeta R20m de un producto .SAFE.

    Args:
        carpeta_r20m: Ruta a la carpeta R20m dentro del .SAFE
    Returns:
        dict con claves B4, B8A, B11, SCL y meta
    """
    carpeta = Path(carpeta_r20m)

    codigos = {
        "B4":  "B04",
        "B8A": "B8A",
        "B11": "B11",
        "SCL": "SCL",
    }

    bandas = {}
    meta   = None

    for clave, codigo in codigos.items():
        archivos = list(carpeta.glob(f"*_{codigo}_20m.jp2"))
        if not archivos:
            raise FileNotFoundError(
                f"No se encontró banda {codigo} en {carpeta}\n"
                f"Verifica que estás apuntando a la carpeta R20m."
            )
        array, meta = cargar_banda(str(archivos[0]))

        # SCL es máscara entera — no se normaliza
        bandas[clave] = normalizar(array) if clave != "SCL" else array
        print(f"  [OK] {clave:4s} cargada - shape: {array.shape}  "
              f"min: {np.nanmin(array):.1f}  max: {np.nanmax(array):.1f}")

    bandas["meta"] = meta
    return bandas


def obtener_bounds_geograficos(carpeta_r20m: str) -> dict:
    """
    Retorna los límites geográficos de la imagen en coordenadas UTM.

    Returns:
        dict con left, right, top, bottom, crs
    """
    carpeta = Path(carpeta_r20m)
    archivos = list(carpeta.glob("*_B04_20m.jp2"))
    if not archivos:
        raise FileNotFoundError("No se encontró B04 para extraer bounds.")

    with rasterio.open(str(archivos[0])) as src:
        b = src.bounds
        return {
            "left":   b.left,
            "right":  b.right,
            "top":    b.top,
            "bottom": b.bottom,
            "crs":    str(src.crs),
        }
