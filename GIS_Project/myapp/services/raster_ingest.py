import subprocess
import os


def ingest_raster(file_path, output_dir):
    cog_path = os.path.join(output_dir, "raster_cog.tif")

    cmd = [
        "gdal_translate",
        file_path,
        cog_path,
        "-of", "COG"
    ]

    subprocess.check_call(cmd)

    return cog_path
