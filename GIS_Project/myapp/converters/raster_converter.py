# def convert_raster_to_tiles(raster_file_path):
#     # Dummy implementation (placeholder)
#     return {"message": "Raster converted to tiles", "path": raster_file_path}

# utils/raster_converter.py
import os
import shutil
import subprocess
import sys

def convert_raster_to_tiles(raster_path, out_folder=None, zoom_levels=None):
    """
    Convert GeoTIFF/JPG/other raster to slippy-map tiles using gdal2tiles.
    Returns path to tiles folder.
    zoom_levels: str like "0-5" or None for defaults.
    """
    if not raster_path or not os.path.exists(raster_path):
        raise FileNotFoundError(f"Raster not found: {raster_path}")

    if out_folder is None:
        base = os.path.splitext(os.path.basename(raster_path))[0]
        out_folder = os.path.join(os.path.dirname(raster_path), f"{base}_tiles")

    # ensure clean output folder
    if os.path.exists(out_folder):
        # we keep existing tiles if you want, else uncomment remove line
        # shutil.rmtree(out_folder)
        pass
    else:
        os.makedirs(out_folder, exist_ok=True)

    # Try calling gdal2tiles.py; depending on platform it may be on PATH as gdal2tiles.py
    cmd = [sys.executable, "-m", "gdal2tiles", raster_path, out_folder]
    if zoom_levels:
        cmd.extend(["-z", zoom_levels])

    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        # fallback: maybe gdal2tiles.py is a standalone script on PATH
        try:
            cmd2 = ["gdal2tiles.py", raster_path, out_folder]
            if zoom_levels:
                cmd2.extend(["-z", zoom_levels])
            subprocess.check_call(cmd2)
        except Exception as e2:
            raise RuntimeError(f"gdal2tiles failed: {e} / {e2}")

    return out_folder

