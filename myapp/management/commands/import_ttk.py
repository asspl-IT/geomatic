import os
from django.core.management.base import BaseCommand
from lxml import etree
from gis_app.models import Project, Layer
from django.conf import settings

class Command(BaseCommand):
    help = 'Import .ttkproject and create Project & Layer records'

    def add_arguments(self, parser):
        parser.add_argument('ttk_file', type=str)
        parser.add_argument('--project-name', type=str, default='Imported Project')

    def handle(self, *args, **options):
        ttk_path = options['ttk_file']
        name = options['project_name']
        if not os.path.exists(ttk_path):
            self.stderr.write('File not found')
            return

        project = Project.objects.create(name=name, ttk_path=ttk_path)
        tree = etree.parse(ttk_path)
        root = tree.getroot()

        # find Layer elements (tag names may differ; inspect your .ttkproject)
        for layer_elem in root.xpath('.//Layer'):
            file_attr = layer_elem.get('File') or layer_elem.get('file')
            if not file_attr:
                continue
            layer_name = layer_elem.get('Name') or os.path.basename(file_attr)
            # determine type by extension
            ext = os.path.splitext(file_attr)[1].lower()
            if ext in ('.shp', '.geojson', '.json'):
                layer_type = 'vector'
            else:
                layer_type = 'raster'

            Layer.objects.create(
                project=project,
                name=layer_name,
                layer_type=layer_type,
                source_path=file_attr,
            )
        self.stdout.write(f'Imported project {project.id} with layers: {project.layers.count()}')