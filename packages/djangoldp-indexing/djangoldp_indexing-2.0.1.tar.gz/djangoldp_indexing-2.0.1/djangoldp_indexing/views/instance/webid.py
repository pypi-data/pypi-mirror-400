from django.conf import settings
from rest_framework.response import Response

from ...views.base import IndexBaseView


class InstanceWebIDView(IndexBaseView):
    """View for serving the WebID profile of the instance.
    
    This view returns the instance's WebID profile document, which includes
    references to the public type index and other identity information.
    """
    
    def get(self, request, *args, **kwargs):
        return self.on_request(request)
    
    def on_request(self, request):
        # Get the type index location from settings or use default
        type_index_location = getattr(settings, 'TYPE_INDEX_LOCATION', '/profile/publicTypeIndex')
        
        # Generate the WebID profile response
        response = {
            '@graph': [
                {
                    "@id": request.build_absolute_uri("/profile"),
                    "@type": "foaf:PersonalProfileDocument",
                    "foaf:primaryTopic": request.build_absolute_uri("/profile#me"),
                },
                {
                    "@id": request.build_absolute_uri("/profile#me"),
                    "@type": ["sib:HublApplication", "solid:Application", "foaf:Agent"],
                    "solid:publicTypeIndex": request.build_absolute_uri(type_index_location),
                }
            ]
        }
        
        return Response(
            response,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'public, max-age=3600',
            }
        ) 