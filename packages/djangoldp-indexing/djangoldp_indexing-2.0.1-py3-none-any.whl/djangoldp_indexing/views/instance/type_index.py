from django.apps import apps
from django.conf import settings
from rest_framework.response import Response

from ...views.base import IndexBaseView


class PublicTypeIndexView(IndexBaseView):
    """View for serving the public type index of the instance.
    
    This view returns a list of all indexed models and their properties,
    following the Solid Type Index specification.
    """
    
    def get(self, request, *args, **kwargs):
        return self.on_request(request)
    
    def on_request(self, request):
        # Generate the base response structure
        response = {
            '@graph': [{
                "@id": request.build_absolute_uri('publicTypeIndex'),
                "@type": "solid:TypeIndex"
            }]
        }
        
        # Add index registrations for models with indexed fields
        for app in apps.get_app_configs():
            app_models = [model.__name__ for model in app.get_models()]
            for model_name in app_models:
                model = apps.get_model(app.label, model_name)
                if model._meta and hasattr(model._meta, 'indexed_fields'):
                    if hasattr(model._meta, 'rdf_type') and hasattr(model, 'get_container_path'):
                        response['@graph'].append({
                            "@type": "solid:TypeIndexRegistration",
                            "solid:forClass": "idx:Index",
                            '@id': request.build_absolute_uri(f"publicTypeIndex#indexes-{model.get_container_path()[1:-1]}"),
                            "solid:instance": request.build_absolute_uri('/indexes' + model.get_container_path() + 'index')
                        })
        
        # Add type registrations for all models with RDF types
        for app in apps.get_app_configs():
            app_models = [model.__name__ for model in app.get_models()]
            for model_name in app_models:
                model = apps.get_model(app.label, model_name)
                if model._meta and hasattr(model._meta, 'rdf_type') and hasattr(model, 'get_container_path'):
                    response['@graph'].append({
                        "@id": request.build_absolute_uri(f"publicTypeIndex#{model.get_container_path()[1:-1]}"),
                        "@type": "solid:TypeIndexRegistration",
                        "solid:forClass": model._meta.rdf_type,
                        "solid:instanceContainer": request.build_absolute_uri(model.get_container_path())
                    })
        
        return Response(
            response,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'public, max-age=3600',
            }
        ) 