# myapp/urls.py
from django.urls import path
from .views import upload_gis_project

urlpatterns = [
    path("api/upload-geo-project/", upload_gis_project),
]
