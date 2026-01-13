from django.conf import settings
from django.http import Http404
from django.db.models.functions import Substr
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from urllib.parse import quote

from ...views.base import IndexBaseView


class ModelPropertyIndexView(IndexBaseView):
    """View for serving the property index of a model.

    This view returns the index structure for a specific model property,
    including entries for each distinct pattern found in the data.

    Permissions are checked via permission_classes defined in IndexBaseView,
    configured via DJANGOLDP_INDEXING_PERMISSION_CLASSES setting.
    """

    def get_property_series(self, model_name, property_name):
        """
        Get distinct 3-character patterns from the property values
        Excludes empty values and returns unique prefixes
        """
        exclude_kwargs = {f'{property_name}': ''}

        # Group by first 3 characters
        property_3_chars = model_name.objects.exclude(**exclude_kwargs).annotate(
            first_chars=Substr(property_name, 1, 3)
        ).values('first_chars').distinct()

        return {
            '3_chars': [entry['first_chars'] for entry in property_3_chars],
        }

    def get(self, request, *args, **kwargs):
        # Permissions are automatically checked by DRF via permission_classes
        # Get the model and property name from the URL pattern context
        model = self.request.resolver_match.kwargs.get('model')
        property_name = self.request.resolver_match.kwargs.get('field_name')

        if not model or not hasattr(model._meta, 'indexed_fields'):
            raise Http404('Model not found or has no indexed fields')

        if property_name not in model._meta.indexed_fields:
            raise Http404(f'Property {property_name} is not indexed for this model')

        base_url = request.build_absolute_uri('/indexes/')
        model_path = model.get_container_path().strip('/')
        index_url = f"{base_url}{model_path}/{property_name}/index"

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

        # Get patterns from actual data
        patterns = self.get_property_series(model, property_name)

        # Add index entries for each pattern
        for pattern in patterns['3_chars']:
            if pattern:  # Skip empty patterns
                pattern = pattern.lower()  # Normalize pattern
                encoded_pattern = quote(pattern)  # URL encode the pattern
                entry = {
                    '@id': f'{index_url}#{encoded_pattern}',  # Also encode in the @id
                    '@type': 'idx:IndexEntry',
                    'idx:hasShape': {
                        '@type': 'sh:NodeShape',
                        'sh:closed': 'false',
                        'sh:property': [
                            {
                                '@id': f'{index_url}#target'
                            },
                            {
                                'sh:path': f'sib:{property_name}',
                                'sh:pattern': f'{pattern}.*'
                            }
                        ]
                    },
                    'idx:hasSubIndex': f"{base_url}{model_path}/{property_name}/{encoded_pattern}"
                }
                response['@graph'].append(entry)

        return Response(
            response,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'public, max-age=3600',
            }
        ) 