"""
utils.py — Funciones auxiliares del proyecto
Autor: Alexander Gallegos — UADY FC 2026
"""
from datetime import datetime
from pathlib import Path


def extraer_fecha_safe(nombre_safe: str) -> str:
    """
    Extrae la fecha de captura del nombre del archivo .SAFE.

    Ejemplo:
        S2B_MSIL2A_20220511T160829_... → '2022-05-11'
    """
    try:
        partes = Path(nombre_safe).name.split("_")
        fecha_raw = partes[2][:8]  # '20220511'
        return datetime.strptime(fecha_raw, "%Y%m%d").strftime("%Y-%m-%d")
    except (IndexError, ValueError):
        return "fecha-desconocida"


def imprimir_resumen(info: dict, fecha: str) -> None:
    """
    Imprime un resumen formateado de la detección en consola.

    Args:
        info:  dict retornado por afai.resumen_deteccion()
        fecha: Fecha de la imagen
    """
    sep = "─" * 48
    print(f"\n{sep}")
    print(f"  DETECCIÓN DE SARGAZO — {fecha}")
    print(sep)
    print(f"  Umbral Otsu       : {info['umbral_otsu']:.6f}")
    print(f"  Píxeles de agua   : {info['pixeles_agua']:,}")
    print(f"  Píxeles sargazo   : {info['pixeles_sargazo']:,}")
    print(f"  Área detectada    : {info['area_km2']:.2f} km²")
    print(f"  Cobertura         : {info['cobertura_pct']:.2f}% del área marina")
    print(f"  AFAI min/max      : {info['afai_min']:.4f} / {info['afai_max']:.4f}")
    print(f"  AFAI promedio     : {info['afai_media']:.6f}")
    print(sep + "\n")


def validar_ruta(ruta: str, descripcion: str = "Ruta") -> Path:
    """
    Verifica que una ruta existe y lanza error descriptivo si no.

    Args:
        ruta:        Ruta a validar
        descripcion: Nombre descriptivo para el mensaje de error
    Returns:
        Path validado
    """
    p = Path(ruta)
    if not p.exists():
        raise FileNotFoundError(
            f"{descripcion} no encontrada: {ruta}\n"
            "Verifica que el archivo .SAFE esté descomprimido en data/raw/"
        )
    return 