import subprocess
import os
from django.conf import settings

def ingest_raster(file_path):
    output_dir = os.path.dirname(file_path)
    cog_path = os.path.join(output_dir, "raster_cog.tif")

    cmd = [
        "gdal_translate",
        file_path,
        cog_path,
        "-of", "COG"
    ]

    subprocess.check_call(cmd)

    return cog_path, {
        "bbox": None
    }
