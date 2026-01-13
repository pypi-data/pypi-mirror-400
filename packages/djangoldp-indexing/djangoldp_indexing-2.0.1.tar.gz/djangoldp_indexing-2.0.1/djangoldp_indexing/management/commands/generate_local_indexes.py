from django.conf import settings
import json
import os
import shutil
from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.apps import apps
from urllib.parse import urlparse
from django.http import Http404
from djangoldp.views.commons import JSONLDRenderer
from ...views.model.root import ModelRootIndexView
from ...views.model.property import ModelPropertyIndexView
from ...views.model.pattern import ModelPropertyPatternIndexView

class Command(BaseCommand):
    help = 'Generate static local index files for models with indexed_fields metadata'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.factory = RequestFactory()
        self.root_view = ModelRootIndexView()
        self.property_view = ModelPropertyIndexView()
        self.pattern_view = ModelPropertyPatternIndexView()
        self.renderer = JSONLDRenderer()

    def add_arguments(self, parser):
        parser.add_argument(
            '--root_location',
            type=str,
            help='The root location where to save the files',
            default='indexes'
        )
        parser.add_argument(
            '--root_url',
            type=str,
            help='The root URL to use in the generated indexes',
            default='http://localhost:8000'
        )

    def clean_directory(self, directory):
        """Remove all contents of the directory if it exists, then create it."""
        if os.path.exists(directory):
            self.stdout.write(f'Cleaning directory: {directory}')
            shutil.rmtree(directory)
        os.makedirs(directory)

    def handle_patterns(self, model, model_path, field_name, property_response, root_location, request_meta):
        """Handle pattern index generation for a property."""
        patterns = []
        for entry in property_response.data.get('@graph', []):
            if entry.get('@type') == 'idx:IndexEntry':
                sub_index = entry.get('idx:hasSubIndex', '')
                if sub_index:
                    pattern = sub_index.split('/')[-1]
                    patterns.append(pattern)
        
        for pattern in patterns:
            try:
                request = self.factory.get(f'/indexes/{model_path}/{field_name}/{pattern}')
                request.META.update(request_meta)
                
                self.pattern_view.request = request
                self.pattern_view.request.resolver_match = type('ResolverMatch', (), {
                    'kwargs': {
                        'model': model,
                        'field_name': field_name,
                        'pattern': pattern
                    }
                })
                
                pattern_response = self.pattern_view.get(request)
                # Render the response data
                rendered_data = self.renderer.render(pattern_response.data)
                # Decode bytes to string and parse JSON
                rendered_data = json.loads(rendered_data.decode('utf-8'))

                pattern_file_path = os.path.join(root_location, model_path, field_name, f'{pattern}.jsonld')
                os.makedirs(os.path.dirname(pattern_file_path), exist_ok=True)
                with open(pattern_file_path, 'w') as f:
                    json.dump(rendered_data, f, indent=2)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Generated pattern index for {model.__name__}.{field_name}[{pattern}] at {pattern_file_path}'
                    )
                )
            except Http404 as e:
                self.stdout.write(
                    self.style.WARNING(
                        f'Skipping empty pattern index for {model.__name__}.{field_name}[{pattern}]: {str(e)}'
                    )
                )

    def handle_properties(self, model, model_path, root_location, request_meta):
        """Handle property index generation for a model."""
        for field_name in model._meta.indexed_fields:
            request = self.factory.get(f'/indexes/{model_path}/{field_name}/index')
            request.META.update(request_meta)
            
            self.property_view.request = request
            self.property_view.request.resolver_match = type('ResolverMatch', (), {
                'kwargs': {
                    'model': model,
                    'field_name': field_name
                }
            })
            
            property_response = self.property_view.get(request)
            # Render the response data
            rendered_data = self.renderer.render(property_response.data)
            # Decode bytes to string and parse JSON
            rendered_data = json.loads(rendered_data.decode('utf-8'))

            property_file_path = os.path.join(root_location, model_path, field_name, 'index.jsonld')
            os.makedirs(os.path.dirname(property_file_path), exist_ok=True)
            with open(property_file_path, 'w') as f:
                json.dump(rendered_data, f, indent=2)
            
            self.stdout.write(
                self.style.SUCCESS(f'Generated property index for {model.__name__}.{field_name} at {property_file_path}')
            )
            
            self.handle_patterns(model, model_path, field_name, property_response, root_location, request_meta)

    def handle_models(self, root_location, request_meta):
        """Handle root index generation for all models."""
        for model in apps.get_models():
            if hasattr(model._meta, 'indexed_fields'):
                model_path = model.get_container_path().strip('/')
                
                request = self.factory.get(f'/indexes/{model_path}/index')
                request.META.update(request_meta)
                
                self.root_view.request = request
                self.root_view.request.resolver_match = type('ResolverMatch', (), {
                    'kwargs': {'model': model}
                })
                
                root_response = self.root_view.get(request)
                # Render the response data
                rendered_data = self.renderer.render(root_response.data)
                # Decode bytes to string and parse JSON
                rendered_data = json.loads(rendered_data.decode('utf-8'))
                root_file_path = os.path.join(root_location, model_path, 'index.jsonld')
                os.makedirs(os.path.dirname(root_file_path), exist_ok=True)
                with open(root_file_path, 'w') as f:
                    json.dump(rendered_data, f, indent=2)
                
                self.stdout.write(
                    self.style.SUCCESS(f'Generated root index for {model.__name__} at {root_file_path}')
                )
                
                self.handle_properties(model, model_path, root_location, request_meta)

    def handle(self, *args, **kwargs):
        root_location = f"{settings.STATIC_ROOT}/{kwargs['root_location']}"
        host = kwargs['root_url']
        
        self.clean_directory(root_location)
        
        parsed_host = urlparse(host)
        request_meta = {
            'SERVER_NAME': parsed_host.hostname,
            'SERVER_PORT': str(parsed_host.port) if parsed_host.port else '80',
            'wsgi.url_scheme': parsed_host.scheme or 'http',
            'HTTP_X_BYPASS_POLICY': 'true',  # Bypass authentication for static generation
        }
        
        self.handle_models(root_location, request_meta)
