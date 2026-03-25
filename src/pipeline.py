"""
pipeline.py — Pipeline completo de detección de sargazo
Ejecuta el flujo completo: carga → procesamiento → detección → resultados
"""
import json
from datetime import datetime
from pathlib import Path

from .loader import cargar_sentinel2
from .afai import (calcular_afai, aplicar_mascara_agua,
                   aplicar_mascara_nubes, detectar_sargazo,
                   resumen_deteccion, calcular_area_km2)
from .utils import extraer_fecha_safe


def ejecutar_pipeline(ruta_r20m: str, percentil: float = 95.0, guardar_json: bool = True) -> dict:
    """
    Ejecuta el pipeline completo de detección de sargazo.

    Args:
        ruta_r20m: Ruta a la carpeta R20m dentro del .SAFE
        percentil: Percentil para detección de sargazo (default 95.0)
        guardar_json: Si guardar resultado en data/history/

    Returns:
        dict con todos los resultados del procesamiento
    """
    print("Iniciando pipeline de detección de sargazo...")
    print(f"   Ruta procesada: {ruta_r20m}")

    # 1. Cargar bandas Sentinel-2
    print("\n[1/7] Cargando bandas Sentinel-2...")
    try:
        bandas = cargar_sentinel2(ruta_r20m)
        print("   ✓ Bandas cargadas exitosamente")
    except Exception as e:
        raise RuntimeError(f"Error cargando bandas: {e}")

    # 2. Extraer fecha de la imagen
    ruta_safe = Path(ruta_r20m).parent.parent.parent
    fecha_imagen = extraer_fecha_safe(str(ruta_safe))
    print(f"   ✓ Fecha de imagen: {fecha_imagen}")

    # 3. Calcular índice AFAI
    print("\n[2/7] Calculando índice AFAI...")
    afai_raw = calcular_afai(bandas["B4"], bandas["B8A"], bandas["B11"])
    print("   ✓ AFAI calculado")

    # 4. Aplicar filtros SCL (agua + nubes)
    print("\n[3/7] Aplicando filtros SCL...")
    afai_agua = aplicar_mascara_agua(afai_raw, bandas["SCL"])
    afai_limpio = aplicar_mascara_nubes(afai_agua, bandas["SCL"])
    print("   ✓ Filtros aplicados (tierra, vegetación, nubes eliminadas)")

    # 5. Detectar sargazo con Otsu
    print("\n[4/7] Detectando sargazo...")
    mascara, umbral = detectar_sargazo(afai_limpio, percentil=percentil)
    print(f"   ✓ Umbral calculado: {umbral:.6f}")

    # 6. Calcular estadísticas completas
    print("\n[5/7] Calculando estadísticas...")
    info = resumen_deteccion(afai_limpio, mascara, umbral)
    print(f"   ✓ Área detectada: {info['area_km2']:.2f} km²")
    print(f"   ✓ Cobertura: {info['cobertura_pct']:.2f}%")

    # 7. Imprimir resumen en consola
    print("\n" + "="*60)
    print("           DETECCIÓN DE SARGAZO COMPLETADA")
    print("="*60)
    print(f"Fecha de imagen:     {fecha_imagen}")
    print(f"Fecha de ejecución:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Área de sargazo:     {info['area_km2']:.2f} km²")
    print(f"Píxeles sargazo:     {info['pixeles_sargazo']:,}")
    print(f"Píxeles agua total:  {info['pixeles_agua']:,}")
    print(f"Cobertura:           {info['cobertura_pct']:.2f}%")
    print(f"Umbral Otsu:         {info['umbral_otsu']:.6f}")
    print(f"AFAI (min/max):      {info['afai_min']:.4f} / {info['afai_max']:.4f}")
    print(f"AFAI promedio:       {info['afai_media']:.6f}")
    print("="*60)

    # 8. Crear resultado estructurado
    resultado = {
        "metadata": {
            "fecha_ejecucion": datetime.now().isoformat(),
            "fecha_imagen": fecha_imagen,
            "ruta_procesada": str(ruta_r20m),
            "percentil_usado": percentil
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

    # 9. Guardar resultado en JSON (opcional)
    if guardar_json:
        print("\n[6/7] Guardando resultado...")
        filepath = guardar_resultado_json(resultado)
        print(f"   ✓ Resultado guardado en: {filepath}")

    # 10. Retornar resultado completo
    print("\n[7/7] Pipeline completado exitosamente!")
    return resultado


def guardar_resultado_json(resultado: dict) -> str:
    """
    Guarda el resultado en formato JSON en data/history/

    Args:
        resultado: dict con los resultados

    Returns:
        ruta del archivo guardado
    """
    # Crear directorio si no existe
    output_dir = Path("data/history")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Nombre del archivo: fecha_ejecucion.json
    fecha = resultado["metadata"]["fecha_ejecucion"][:10]  # YYYY-MM-DD
    filename = f"{fecha}.json"
    filepath = output_dir / filename

    # Guardar como JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    return str(filepath)


def cargar_resultado_json(fecha: str) -> dict:
    """
    Carga un resultado guardado por fecha.

    Args:
        fecha: Fecha en formato YYYY-MM-DD

    Returns:
        dict con el resultado cargado
    """
    filepath = Path("data/history") / f"{fecha}.json"
    if not filepath.exists():
        raise FileNotFoundError(f"No se encontró resultado para fecha {fecha}")

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


if __name__ == "__main__":
    # Ejemplo de uso con la imagen que tienes
    RUTA_R20M = (
        r"C:\Users\adria\Desktop\Sargazo_Project\data\raw"
        r"\S2B_MSIL2A_20220511T160829_N0510_R140_T16QEJ_20240611T002406.SAFE"
        r"\GRANULE\L2A_T16QEJ_A027050_20220511T162216\IMG_DATA\R20m"
    )

    try:
        # Ejecutar pipeline
        resultado = ejecutar_pipeline(RUTA_R20M, percentil=95.0, guardar_json=True)

        # Mostrar resultado final
        print("\nRESULTADO FINAL:")
        print(f"   Área de sargazo: {resultado['deteccion']['area_km2']} km²")
        print(f"   Cobertura: {resultado['deteccion']['cobertura_porcentaje']}%")
        print(f"   Umbral usado: {resultado['deteccion']['umbral_otsu']}")

    except Exception as e:
        print(f"Error ejecutando pipeline: {e}")
        import traceback
        traceback.print_exc()
