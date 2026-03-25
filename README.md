# 🌊 Detección de Sargazo con Sentinel-2 y AFAI

Detector de sargazo frente a las costas de Quintana Roo usando imágenes Sentinel-2 y el índice AFAI. 

La idea es simple: procesar datos públicos de satélite para detectar sargazo flotante. La CONABIO-SIMAR hace algo parecido pero con MODIS (1 km de resolución). Nosotros usamos Sentinel-2 (20 m de resolución), así que ves el doble de detalle... y los datos también son gratis.

El 11 de mayo de 2022, el sistema detectó **413.8 km²** de sargazo frente a Cozumel. Aquí está:

![Detección](evidencias/sargazo_20220511.png)

## 🚀 Empezar

### Instalación rápida
```bash
pip install -r requirements.txt
```

### Procesar una imagen
```bash
python -m src.pipeline
```

Eso es. La imagen se procesa, detecta sargazo, y guarda los resultados en JSON.

## 📊 Qué genera

El pipeline hace lo siguiente:

- Calcula el índice AFAI (Algal Floating Algae Index)
- Aplica filtros para eliminar nubes y tierra
- Detecta dónde está el sargazo
- Te dice cuántos km² hay y qué cobertura es

Ejemplo de lo que sale:

```
DETECCIÓN DE SARGAZO COMPLETADA
============================================================
Fecha de imagen:     2022-05-11
Área de sargazo:     413.82 km²
Cobertura:           5.00%
Umbral Otsu:         0.008044
AFAI (min/max):      -0.2274 / 0.4486
============================================================
```

## 🏗️ Cómo está armado

```
src/
├── loader.py        # Lee las bandas Sentinel-2
├── afai.py          # Calcula AFAI y detecta sargazo
├── visualize.py     # Genera los mapas
├── utils.py         # Cosas útiles sin categoría
└── pipeline.py      # Orquesta todo
```

## 🎯 Usando el generador de dataset

Si tienes varias imágenes para procesar:

```bash
python scripts/generar_dataset.py
```

Detecta automáticamente todas las imágenes en `data/raw/`, las procesa, y guarda los resultados organizados por fecha en `data/dataset/`. También puedes hacer cosas como:

```bash
# Reprocesar imágenes ya procesadas
python scripts/generar_dataset.py --forzar

# Cambiar el percentil
python scripts/generar_dataset.py --percentil 90

# Generar visualizaciones (más lento)
python scripts/generar_dataset.py --generar-imagenes
```

Ver `scripts/README_generar_dataset.md` para más detalles.

## 📁 Estructura

```
data/
├── raw/           # Imágenes Sentinel-2 sin procesar
└── dataset/       # Resultados procesados por fecha
     ├── 2022-05-11/
     │   └── resultados.json
     └── 2022-05-12/
         └── resultados.json
```

## 📋 Qué necesitas

- Python 3.8+
- Una imagen Sentinel-2 Level-2A (gratis desde Copernicus)
- Las bandas: B4, B8A, B11 y SCL

## 🔧 Personalizar

Si queres ejecutar el pipeline programáticamente:

```python
from src.pipeline import ejecutar_pipeline

resultado = ejecutar_pipeline(
    ruta_r20m="ruta/a/carpeta/R20m",
    percentil=95.0,
    guardar_json=True
)

# 'resultado' es un dict con toda la info
print(resultado['deteccion']['area_km2'])  # 413.82
```

## 📚 Referencias

- **AFAI**: Wang & Hu (2009) - Índice para detectar algas flotantes
- **Sentinel-2**: ESA - Misión Copernicus (datos públicos)
- **CONABIO-SIMAR**: Monitoreo oficial del sargazo en México
└── pipeline.py    # Pipeline completo
```

## 📈 Algoritmo

1. **Carga**: Bandas B4, B8A, B11 y SCL de Sentinel-2
2. **AFAI**: Cálculo del índice de algas flotantes
3. **Filtros**: Aplicación de máscaras SCL (agua + nubes)
4. **Detección**: Umbralización automática con Otsu
5. **Estadísticas**: Cálculo de área y cobertura

## 🔧 Personalización

```python
from src.pipeline import ejecutar_pipeline

# Ejecutar con parámetros personalizados
resultado = ejecutar_pipeline(
    ruta_r20m="ruta/a/carpeta/R20m",
    percentil=95.0,      # Percentil para Otsu
    guardar_json=True    # Guardar en data/history/
)
```

## 📋 Requisitos

- Python 3.8+
- Datos Sentinel-2 Level-2A (.SAFE)
- Bandas: B4 (665nm), B8A (865nm), B11 (1610nm), SCL

## 📁 Estructura de datos

```
data/
├── raw/           # Imágenes Sentinel-2 .SAFE
└── history/       # Resultados JSON por fecha
```
