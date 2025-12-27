# gis_app/serializers.py
from rest_framework import serializers
from .models import Project, Layer

class LayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Layer
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    layers = LayerSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'file', 'layers']
