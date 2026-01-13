from djangoldp.views.ldp_api import LDPAPIView
from djangoldp.views.commons import JSONLDRenderer
from django.conf import settings
from django.utils.module_loading import import_string


def _resolve_permission_classes():
    """
    Resolve permission class strings to actual class objects.

    Reads DJANGOLDP_INDEXING_PERMISSION_CLASSES from settings and imports
    the classes. Supports both string paths and class objects.

    Returns:
        list: List of permission class objects
    """
    permission_classes_config = getattr(
        settings,
        'DJANGOLDP_INDEXING_PERMISSION_CLASSES',
        []
    )

    if not permission_classes_config:
        return []

    resolved_classes = []
    for perm_class in permission_classes_config:
        if isinstance(perm_class, str):
            # Import the class from string path
            try:
                resolved_classes.append(import_string(perm_class))
            except (ImportError, AttributeError) as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(
                    f"Failed to import permission class '{perm_class}': {e}"
                )
        else:
            # Already a class object
            resolved_classes.append(perm_class)

    return resolved_classes


class IndexBaseView(LDPAPIView):
    """Base view for all indexing-related views.

    Provides common functionality for index views including:
    - JSON-LD rendering
    - Response formatting
    - Error handling
    - Permission checking via DRF permission_classes
    """
    renderer_classes = (JSONLDRenderer,)

    def get_permissions(self):
        """
        Get permission instances from settings.

        Allows flexible configuration of permissions for indexing views via
        DJANGOLDP_INDEXING_PERMISSION_CLASSES setting.

        Configure in settings.yml:
        DJANGOLDP_INDEXING_PERMISSION_CLASSES:
          - djangoldp_tems.permissions_v3.EdcContractPermissionV3

        Returns:
            list: List of permission instances
        """
        permission_classes = _resolve_permission_classes()
        return [permission() for permission in permission_classes]
