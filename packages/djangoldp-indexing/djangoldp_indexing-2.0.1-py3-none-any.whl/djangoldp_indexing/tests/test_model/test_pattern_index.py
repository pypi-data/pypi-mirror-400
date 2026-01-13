from ..models import TestObject
from ..base import IndexTestCase
from ...views.model.pattern import ModelPropertyPatternIndexView
from django.http import Http404
class TestModelPatternIndexView(IndexTestCase):
    """Test suite for ModelPatternIndexView.
    
    Tests the pattern-specific index endpoint that provides entries for all objects
    matching a specific pattern within a model property, validating against the
    specification in Indexing-specifications.md.
    """
    
    def setUp(self):
        """Set up test data and client."""
        super().setUp()
        # Create test objects with titles that will match our pattern
        self.test_objects = [
            TestObject.objects.create(title="Title One"),
            TestObject.objects.create(title="Title Two"),
            TestObject.objects.create(title="Different")  # Won't match 'tit' pattern
        ]
        
        # URL for the pattern index (for 'tit' pattern)
        self.field_name = 'title'
        self.pattern = 'tit'
        self.index_url = f'/indexes/test-objects/{self.field_name}/{self.pattern}'
        self.tested_view = ModelPropertyPatternIndexView()
        
    def test_renderer(self):
        """Test that the model uses the JSONLD renderer"""
        self._test_renderer()

    def test_response_format(self):
        """Test that the response follows the specified JSON-LD format."""
        response = self.get_view_response(self.index_url, kwargs={
                    'field_name': self.field_name,
                    'pattern': self.pattern
                })
        data = response.data
        
        # Example response format:
        # {
        #     "@context": {
        #         "@vocab": "http://www.w3.org/ns/ldp#",
        #         "idx": "http://startinblox.com/indexes#",
        #         "ldp": "http://www.w3.org/ns/ldp#",
        #         "foaf": "http://xmlns.com/foaf/0.1/"
        #     },
        #     "@graph": [
        #         {
        #             "@id": "http://testserver/indexes/test-objects/title/tit",
        #             "@type": "idx:Index"
        #         },
        #         {
        #             "@id": "http://testserver/indexes/test-objects/title/tit#target",
        #             "@type": "sh:NodeShape",
        #             "sh:closed": "false",
        #             "sh:property": [
        #                 {
        #                     "sh:path": "rdf:type",
        #                     "sh:hasValue": {
        #                         "@id": "test:Object"
        #                     }
        #                 },
        #                 {
        #                     "sh:path": "sib:title",
        #                     "sh:pattern": "tit.*"
        #                 }
        #             ]
        #         },
        #         {
        #             "@id": "http://testserver/indexes/test-objects/title/tit#0",
        #             "@type": "idx:IndexEntry",
        #             "idx:hasShape": "http://testserver/indexes/test-objects/title/tit#target",
        #             "idx:hasTarget": "http://testserver/test-objects/1"
        #         },
        #         {
        #             "@id": "http://testserver/indexes/test-objects/title/tit#1",
        #             "@type": "idx:IndexEntry",
        #             "idx:hasShape": "http://testserver/indexes/test-objects/title/tit#target",
        #             "idx:hasTarget": "http://testserver/test-objects/2"
        #         }
        #     ]
        # }
               
        # Verify @graph array
        self.assertIn(
            '@graph', 
            data,
            "Response should contain @graph array"
        )
        self.assertTrue(
            isinstance(data['@graph'], list),
            "@graph should be a list"
        )
        
        # Find the main index object
        index_obj = next(
            (item for item in data['@graph'] 
             if item.get('@type') == 'idx:Index'),
            None
        )
        self.assertIsNotNone(
            index_obj,
            "Graph should contain an idx:Index object"
        )
        self.assertEqual(
            index_obj['@id'],
            f'http://testserver{self.index_url}',
            "Index @id should match the request URL"
        )
        
        # Find the target shape object
        target_obj = next(
            (item for item in data['@graph'] 
             if item['@id'].endswith('#target')),
            None
        )
        self.assertIsNotNone(
            target_obj,
            "Graph should contain a target shape object"
        )
        self.assertEqual(
            target_obj['@type'],
            'sh:NodeShape',
            "Target shape should be of type sh:NodeShape"
        )
        self.assertEqual(
            target_obj['sh:closed'],
            'false',
            "Target shape should not be closed"
        )
        
        # Verify target shape properties
        self.assertTrue(
            isinstance(target_obj['sh:property'], list),
            "Target shape properties should be a list"
        )
        self.assertEqual(
            len(target_obj['sh:property']),
            2,
            "Target shape should have exactly 2 properties (type + pattern)"
        )
        
        # Verify type constraint
        type_prop = next(
            (prop for prop in target_obj['sh:property'] 
             if prop['sh:path'] == 'rdf:type'),
            None
        )
        self.assertIsNotNone(
            type_prop,
            "Target shape should include rdf:type constraint"
        )
        self.assertEqual(
            type_prop['sh:hasValue']['@id'],
            TestObject._meta.rdf_type[-1] if isinstance(TestObject._meta.rdf_type, (list, tuple)) else TestObject._meta.rdf_type,
            "Type constraint should reference the model's RDF type"
        )
        
        # Verify pattern constraint
        pattern_prop = next(
            (prop for prop in target_obj['sh:property'] 
             if prop['sh:path'] == 'sib:title'),
            None
        )
        self.assertIsNotNone(
            pattern_prop,
            "Target shape should include title pattern constraint"
        )
        self.assertEqual(
            pattern_prop['sh:pattern'],
            'tit.*',
            "Pattern constraint should match 'tit' prefix"
        )
        
        # Find matching entries
        entries = [
            item for item in data['@graph'] 
            if item.get('@type') == 'idx:IndexEntry'
        ]
        self.assertEqual(
            len(entries),
            2,
            "Should have exactly 2 entries for objects matching 'tit' pattern"
        )
        
        # Verify entry structure
        for i, entry in enumerate(entries):
            self.assertTrue(
                entry['@id'].endswith(f'#{i}'),
                f"Entry {i} should have correct ID suffix"
            )
            self.assertEqual(
                entry['idx:hasShape'],
                f'http://testserver{self.index_url}#target',
                f"Entry {i} should reference the target shape"
            )
            self.assertTrue(
                entry['idx:hasTarget'].startswith('http://'),
                f"Entry {i} should reference a valid object URL"
            )

    def test_error_cases(self):
        """Test error cases for the pattern index view."""
        # Example error response for non-existent model:
        # {
        #     "detail": "Not found."
        # }
        
        
        # Test non-indexed property
        with self.assertRaises(Http404, msg="Request for non-indexed property should raise Http404"):
            response = self.get_view_response('/indexes/test-objects/non-indexed/tit', kwargs={
                    'field_name': 'non-indexed-property',
                    'pattern': self.pattern
                })
        
        # Test non-existent pattern
        with self.assertRaises(Http404, msg="Request for non-existent pattern should raise Http404"):
            response = self.get_view_response('/indexes/test-objects/title/xyz', kwargs={
                    'field_name': self.field_name,
                    'pattern': 'xyz'
                })


