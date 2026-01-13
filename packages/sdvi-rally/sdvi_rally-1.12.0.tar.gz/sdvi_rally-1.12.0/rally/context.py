import json
import os
from functools import lru_cache

_ENV_API_TOKEN = 'RALLY_API_TOKEN'
_ENV_API_URL = 'RALLY_URL'
_ENV_CONTEXT = 'RALLY_USER_CONTEXT'

ASSET_ID = 'assetId'
ASSET_NAME = 'assetName'
BASE_ASSET_ID = 'baseAssetId'
DYNAMIC_PRESET_DATA = 'dynamicPresetData'
ERROR_JOB_UUID = 'errorJobUuid'
JOB_UUID = 'jobUuid'
ORG_ID = 'orgId'
PRIORITY = 'priority'
RALLY_API_TOKEN = 'rallyApiToken'
RALLY_URL = 'rallyUrl'
RETRY_COUNT = 'retryCount'
USER_ID = 'userId'
WORKFLOW_BASE_ID = 'workflowBaseId'
WORKFLOW_ID = 'workflowId'
WORKFLOW_PARENT_ID = 'workflowParentId'
WORKFLOW_RULE_ID = 'wfRuleId'


@lru_cache(maxsize=1)
def _make_user_context():
    # User context is only available inside a silo, and does not include any token information
    result = {}
    try:
        for (k, v) in json.loads(os.environ[_ENV_CONTEXT]).items():
            result[k] = v
    except (KeyError, TypeError, ValueError) as err:
        raise ValueError(f"Context missing or non-JSON in environment variable '{_ENV_CONTEXT}'") from err
    return result


@lru_cache(maxsize=1)
def _make_sdk_context():
    # The SDK gets the token and targeted URL from environment variables
    result = {k: v for k, v in _make_user_context().items()}
    # URL will be missing from the context if running the SDK
    if not result.get(RALLY_URL) and _ENV_API_URL in os.environ:
        result[RALLY_URL] = os.environ[_ENV_API_URL]
    # _session needs the token either way
    if not result.get(RALLY_API_TOKEN) and _ENV_API_TOKEN in os.environ:
        result[RALLY_API_TOKEN] = os.environ[_ENV_API_TOKEN]
    return result


def _refresh():
    _make_user_context.cache_clear()
    _make_sdk_context.cache_clear()


def context(key):
    """ Retrieve key from context, or None if not present. """
    return _make_user_context().get(key)


def _sdk_context(key):
    """ Retrieve key from SDK context, a superset of context for internal use. """
    return _make_sdk_context().get(key)
