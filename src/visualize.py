"""
visualize.py - Visualizacion profesional de resultados AFAI
Autor: Alexander Gallegos - UADY FC 2026

Mejoras implementadas:
- Colormaps cientificos (viridis, plasma) para mejor percepcion
- Normalizacion automatica basada en percentiles
- Overlay semi-transparente para mascara de sargazo
- Tema profesional con mejor contraste
- Informacion detallada en titulos y leyendas
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pathlib import Path
import scipy.ndimage as ndi


def mapa_afai_profesional(afai: np.ndarray,
                         mascara: np.ndarray,
                         area_km2: float,
                         fecha: str = "2022-05-11",
                         guardar_en: str = None) -> None:
    """
    Mapa profesional mejorado para deteccion de sargazo.

    MEJORAS CLAVE:
    - Normalizacion centrada en 0 (mejor interpretacion cientifica)
    - Mejor contraste visual (TwoSlopeNorm)
    - Overlay mas claro con borde blanco
    - Eliminacion visual de ruido (NaN)
    - Clasificacion de nivel (BAJO/MEDIO/ALTO)

    Args:
        afai: Array AFAI (con NaN en zonas no validas)
        mascara: Mascara booleana de sargazo
        area_km2: Area detectada
        fecha: Fecha de la imagen
        guardar_en: Ruta de guardado (opcional)
    """

    # ---------------------------
    # CONFIGURACIÓN VISUAL
    # ---------------------------
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 10))
    fig.patch.set_facecolor('#1a1a1a')

    # ---------------------------
    # NORMALIZACIÓN INTELIGENTE
    # ---------------------------
    afai_valid = afai[~np.isnan(afai)]

    if len(afai_valid) > 0:
        vmin = np.percentile(afai_valid, 2)
        vmax = np.percentile(afai_valid, 98)
        if vmax - vmin < 1e-3:
            vmin, vmax = -0.05, 0.05
    else:
        vmin, vmax = -0.05, 0.05

    # Normalizacion centrada en 0 (CLAVE para interpretacion)
    norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)

    # ---------------------------
    # COLORMAP PROFESIONAL
    # ---------------------------
    cmap = plt.cm.coolwarm.copy()
    cmap.set_bad(color='#111111')  # zonas NaN oscuras

    im = ax.imshow(afai, cmap=cmap, norm=norm, alpha=0.85)

    # ---------------------------
    # OVERLAY DE SARGAZO MEJORADO
    # ---------------------------
    mascara_rgba = np.zeros((*mascara.shape, 4))

    # Rojo fuerte para sargazo
    mascara_rgba[mascara] = [1, 0, 0, 0.85]

    # Borde blanco para definición (MUY IMPORTANTE visualmente)
    borde = ndi.binary_dilation(mascara) ^ mascara
    mascara_rgba[borde] = [1, 1, 1, 1]

    ax.imshow(mascara_rgba, interpolation='nearest')

    ax.axis('off')

    # ---------------------------
    # COLORBAR
    # ---------------------------
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Indice AFAI', fontsize=12, fontweight='bold')

    # ---------------------------
    # CLASIFICACION DE RIESGO
    # ---------------------------
    if area_km2 > 300:
        nivel = "ALTO"
        color_nivel = "red"
    elif area_km2 > 100:
        nivel = "MEDIO"
        color_nivel = "orange"
    else:
        nivel = "BAJO"
        color_nivel = "green"

    # ---------------------------
    # TÍTULOS
    # ---------------------------
    ax.set_title(f"DETECCION DE SARGAZO - {fecha}",
                 fontsize=16, fontweight='bold')

    ax.text(0.5, 0.02,
            f"Area: {area_km2:.1f} km² | Rango AFAI: [{vmin:.3f}, {vmax:.3f}]",
            transform=ax.transAxes,
            ha='center',
            fontsize=11,
            style='italic')

    # ---------------------------
    # INFO TÉCNICA
    # ---------------------------
    info = """AFAI (Wang & Hu, 2009)
Sentinel-2 | 20m
Umbral: percentil 95"""

    ax.text(0.02, 0.98, info,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment='top',
            bbox=dict(boxstyle="round",
                      facecolor="#2a2a2a",
                      alpha=0.8))

    # ---------------------------
    # NIVEL DE ALERTA (PRODUCTO REAL)
    # ---------------------------
    ax.text(0.98, 0.02,
            f"NIVEL: {nivel}",
            transform=ax.transAxes,
            ha='right',
            fontsize=12,
            color='white',
            bbox=dict(facecolor=color_nivel, alpha=0.9))

    plt.tight_layout()

    # ---------------------------
    # GUARDADO
    # ---------------------------
    if guardar_en:
        Path(guardar_en).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(guardar_en,
                    dpi=400,
                    bbox_inches='tight',
                    facecolor=fig.get_facecolor())
        print(f"[OK] Mapa guardado en: {guardar_en}")

    plt.show()


def mapa_afai(afai: np.ndarray,
              mascara: np.ndarray,
              area_km2: float,
              fecha: str = "2022-05-11",
              guardar_en: str = None) -> None:
    """
    Función original mejorada - mantiene compatibilidad con pipeline existente.
    Ahora usa mapa_afai_profesional() internamente.
    """
    mapa_afai_profesional(afai, mascara, area_km2, fecha, guardar_en)


def mapa_comparacion_mejorado(afai_sin_filtro: np.ndarray,
                             afai_filtrado: np.ndarray,
                             fecha: str = "2022-05-11",
                             guardar_en: str = None) -> None:
    """
    Comparacion profesional: AFAI sin filtro vs con filtro SCL.

    Mejoras:
    - Colormap plasma para mejor contraste
    - Normalizacion automatica por percentiles
    - Informacion detallada sobre el efecto del filtro
    """
    plt.style.use('dark_background')
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig.patch.set_facecolor('#1a1a1a')

    titulos = [
        "AFAI sin filtro SCL\n(incluye tierra, vegetacion y nubes)",
        "AFAI con filtro SCL\n(solo pixeles de agua)"
    ]
    datos = [afai_sin_filtro, afai_filtrado]

    # Calcular estadísticas para cada panel
    stats = []
    for dato in datos:
        dato_valid = dato[~np.isnan(dato)]
        if len(dato_valid) > 0:
            vmin = np.percentile(dato_valid, 1)
            vmax = np.percentile(dato_valid, 99)
            media = np.mean(dato_valid)
            stats.append((vmin, vmax, media))
        else:
            stats.append((-0.05, 0.05, 0.0))

    for ax, dato, titulo, (vmin, vmax, media) in zip(axes, datos, titulos, stats):
        ax.set_facecolor('#1a1a1a')
        ax.axis('off')

        # Usar colormap plasma para mejor percepción de diferencias
        im = ax.imshow(dato, cmap='plasma', vmin=vmin, vmax=vmax,
                       interpolation='bilinear', alpha=0.9)

        ax.set_title(titulo, fontsize=13, fontweight='bold', pad=15)

        # Barra de color
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, shrink=0.8)
        cbar.set_label('AFAI', fontsize=10, labelpad=5)
        cbar.ax.tick_params(labelsize=9)

        # Información estadística
        info_stats = f'Promedio: {media:.4f}\nRango: [{vmin:.3f}, {vmax:.3f}]'
        ax.text(0.02, 0.02, info_stats, transform=ax.transAxes,
                fontsize=9, color='white', alpha=0.9,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="#333333", alpha=0.8))

    plt.suptitle(f'Efecto del Filtro SCL en AFAI - {fecha}',
                 fontsize=16, fontweight='bold', y=0.98)

    # Información adicional
    explicacion = """El filtro SCL elimina pixeles de tierra, vegetacion y nubes,
dejando solo el agua para analisis preciso de sargazo."""
    fig.text(0.5, 0.02, explicacion, ha='center', fontsize=10,
             style='italic', alpha=0.8)

    plt.tight_layout()

    if guardar_en:
        Path(guardar_en).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(guardar_en, dpi=300, bbox_inches='tight',
                    facecolor=fig.get_facecolor(), edgecolor='none')
        print(f'  [OK] Comparación mejorada guardada en: {guardar_en}')

    plt.show()


def mapa_comparacion(afai_sin_filtro: np.ndarray,
                      afai_filtrado: np.ndarray,
                      fecha: str = "2022-05-11",
                      guardar_en: str = None) -> None:
    """
    Función original - mantiene compatibilidad.
    Ahora usa mapa_comparacion_mejorado() internamente.
    """
    mapa_comparacion_mejorado(afai_sin_filtro, afai_filtrado, fecha, guardar_en)


def crear_visualizacion_completa(afai_sin_filtro: np.ndarray,
                                 afai_filtrado: np.ndarray,
                                 mascara: np.ndarray,
                                 area_km2: float,
                                 fecha: str = "2022-05-11",
                                 directorio_salida: str = "resultados") -> None:
    """
    Genera suite completa de visualizaciones profesionales.

    Crea:
    1. Mapa de detección final (AFAI + overlay de sargazo)
    2. Comparación antes/después del filtro SCL
    3. Guarda todo en directorio organizado

    Args:
        afai_sin_filtro: AFAI antes del filtro SCL
        afai_filtrado: AFAI después del filtro SCL
        mascara: Máscara binaria de sargazo detectado
        area_km2: Área de sargazo en km²
        fecha: Fecha de la imagen
        directorio_salida: Directorio donde guardar imágenes
    """
    Path(directorio_salida).mkdir(parents=True, exist_ok=True)

    # 1. Mapa de detección final
    ruta_deteccion = f"{directorio_salida}/deteccion_sargazo_{fecha}.png"
    mapa_afai_profesional(afai_filtrado, mascara, area_km2, fecha, ruta_deteccion)

    # 2. Comparación de filtros
    ruta_comparacion = f"{directorio_salida}/comparacion_filtros_{fecha}.png"
    mapa_comparacion_mejorado(afai_sin_filtro, afai_filtrado, fecha, ruta_comparacion)

    print(f"\n=== VISUALIZACIONES COMPLETAS GENERADAS ===")
    print(f"📊 Detección final: {ruta_deteccion}")
    print(f"🔍 Comparación filtros: {ruta_comparacion}")
    print(f"📁 Directorio: {directorio_salida}")
    print("=" * 50)