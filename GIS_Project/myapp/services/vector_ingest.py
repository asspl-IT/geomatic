import os
import subprocess
import uuid
from django.conf import settings
from django.db import connection

def ingest_vector(file_path):
    """
    Ingest vector (SHP or GeoJSON) into PostGIS
    """

    base = os.path.splitext(os.path.basename(file_path))[0].lower()
    table_name = f"layer_{base}_{uuid.uuid4().hex[:8]}"

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

        # Safe default
        "-t_srs", "EPSG:4326"
    ]

    subprocess.check_call(ogr_cmd)

    with connection.cursor() as cursor:
        cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        count = cursor.fetchone()[0]

    return table_name, {
        "feature_count": count
    }
