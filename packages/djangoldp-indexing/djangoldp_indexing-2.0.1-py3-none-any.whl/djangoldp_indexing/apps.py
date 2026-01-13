import yaml, os, sys, logging
from django.apps import AppConfig
from django.apps import apps

logger = logging.getLogger(__name__)

class DjangoLDPIndexingConfig(AppConfig):
    name = 'djangoldp_indexing'
    verbose_name = 'DjangoLDP Indexing'

    def ready(self):
        """
        Initialize the app. This method will set the indexed_fields meta
        for models based on the configuration defined in indexing_config.yml.
        """
        # Get the path of the script that was called (manage.py)
        manage_py_path = os.path.abspath(sys.argv[0])
        # Define the path to the YAML file relative to manage.py
        yaml_file_path = os.path.join(os.path.dirname(manage_py_path), 'indexing_config.yml')

        # Load the YAML configuration
        try:
            with open(yaml_file_path, 'r') as file:
                indexing_config = yaml.safe_load(file)
                logger.info("Loaded indexing configuration: %s", indexing_config)
        except FileNotFoundError:
            logger.error("Indexing configuration file not found: %s", yaml_file_path)
            return
        except yaml.YAMLError as e:
            logger.error("Error loading YAML file: %s", e)
            return


        # Iterate through the package configuration
        for package_name, models in indexing_config.items():
            for model_name, config in models.items():
                try:
                    # Get the model class from the installed apps
                    model = apps.get_model(package_name, model_name)  # Use package_name for app label
                    logger.info("Adding indexed_fields %s to : %s", model_name, config.get('indexed_fields', []))
                    # Set the indexed_fields meta
                    model._meta.indexed_fields = config.get('indexed_fields', [])
                except LookupError:
                    print(f"Model {model_name} not found in package {package_name}.")
                except Exception as e:
                    print(f"Error setting indexed_fields for {model_name}: {e}") 