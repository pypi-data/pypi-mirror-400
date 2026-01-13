from django.conf import settings
from django.http import Http404
from rest_framework.response import Response

from ...views.base import IndexBaseView


class ModelRootIndexView(IndexBaseView):
    """View for serving the root index of a model.

    This view returns the index structure for a specific model,
    including entries for each indexed field.

    Permissions are checked via permission_classes defined in IndexBaseView,
    configured via DJANGOLDP_INDEXING_PERMISSION_CLASSES setting.
    """

    def get(self, request, *args, **kwargs):
        # Permissions are automatically checked by DRF via permission_classes
        # Get the model from the URL pattern context
        model = self.request.resolver_match.kwargs.get('model')
        if not model or not hasattr(model._meta, 'indexed_fields'):
            raise Http404('Model not found or has no indexed fields')

        base_url = request.build_absolute_uri('/indexes/')
        model_path = model.get_container_path().strip('/')
        index_url = request.build_absolute_uri()
        # Create the base index structure
        response = {
            '@graph': [
                {
                    '@type': 'idx:Index',
                    '@id': index_url
                },
                {
                    '@id': f'{index_url}#target',
                    'sh:path': 'rdf:type',
                    'sh:hasValue': {
                        '@id': model._meta.rdf_type[-1] if isinstance(model._meta.rdf_type, (list, tuple)) else model._meta.rdf_type
                    }
                }
            ]
        }

        # Add index entries for each indexed field
        for field_name in model._meta.indexed_fields:
            entry = {
                '@id': f'{index_url}#{field_name}',
                '@type': 'idx:IndexEntry',
                'idx:hasShape': {
                    '@type': 'sh:NodeShape',
                    'sh:closed': 'false',
                    'sh:property': [
                        {
                            '@id': f'{index_url}#target'
                        },
                        {
                            'sh:path': f'sib:{field_name}'
                        }
                    ]
                },
                'idx:hasSubIndex': f"{base_url}{model_path}/{field_name}/index"
            }
            response['@graph'].append(entry)

        return Response(
            response,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'public, max-age=3600',
            }
        ) 