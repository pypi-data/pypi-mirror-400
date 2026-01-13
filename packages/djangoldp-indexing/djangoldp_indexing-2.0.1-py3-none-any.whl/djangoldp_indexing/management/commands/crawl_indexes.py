import requests
import json
import os
from urllib.parse import urlparse, urljoin, urlunparse
from apscheduler.schedulers.blocking import BlockingScheduler
from django.conf import settings
from django.core.management.base import BaseCommand
from djangoldp.models import LDPSource
import re
import copy

class Command(BaseCommand):
    help = 'Crawl JSON-LD data from specified instances indexes and save them to local files.'
    regenerated_urls = []

    def add_arguments(self, parser):
        parser.add_argument(
          '--root_location',
          type=str,
          help='The root location where to save the files',
          nargs='?',
          default='fedex'
        )
        parser.add_argument(
          '--root_url',
          type=str,
          help='The root url where to expose the files',
          nargs='?',
          default='http://localhost:8000/fedex'
        )

    def fetch_data(self, url):
        """Fetch data from a given URL."""
        try:
            headers = {
                'X-Bypass-Policy': 'true'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            return {}

    def rewrite_property(self, data, property_name, root_url):
        new_netloc = urlparse(root_url).netloc
        """Rewrite a property with the base URL."""
        if property_name in data:
            try:
              parsed_uri = urlparse(data[property_name])
              if not urlparse(root_url).path in parsed_uri.path:
                new_path = urlparse(root_url).path + parsed_uri.path
              else:
                new_path = parsed_uri.path
              data[property_name] = parsed_uri._replace(netloc=new_netloc, path=new_path).geturl()
            except:
              if ("@type" in data[property_name] and
                  data[property_name]["@type"] == "sh:NodeShape" and
                  property_name == "idx:hasShape"):
                try:
                  parsed_uri = urlparse(data[property_name]['sh:property'][0])
                  if not urlparse(root_url).path in parsed_uri.path:
                    new_path = urlparse(root_url).path + parsed_uri.path
                  else:
                    new_path = parsed_uri.path
                  data[property_name]['sh:property'][0] = parsed_uri._replace(netloc=new_netloc, path=new_path).geturl()
                except:
                  pass
        return data

    def rewrite_ids(self, data, root_url):
        """Rewrite @id fields with the base URL."""
        if '@graph' in data:
            for item in data['@graph']:
                if '@id' in item and ('@type' in item and (
                    item['@type'] in [
                      'foaf:PersonalProfileDocument',
                      'idx:Index',
                      'idx:IndexEntry',
                      'foaf:primaryTopic',
                      'solid:TypeIndexRegistration',
                      'solid:TypeIndex',
                      'sh:NodeShape',
                    ]) or ('solid:publicTypeIndex' in item
                      or 'idx:hasSubIndex' in item
                      or 'foaf:primaryTopic' in item
                      or 'sh:path' in item)):
                    item = self.rewrite_property(item, '@id', root_url)
                    item = self.rewrite_property(item, 'solid:publicTypeIndex', root_url)
                    item = self.rewrite_property(item, 'foaf:primaryTopic', root_url)
                    item = self.rewrite_property(item, 'idx:hasSubIndex', root_url)
                    item = self.rewrite_property(item, 'solid:instanceContainer', root_url)
                    item = self.rewrite_property(item, 'solid:instance', root_url)
                    item = self.rewrite_property(item, 'idx:hasShape', root_url)
        elif '@id' in data:
            data = self.rewrite_property(data, '@id', root_url)
            data = self.rewrite_property(data, 'solid:instanceContainer', root_url)
            data = self.rewrite_property(data, 'solid:instance', root_url)
            if 'ldp:contains' in data:
              for item in data['ldp:contains']:
                  if '@id' in item and (
                        item['@type'] in [
                            'idx:Index',
                            'idx:IndexEntry'
                        ]
                    ):
                    item = self.rewrite_property(item, '@id', root_url)
        return data

    def get_public_type_index(self, root_data):
        """Extract solid:publicTypeIndex from root data."""
        for item in root_data.get('@graph', []):
            if 'solid:publicTypeIndex' in item:
                return item['solid:publicTypeIndex']
        return None

    def get_instance_containers(self, public_type_index_data):
        """Extract solid:instanceContainer from publicTypeIndex data."""
        instance_containers = []
        for item in public_type_index_data.get('@graph', []):
            if item.get('@type') == 'solid:TypeIndexRegistration' and item.get('solid:forClass') == 'idx:Index':
                if 'solid:instanceContainer' in item:
                  instance_containers.append(item['solid:instanceContainer'])
                elif 'solid:instance' in item:
                  instance_containers.append(item['solid:instance'])
        return instance_containers

    def merge_jsonld_graphs(self, old_graph, new_graph):
        # Ensure the contexts are the same, otherwise merging is complex
        # if old_graph['@context'] != new_graph['@context']:
        #     raise ValueError("Contexts do not match, merging is not straightforward.")

        # Combine the @graph entries
        merged_graph = old_graph['@graph'] + new_graph['@graph']

        # Remove duplicates based of combination of @id and hasTarget
        seen_ids = set()
        seen_targets = set()
        unique_graph = []
        for entry in merged_graph:
            if entry["@id"] not in seen_ids and "idx:hasTarget" in entry and entry["idx:hasTarget"] not in seen_targets:
                unique_graph.append(entry)
                seen_targets.add(entry["idx:hasTarget"])
                seen_ids.add(entry["@id"])
            elif entry["@id"] not in seen_ids:
                unique_graph.append(entry)
                seen_ids.add(entry["@id"])

        # Create the merged JSON-LD structure
        merged_jsonld = {
            "@context": old_graph["@context"],
            "@graph": unique_graph
        }
        return merged_jsonld

    def process_indexes(self, url, aggregated_data, root_location, root_url):
        """Process indexes recursively."""

        data = self.fetch_data(url)

        if data:
          if url not in aggregated_data['indexes']:
              aggregated_data['indexes'][url] = {
                'data': data,
              }

    def aggregate_data(self, servers, root_location, root_url):
        """Aggregate data from all servers and endpoints."""
        aggregated_data = {
            'indexes': {},
            'users': [],
            'fedex_profile': None
        }

        for server in servers:
            try:
                # Step 1: Fetch root data
                server_profile = self.fetch_data(server + 'profile')
                
                #Create or update the fedex profile
                fedex_profile = self.rewrite_ids(copy.deepcopy(server_profile), root_url)
                if (aggregated_data['fedex_profile'] is None and fedex_profile is not None and '@graph' in fedex_profile):
                    aggregated_data['fedex_profile'] = fedex_profile
                elif (fedex_profile is not None and '@graph' in fedex_profile):
                    aggregated_data['fedex_profile'] = self.merge_jsonld_graphs(aggregated_data['fedex_profile'], fedex_profile)
                
                # Step 2: Extract solid:publicTypeIndex
                public_type_index_url = self.get_public_type_index(server_profile)
                if not public_type_index_url:
                    print(f"No publicTypeIndex found for {server}")
                    continue

                # Step 3: Fetch publicTypeIndex data
                public_type_index_data = self.fetch_data(public_type_index_url)

                # Step 4: Extract instance containers that relate to the publicTypeIndex
                instance_containers = self.get_instance_containers(public_type_index_data)
                print(f"Processing index related instance containers for {server}: {instance_containers}")

                for container_url in instance_containers:
                    # Step 5: Fetch and process indexes
                    self.process_indexes(container_url, aggregated_data, root_location, root_url)


            except requests.RequestException as e:
                print(f"Error fetching data from {server}: {e}")
                pass

        return aggregated_data
    
    def group_containers_by_rdf_type(self, aggregated_data, root_url):
        # Dictionary to store containers grouped by their types
        type_containers = {}

        # Process each index to extract type information and group containers
        # for url, index in [item for item in aggregated_data['indexes'].items() if item['nesting_level'] == nesting_level]:
        for url, index in aggregated_data['indexes'].items():
            data = index['data']
            if '@graph' not in data:
                continue
                
            # Find the shape entry for rdf:type
            shape_entry = next((item for item in data['@graph'] if 
                                '@id' in item and 
                                item['@id'].endswith('#target') and
                                'sh:path' in item and 
                                item['sh:path'] == 'rdf:type'
                            ), None)
            
            if shape_entry and 'sh:hasValue' in shape_entry and '@id' in shape_entry['sh:hasValue']:
                types = shape_entry['sh:hasValue'].get('@id')
                # Type may be a list or a string
                if not isinstance(types, list):
                    types = [types]

                # Now, group the containers by their types
                for type_id in types:
                    if type_id not in type_containers:
                        # First occurrence of this type_id in this nesting level
                        type_containers[type_id] = {
                            'shape': copy.deepcopy(shape_entry),
                            'containers': []
                        }
                        type_containers[type_id]['shape']['sh:hasValue']['@id'] = type_id
                        type_containers[type_id]['shape']['@id'] = f"{root_url}/{type_id.replace(':', '-').lower()}/index#target"
                        
                    # Add the index to the type container
                    type_containers[type_id]['containers'].append({
                        'url': url,
                        'entry': next((item for item in data['@graph'] if item.get('@type') == 'idx:Index'), None)
                    })
        return type_containers

    def generate_federated_indexes(self, type_containers, root_location, root_url):
        """Generate federated index files for each type of data."""
        for type_id, info in type_containers.items():
            # Create file name from type_id (e.g., "tems:3DObject" -> "tems-3dobject")
            type_name = type_id.replace(':', '-').lower()
            file_path = os.path.join(root_location, f"{type_name}.jsonld")

            if file_path and not os.path.exists(root_location):
                os.makedirs(root_location, exist_ok=True)

            # Create the federated index structure
            federated_index = {
                "@context": settings.LDP_RDF_CONTEXT,
                "@graph": [
                    {
                        "@type": "idx:Index",
                        "@id": f"{root_url}/{type_name}/index"
                    },
                    info['shape']  # Include the shape definition
                ]
            }
            
            # Add an IndexEntry for each container, referencing the sub-index
            for idx, container in enumerate(info['containers']):
                entry = {
                    "@id": f"{root_url}/{type_name}/index#source{idx}",
                    "@type": "idx:IndexEntry",
                    "idx:hasShape": {
                        "@type": "sh:NodeShape",
                        "sh:closed": "false",
                        # "sh:property": [
                        #     info['shape']['@id']
                        # ],
                        "sh:property": {
                            "@id": info['shape']['@id']
                        }
                    },
                    "idx:hasSubIndex": container['url']  # Reference the sub-index
                }
                federated_index['@graph'].append(entry)

            # Save the federated index file
            with open(file_path, 'w') as f:
                json.dump(federated_index, f, indent=2)

    def generate_profile_file(self, aggregated_data, root_location):
        """Generate the profile.jsonld file."""
        file_path = os.path.join(root_location, 'profile.jsonld')
        print(f"Generating profile.jsonld file at {file_path}")
        with open(file_path, 'w') as f:
            json.dump(aggregated_data['fedex_profile'], f, indent=2)
                        
    def generate_public_type_index_file(self, type_containers, root_location, root_url):
        """Generate the publicTypeIndex.jsonld file."""
        os.makedirs(f"{root_location}/profile", exist_ok=True)
        file_path = os.path.join(root_location, 'profile/publicTypeIndex.jsonld')
        print(f"Generating publicTypeIndex.jsonld file at {file_path}")
        publicTypeIndex = {
            '@context': settings.LDP_RDF_CONTEXT,
            '@graph': [
                {
                    "@id": f"{root_url}/profile/publicTypeIndex",
                    "@type": "solid:TypeIndex"
                }
            ]
        }
        
        for type_id, info in type_containers.items():
            type_name = type_id.replace(':', '-').lower()
            publicTypeIndex['@graph'].append({
                "@id": f"{root_url}/profile/publicTypeIndex#{type_name}",
                "@type": "solid:TypeIndexRegistration",
                "solid:forClass": "idx:Index",
                "solid:instance": f"{root_url}/{type_name}/index"
            })
            
        with open(file_path, 'w') as f:
            json.dump(publicTypeIndex, f, indent=2)

    def generate_federated_index(self, aggregated_data, root_location, root_url):
        """Generate federated index files for each type of data."""
        type_containers = self.group_containers_by_rdf_type(aggregated_data, root_url)
        self.generate_federated_indexes(type_containers, root_location, root_url)
        self.generate_profile_file(aggregated_data, root_location)
        self.generate_public_type_index_file(type_containers, root_location, root_url)
    
    def run_crawler(self, root_location, root_url):
        """Run the crawler and output the aggregated JSON."""
        sources = LDPSource.objects.filter(federation='indexes')
        servers = [source.urlid for source in sources]

        #root_url = getattr(settings, 'BASE_URL', root_url) + '/' + root_location
        # print(f"Fetching data from {servers} and saving it to {root_location} with base URL {root_url}")
        aggregated_data = self.aggregate_data(servers, root_location, root_url)
        
        # Generate federated indexes after aggregating all data
        self.generate_federated_index(aggregated_data, root_location, root_url)

        
    def handle(self, *args, **kwargs):
        root_location = f"{settings.STATIC_ROOT}/{kwargs['root_location']}"
        root_url = kwargs['root_url']
        print(f"Running crawler with root_location={root_location}, root_url={root_url}")

        # Set up the scheduler
        scheduler = BlockingScheduler()

        # Schedule the crawler to run every X hours (e.g., every 6 hours)
        # X = 6  # Change X to the number of hours you need
        # scheduler.add_job(lambda: self.run_crawler(root_location), 'interval', hours=X)
        self.run_crawler(root_location, root_url)

        # try:
        #     print(f"Scheduler started. The crawler will run every {X} hours.")
        #     scheduler.start()
        # except (KeyboardInterrupt, SystemExit):
        #     pass

