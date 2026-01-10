from django.contrib.gis.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_READY = "ready"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_READY, "Ready"),
        (STATUS_FAILED, "Failed"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    crs = models.CharField(max_length=64, null=True, blank=True)
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Layer(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    layer_type = models.CharField(max_length=16)  
    source_format = models.CharField(max_length=32)   
    storage_type = models.CharField(max_length=32)    
    table_name = models.CharField(max_length=255, null=True, blank=True)
    file_path = models.TextField(null=True, blank=True)
    crs = models.CharField(max_length=32, default="EPSG:4326")   # ✅ ADD
    original_crs = models.CharField(max_length=32, null=True, blank=True)
    bbox = models.JSONField(null=True, blank=True)
    feature_count = models.IntegerField(null=True, blank=True)
