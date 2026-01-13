"""DjangoLDP extension for model indexing and pattern-based search."""

from django.db.models import options

__version__ = '2.0.1'

# Register indexed_fields as a valid Meta option
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('indexed_fields',)

default_app_config = 'djangoldp_indexing.apps.DjangoLDPIndexingConfig'