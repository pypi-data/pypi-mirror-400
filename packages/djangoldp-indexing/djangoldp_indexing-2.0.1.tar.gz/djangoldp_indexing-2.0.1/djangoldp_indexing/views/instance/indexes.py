from django.apps import apps
from django.conf import settings
from rest_framework.response import Response

from ...views.base import IndexBaseView


class InstanceIndexesRootView(IndexBaseView):
    """View for serving the root of all indexes.
    
    This view returns a list of all model indexes available in the system,
    providing entry points for model-specific indexes.
    """
    
    def get(self, request, *args, **kwargs):
        return self.on_request(request)
    
    def on_request(self, request):
        # Generate the base response structure
        response = {
            '@id': request.build_absolute_uri(),
            '@type': 'ldp:Container',
            'ldp:contains': []
        }
        
        # Add index entries for all models with indexed fields
        for app in apps.get_app_configs():
            app_models = [model.__name__ for model in app.get_models()]
            for model_name in app_models:
                model = apps.get_model(app.label, model_name)
                if model._meta and hasattr(model._meta, 'indexed_fields'):
                    if hasattr(model._meta, 'rdf_type') and hasattr(model, 'get_container_path'):
                        response['ldp:contains'].append({
                            "@type": "idx:Index",
                            '@id': request.build_absolute_uri('/indexes' + model.get_container_path() + 'index'),
                        })
        
        return Response(
            response,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'public, max-age=3600',
            }
        ) 