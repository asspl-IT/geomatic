import os
import zipfile

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.conf import settings

from .services.project_service import ProjectService
from .converters.ttk_converter import parse_ttkproject
from .converters.raster_converter import convert_raster_to_tiles

# optional
try:
    import laspy
    LAS_SUPPORTED = True
except ImportError:
    LAS_SUPPORTED = False


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload_gis_project(request):

    file = request.FILES.get("file")
    if not file:
        return Response({"error": "No file uploaded"}, status=400)

    upload_dir = os.path.join(settings.MEDIA_ROOT, "geo_projects")
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.name)

    # --------------------------------------------------
    # Save uploaded file
    # --------------------------------------------------
    with open(file_path, "wb+") as f:
        for chunk in file.chunks():
            f.write(chunk)

    ext = os.path.splitext(file.name)[1].lower()

    # --------------------------------------------------
    # Reject MXD explicitly
    # --------------------------------------------------
    if ext == ".mxd":
        return Response(
            {
                "error": (
                    "MXD (ArcMap) projects are not supported. "
                    "Please convert MXD to QGIS (.qgs) or GeoPackage (.gpkg)."
                )
            },
            status=400
        )

    # --------------------------------------------------
    # Handle ZIP (SHP / QGIS / JPG+JGW / Raster)
    # --------------------------------------------------
    if ext == ".zip":
        extract_dir = os.path.join(upload_dir, os.path.splitext(file.name)[0])
        os.makedirs(extract_dir, exist_ok=True)

        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        extracted_file = None

        for root, _, files in os.walk(extract_dir):
            for fname in files:
                lname = fname.lower()

                # priority order
                if lname.endswith(".shp"):
                    extracted_file = os.path.join(root, fname)
                    break

                if lname.endswith(".qgs"):
                    extracted_file = os.path.join(root, fname)
                    break

                if lname.endswith((".tif", ".tiff")):
                    extracted_file = os.path.join(root, fname)
                    break

                if lname.endswith((".jpg", ".jpeg")):
                    extracted_file = os.path.join(root, fname)
                    break

            if extracted_file:
                break

        if not extracted_file:
            return Response(
                {
                    "error": (
                        "ZIP must contain one of the following: "
                        ".shp, .qgs, .tif, .jpg (+ .jgw)"
                    )
                },
                status=400
            )

        file_path = extracted_file
        ext = os.path.splitext(file_path)[1].lower()


    # --------------------------------------------------
    # Handle LAS / LAZ
    # --------------------------------------------------
    if ext in (".las", ".laz"):
        if not LAS_SUPPORTED:
            return Response(
                {"error": "LAS/LAZ support not installed (laspy missing)"},
                status=400
            )

        try:
            las = laspy.read(file_path)
            header = las.header

            # CRS is OPTIONAL in LAS
            try:
                crs_obj = header.parse_crs()
                crs = crs_obj.to_string() if crs_obj else None
            except Exception:
                crs = None

            return Response({
                "file": file.name,
                "project_type": "lidar",
                "coordinate_system": crs,
                "layers": [
                    {
                        "name": os.path.splitext(file.name)[0],
                        "type": "pointcloud",
                        "points": header.point_count,
                        "bounds": {
                            "xmin": header.mins[0],
                            "ymin": header.mins[1],
                            "zmin": header.mins[2],
                            "xmax": header.maxs[0],
                            "ymax": header.maxs[1],
                            "zmax": header.maxs[2],
                        },
                        "children": []
                    }
                ]
            })

        except Exception as e:
            return Response(
                {"error": f"Failed to read LAS file: {str(e)}"},
                status=400
            )


    # --------------------------------------------------
    # Handle TTK separately (legacy compatibility)
    # --------------------------------------------------
    if ext == ".ttkproject":
        project_data = parse_ttkproject(file_path)
        return Response({
            "file": file.name,
            **project_data
        })
    
    # --------------------------------------------------
    # JPG or JPEG and JGW handling (FIXED)
    # --------------------------------------------------
    if ext in (".jpg", ".jpeg"):
        base = os.path.splitext(os.path.basename(file_path))[0]
        base_dir = os.path.dirname(file_path)

        jgw_path = os.path.join(base_dir, base + ".jgw")
        prj_path = os.path.join(base_dir, base + ".prj")

        if not os.path.exists(jgw_path):
            return Response(
                {
                    "error": (
                        "Georeferenced JPG requires a .jgw world file. "
                        "Upload JPG + JGW together (preferably zipped)."
                    )
                },
                status=400
            )

        try:
            import rasterio

            with rasterio.open(file_path) as ds:
                crs = ds.crs.to_string() if ds.crs else None
                bounds = ds.bounds

            return Response({
                "file": os.path.basename(file_path),
                "project_type": "raster",
                "coordinate_system": crs,
                "layers": [
                    {
                        "name": base,
                        "type": "raster",
                        "format": "jpg+jgw",
                        "bounds": {
                            "xmin": bounds.left,
                            "ymin": bounds.bottom,
                            "xmax": bounds.right,
                            "ymax": bounds.top,
                        },
                        "children": []
                    }
                ]
            })

        except Exception as e:
            return Response(
                {"error": f"Failed to read georeferenced JPG: {str(e)}"},
                status=400
            )

    # --------------------------------------------------
    # Handle GeoJSON
    # --------------------------------------------------
    if ext in (".geojson", ".json"):
        try:
            import geopandas as gpd

            gdf = gpd.read_file(file_path)

            # CRS handling
            crs = gdf.crs.srs if gdf.crs else "EPSG:4326"

            # Geometry type summary
            geom_types = gdf.geom_type.unique().tolist()

            return Response({
                "file": os.path.basename(file_path),
                "project_type": "vector",
                "coordinate_system": crs,
                "layers": [
                    {
                        "name": os.path.splitext(os.path.basename(file_path))[0],
                        "type": "vector",
                        "format": "geojson",
                        "geometry_types": geom_types,
                        "feature_count": len(gdf),
                        "children": []
                    }
                ]
            })

        except Exception as e:
            return Response(
                {"error": f"Failed to read GeoJSON: {str(e)}"},
                status=400
            )


    # --------------------------------------------------
    # ALL OTHER GIS FORMATS
    # --------------------------------------------------
    try:
        project_data = ProjectService.fetch_project(file_path)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

    return Response({
        "file": file.name,
        **project_data
    })
