import os
import rasterio
import laspy
from django.db import connection


def fetch_geojson_from_table(table_name, limit=500):
    with connection.cursor() as cursor:
        # detect geometry column safely
        cursor.execute("""
            SELECT f_geometry_column
            FROM geometry_columns
            WHERE f_table_name = %s
            LIMIT 1
        """, [table_name])

        row = cursor.fetchone()
        if not row:
            return None

        geom_col = row[0]

        cursor.execute(f"""
            SELECT jsonb_build_object(
                'type','FeatureCollection',
                'features', jsonb_agg(f)
            )
            FROM (
                SELECT jsonb_build_object(
                    'type','Feature',
                    'geometry', ST_AsGeoJSON({geom_col})::jsonb,
                    'properties', to_jsonb(t) - '{geom_col}'
                ) f
                FROM "{table_name}" t
                LIMIT {limit}
            ) q;
        """)

        return cursor.fetchone()[0]


def raster_preview(file_path):
    with rasterio.open(file_path) as ds:
        return {
            "type": "raster",
            "crs": ds.crs.to_string() if ds.crs else None,
            "bounds": {
                "xmin": ds.bounds.left,
                "ymin": ds.bounds.bottom,
                "xmax": ds.bounds.right,
                "ymax": ds.bounds.top,
            },
            "width": ds.width,
            "height": ds.height,
            "bands": ds.count,
        }


def las_preview(file_path):
    las = laspy.read(file_path)
    h = las.header
    return {
        "type": "lidar",
        "points": h.point_count,
        "bounds": {
            "xmin": h.mins[0],
            "ymin": h.mins[1],
            "zmin": h.mins[2],
            "xmax": h.maxs[0],
            "ymax": h.maxs[1],
            "zmax": h.maxs[2],
        }
    }
