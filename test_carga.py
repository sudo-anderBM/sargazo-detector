from src.loader import cargar_sentinel2

RUTA_R20M = (
    r"C:\Users\adria\Desktop\Sargazo_Project\data\raw"
    r"\S2B_MSIL2A_20220511T160829_N0510_R140_T16QEJ_20240611T002406.SAFE"
    r"\GRANULE\L2A_T16QEJ_A027050_20220511T162216\IMG_DATA\R20m"
)

print("Cargando bandas Sentinel-2...")
bandas = cargar_sentinel2(RUTA_R20M)

print(f"\nResumen:")
print(f"  Shape imagen: {bandas['B4'].shape}")
print(f"  B4  min/max: {bandas['B4'].min():.4f} / {bandas['B4'].max():.4f}")
print(f"  B8A min/max: {bandas['B8A'].min():.4f} / {bandas['B8A'].max():.4f}")
print(f"  B11 min/max: {bandas['B11'].min():.4f} / {bandas['B11'].max():.4f}")
print(f"\nTodo listo para calcular AFAI!")