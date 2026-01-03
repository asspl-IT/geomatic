import os
import zipfile

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response

from django.conf import settings
from django.shortcuts import get_object_or_404

from myapp.models import Project, Layer
from myapp.services.ingest_service import ingest_uploaded_file
from myapp.parsers.ttk_parser import parse_ttkproject
from myapp.services.preview_service import (
    fetch_geojson_from_table,
    raster_preview,
    las_preview,
)

# ============================================================
# HELPERS
# ============================================================

def api_error(message, status=400):
    return Response({"error": message}, status=status)


# ============================================================
# ADMIN UPLOAD + PREVIEW (WRITE API)
# ============================================================

@api_view(["POST"])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def admin_upload_project(request):
    upload = request.FILES.get("file")
    name = request.data.get("name")

    if not upload or not name:
        return api_error("file and name required", 400)

    project = Project.objects.create(
        name=name,
        owner=request.user,
        status=Project.STATUS_PROCESSING,
    )

    upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads", str(project.id))
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, upload.name)
    with open(file_path, "wb+") as f:
        for chunk in upload.chunks():
            f.write(chunk)

    ext = os.path.splitext(upload.name)[1].lower()
    preview = None

    try:
        # ==================================================
        # ZIP HANDLING
        # ==================================================
        if ext == ".zip":
            extract_dir = os.path.join(upload_dir, "extracted")
            os.makedirs(extract_dir, exist_ok=True)

            with zipfile.ZipFile(file_path) as z:
                z.extractall(extract_dir)

            shp = jpg = jgw = None

            for root, _, files in os.walk(extract_dir):
                for fname in files:
                    lf = fname.lower()
                    full = os.path.join(root, fname)

                    if lf.endswith(".shp"):
                        shp = full
                    elif lf.endswith((".jpg", ".jpeg")):
                        jpg = full
                    elif lf.endswith(".jgw"):
                        jgw = full

            if shp:
                result = ingest_uploaded_file(shp, project)

                layer = Layer.objects.create(
                    project=project,
                    name=os.path.basename(shp),
                    layer_type="vector",
                    source_format="shp",
                    storage_type="postgis",
                    table_name=result["table_name"],
                    bbox=result["meta"].get("bbox"),
                    feature_count=result["meta"].get("feature_count"),
                )

                preview = fetch_geojson_from_table(layer.table_name, 500)

            elif jpg and jgw:
                result = ingest_uploaded_file(jpg, project)

                layer = Layer.objects.create(
                    project=project,
                    name=os.path.basename(jpg),
                    layer_type="raster",
                    source_format="jpg",
                    storage_type="cog",
                    file_path=result["file_path"],
                    bbox=result["meta"].get("bbox"),
                )

                preview = raster_preview(result["file_path"])

            else:
                raise ValueError("ZIP does not contain supported GIS data")

        # ==================================================
        # SINGLE FILE INGEST
        # ==================================================
        else:
            result = ingest_uploaded_file(file_path, project)

            layer = Layer.objects.create(
                project=project,
                name=upload.name,
                layer_type=result["layer_type"],
                source_format=ext.replace(".", ""),
                storage_type=result["storage_type"],
                table_name=result.get("table_name"),
                file_path=result.get("file_path"),
                bbox=result["meta"].get("bbox"),
                feature_count=result["meta"].get("feature_count"),
            )

            if layer.layer_type == "vector":
                preview = fetch_geojson_from_table(layer.table_name, 500)
            elif layer.layer_type == "raster":
                preview = raster_preview(layer.file_path)
            elif layer.layer_type == "lidar":
                preview = result["meta"]

        project.status = Project.STATUS_READY
        project.save()

        return Response({
            "project_id": project.id,
            "status": project.status,
            "preview": preview
        })

    except Exception as e:
        project.status = Project.STATUS_FAILED
        project.error_message = str(e)
        project.save()
        return api_error(str(e), 500)

# ============================================================
# VIEWER APIs (READ-ONLY)
# ============================================================

@api_view(["GET"])
@permission_classes([AllowAny])
def list_projects(request):
    projects = Project.objects.filter(status=Project.STATUS_READY)

    return Response([
        {
            "id": p.id,
            "name": p.name,
            "crs": p.crs,
            "created_at": p.created_at,
        }
        for p in projects
    ])


@api_view(["GET"])
@permission_classes([AllowAny])
def project_layers(request, project_id):
    layers = Layer.objects.filter(project_id=project_id)

    return Response([
        {
            "id": l.id,
            "name": l.name,
            "type": l.layer_type,
            "storage": l.storage_type,
            "feature_count": l.feature_count,
            "bbox": l.bbox,
        }
        for l in layers
    ])


@api_view(["GET"])
@permission_classes([AllowAny])
def vector_layer_geojson(request, layer_id):
    layer = get_object_or_404(Layer, id=layer_id)

    if layer.layer_type != "vector":
        return api_error("Not a vector layer", 400)

    geojson = fetch_geojson_from_table(
        layer.table_name,
        limit=5000
    )
    return Response(geojson)


@api_view(["GET"])
@permission_classes([AllowAny])
def raster_layer_info(request, layer_id):
    layer = get_object_or_404(Layer, id=layer_id)

    if layer.layer_type != "raster":
        return api_error("Not a raster layer", 400)

    return Response({
        "type": "raster",
        "tile_url": f"/api/tiles/{layer.id}/{{z}}/{{x}}/{{y}}.png"
    })
