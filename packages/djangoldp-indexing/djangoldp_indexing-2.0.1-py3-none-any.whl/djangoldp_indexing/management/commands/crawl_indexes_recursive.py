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
          'root_location',
          type=str,
          help='The root location where to save the files',
          nargs='?',
          default='fedex'
        )
        parser.add_argument(
          'root_url',
          type=str,
          help='The root url where to expose the files',
          nargs='?',
          default='http://localhost:8000/fedex'
        )
        parser.add_argument(
          '--max_recursion',
          type=int,
          help='The number of levels of recursion to follow on indexes, 0 means no limit to the depth',
          default=1
        )

    def fetch_data(self, url):
        """Fetch data from a given URL."""
        try:
          response = requests.get(url)
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

    def process_indexes(self, url, aggregated_data, root_location, root_url, max_recursion, save_as_file=False, nesting_level=0):
        """Process indexes recursively."""
        # stop recursion if we have reached the maximum recursion level
        if max_recursion > 0 and nesting_level > max_recursion-1:
          return

        data = self.fetch_data(url)

        if data:
          aggregated_data['depth'] = max(aggregated_data['depth'], nesting_level+1)

          if url not in aggregated_data['indexes']:
              aggregated_data['indexes'][url] = {
                'data': data,
                'nesting_level': nesting_level
              }

          # if we are in a non empty ldp:Container, and it contains "idx:Index" entries, process them
          if (data.get('@type') in ['ldp:Container'] and
              data.get('ldp:contains')):
            for item in data['ldp:contains']:
              if item.get('@type') in ['idx:Index']:
                self.process_indexes(item['@id'], aggregated_data, root_location, root_url, max_recursion, save_as_file, nesting_level + 1)

          # process the entries in the @graph
          for item in data.get('@graph', []):
              #ignore the entry that is the container itself
              if item.get('@id') == url:
                  continue
              # process the entries that are idx:IndexEntry or ex:StartsWithIndexRegistration if they have an idx:hasSubIndex or rdfs:seeAlso predicate
              if item.get('@type') in ['idx:IndexEntry', 'ex:StartsWithIndexRegistration']:
                  instances_in = item.get('idx:hasSubIndex') or item.get('rdfs:seeAlso')
                  if instances_in:
                      self.process_indexes(instances_in, aggregated_data, root_location, root_url, max_recursion, save_as_file, nesting_level + 1)
              # process the entries that are idx:Index, ex:PropertyIndex or ex:StartsWithIndex using the @id as url
              elif item.get('@type') in ['idx:Index', 'ex:PropertyIndex', 'ex:StartsWithIndex']:
                  self.process_indexes(item['@id'], aggregated_data, root_location, root_url, max_recursion, save_as_file, nesting_level + 1)

    def aggregate_data(self, servers, root_location, root_url, max_recursion):
        """Aggregate data from all servers and endpoints."""
        aggregated_data = {
            'indexes': {},
            'users': [],
            'depth': 0
        }

        for server in servers:
            try:
                # Step 1: Fetch root data
                root_data = self.fetch_data(server + 'profile')
                
                # Step 2: Extract solid:publicTypeIndex
                public_type_index_url = self.get_public_type_index(root_data)
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
                    self.process_indexes(container_url, aggregated_data, root_location, root_url, max_recursion, False)


            except requests.RequestException as e:
                print(f"Error fetching data from {server}: {e}")
                pass

        # Generate federated indexes after aggregating all data
        self.generate_federated_indexes(aggregated_data, root_location, root_url)

        #for every file created in the root location, check the @id and the values of ex:instancesIn, rdfs:seeAlso
        #and rewrite them using root_url as base_url
        # for root, dirs, files in os.walk(root_location):
        #     for file in files:
        #         file_path = os.path.join(root, file)
        #         print(f"Rewriting IDs in {file_path}")
        #         with open(file_path, 'r') as f:
        #             data = json.load(f)
        #             self.rewrite_ids(data, root_url)
        #             # additionnally, if you find the same data twice in the @graph in the file, remove one instance
        #             if 'ldp:contains' in data:
        #                 data['ldp:contains'] = self.deduplicate_graph(data['ldp:contains'])

        #             if '@graph' in data:
        #                 data['@graph'] = self.deduplicate_graph(data['@graph'])

        #             with open(file_path, 'w') as f:
        #                 json.dump(data, f, indent=2)

        return aggregated_data
    
    def generate_federated_indexes(self, aggregated_data, root_location, root_url):
        """Generate federated index files for each type of data."""
        # Dictionary to store containers grouped by their types
        type_containers = {}

        for nesting_level in range(0, aggregated_data['depth']):
            # Process each index to extract type information and group containers
            # for url, index in [item for item in aggregated_data['indexes'].items() if item['nesting_level'] == nesting_level]:
            for url, index in aggregated_data['indexes'].items():
                if index['nesting_level'] != nesting_level:
                    continue
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

                    if type_containers.get(nesting_level, None) is None:
                        # First time we see this nesting level
                        type_containers[nesting_level] = {}

                    # Now, group the containers by their types
                    for type_id in types:
                        if type_id not in type_containers[nesting_level]:
                            # First occurrence of this type_id in this nesting level
                            type_containers[nesting_level][type_id] = {
                                'shape': copy.deepcopy(shape_entry),
                                'containers': []
                            }
                            type_containers[nesting_level][type_id]['shape']['sh:hasValue']['@id'] = type_id
                        # Add the index to the type container
                        type_containers[nesting_level][type_id]['containers'].append({
                            'url': url,
                            'entry': next((item for item in data['@graph'] if item.get('@type') == 'idx:Index'), None),
                            'source_name': urlparse(url).netloc.replace(':', '-')
                        })
        
        for nesting_level, containers in type_containers.items():
            # Generate a federated index file for each type
            for type_id, info in containers.items():
                # Create file name from type_id (e.g., "tems:3DObject" -> "3dobject")
                type_name = type_id.replace(':', '-').lower()
                file_path = os.path.join(root_location, f"{type_name}.jsonld")

                if file_path and not os.path.exists(root_location):
                    os.makedirs(root_location, exist_ok=True)

                # Create the federated index structure
                federated_index = {
                    "@context": "https://cdn.startinblox.com/owl/context.jsonld",
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
                            "sh:property": [
                                info['shape']['@id']
                            ]
                        },
                        "idx:hasSubIndex": container['url']  # Reference the sub-index
                    }
                    federated_index['@graph'].append(entry)

                # Save the federated index file
                with open(file_path, 'w') as f:
                    json.dump(federated_index, f, indent=2)

    def run_crawler(self, root_location, root_url, max_recursion):
        """Run the crawler and output the aggregated JSON."""
        sources = LDPSource.objects.filter(federation='indexes')
        servers = [source.urlid for source in sources]

        root_url = getattr(settings, 'BASE_URL', root_url) + '/' + root_location
        # print(f"Fetching data from {servers} and saving it to {root_location} with base URL {root_url}")
        aggregated_data = self.aggregate_data(servers, root_location, root_url, max_recursion)
        
    def handle(self, *args, **kwargs):
        root_location = f"{settings.STATIC_ROOT}/{kwargs['root_location']}"
        root_url = kwargs['root_url']
        max_recursion = int(kwargs['max_recursion'])
        print(f"Running crawler with root_location={root_location}, root_url={root_url}, maw_recursion={max_recursion}")

        # Set up the scheduler
        scheduler = BlockingScheduler()

        # Schedule the crawler to run every X hours (e.g., every 6 hours)
        # X = 6  # Change X to the number of hours you need
        # scheduler.add_job(lambda: self.run_crawler(root_location), 'interval', hours=X)
        self.run_crawler(root_location, root_url, max_recursion)

        # try:
        #     print(f"Scheduler started. The crawler will run every {X} hours.")
        #     scheduler.start()
        # except (KeyboardInterrupt, SystemExit):
        #     pass

