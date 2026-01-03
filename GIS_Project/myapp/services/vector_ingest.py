import os
import subprocess
from django.conf import settings
from django.db import connection

def ingest_vector(file_path):
    """
    Ingest vector (SHP or GeoJSON) into PostGIS
    """
    table_name = "layer_" + os.path.splitext(os.path.basename(file_path))[0].lower()

    ogr_cmd = [
        "ogr2ogr",
        "-f", "PostgreSQL",
        f"PG:dbname={settings.DATABASES['default']['NAME']} "
        f"user={settings.DATABASES['default']['USER']} "
        f"password={settings.DATABASES['default']['PASSWORD']} "
        f"host={settings.DATABASES['default']['HOST']} "
        f"port={settings.DATABASES['default']['PORT']}",

        file_path,

        "-nln", table_name,
        "-overwrite",

        "-lco", "GEOMETRY_NAME=geom",
        "-lco", "FID=id",

        # 🔑 FORCE CRS IF UNKNOWN
        "-a_srs", "EPSG:4326"
    ]

    subprocess.check_call(ogr_cmd)

    # get feature count
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        count = cursor.fetchone()[0]

    return table_name, {
        "feature_count": count
    }
