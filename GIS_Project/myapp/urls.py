from django.urls import path
from .views import admin_upload_project, list_projects, project_layers, vector_layer_geojson, raster_layer_info

urlpatterns = [
    path("upload-project/", admin_upload_project),
    path("api/projects/", list_projects),
    path("api/projects/<int:project_id>/layers/", project_layers),
    path("api/layers/<int:layer_id>/geojson/", vector_layer_geojson),
    path("api/layers/<int:layer_id>/raster-info/", raster_layer_info),
]



