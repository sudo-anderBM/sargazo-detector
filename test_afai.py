from src.loader import cargar_sentinel2
from src.afai import calcular_afai, detectar_sargazo, calcular_area_km2
import matplotlib.pyplot as plt
import numpy as np

RUTA_R20M = (
    r"C:\Users\adria\Desktop\Sargazo_Project\data\raw"
    r"\S2B_MSIL2A_20220511T160829_N0510_R140_T16QEJ_20240611T002406.SAFE"
    r"\GRANULE\L2A_T16QEJ_A027050_20220511T162216\IMG_DATA\R20m"
)

print("Cargando bandas...")
bandas = cargar_sentinel2(RUTA_R20M)

print("Calculando AFAI...")
afai = calcular_afai(bandas["B4"], bandas["B8A"], bandas["B11"])

print("Detectando sargazo con umbral Otsu...")
mascara, umbral = detectar_sargazo(afai)
area = calcular_area_km2(mascara)

print(f"\n  Umbral Otsu encontrado: {umbral:.6f}")
print(f"  Área de sargazo detectada: {area:.2f} km²")

print("\nGenerando mapa...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].imshow(afai, cmap="RdYlGn", vmin=-0.05, vmax=0.05)
axes[0].set_title("Índice AFAI — 11 Mayo 2022")
axes[0].axis("off")
plt.colorbar(axes[0].images[0], ax=axes[0], label="AFAI")

axes[1].imshow(mascara, cmap="YlOrRd")
axes[1].set_title(f"Sargazo detectado — {area:.1f} km²")
axes[1].axis("off")

plt.tight_layout()
plt.savefig("data/results/afai_20220511.png", dpi=150, bbox_inches="tight")
print("  Mapa guardado en data/results/afai_20220511.png")
plt.show()