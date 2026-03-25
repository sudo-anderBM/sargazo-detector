"""
visualize.py — Visualización de resultados AFAI
Autor: Alexander Gallegos — UADY FC 2026
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pathlib import Path


def mapa_afai(afai: np.ndarray,
              mascara: np.ndarray,
              area_km2: float,
              fecha: str = "2022-05-11",
              guardar_en: str = None) -> None:
    """
    Genera figura con dos paneles:
      - Izquierda: mapa de calor AFAI continuo
      - Derecha:   máscara binaria de sargazo detectado

    Args:
        afai:      Array AFAI filtrado (con NaN en no-agua)
        mascara:   Array booleano de sargazo
        area_km2:  Área detectada en km²
        fecha:     Fecha de la imagen para el título
        guardar_en: Ruta donde guardar el PNG (None = solo mostrar)
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 7))
    fig.patch.set_facecolor("#0d1b2a")

    for ax in axes:
        ax.set_facecolor("#0d1b2a")
        ax.axis("off")

    # Panel 1 — Índice AFAI continuo
    im = axes[0].imshow(
        afai,
        cmap="RdYlGn",
        vmin=-0.05,
        vmax=0.05,
        interpolation="nearest"
    )
    axes[0].set_title(
        f"Índice AFAI — {fecha}",
        color="white", fontsize=14, pad=12, fontweight="bold"
    )
    cbar = plt.colorbar(im, ax=axes[0], fraction=0.046, pad=0.04)
    cbar.set_label("AFAI", color="white", fontsize=11)
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="white", fontsize=9)

    # Panel 2 — Máscara binaria
    cmap_sarg = mcolors.ListedColormap(["#0a2540", "#c0392b"])
    axes[1].imshow(
        mascara.astype(np.uint8),
        cmap=cmap_sarg,
        vmin=0, vmax=1,
        interpolation="nearest"
    )
    axes[1].set_title(
        f"Sargazo detectado — {area_km2:.1f} km²",
        color="white", fontsize=14, pad=12, fontweight="bold"
    )

    # Leyenda manual panel 2
    from matplotlib.patches import Patch
    leyenda = [
        Patch(color="#0a2540", label="Océano / sin dato"),
        Patch(color="#c0392b", label=f"Sargazo ({area_km2:.1f} km²)"),
    ]
    axes[1].legend(
        handles=leyenda,
        loc="lower right",
        fontsize=10,
        framealpha=0.6,
        facecolor="#0d1b2a",
        labelcolor="white"
    )

    plt.suptitle(
        "Detección de Sargazo — Costa de Quintana Roo, México",
        color="white", fontsize=16, fontweight="bold", y=1.01
    )
    plt.tight_layout()

    if guardar_en:
        Path(guardar_en).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(guardar_en, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        print(f"  ✓ Mapa guardado en: {guardar_en}")

    plt.show()


def mapa_comparacion(afai_sin_filtro: np.ndarray,
                      afai_filtrado: np.ndarray,
                      fecha: str = "2022-05-11",
                      guardar_en: str = None) -> None:
    """
    Comparación visual: AFAI sin filtro SCL vs con filtro SCL.
    Útil para demostrar el valor del filtrado de tierra/nubes.
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 7))
    fig.patch.set_facecolor("#0d1b2a")

    titulos = [
        "Sin filtro SCL\n(incluye tierra y vegetación)",
        "Con filtro SCL\n(solo píxeles de agua)",
    ]
    datos = [afai_sin_filtro, afai_filtrado]

    for ax, dato, titulo in zip(axes, datos, titulos):
        ax.set_facecolor("#0d1b2a")
        ax.axis("off")
        im = ax.imshow(dato, cmap="RdYlGn", vmin=-0.05, vmax=0.05)
        ax.set_title(titulo, color="white", fontsize=13, pad=12)
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04).ax.yaxis.set_tick_params(color="white")

    plt.suptitle(
        f"Efecto del filtro SCL — {fecha}",
        color="white", fontsize=15, fontweight="bold"
    )
    plt.tight_layout()

    if guardar_en:
        plt.savefig(guardar_en, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        print(f"  ✓ Comparación guardada en: {guardar_en}")

    plt.show()
