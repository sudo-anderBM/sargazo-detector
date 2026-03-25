# 🌊 Detección de Sargazo con Sentinel-2 y AFAI

Sistema completo de detección automática de sargazo en imágenes Sentinel-2 usando el índice AFAI (Algal Floating Algae Index).


Detección de sargazo en costas yucatecas con imágenes del satélite Sentinel-2.  
 — Ingeniería en Computación, UADY 2026.

La CONABIO-SIMAR — la institución que monitorea el sargazo en México — también usa el índice AFAI. La diferencia es que ellos trabajan con MODIS a 1 km de resolución. Nosotros usamos Sentinel-2 a 20 m. Cincuenta veces más detalle, con datos igualmente gratuitos.
---

El proyecto implementa el índice AFAI sobre imágenes reales de la ESA para
detectar manchas de sargazo flotante en el Caribe mexicano. El 11 de mayo
de 2022 se detectaron **413.8 km²** frente a las costas de Quintana Roo.

![Detección](evidencias/sargazo_20220511.png)

![Comparación SCL](evidencias/comparacion_scl.png)


## 🚀 Inicio Rápido

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar pipeline
```bash
python -m src.pipeline
```

## 📊 Resultados

El pipeline genera:
- **Área de sargazo detectada** (km²)
- **Porcentaje de cobertura** sobre agua
- **Estadísticas del índice AFAI**
- **Archivo JSON** con historial en `data/history/`

### Ejemplo de salida:
```
============================================================
           DETECCIÓN DE SARGAZO COMPLETADA
============================================================
Fecha de imagen:     2022-05-11
Fecha de ejecución:  2026-03-24 18:40:10
Área de sargazo:     413.82 km²
Píxeles sargazo:     1,034,545
Píxeles agua total:  20,693,720
Cobertura:           5.00%
Umbral Otsu:         0.008044
AFAI (min/max):      -0.2274 / 0.4486
AFAI promedio:       -0.001259
============================================================
```

## 🏗️ Arquitectura

```
src/
├── __init__.py      # Paquete Python
├── loader.py        # Carga de bandas Sentinel-2
├── afai.py          # Algoritmos AFAI y detección
├── utils.py         # Utilidades
├── visualize.py     # Visualización (opcional)
└── pipeline.py      # Pipeline principal
```

## 🔧 Uso Avanzado

### Ejecutar con parámetros personalizados
```python
from src.pipeline import ejecutar_pipeline

resultado = ejecutar_pipeline(
    ruta_r20m="ruta/a/carpeta/R20m",
    percentil=95.0,      # Percentil para Otsu
    guardar_json=True    # Guardar en data/history/
)
```

### Ejecutar módulo directamente
```bash
python -m src.pipeline
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
├── afai.py        # Cálculo AFAI y detección
├── utils.py       # Utilidades
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
