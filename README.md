# Sargazo Detector

Detección de sargazo en costas yucatecas con imágenes del satélite Sentinel-2.  
 — Ingeniería en Computación, UADY 2026.
 
La CONABIO-SIMAR — la institución que monitorea el sargazo en México — también usa el índice AFAI. La diferencia es que ellos trabajan con MODIS a 1 km de resolución. Nosotros usamos Sentinel-2 a 20 m. Cincuenta veces más detalle, con datos igualmente gratuitos.
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

Algoritmo
```
AFAI = B8A − [B04 + (B11 − B04) × (865−665)/(1610−665)]
```

- **B04** — Banda roja (665 nm)
- **B8A** — Infrarrojo cercano (865 nm)  
- **B11** — Infrarrojo de onda corta (1610 nm)

Referencia: Wang & Hu, 2009 — *Remote Sensing of Environment*


¿Funciona nuestro detector?

Procesamos una imagen del 11 de mayo de 2022 sobre el Caribe frente a Cancún. El algoritmo detectó 413.8 km² de sargazo. Aquí comparamos ese resultado con lo que reportaron en tierra ese mismo mes.

El punto de comparación más cercano que encontramos es el reporte de la Red de Monitoreo del Sargazo de Quintana Roo del 7 de mayo: cuatro días antes de nuestra imagen, no es perfecto porque el sargazo se mueve con las corrientes, pero es lo que hay y es suficiente para saber si el detector apunta en la dirección correcta



Hay tres cosas que limitan esta comparación y que vale la pena mencionar sin esconderlas:

Cuatro días de diferencia, el reporte es del 7 de mayo, la imagen del 11. El sargazo puede recorrer bastante distancia en ese tiempo.
Unidades distintas. Nosotros medimos km² en el mar, los reportes cuentan playas, no superficie, no son equivalentes directos.
13% de nubes los píxeles bajo nubes son ciegos para el satélite, el área real detectada probablemente es mayor.
->El siguiente paso lógico sería contactar a la UNAM UMDI Sisal — están en Yucatán y tienen datos de campo reales con coordenadas, con eso sí podríamos calcular métricas de precisión formales.

## Stack


`rasterio` · `numpy` · `scikit-image` · `matplotlib` · `folium`

---

Alexander Gallegos · Facultad de Matemáticas UADY
