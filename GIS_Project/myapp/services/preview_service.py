import os
import rasterio
import laspy
from django.db import connection

def fetch_geojson_from_table(table_name, limit=5000):
    with connection.cursor() as cursor:

        # --------------------------------------------------
        # 1. Detect geometry column
        # --------------------------------------------------
        cursor.execute("""
            SELECT f_geometry_column
            FROM geometry_columns
            WHERE f_table_name = %s
            LIMIT 1
        """, [table_name])

        row = cursor.fetchone()
        if not row:
            raise ValueError("No geometry column found")

        geom_col = row[0]

        # --------------------------------------------------
        # 2. Detect SRID safely (PostGIS 3+ compliant)
        # --------------------------------------------------
        cursor.execute(f"""
            SELECT ST_SRID({geom_col})
            FROM "{table_name}"
            WHERE {geom_col} IS NOT NULL
            LIMIT 1
        """)

        srid_row = cursor.fetchone()
        source_srid = srid_row[0] if srid_row and srid_row[0] else 4326

        # --------------------------------------------------
        # 3. Build GeoJSON (reproject only if needed)
        # --------------------------------------------------
        geom_expr = (
            f"ST_Transform({geom_col}, 4326)"
            if source_srid != 4326
            else geom_col
        )

        cursor.execute(f"""
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'crs', jsonb_build_object(
                    'type', 'name',
                    'properties', jsonb_build_object(
                        'name', 'EPSG:4326'
                    )
                ),
                'features', COALESCE(jsonb_agg(feature), '[]'::jsonb)
            )
            FROM (
                SELECT jsonb_build_object(
                    'type', 'Feature',
                    'geometry',
                        ST_AsGeoJSON({geom_expr})::jsonb,
                    'properties',
                        to_jsonb(t) - '{geom_col}'
                ) AS feature
                FROM "{table_name}" t
                WHERE {geom_col} IS NOT NULL
                LIMIT %s
            ) AS features;
        """, [limit])

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
