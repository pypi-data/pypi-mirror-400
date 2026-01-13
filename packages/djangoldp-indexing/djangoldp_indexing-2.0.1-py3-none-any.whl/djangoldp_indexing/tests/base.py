"""Base classes for djangoldp-indexing tests."""

from abc import ABC
from django.test import TestCase
from rest_framework.test import APIClient
from .models import TestObject
from django.test.client import RequestFactory
from djangoldp.views.commons import JSONLDRenderer

class IndexTestCase(ABC, TestCase):
    """Base test class for all index-related tests.
    
    Provides common functionality for testing index views including:
    - API client setup
    - Request helper methods
    - Common assertions
    """
    
    def setUp(self):
        """Set up test data and client."""
        super().setUp()
        self.client = APIClient()
                # Setup view and request factory
        self.factory = RequestFactory()
        self.tested_view = None


    def make_request(self, path, headers=None):
        """Make HTTP request with default headers.
        
        Uses Django's test client header convention where:
        - Headers are prefixed with 'HTTP_'
        - Names are uppercase with hyphens replaced by underscores
        For example, 'Accept: application/ld+json' becomes {'HTTP_ACCEPT': 'application/ld+json'}
        
        Args:
            path: URL path to request
            headers: Optional additional headers (using Django's HTTP_ prefix convention)
            
        Returns:
            Response from the API client
        """
        default_headers = {'HTTP_ACCEPT': 'application/ld+json'}
        if headers:
            default_headers.update(headers)
        return self.client.get(path, **default_headers) 
    
    def get_view_response(self, url=None, model=None, kwargs={}, bypass_policy=True):
        """Create and execute a request to the view.

        Args:
            url: URL to request (defaults to self.index_url)
            model: Model class to use in resolver_match (defaults to TestObject)
            bypass_policy: If True, adds X-Bypass-Policy header (default: True)

        Returns:
            Response from the view
        """
        if url is None:
            url = self.index_url
        if model is None:
            model = TestObject

        request = self.factory.get(url)
        request.META.update({
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': '80',
            'wsgi.url_scheme': 'http',
        })

        # Add bypass header for tests by default
        if bypass_policy:
            request.META['HTTP_X_BYPASS_POLICY'] = 'true'
        
        kwargs['model'] = model
        self.tested_view.request = request
        self.tested_view.request.resolver_match = type('ResolverMatch', (), {
            'kwargs': kwargs
        })
        
        response = self.tested_view.get(request)
        
        return response
    
    def _test_renderer(self):
        """Test that the model uses the JSONLD renderer"""
        self.assertIn(
            JSONLDRenderer,
            self.tested_view.renderer_classes,
            "ModelRootIndexView should use JSONLDRenderer"
        )
