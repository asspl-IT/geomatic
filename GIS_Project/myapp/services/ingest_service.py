import os

from myapp.models import Layer
from myapp.services.format_detector import detect_format
from myapp.services.vector_ingest import ingest_vector
from myapp.services.raster_ingest import ingest_raster
from myapp.services.lidar_ingest import ingest_lidar
from myapp.parsers.ttk_parser import parse_ttkproject
from myapp.services.ingest_layer_service import ingest_layer


def ingest_uploaded_file(file_path, project):
    """
    Central ingestion pipeline.
    Assumes:
    - ZIP already extracted
    - file_path is absolute
    """

    file_path = os.path.abspath(file_path)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ftype = detect_format(file_path)
    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)

    # ==================================================
    # TTK PROJECT
    # ==================================================
    if ftype == "ttkproject":
        project_data = parse_ttkproject(file_path)

        for layer_def in project_data.get("layers", []):
            ingest_layer(layer_def, project)

        return {
            "layer_type": "project",
            "storage_type": "mixed",
            "meta": {
                "layer_count": len(project_data.get("layers", []))
            }
        }

    # ==================================================
    # VECTOR (SHP / GEOJSON / GPKG)
    # ==================================================
    if ftype == "vector":
        # Validate shapefile integrity
        if ext.lower() == ".shp":
            base = file_path[:-4]
            for req in (".dbf", ".shx"):
                if not os.path.exists(base + req):
                    raise ValueError(
                        f"Invalid Shapefile: missing {req} for {file_path}"
                    )

        table_name, meta = ingest_vector(file_path)

        Layer.objects.create(
            project=project,
            name=name,
            layer_type="vector",
            source_format=ext.lstrip("."),
            storage_type="postgis",
            table_name=table_name,
            feature_count=meta.get("feature_count"),
            bbox=meta.get("bbox"),
        )

        return {
            "layer_type": "vector",
            "storage_type": "postgis",
            "table_name": table_name,
            "meta": meta,
        }

    # ==================================================
    # RASTER (TIF / JPG+JGW / COG)
    # ==================================================
    if ftype == "raster":
        cog_path, meta = ingest_raster(file_path)

        Layer.objects.create(
            project=project,
            name=name,
            layer_type="raster",
            source_format=ext.lstrip("."),
            storage_type="cog",
            file_path=cog_path,
            bbox=meta.get("bbox"),
        )

        return {
            "layer_type": "raster",
            "storage_type": "cog",
            "file_path": cog_path,
            "meta": meta,
        }

    # ==================================================
    # LIDAR (LAS / LAZ)
    # ==================================================
    if ftype == "lidar":
        meta = ingest_lidar(file_path)

        Layer.objects.create(
            project=project,
            name=name,
            layer_type="lidar",
            source_format=ext.lstrip("."),
            storage_type="potree",
        )

        return {
            "layer_type": "lidar",
            "storage_type": "potree",
            "meta": meta,
        }

    # ==================================================
    # UNSUPPORTED
    # ==================================================
    raise ValueError(f"Unsupported GIS format: {file_path}")
