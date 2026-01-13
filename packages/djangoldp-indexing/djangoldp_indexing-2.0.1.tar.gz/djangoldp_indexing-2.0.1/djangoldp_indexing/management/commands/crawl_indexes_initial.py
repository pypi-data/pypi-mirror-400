import requests
import json
import os
from urllib.parse import urlparse, urljoin, urlunparse
from apscheduler.schedulers.blocking import BlockingScheduler
from django.conf import settings
from django.core.management.base import BaseCommand
from djangoldp.models import LDPSource
import re

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

    def save_data(self, url, data, root_location, root_url, save_as_file=False):
        """Save JSON data to a local file, maintaining the directory structure."""
        parsed_url = urlparse(url)
        path = parsed_url.path.lstrip('/')

        if save_as_file and not url in self.regenerated_urls:
            path = path.rstrip('/')

            print(f"Saving data to {path}")
            if path == '': path = 'profile'

            # Save data directly to a file, treat path as file name
            file_path = os.path.join(root_location, path + '.jsonld')

            # Read existing data if it exists
            old_data = None
            merged_data = None
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    old_data = json.load(f)

            if old_data:
                # Determine the merging strategy
                if '@graph' in old_data and '@graph' in data:
                    merged_data = self.merge_jsonld_graphs(old_data, data)
                else:
                    merged_data = data

                if merged_data:
                    # print(f"Merging {old_data['@graph'][0]['@id']} with {data['@graph'][0]['@id']}: {json.dumps(merged_data)}")
                    with open(file_path, 'w') as f:
                        json.dump(merged_data, f, indent=2)
                    self.regenerated_urls.append(url)
            else:
                dir_name = os.path.dirname(file_path)
                if dir_name and not os.path.exists(dir_name):
                    os.makedirs(dir_name, exist_ok=True)

                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)

                self.regenerated_urls.append(url)
        else:
            dir_path = os.path.join(root_location, os.path.dirname(path))
            if not path:
                path = 'index'
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)

    def read_local_data(self, path, root_location):
        """Read JSON data from a local file."""
        file_path = os.path.join(root_location, path + '.jsonld') 

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return None

    # def merge_graphs(self, old_data, new_data):
    #     """Merge old and new data, combining @graph arrays without duplicates."""
    #     print(f"Merging {old_data['@graph'][0].get('@id')} with {new_data['@graph'][0].get('@id')}")
    #     old_graph = {item['@id']: item for item in old_data.get('@graph', []) if item.get('@type')}
    #     new_graph = {item['@id']: item for item in new_data.get('@graph', []) if item.get('@type') in ['idx:IndexEntry', 'ex:PropertyIndexRegistration', 'solid:TypeIndexRegistration', 'ex:StartsWithIndexRegistration']}
        
    #     print(f"Merging {json.dumps(old_graph)} with {json.dumps(new_graph)}")
    #     merged_graph = {**old_graph, **new_graph}  # merge dictionaries, new_data will overwrite old_data for duplicate keys    

    #     merged_data = {
    #         "@context": old_data.get("@context"),
    #         "@graph": list(merged_graph.values())
    #     }
    #     return merged_data

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


    # def merge_instances(self, old_data, new_data):
    #     """Merge old and new data, combining ex:instance arrays without duplicates."""
    #     merged_data = old_data.copy()
    #     if 'ex:instance' in old_data and 'ex:instance' in new_data:
    #         merged_instances = self.diff_references(old_data, new_data)
    #         merged_data['ex:instance'] = merged_instances
    #     return merged_data


    # def diff_references(self, old_data, new_data):
    #     """Compare and merge ex:instance arrays in old and new data."""
    #     old_instances = set(old_data.get('ex:instance', []))
    #     new_instances = set(new_data.get('ex:instance', []))
    #     return list(old_instances | new_instances)


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


    def process_indexes(self, url, aggregated_data, root_location, root_url, save_as_file=False):
        """Process indexes recursively."""
        data = self.fetch_data(url)

        if data:
          self.save_data(url, data, root_location, root_url, save_as_file)

          if url not in aggregated_data['indexes']:
              aggregated_data['indexes'][url] = data

          if (data.get('@type') in ['ldp:Container'] and
              data.get('ldp:contains', [])):
            for item in data['ldp:contains']:
              if item.get('@type') in ['idx:Index']:
                self.process_indexes(item['@id'], aggregated_data, root_location, root_url, True)

          for item in data.get('@graph', []):
              if item.get('@id') == url:
                  continue
              if item.get('@type') in ['idx:IndexEntry', 'ex:StartsWithIndexRegistration']:
                  instances_in = item.get('idx:hasSubIndex') or item.get('rdfs:seeAlso')
                  if instances_in:
                      self.process_indexes(instances_in, aggregated_data, root_location, root_url, True)
              elif item.get('@type') in ['idx:Index', 'ex:PropertyIndex', 'ex:StartsWithIndex']:
                  self.process_indexes(item['@id'], aggregated_data, root_location, root_url, True)

          if not data.get('@graph', None) and '@type' in data and data['@type'] in ['idx:Index', 'ex:PropertyIndex', 'ex:StartsWithIndex']:
              self.save_data(data['@id'], data, root_location, root_url, True)

    # Function to deduplicate entries based on '@id'
    def deduplicate_graph(self, data):
        seen_ids = set()
        unique_graph = []
        seen_base_ids = {}
        seen_targets = set()

        for item in data:
            match = re.match(r"(.*#)(\d+)$", item['@id'])
            if match:
              if 'idx:hasTarget' in item and item['idx:hasTarget'] not in seen_targets:
                base_id, suffix = match.groups()
                seen_ids.add(item["@id"])
                if base_id not in seen_base_ids:
                  seen_base_ids[base_id] = []
                seen_base_ids[base_id].append(item)
                seen_targets.add(item['idx:hasTarget'])
            elif item['@id'] not in seen_ids:
                unique_graph.append(item)
                seen_ids.add(item['@id'])

        for base_id, entries in seen_base_ids.items():
          for i, entry in enumerate(entries):
              new_id = f"{base_id}{i}"
              entry["@id"] = new_id
              unique_graph.append(entry)
        return unique_graph

    def aggregate_data(self, servers, root_location, root_url):
        """Aggregate data from all servers and endpoints."""
        aggregated_data = {
            'indexes': {},
            'users': []
        }

        for server in servers:
            try:
                # Step 1: Fetch root data
                root_data = self.fetch_data(server + 'profile')
                self.save_data(server, root_data, root_location, root_url, save_as_file=True)
                
                # Step 2: Extract solid:publicTypeIndex
                public_type_index_url = self.get_public_type_index(root_data)
                if not public_type_index_url:
                    print(f"No publicTypeIndex found for {server}")
                    continue

                # Step 3: Fetch publicTypeIndex data
                public_type_index_data = self.fetch_data(public_type_index_url)
                self.save_data(public_type_index_url, public_type_index_data, root_location, root_url, save_as_file=True)

                # Step 4: Extract instance containers
                instance_containers = self.get_instance_containers(public_type_index_data)
                print(f"Processing instance containers for {server}: {instance_containers}")

                for container_url in instance_containers:
                    # Step 5: Fetch and process indexes
                    self.process_indexes(container_url, aggregated_data, root_location, root_url, True)


            except requests.RequestException as e:
                print(f"Error fetching data from {server}: {e}")
                pass

        #for every file created in the root location, check the @id and the values of ex:instancesIn, rdfs:seeAlso
        #and rewrite them using root_url as base_url
        for root, dirs, files in os.walk(root_location):
            for file in files:
                file_path = os.path.join(root, file)
                print(f"Rewriting IDs in {file_path}")
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self.rewrite_ids(data, root_url)
                    # additionnally, if you find the same data twice in the @graph in the file, remove one instance
                    if 'ldp:contains' in data:
                        data['ldp:contains'] = self.deduplicate_graph(data['ldp:contains'])

                    if '@graph' in data:
                        data['@graph'] = self.deduplicate_graph(data['@graph'])

                    with open(file_path, 'w') as f:
                        json.dump(data, f, indent=2)

        return aggregated_data

    def run_crawler(self, root_location, root_url):
        """Run the crawler and output the aggregated JSON."""
        sources = LDPSource.objects.filter(federation='indexes')
        servers = [source.urlid for source in sources]

        root_url = getattr(settings, 'BASE_URL', root_url) + '/' + root_location
        # print(f"Fetching data from {servers} and saving it to {root_location} with base URL {root_url}")
        aggregated_data = self.aggregate_data(servers, root_location, root_url)


    def handle(self, *args, **kwargs):
        root_location = kwargs['root_location']
        root_url = kwargs['root_url']

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

