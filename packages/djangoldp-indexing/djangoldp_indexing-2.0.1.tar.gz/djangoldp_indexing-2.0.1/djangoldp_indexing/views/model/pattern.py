from django.conf import settings
from django.http import Http404
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from urllib.parse import unquote, quote

from ...views.base import IndexBaseView


class ModelPropertyPatternIndexView(IndexBaseView):
    """View for serving the pattern-specific index of a model property.

    This view returns the index structure for a specific pattern within
    a model property, including entries for all matching objects.

    Permissions are checked via permission_classes defined in IndexBaseView,
    configured via DJANGOLDP_INDEXING_PERMISSION_CLASSES setting.
    """

    def get(self, request, *args, **kwargs):
        # Permissions are automatically checked by DRF via permission_classes
        # Get the model, property name and pattern from the URL pattern context
        model = self.request.resolver_match.kwargs.get('model')
        property_name = self.request.resolver_match.kwargs.get('field_name')
        pattern = unquote(self.request.resolver_match.kwargs.get('pattern'))

        if not model or not hasattr(model._meta, 'indexed_fields'):
            raise Http404('Model not found or has no indexed fields')

        if property_name not in model._meta.indexed_fields:
            raise Http404(f'Property {property_name} is not indexed for this model')

        base_url = request.build_absolute_uri('/indexes/')
        model_path = model.get_container_path().strip('/')
        encoded_pattern = quote(pattern)
        pattern_url = f"{base_url}{model_path}/{property_name}/{encoded_pattern}"

        # Create the pattern index response structure
        response = {
            '@graph': [
                {
                    '@id': pattern_url,
                    '@type': 'idx:Index'
                },
                {
                    '@id': f'{pattern_url}#target',
                    '@type': 'sh:NodeShape',
                    'sh:closed': 'false',
                    'sh:property': [
                        {
                            'sh:path': 'rdf:type',
                            'sh:hasValue': {
                                '@id': model._meta.rdf_type[-1] if isinstance(model._meta.rdf_type, (list, tuple)) else model._meta.rdf_type
                            }
                        },
                        {
                            'sh:path': f'sib:{property_name}',
                            'sh:pattern': f'{pattern}.*'
                        }
                    ]
                }
            ]
        }

        # Find objects matching the pattern
        filter_kwargs = {f'{property_name}__istartswith': pattern}
        matching_objects = model.objects.filter(**filter_kwargs)

        if matching_objects.count() == 0:
            raise Http404(f'No result for pattern: {pattern} on property: {property_name} of model: {model}')

        # Add index entries for matching objects
        for i, obj in enumerate(matching_objects):
            entry = {
                '@id': f'{pattern_url}#{i}',
                '@type': 'idx:IndexEntry',
                'idx:hasShape': f'{pattern_url}#target',
                'idx:hasTarget': request.build_absolute_uri(obj.get_absolute_url())
            }
            response['@graph'].append(entry)

        return Response(
            response,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'public, max-age=3600',
            }
        ) 