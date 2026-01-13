import requests
import os
import json
import warnings
from django.conf import settings
from django.http import Http404, JsonResponse
from django.utils.http import http_date
from django.views.static import was_modified_since
from django.core.exceptions import PermissionDenied
from django.utils.module_loading import import_string
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes as drf_permission_classes
import logging

logger = logging.getLogger(__name__)


def get_index_permission_classes():
    """
    Helper function to get permission classes from settings for indexing views.

    Resolves string paths to actual class objects. Supports both string paths
    and class objects.

    Returns the permission classes configured via DJANGOLDP_INDEXING_PERMISSION_CLASSES.
    Returns empty list by default (no permissions, open access).
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
                logger.error(
                    f"Failed to import permission class '{perm_class}': {e}"
                )
        else:
            # Already a class object
            resolved_classes.append(perm_class)

    return resolved_classes


def serve_static_profile(request, path=None):
    """
    Serve the static profile.jsonld file if it exists.
    """
    if path is None:
        path = 'profile.jsonld'
        subpath = ['fedex']
    else:
        subpath = ['fedex', 'profile']
    # Ensure path ends with .jsonld
    if not path.endswith('.jsonld'):
        path = f"{path}.jsonld"
    file_path = os.path.join(settings.STATIC_ROOT, *subpath, path)


    if not os.path.exists(file_path):
        raise Http404("Profile not found")
        
    # Check if-modified-since header
    statobj = os.stat(file_path)
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                            statobj.st_mtime):
        return JsonResponse(None, status=304, safe=False)
        
    # Read and return the profile
    with open(file_path) as f:
        data = json.load(f)
        
    response = JsonResponse(
        data,
        content_type='application/ld+json'
    )
    response["Last-Modified"] = http_date(statobj.st_mtime)
    response["Cache-Control"] = "public, max-age=3600"
    return response


def serve_static_fedex(request, path):
    """
    Serve static index files from the indexes directory.
    The path should be relative to STATIC_ROOT/indexes/.
    """
    # Ensure path ends with .jsonld
    if not path.endswith('.jsonld'):
        path = f"{path}.jsonld"
        
    file_path = os.path.join(settings.STATIC_ROOT, 'fedex', path)
    
    if not os.path.exists(file_path):
        raise Http404("Index not found")
        
    # Check if-modified-since header
    statobj = os.stat(file_path)
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                            statobj.st_mtime):
        return JsonResponse(None, status=304, safe=False)
        
    # Read and return the index
    with open(file_path) as f:
        data = json.load(f)
        
    response = JsonResponse(
        data,
        content_type='application/ld+json'
    )
    response["Last-Modified"] = http_date(statobj.st_mtime)
    response["Cache-Control"] = "public, max-age=3600"
    return response

@api_view(['GET'])
@drf_permission_classes(get_index_permission_classes())
def serve_static_index(request, path):
    """
    Serve static index files from the indexes directory.
    The path should be relative to STATIC_ROOT/indexes/.

    Permissions are checked via decorator using DJANGOLDP_INDEXING_PERMISSION_CLASSES setting.
    """
    # Ensure path ends with .jsonld
    if not path.endswith('.jsonld'):
        path = f"{path}.jsonld"

    file_path = os.path.join(settings.STATIC_ROOT, 'indexes', path)

    if not os.path.exists(file_path):
        raise Http404("Index not found")

    # Permissions are automatically checked by DRF via decorator

    # Check if-modified-since header
    statobj = os.stat(file_path)
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                            statobj.st_mtime):
        return JsonResponse(None, status=304, safe=False)
        
    # Read and return the index
    with open(file_path) as f:
        data = json.load(f)
        
    response = JsonResponse(
        data,
        content_type='application/ld+json'
    )
    response["Last-Modified"] = http_date(statobj.st_mtime)
    response["Cache-Control"] = "public, max-age=3600"
    return response

def verify_contract_agreement(request, contract_agreement_id):
    """
    Verify that the contract agreement ID is valid and grants access to the requested resource.

    Args:
        request: The Django request object
        contract_agreement_id: The contract agreement ID from DSP-AGREEMENT-ID header

    Returns:
        bool: True if the contract is valid and grants access

    Raises:
        PermissionDenied: If the contract is invalid or doesn't grant access
    """
    import logging
    logger = logging.getLogger(__name__)

    # Get participant ID from header
    participant_id = request.headers.get('DSP-PARTICIPANT-ID')
    if not participant_id:
        raise PermissionDenied('DSP-PARTICIPANT-ID header is required for contract-based authorization')

    edc_url = getattr(settings, 'EDC_URL', 'http://localhost')
    requested_url = request.build_absolute_uri()

    logger.info(f"Verifying contract {contract_agreement_id} for participant {participant_id}")
    logger.info(f"EDC URL: {edc_url}")
    logger.info(f"Requested URL: {requested_url}")

    # Query EDC API to verify the contract agreement
    url = f"{edc_url}/management/v3/contractagreements/{contract_agreement_id}"

    headers = {
        'Content-Type': 'application/json',
        'DSP-PARTICIPANT-ID': participant_id,
    }

    try:
        logger.info(f"Calling EDC API: {url}")
        response = requests.get(url, headers=headers)
        logger.info(f"EDC API response status: {response.status_code}")
        logger.info(f"EDC API response body: {response.text[:500]}...")  # Log first 500 chars
        response.raise_for_status()
        contract_data = response.json()
        logger.info(f"Contract data keys: {list(contract_data.keys())}")
        logger.info(f"Full contract data: {contract_data}")

        # Check if the contract is valid (not expired, etc.)
        # The contract should contain information about what resources are accessible
        if not is_contract_valid(contract_data):
            logger.warning(f"Contract {contract_agreement_id} is not valid. State: {contract_data.get('state')}")
            raise PermissionDenied(f'Contract agreement {contract_agreement_id} is not valid (state: {contract_data.get("state")})')

        # Check if the requested URL is covered by this contract
        if not is_resource_covered_by_contract(contract_data, requested_url):
            logger.warning(f"Contract {contract_agreement_id} does not cover {requested_url}. AssetId: {contract_data.get('assetId')}")
            raise PermissionDenied(f'Contract agreement {contract_agreement_id} does not cover access to {requested_url} (assetId: {contract_data.get("assetId")})')

        logger.info(f"Contract verification successful for {contract_agreement_id}")
        return True

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == status.HTTP_404_NOT_FOUND:
            raise PermissionDenied(f'Contract agreement {contract_agreement_id} not found')
        elif e.response.status_code == status.HTTP_401_UNAUTHORIZED:
            raise PermissionDenied(f'Unauthorized to verify contract agreement')
        raise PermissionDenied(f'Error verifying contract agreement: {str(e)}')
    except Exception as e:
        raise PermissionDenied(f'Error verifying contract agreement: {str(e)}')


def is_contract_valid(contract_data):
    """
    Check if the contract agreement is valid (not expired, properly signed, etc.).

    Args:
        contract_data: The contract data from EDC API

    Returns:
        bool: True if the contract is valid
    """
    import logging
    logger = logging.getLogger(__name__)

    # Try different field names that EDC might use for state
    contract_state = (
        contract_data.get('state') or
        contract_data.get('edc:state') or
        contract_data.get('contractAgreement', {}).get('state') or
        contract_data.get('contractAgreement', {}).get('edc:state')
    )

    logger.info(f"Contract state found: {contract_state}")

    # If we can't find a state field, assume the contract exists and is valid
    # (the fact that we got it from the API means it exists)
    if contract_state is None:
        logger.warning("No state field found in contract data, assuming valid")
        return True

    # Check contract state - should be FINALIZED or VERIFIED
    valid_states = ['FINALIZED', 'VERIFIED', 'CONFIRMED', 'AGREED']
    if contract_state not in valid_states:
        logger.warning(f"Contract state '{contract_state}' is not in valid states: {valid_states}")
        return False

    # Check expiration if present
    # Add more validation as needed based on your EDC contract structure

    return True


def is_resource_covered_by_contract(contract_data, requested_url):
    """
    Check if the requested resource URL is covered by the contract agreement.

    Args:
        contract_data: The contract data from EDC API
        requested_url: The URL being requested

    Returns:
        bool: True if the resource is covered by the contract
    """
    import logging
    logger = logging.getLogger(__name__)

    # Try different field names that EDC might use for asset ID
    asset_id = (
        contract_data.get('assetId') or
        contract_data.get('edc:assetId') or
        contract_data.get('@id') or
        contract_data.get('contractAgreement', {}).get('assetId') or
        ''
    )

    logger.info(f"Asset ID found: {asset_id}")
    logger.info(f"Requested URL: {requested_url}")

    # If no assetId, check policy.target as fallback
    if not asset_id:
        policy_target = (
            contract_data.get('policy', {}).get('target') or
            contract_data.get('edc:policy', {}).get('target') or
            contract_data.get('edc:policy', {}).get('edc:target')
        )
        if policy_target:
            logger.info(f"No assetId, using policy target: {policy_target}")
            asset_id = policy_target
        else:
            logger.warning("No assetId or policy target found in contract, denying access")
            return False

    # If asset_id looks like a URL (starts with http:// or https://), do direct matching
    if asset_id.startswith('http://') or asset_id.startswith('https://'):
        logger.info(f"Asset ID is a URL, doing direct matching")
        # Exact match
        if requested_url == asset_id:
            logger.info(f"Exact match: {requested_url} == {asset_id}")
            return True
        # Subresource match (remove /index suffix and check if it's a parent)
        asset_base = asset_id.rsplit('/index', 1)[0] if '/index' in asset_id else asset_id
        if requested_url.startswith(asset_base + '/'):
            logger.info(f"Subresource match: {requested_url} starts with {asset_base}/")
            return True
        logger.warning(f"URL mismatch. Asset: {asset_id}, Requested: {requested_url}")
        return False

    # Otherwise, asset_id is just an ID - need to fetch the asset details from EDC
    logger.info(f"Asset ID is not a URL, fetching asset details from EDC")

    edc_url = getattr(settings, 'EDC_URL', 'http://localhost')
    asset_url = f"{edc_url}/management/v3/assets/{asset_id}"

    try:
        logger.info(f"Fetching asset from: {asset_url}")
        asset_response = requests.get(asset_url, headers={'Content-Type': 'application/json'})
        asset_response.raise_for_status()
        asset_data = asset_response.json()
        logger.info(f"Asset data: {asset_data}")

        # Extract dataAddress.baseUrl from the asset
        data_address = asset_data.get('dataAddress', {}) or asset_data.get('edc:dataAddress', {})
        base_url = (
            data_address.get('baseUrl') or
            data_address.get('edc:baseUrl') or
            data_address.get('baseurl') or
            data_address.get('edc:baseurl') or
            ''
        )

        logger.info(f"Base URL from asset: {base_url}")

        if not base_url:
            logger.warning("No baseUrl found in asset dataAddress, denying access")
            return False

        # Check if requested URL matches or is a subresource of base URL
        if requested_url == base_url:
            logger.info(f"Exact match with base URL")
            return True

        # Subresource match (remove /index suffix and check if it's a parent)
        base_url_stripped = base_url.rsplit('/index', 1)[0] if '/index' in base_url else base_url
        if requested_url.startswith(base_url_stripped + '/'):
            logger.info(f"Subresource match: {requested_url} starts with {base_url_stripped}/")
            return True

        logger.warning(f"Requested URL does not match base URL. Base: {base_url}, Requested: {requested_url}")
        return False

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching asset {asset_id}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking asset coverage: {str(e)}")
        return False


def check_dataspace_policy(request, path):
    """
    DEPRECATED: Check the dataspace policy for the given path.

    This function is deprecated and will be removed in a future version.
    Use DRF permission_classes instead via DJANGOLDP_INDEXING_PERMISSION_CLASSES setting.

    Migration instructions:
    1. Configure DJANGOLDP_INDEXING_PERMISSION_CLASSES in settings.yml:
       DJANGOLDP_INDEXING_PERMISSION_CLASSES:
         - djangoldp_tems.permissions_v3.EdcContractPermissionV3

    2. Remove manual check_dataspace_policy() calls from your views
    3. Permissions will be automatically checked by DRF

    ---

    Skip check if X-Bypass-Policy header is present.

    Tries two approaches in order:
    1. Contract-based: Check for DSP-AGREEMENT-ID header and verify with EDC API
    2. Profile-based (fallback): Check user's dataSpaceProfile and query catalog
    """
    warnings.warn(
        "check_dataspace_policy() is deprecated and will be removed in a future version. "
        "Use DJANGOLDP_INDEXING_PERMISSION_CLASSES setting with DRF permission classes instead. "
        "See function docstring for migration instructions.",
        DeprecationWarning,
        stacklevel=2
    )

    import logging
    logger = logging.getLogger(__name__)

    if request.headers.get('X-Bypass-Policy') == 'true':
        return

    # Try contract-based approach first
    contract_agreement_id = request.headers.get('DSP-AGREEMENT-ID')
    if contract_agreement_id:
        try:
            logger.info(f"Attempting contract-based authorization with contract ID: {contract_agreement_id}")
            if verify_contract_agreement(request, contract_agreement_id):
                logger.info(f"Contract-based authorization succeeded for {contract_agreement_id}")
                return  # Access granted via contract
        except PermissionDenied as e:
            # Contract verification failed, log the reason
            logger.warning(f"Contract-based authorization failed: {str(e)}")
            # If user explicitly provided contract headers, don't fall back silently
            # Re-raise the exception with more context
            raise PermissionDenied(f'Contract-based authorization failed: {str(e)}')

    # Fallback to profile-based approach (only if no contract headers provided)
    logger.info("Using profile-based authorization (no contract headers provided)")
    catalog = get_catalog(request)
    requested_url = request.build_absolute_uri()
    if not find_index_entry_in_catalog(catalog, requested_url):
        raise PermissionDenied(f'Access to this index is not allowed: {requested_url}')
    
def get_catalog(request):
    """
    Get the catalog for the requesting user.
    """
    if not request.user.is_authenticated:
      raise PermissionDenied(f'Access to this index is not allowed')

    # only allow access to the index if the user has a dataSpaceProfile
    headers = dict(request.headers)
    headers.pop('Host', None)
    remote_user = requests.get(request.user.urlid, headers=headers).json()

    # Check if dataSpaceProfile exists
    dataspace_profile = remote_user.get("dataSpaceProfile")
    if not dataspace_profile:
        raise PermissionDenied(f'Access to this index is not allowed: user has no dataSpaceProfile')

    edc_url = getattr(settings, 'EDC_URL', 'http://localhost')
    edc_api_key = dataspace_profile.get("edc_api_key", "")
    if not edc_api_key:
        edc_api_key = ""

    url = f"{edc_url}/management/v3/catalog/request"
    payload = json.dumps({
        "@context": {
            "edc": "https://w3id.org/edc/v0.0.1/ns/"
        },
        "@type": "CatalogRequest",
        "counterPartyAddress": edc_url,
        "protocol": "dataspace-protocol-http"
    })
    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': edc_api_key
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == status.HTTP_401_UNAUTHORIZED:
            raise PermissionDenied(f'Access to this index is not allowed')
        raise e
    except Exception as e:
        raise e
    
def find_index_entry_in_catalog(catalog, requested_url):
    """
    Recursively search for the requested URL in the catalog's idx:IndexEntry fields.
    Also checks if the requested URL is a subindex of any allowed index.
    """
    if isinstance(catalog, list):
        for item in catalog:
            if find_index_entry_in_catalog(item, requested_url):
                return True
        return False
    
    if isinstance(catalog, dict):
        # Check direct idx:IndexEntry
        if catalog.get('idx:IndexEntry'):
            base_index = catalog.get('idx:IndexEntry')
            # Check if requested_url is the same or is a subindex
            if requested_url == base_index or requested_url.startswith(base_index.rsplit('/index', 1)[0] + '/'):
                return True
        
        # Recursively check all nested objects
        for value in catalog.values():
            if find_index_entry_in_catalog(value, requested_url):
                return True
    
    return False