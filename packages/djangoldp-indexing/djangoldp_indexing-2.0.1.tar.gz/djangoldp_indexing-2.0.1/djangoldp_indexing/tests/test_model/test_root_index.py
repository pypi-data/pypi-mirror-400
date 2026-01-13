from ..models import TestObject
from ..base import IndexTestCase
from ...views.model.root import ModelRootIndexView


class TestModelRootIndexView(IndexTestCase):
    """Test suite for ModelRootIndexView.
    
    Tests the model root index endpoint that provides the index structure
    for a specific model, validating:
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
        
        self.index_url = '/indexes/test-objects/index'
        self.tested_view = ModelRootIndexView()

    def test_renderer(self):
        """Test that the model uses the JSONLD renderer"""
        self._test_renderer()
        
    def test_response_format(self):
        """Test that the response follows the specified JSON-LD format."""
        response = self.get_view_response()
        data = response.data
        
        # Example expected format:
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
        #             "@id": "http://testserver/indexes/test-objects/index"
        #         },
        #         {
        #             "@id": "http://testserver/indexes/test-objects/index#target",
        #             "sh:path": "rdf:type",
        #             "sh:hasValue": {
        #                 "@id": "test:Object"
        #             }
        #         },
        #         {
        #             "@id": "http://testserver/indexes/test-objects/index#title",
        #             "@type": "idx:IndexEntry",
        #             "idx:hasShape": {
        #                 "@type": "sh:NodeShape",
        #                 "sh:closed": "false",
        #                 "sh:property": [
        #                     "http://testserver/indexes/test-objects/index#target",
        #                     {
        #                         "sh:path": "sib:title"
        #                     }
        #                 ]
        #             },
        #             "idx:hasSubIndex": "http://testserver/indexes/test-objects/title/index"
        #         }
        #     ]
        # }
        
        # Verify basic JSON-LD structure
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
        
        # Find field index entries
        field_entries = [
            item for item in data['@graph'] 
            if item.get('@type') == 'idx:IndexEntry'
        ]
        self.assertEqual(
            len(field_entries),
            len(TestObject._meta.indexed_fields),
            f"Number of index entries ({len(field_entries)}) should match number of indexed fields ({len(TestObject._meta.indexed_fields)})"
        )
        
        # Verify title field entry
        title_entry = next(
            (item for item in field_entries 
             if item['@id'].endswith('#title')),
            None
        )
        self.assertIsNotNone(
            title_entry,
            "Graph should include an index entry for the 'title' field"
        )
        self.assertEqual(
            title_entry['@type'],
            'idx:IndexEntry',
            "Field entry should be of type idx:IndexEntry"
        )
        
        # Verify title field shape
        shape = title_entry['idx:hasShape']
        self.assertEqual(
            shape['@type'],
            'sh:NodeShape',
            "Field shape should be of type sh:NodeShape"
        )
        self.assertEqual(
            shape['sh:closed'],
            'false',
            "Field shape should not be closed"
        )
        self.assertEqual(
            len(shape['sh:property']),
            2,
            "Field shape should have exactly 2 properties (target + field)"
        )
        
        # Verify target reference
        self.assertEqual(
            shape['sh:property'][0]['@id'],
            f'http://testserver{self.index_url}#target',
            "First property should reference the target shape"
        )
        
        # Verify field property
        field_prop = shape['sh:property'][1]
        self.assertEqual(
            field_prop['sh:path'],
            'sib:title',
            "Field property should reference the 'title' field"
        )
        
        # Verify sub-index reference
        self.assertEqual(
            title_entry['idx:hasSubIndex'],
            f'http://testserver/indexes/test-objects/title/index',
            "Field entry should reference its sub-index"
        )

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
        #             "@id": "http://testserver/indexes/test-objects/index"
        #         },
        #         {
        #             "@id": "http://testserver/indexes/test-objects/index#target",
        #             "sh:path": "rdf:type",
        #             "sh:hasValue": {
        #                 "@id": "test:Object"
        #             }
        #         },
        #         {
        #             "@id": "http://testserver/indexes/test-objects/index#title",
        #             "@type": "idx:IndexEntry",
        #             "idx:hasShape": {
        #                 "@type": "sh:NodeShape",
        #                 "sh:closed": "false",
        #                 "sh:property": [
        #                     "http://testserver/indexes/test-objects/index#target",
        #                     {
        #                         "sh:path": "sib:title"
        #                     }
        #                 ]
        #             },
        #             "idx:hasSubIndex": "http://testserver/indexes/test-objects/title/index"
        #         }
        #     ]
        # }
        
        # Clear all test objects
        TestObject.objects.all().delete()
        
        response = self.get_view_response()
        data = response.data
        
        # The index structure should be the same even with no objects
        self.assertEqual(
            response.status_code,
            200,
            "Index should be accessible even with no objects"
        )
        
        # Should still have @graph with all components
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
        
        # Verify field entries are still present
        field_entries = [
            item for item in graph 
            if item.get('@type') == 'idx:IndexEntry'
        ]
        self.assertEqual(
            len(field_entries),
            len(TestObject._meta.indexed_fields),
            "All indexed fields should be listed even with no objects"
        ) 