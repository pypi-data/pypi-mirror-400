from ..models import TestObject
from ..base import IndexTestCase
from ...views.model.property import ModelPropertyIndexView
from django.http import Http404


class TestModelPropertyIndexView(IndexTestCase):
    """Test suite for ModelPropertyIndexView.
    
    Tests the property index endpoint that provides pattern-based indexing
    for a specific model property, validating against the specification in
    Indexing-specifications.md.
    """
    
    def setUp(self):
        """Set up test data and client."""
        super().setUp()
        # Create test objects with titles that will generate specific patterns
        self.test_objects = [
            TestObject.objects.create(title="Title One"),
            TestObject.objects.create(title="Title Two"),
            TestObject.objects.create(title="Different")
        ]
        self.field_name = 'title'
        # URL for the property index
        self.index_url = f'/indexes/test-objects/{self.field_name}/index'
        self.tested_view = ModelPropertyIndexView()

    def test_renderer(self):
        """Test that the model uses the JSONLD renderer"""
        self._test_renderer()

    def test_response_format(self):
        """Test that the response follows the specified JSON-LD format."""
        response = self.get_view_response(self.index_url, kwargs={
                    'field_name': self.field_name
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
        #             "@type": "idx:Index",
        #             "@id": "http://testserver/indexes/test-objects/title/index"
        #         },
        #         {
        #             "@id": "http://testserver/indexes/test-objects/title/index#target",
        #             "sh:path": "rdf:type",
        #             "sh:hasValue": {
        #                 "@id": "test:Object"
        #             }
        #         },
        #         {
        #             "@id": "http://testserver/indexes/test-objects/title/index#tit",
        #             "@type": "idx:IndexEntry",
        #             "idx:hasShape": {
        #                 "@type": "sh:NodeShape",
        #                 "sh:closed": "false",
        #                 "sh:property": [
        #                     "http://testserver/indexes/test-objects/title/index#target",
        #                     {
        #                         "sh:path": "sib:title",
        #                         "sh:pattern": "tit.*"
        #                     }
        #                 ]
        #             },
        #             "idx:hasSubIndex": "http://testserver/indexes/test-objects/title/tit"
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
            target_obj['sh:path'],
            'rdf:type',
            "Target shape should define rdf:type path"
        )
        self.assertEqual(
            target_obj['sh:hasValue']['@id'],
            TestObject._meta.rdf_type[-1] if isinstance(TestObject._meta.rdf_type, (list, tuple)) else TestObject._meta.rdf_type,
            "Target shape should reference the model's RDF type"
        )
        
        # Find pattern entries
        pattern_entries = [
            item for item in data['@graph'] 
            if item.get('@type') == 'idx:IndexEntry'
        ]
        self.assertTrue(
            len(pattern_entries) > 0,
            "Graph should contain pattern-based index entries"
        )
        
        # Verify a pattern entry (using 'tit' as it matches our test data)
        pattern_entry = next(
            (item for item in pattern_entries 
             if item['@id'].endswith('#tit')),
            None
        )
        self.assertIsNotNone(
            pattern_entry,
            "Graph should contain an entry for the 'tit' pattern"
        )
        
        # Verify pattern entry structure
        shape = pattern_entry['idx:hasShape']
        self.assertEqual(
            shape['@type'],
            'sh:NodeShape',
            "Pattern shape should be of type sh:NodeShape"
        )
        self.assertEqual(
            shape['sh:closed'],
            'false',
            "Pattern shape should not be closed"
        )
        
        # Verify shape properties
        self.assertTrue(
            isinstance(shape['sh:property'], list),
            "Shape properties should be a list"
        )
        self.assertEqual(
            len(shape['sh:property']),
            2,
            "Shape should have exactly 2 properties (target + pattern)"
        )
        
        # Verify target reference
        self.assertEqual(
            shape['sh:property'][0]['@id'],
            f'http://testserver{self.index_url}#target',
            "First property should reference the target shape"
        )
        
        # Verify pattern property
        pattern_prop = shape['sh:property'][1]
        self.assertEqual(
            pattern_prop['sh:path'],
            'sib:title',
            "Pattern property should reference the title field"
        )
        self.assertEqual(
            pattern_prop['sh:pattern'],
            'tit.*',
            "Pattern property should include the pattern with wildcard"
        )
        
        # Verify sub-index reference
        self.assertEqual(
            pattern_entry['idx:hasSubIndex'],
            f'http://testserver/indexes/test-objects/title/tit',
            "Pattern entry should reference its sub-index"
        )

    def test_error_cases(self):
        """Test error cases for the property index view."""
        # Example error response for non-existent model:
        # {
        #     "detail": "Not found."
        # }
              
        # Test non-indexed property
        with self.assertRaises(Http404, msg="Request for non-indexed property should raise Http404"):
            self.get_view_response('/indexes/test-objects/non-indexed/index', kwargs={
                    'field_name': 'non-indexed-property'
                })

    def test_empty_model(self):
        """Test response when no objects exist in the model."""
        # Example response for empty model:
        # {
        #     "@context": {
        #         "@vocab": "http://www.w3.org/ns/ldp#",
        #         "idx": "http://startinblox.com/indexes#",
        #         "ldp": "http://www.w3.org/ns/ldp#",
        #         "foaf": "http://xmlns.com/foaf/0.1/"
        #     },
        #     "@graph": [
        #         {
        #             "@type": "idx:Index",
        #             "@id": "http://testserver/indexes/test-objects/title/index"
        #         },
        #         {
        #             "@id": "http://testserver/indexes/test-objects/title/index#target",
        #             "sh:path": "rdf:type",
        #             "sh:hasValue": {
        #                 "@id": "test:Object"
        #             }
        #         }
        #     ]
        # }
        
        # Clear all test objects
        TestObject.objects.all().delete()
        
        response = self.get_view_response(self.index_url, kwargs={
                    'field_name': self.field_name
                })
        data = response.data
        
        # The index structure should still be valid but with no pattern entries
        self.assertEqual(
            response.status_code,
            200,
            "Index should be accessible even with no objects"
        )
        
        # Should still have @graph with index and target objects
        graph = data['@graph']
        self.assertEqual(
            len([item for item in graph if item.get('@type') == 'idx:Index']),
            1,
            "Empty response should still contain the index object"
        )
        self.assertEqual(
            len([item for item in graph if item['@id'].endswith('#target')]),
            1,
            "Empty response should still contain the target shape"
        )
        
        # But should have no pattern entries
        pattern_entries = [
            item for item in graph 
            if item.get('@type') == 'idx:IndexEntry'
        ]
        self.assertEqual(
            len(pattern_entries),
            0,
            "Empty model should have no pattern entries"
        ) 