import os
import subprocess
from django.conf import settings

POTREE_EXE = r"C:\PotreeConverter_windows_x64\PotreeConverter.exe"

def ingest_lidar(file_path, project_id, layer_id):
    """
    Convert LAS/LAZ to Potree format
    """

    out_dir = os.path.join(
        settings.MEDIA_ROOT,
        "potree",
        f"project_{project_id}",
        f"layer_{layer_id}"
    )

    os.makedirs(out_dir, exist_ok=True)

    cmd = [
        POTREE_EXE,
        file_path,
        "-o", out_dir,
        "--generate-page", "index",
        "--encoding", "BROTLI"
    ]

    subprocess.check_call(cmd)

    return {
        "viewer": "potree",
        "file_path": out_dir
    }
