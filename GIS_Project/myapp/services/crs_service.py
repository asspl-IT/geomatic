from django.db import connection

def detect_table_crs(table_name):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT srid
            FROM geometry_columns
            WHERE f_table_name = %s
            LIMIT 1
        """, [table_name])

        row = cursor.fetchone()
        if row and row[0] and row[0] > 0:
            return f"EPSG:{row[0]}"

    # fallback (safe default)
    return "EPSG:4326"
