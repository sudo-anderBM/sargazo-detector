# Sargazo Detector

Detección de sargazo en costas yucatecas con imágenes del satélite Sentinel-2.  
 — Ingeniería en Computación, UADY 2026.


---

El proyecto implementa el índice AFAI sobre imágenes reales de la ESA para
detectar manchas de sargazo flotante en el Caribe mexicano. El 11 de mayo
de 2022 se detectaron **413.8 km²** frente a las costas de Quintana Roo.

![Detección](evidencias/sargazo_20220511.png)

![Comparación SCL](evidencias/comparacion_scl.png)

---

## Cómo correrlo
```bash
conda activate sargazo
python test_afai.py
```

## Stack

`rasterio` · `numpy` · `scikit-image` · `matplotlib` · `folium`

---

Alexander Gallegos · Facultad de Matemáticas UADY
