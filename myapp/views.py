from django.shortcuts import render
import os
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from .models import Project, Layer
from .serializers import ProjectSerializer
from .utils.ttk_converter import parse_ttkproject
from .utils.raster_converter import convert_raster_to_tiles


# @api_view(["POST"])
# @parser_classes([MultiPartParser, FormParser])
# def upload_ttkproject(request):
#     file = request.FILES.get("file")
#     if not file:
#         return Response({"error": "No file uploaded"}, status=400)

#     upload_folder = os.path.join(settings.MEDIA_ROOT, "ttk_projects")
#     os.makedirs(upload_folder, exist_ok=True)
#     file_path = os.path.join(upload_folder, file.name)

#     with open(file_path, "wb+") as dest:
#         for chunk in file.chunks():
#             dest.write(chunk)

#     # Parse
#     project_data = parse_ttkproject(file_path)

#     # Read parsed data PROPERLY
#     coordinate_system = project_data["coordinate_system"]
#     layers = project_data["layers"]

#     # Build final response
#     return Response({
#         "project_name": file.name,
#         "coordinate_system": coordinate_system,
#         "layers": layers
#     })

@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload_ttkproject(request):
    file = request.FILES.get("file")
    if not file:
        return Response({"error": "No file uploaded"}, status=400)

    upload_folder = os.path.join(settings.MEDIA_ROOT, "ttk_projects")
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, file.name)

    with open(file_path, "wb+") as dest:
        for chunk in file.chunks():
            dest.write(chunk)

    # parse
    project_data = parse_ttkproject(file_path)
    coordinate_system = project_data.get("coordinate_system")
    layers = project_data.get("layers", [])

    # Optionally convert layer files (convert=true)
    do_convert = request.query_params.get("convert", "false").lower() == "true"

    conversion_results = []
    if do_convert:
        for layer in layers:
            # support groups (type == group) recursively
            def handle_layer(l):
                if not isinstance(l, dict):
                    return
                ltype = l.get("type")
                # if group, handle children
                if ltype == "group":
                    for child in l.get("layers", []):
                        handle_layer(child)
                    return

                full_path = l.get("full_path") or l.get("file")
                # if the path is relative (as saved by parser) try to resolve relative to upload_folder
                if full_path and not os.path.isabs(full_path):
                    full_path = os.path.normpath(os.path.join(upload_folder, full_path))
                # SHP conversion
                if ltype == "vector" and full_path and full_path.lower().endswith(".shp"):
                    try:
                        geojson_path = convert_shp_to_geojson(full_path, out_folder=os.path.dirname(full_path))
                        conversion_results.append({"layer": l.get("name"), "geojson": geojson_path})
                    except Exception as e:
                        conversion_results.append({"layer": l.get("name"), "error": str(e)})
                # raster conversion
                elif ltype == "raster" and full_path:
                    try:
                        tiles_folder = convert_raster_to_tiles(full_path)
                        conversion_results.append({"layer": l.get("name"), "tiles": tiles_folder})
                    except Exception as e:
                        conversion_results.append({"layer": l.get("name"), "error": str(e)})

            handle_layer(layer)

    response = {
        "project_name": file.name,
        "coordinate_system": coordinate_system,
        "layers": layers,
        "conversions": conversion_results
    }
    return Response(response)
