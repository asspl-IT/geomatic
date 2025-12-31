from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=255)
    ttk_path = models.FileField(upload_to='projects/ttk/')
    created_at = models.DateTimeField(auto_now_add=True)

class Layer(models.Model):
    project = models.ForeignKey(Project, related_name='layers', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    layer_type = models.CharField(max_length=20, choices=(('vector','vector'),('raster','raster')))
    source_path = models.CharField(max_length=1024)  # original path from .ttkproject or uploaded
    web_geojson = models.CharField(max_length=1024, blank=True, null=True)  # path to generated geojson
    tile_folder = models.CharField(max_length=1024, blank=True, null=True)   # for raster tiles
    style = models.JSONField(default=dict, blank=True)  # symbology
    visible = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
