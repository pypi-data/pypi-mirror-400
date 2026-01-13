from ..models import TestObject
from ..base import IndexTestCase
from ...views.instance.root import InstanceRootContainerView

class TestInstanceIndexesRootView(IndexTestCase):
    """Test suite for InstanceIndexesRootView.
    
    Tests the root index endpoint that lists all available model indexes,
    validating:
    - Route accessibility
    - Response format and content according to specifications
    - Error cases and edge cases
    """
    
    def setUp(self):
        """Set up test data and client."""
        super().setUp()
        # Create some test objects to ensure we have data to index
        self.test_objects = [
            TestObject.objects.create(
                title=f"Test Object {i}",
                description=f"Description {i}"
            ) for i in range(3)
        ]
        
        self.tested_view = InstanceRootContainerView()
        # URL for the instance indexes root
        self.index_url = '/indexes/'

    def test_renderer(self):
        """Test that the model uses the JSONLD renderer"""
        self._test_renderer()

    def find_first_matching_index(self, indexes, suffix):
        """Find the first index entry whose @id ends with the given suffix.
        
        Args:
            indexes: List of index entries from ldp:contains
            suffix: String to match at the end of @id
            
        Returns:
            The first matching index entry or None if not found
        """
        return next(
            (item for item in indexes if item['@id'].endswith(suffix)),
            None
        )

    def test_route_accessibility(self):
        """Test that the instance indexes root is accessible."""
        response = self.make_request(self.index_url)
        self.assertEqual(
            response.status_code, 
            200, 
            f"Expected route {self.index_url} to be accessible, got status {response.status_code}"
        )
        # Example response header:
        # Content-Type: application/ld+json
        self.assertEqual(
            response['Content-Type'], 
            'application/ld+json',
            "Response should have Content-Type: application/ld+json"
        )

    def test_response_format(self):
        """Test that the response follows the specified JSON-LD format."""
        response = self.make_request(self.index_url)
        data = response.json()
        
        # Example expected format:
        # {
        #     "@context": {
        #         "@vocab": "http://www.w3.org/ns/ldp#",
        #         "idx": "http://startinblox.com/indexes#",
        #         "ldp": "http://www.w3.org/ns/ldp#"
        #     },
        #     "@id": "http://testserver/indexes/",
        #     "@type": "ldp:Container",
        #     "ldp:contains": [
        #         {
        #             "@type": "idx:Index",
        #             "@id": "http://testserver/indexes/test-objects/index"
        #         }
        #     ]
        # }
        
        # Verify basic JSON-LD structure
        self.assertIn(
            '@context', 
            data,
            "Response should contain @context field for JSON-LD"
        )
        self.assertIn(
            '@id', 
            data,
            "Response should contain @id field identifying the index"
        )
        self.assertEqual(
            data['@id'],
            f'http://testserver{self.index_url}',
            "Index @id should match the request URL"
        )
        self.assertEqual(
            data['@type'],
            'ldp:Container',
            "Root index should be of type ldp:Container"
        )
        
        # Example ldp:contains entry:
        # "ldp:contains": [
        #     {
        #         "@type": "idx:Index",
        #         "@id": "http://testserver/indexes/test-objects/index"
        #     }
        # ]
        self.assertIn(
            'ldp:contains', 
            data,
            "Response should contain ldp:contains field listing available indexes"
        )
        self.assertTrue(
            isinstance(data['ldp:contains'], list),
            "ldp:contains should be a list of available indexes"
        )
        
        # Example TestObject index entry:
        # {
        #     "@type": "idx:Index",
        #     "@id": "http://testserver/indexes/test-objects/index"
        # }
        test_object_index = self.find_first_matching_index(
            data['ldp:contains'],
            '/indexes/test-objects/index'
        )
        self.assertIsNotNone(
            test_object_index,
            "Response should include an index for TestObject model"
        )
        self.assertEqual(
            test_object_index['@type'],
            'idx:Index',
            "Model index entry should be of type idx:Index"
        )

    def test_empty_database(self):
        """Test response when no objects exist in the database."""
        # Clear all test objects
        TestObject.objects.all().delete()
        
        response = self.make_request(self.index_url)
        data = response.json()
        
        # Example expected format with empty database:
        # {
        #     "@context": {...},
        #     "@id": "http://testserver/indexes/",
        #     "@type": "ldp:Container",
        #     "ldp:contains": [
        #         {
        #             "@type": "idx:Index",
        #             "@id": "http://testserver/indexes/test-objects/index"
        #         }
        #     ]
        # }
        
        # Even with no objects, the index should still list available model indexes
        self.assertEqual(
            response.status_code,
            200,
            "Index should be accessible even with no objects in database"
        )
        self.assertIn(
            'ldp:contains',
            data,
            "Response should contain ldp:contains even with empty database"
        )
        # TestObject index should still be listed as it's a valid model
        test_object_index = self.find_first_matching_index(
            data['ldp:contains'],
            '/indexes/test-objects/index'
        )
        self.assertIsNotNone(
            test_object_index,
            "Response should include TestObject index even with no objects"
        )

    # def test_model_filtering(self):
    #     """Test that only models with proper configuration are included."""
    #     response = self.make_request(self.index_url)
    #     data = response.json()
        
    #     # Example expected format for each index entry:
    #     # {
    #     #     "@type": "idx:Index",
    #     #     "@id": "http://testserver/indexes/test-objects/index"
    #     # }
        
    #     for index in data['ldp:contains']:
    #         self.assertEqual(
    #             index['@type'],
    #             'idx:Index',
    #             f"Each index entry should be of type idx:Index, got {index.get('@type')} for {index['@id']}"
    #         )
    #         self.assertTrue(
    #             index['@id'].startswith('http://testserver/indexes/'),
    #             f"Index @id should start with base URL and /indexes/, got {index['@id']}"
    #         )
    #         self.assertTrue(
    #             index['@id'].endswith('/index'),
    #             f"Index @id should end with /index, got {index['@id']}"
    #         ) 