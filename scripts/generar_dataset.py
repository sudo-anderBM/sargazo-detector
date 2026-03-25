"""
generar_dataset.py — Generador de dataset temporal para detección de sargazo
Procesa múltiples imágenes Sentinel-2 y guarda resultados organizados por fecha

Autor: Alexander Gallegos — UADY FC 2026
"""
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import gc

# Agregar el directorio raíz del proyecto al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar módulos del proyecto
from src.loader import cargar_sentinel2
from src.afai import (calcular_afai, aplicar_mascara_agua,
                     aplicar_mascara_nubes, detectar_sargazo,
                     resumen_deteccion, calcular_area_km2)
from src.utils import extraer_fecha_safe


def detectar_carpetas_validas(directorio_raw: Path) -> list[Path]:
    """
    Detecta automáticamente carpetas válidas que contienen datos Sentinel-2.

    Una carpeta es válida si:
    - Es un directorio
    - Contiene archivos .SAFE o subcarpetas con estructura Sentinel-2
    - Tiene la ruta R20m/ accesible

    Args:
        directorio_raw: Directorio data/raw/

    Returns:
        Lista de rutas válidas ordenadas por fecha
    """
    carpetas_validas = []

    if not directorio_raw.exists():
        print(f"[ERROR] Directorio {directorio_raw} no existe")
        return []

    for item in directorio_raw.iterdir():
        if not item.is_dir():
            continue

        # Buscar ruta R20m
        ruta_r20m = item / "GRANULE" / "*" / "IMG_DATA" / "R20m"

        # Verificar si existe la ruta (usando glob para el comodín)
        posibles_r20m = list(item.glob("GRANULE/*/IMG_DATA/R20m"))
        if posibles_r20m:
            ruta_r20m = posibles_r20m[0]
            if ruta_r20m.exists():
                carpetas_validas.append((item, ruta_r20m))

    # Ordenar por fecha extraída del nombre
    def extraer_fecha_para_ordenado(carpeta_info):
        carpeta, _ = carpeta_info
        fecha = extraer_fecha_safe(str(carpeta))
        try:
            return datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            return datetime.min  # Fechas inválidas al final

    carpetas_validas.sort(key=extraer_fecha_para_ordenado)

    return [ruta_r20m for _, ruta_r20m in carpetas_validas]


def guardar_resultado_dataset(resultado: dict, directorio_salida: Path) -> str:
    """
    Guarda el resultado en formato JSON en un directorio personalizado.

    Args:
        resultado: dict con los resultados
        directorio_salida: Directorio donde guardar (ej: data/dataset/2022-05-11/)

    Returns:
        ruta del archivo guardado
    """
    directorio_salida.mkdir(parents=True, exist_ok=True)

    # Nombre del archivo: resultados.json
    filename = "resultados.json"
    filepath = directorio_salida / filename

    # Guardar como JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    return str(filepath)


def ejecutar_pipeline_dataset(ruta_r20m: str,
                             percentil: float = 95.0,
                             directorio_salida: Optional[Path] = None,
                             generar_imagenes: bool = False) -> dict:
    """
    Versión optimizada del pipeline para procesamiento de dataset.

    Optimizaciones:
    - Control de generación de imágenes
    - Limpieza de memoria intermedia
    - Guardado en directorio personalizado

    Args:
        ruta_r20m: Ruta a la carpeta R20m dentro del .SAFE
        percentil: Percentil para detección de sargazo (default 95.0)
        directorio_salida: Directorio donde guardar resultados (None = no guardar)
        generar_imagenes: Si generar visualizaciones (False para optimización)

    Returns:
        dict con todos los resultados del procesamiento
    """
    # 1. Cargar bandas Sentinel-2
    try:
        bandas = cargar_sentinel2(ruta_r20m)
    except Exception as e:
        raise RuntimeError(f"Error cargando bandas: {e}")

    # 2. Extraer fecha de la imagen
    ruta_safe = Path(ruta_r20m).parent.parent.parent.parent
    fecha_imagen = extraer_fecha_safe(str(ruta_safe.name))

    # 3. Calcular índice AFAI
    afai_raw = calcular_afai(bandas["B4"], bandas["B8A"], bandas["B11"])

    # 4. Aplicar filtros SCL (agua + nubes)
    afai_agua = aplicar_mascara_agua(afai_raw, bandas["SCL"])
    afai_limpio = aplicar_mascara_nubes(afai_agua, bandas["SCL"])

    # Limpiar memoria intermedia
    del afai_raw, afai_agua, bandas
    gc.collect()

    # 5. Detectar sargazo con Otsu
    mascara, umbral = detectar_sargazo(afai_limpio, percentil=percentil)

    # 6. Calcular estadísticas completas
    info = resumen_deteccion(afai_limpio, mascara, umbral)

    # 7. Crear resultado estructurado
    resultado = {
        "metadata": {
            "fecha_ejecucion": datetime.now().isoformat(),
            "fecha_imagen": fecha_imagen,
            "ruta_procesada": str(ruta_r20m),
            "percentil_usado": percentil,
            "generar_imagenes": generar_imagenes
        },
        "deteccion": {
            "area_km2": round(info["area_km2"], 2),
            "pixeles_sargazo": int(info["pixeles_sargazo"]),
            "pixeles_agua_total": int(info["pixeles_agua"]),
            "cobertura_porcentaje": round(info["cobertura_pct"], 2),
            "umbral_otsu": round(info["umbral_otsu"], 6)
        },
        "estadisticas_afai": {
            "min": round(float(info["afai_min"]), 6),
            "max": round(float(info["afai_max"]), 6),
            "media": round(float(info["afai_media"]), 6)
        }
    }

    # 8. Guardar resultado en JSON si se especifica directorio
    if directorio_salida:
        filepath = guardar_resultado_dataset(resultado, directorio_salida)

        # 9. Generar visualizaciones si se solicita (opcional)
        if generar_imagenes:
            try:
                from src.visualize import crear_visualizacion_completa

                # Nota: Para generar visualizaciones necesitamos recargar algunos datos
                # Esta es una limitación - las imágenes requieren datos que limpiamos
                print("   [INFO] Generación de imágenes requiere datos completos - omitiendo para optimización")
                print("   [INFO] Use generar_imagenes=False para procesamiento rápido")

            except ImportError:
                print("   [WARNING] Módulo de visualización no disponible")

    # Limpiar memoria final
    del afai_limpio, mascara, info
    gc.collect()

    return resultado


def procesar_dataset(directorio_raw: str = "data/raw",
                    directorio_dataset: str = "data/dataset",
                    percentil: float = 95.0,
                    generar_imagenes: bool = False,
                    forzar_reprocesamiento: bool = False) -> None:
    """
    Procesa todas las imágenes Sentinel-2 en data/raw/ y genera dataset organizado.

    Args:
        directorio_raw: Directorio con datos crudos
        directorio_dataset: Directorio donde guardar resultados organizados
        percentil: Percentil para detección de sargazo
        generar_imagenes: Si generar visualizaciones (lento, usa mucha memoria)
        forzar_reprocesamiento: Si reprocesar fechas ya existentes
    """
    print("=" * 70)
    print("  GENERADOR DE DATASET TEMPORAL - DETECCIÓN DE SARGAZO")
    print("=" * 70)
    print(f"Directorio raw: {directorio_raw}")
    print(f"Directorio dataset: {directorio_dataset}")
    print(f"Percentil: {percentil}")
    print(f"Generar imágenes: {generar_imagenes}")
    print(f"Forzar reprocesamiento: {forzar_reprocesamiento}")
    print("=" * 70)

    # Convertir a Path
    dir_raw = Path(directorio_raw)
    dir_dataset = Path(directorio_dataset)

    # 1. Detectar carpetas válidas
    print("\n[1/3] Detectando carpetas válidas...")
    carpetas_r20m = detectar_carpetas_validas(dir_raw)

    if not carpetas_r20m:
        print("[ERROR] No se encontraron carpetas válidas en data/raw/")
        return

    print(f"   ✓ Encontradas {len(carpetas_r20m)} carpetas válidas")

    # 2. Procesar cada carpeta
    print("\n[2/3] Procesando imágenes...")
    procesadas = 0
    errores = 0
    omitidas = 0

    for i, ruta_r20m in enumerate(carpetas_r20m, 1):
        # Extraer fecha para el directorio de salida
        ruta_safe = Path(ruta_r20m).parent.parent.parent.parent
        fecha = extraer_fecha_safe(str(ruta_safe.name))

        print(f"\n  [{i}/{len(carpetas_r20m)}] Procesando: {fecha}")
        print(f"    Ruta: {ruta_r20m.name}")

        # Verificar si ya existe y no forzar reprocesamiento
        dir_salida = dir_dataset / fecha
        archivo_resultado = dir_salida / "resultados.json"

        if archivo_resultado.exists() and not forzar_reprocesamiento:
            print("    [SKIP] Ya procesado (use --forzar para reprocesar)")
            omitidas += 1
            continue

        try:
            # Procesar imagen
            resultado = ejecutar_pipeline_dataset(
                str(ruta_r20m),
                percentil=percentil,
                directorio_salida=dir_salida,
                generar_imagenes=generar_imagenes
            )

            # Mostrar resumen
            area = resultado['deteccion']['area_km2']
            cobertura = resultado['deteccion']['cobertura_porcentaje']

            print("    [OK] Procesamiento completado")
            print(".2f")
            print(".2f")
            procesadas += 1

        except Exception as e:
            print(f"    [ERROR] {str(e)}")
            errores += 1
            continue

    # 3. Resumen final
    print(f"\n[3/3] Resumen del procesamiento:")
    print(f"   ✓ Procesadas: {procesadas}")
    print(f"   ⚠ Omitidas: {omitidas}")
    print(f"   ✗ Errores: {errores}")
    print(f"   📁 Resultados guardados en: {dir_dataset}")

    if errores > 0:
        print(f"\n[INFO] {errores} imágenes tuvieron errores pero el proceso continuó")

    print("\n" + "=" * 70)
    print("  DATASET GENERADO EXITOSAMENTE")
    print("=" * 70)


def main():
    """
    Función principal para ejecución desde línea de comandos.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Generador de dataset temporal para detección de sargazo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python scripts/generar_dataset.py
  python scripts/generar_dataset.py --generar-imagenes
  python scripts/generar_dataset.py --forzar
  python scripts/generar_dataset.py --percentil 90
        """
    )

    parser.add_argument(
        "--raw", "-r",
        default="data/raw",
        help="Directorio con datos crudos (default: data/raw)"
    )

    parser.add_argument(
        "--dataset", "-d",
        default="data/dataset",
        help="Directorio de salida (default: data/dataset)"
    )

    parser.add_argument(
        "--percentil", "-p",
        type=float,
        default=95.0,
        help="Percentil para detección (default: 95.0)"
    )

    parser.add_argument(
        "--generar-imagenes", "-i",
        action="store_true",
        help="Generar visualizaciones (lento, mucha memoria)"
    )

    parser.add_argument(
        "--forzar", "-f",
        action="store_true",
        help="Forzar reprocesamiento de fechas existentes"
    )

    args = parser.parse_args()

    # Ejecutar procesamiento
    procesar_dataset(
        directorio_raw=args.raw,
        directorio_dataset=args.dataset,
        percentil=args.percentil,
        generar_imagenes=args.generar_imagenes,
        forzar_reprocesamiento=args.forzar
    )


if __name__ == "__main__":
    main()