# Generador de Dataset Temporal - Detección de Sargazo

Este script procesa automáticamente múltiples imágenes Sentinel-2 para generar un dataset temporal organizado de detección de sargazo.

## Uso Básico

```bash
# Procesar todas las imágenes en data/raw/
python scripts/generar_dataset.py

# Procesar con opciones personalizadas
python scripts/generar_dataset.py --percentil 90 --generar-imagenes

# Forzar reprocesamiento de imágenes ya procesadas
python scripts/generar_dataset.py --forzar
```

## Opciones

- `--raw, -r`: Directorio con datos crudos (default: `data/raw`)
- `--dataset, -d`: Directorio de salida (default: `data/dataset`)
- `--percentil, -p`: Percentil para detección (default: 95.0)
- `--generar-imagenes, -i`: Generar visualizaciones (lento, mucha memoria)
- `--forzar, -f`: Forzar reprocesamiento de fechas existentes

## Estructura de Salida

```
data/dataset/
├── 2022-05-11/
│   └── resultados.json
├── 2022-05-12/
│   └── resultados.json
└── ...
```

## Archivo resultados.json

Cada procesamiento genera un archivo JSON con:

```json
{
  "metadata": {
    "fecha_ejecucion": "2026-03-24T22:31:10.124585",
    "fecha_imagen": "2022-05-11",
    "ruta_procesada": "...",
    "percentil_usado": 95.0,
    "generar_imagenes": false
  },
  "deteccion": {
    "area_km2": 413.82,
    "pixeles_sargazo": 1034545,
    "pixeles_agua_total": 20693720,
    "cobertura_porcentaje": 5.0,
    "umbral_otsu": 0.008044
  },
  "estadisticas_afai": {
    "min": -0.22736,
    "max": 0.448627,
    "media": -0.001259
  }
}
```

## Optimizaciones

- **Sin imágenes**: Por defecto no genera visualizaciones para procesamiento rápido
- **Limpieza de memoria**: Libera memoria intermedia con `gc.collect()`
- **Detección automática**: Encuentra carpetas válidas Sentinel-2 automáticamente
- **Manejo de errores**: Continúa procesando aunque una imagen falle

## Estructura Esperada de Datos

```
data/raw/
├── imagen1.SAFE/
│   └── GRANULE/
│       └── */IMG_DATA/R20m/
├── imagen2.SAFE/
│   └── GRANULE/
│       └── */IMG_DATA/R20m/
└── ...
```

## Dependencias

Requiere los módulos del proyecto:
- `src.loader`
- `src.afai`
- `src.utils`

## Notas

- Las imágenes Sentinel-2 son muy pesadas (~500MB cada una)
- El procesamiento puede tomar varios minutos por imagen
- Se recomienda `--generar-imagenes` solo para análisis específicos