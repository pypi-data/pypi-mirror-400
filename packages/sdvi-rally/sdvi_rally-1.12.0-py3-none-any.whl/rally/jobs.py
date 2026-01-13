""" Rally jobs support.

Provides management features for asset jobs

Import example:

>>> from rally import jobs
"""
__all__ = [
    'get_jobs_for_asset',
    'get_job_report',
    'cancel_job'
]

import json

from . import exceptions, _session
from ._session import _getSession, _getAssetByName
from ._utils import _toDatetime
from .context import context, ASSET_ID


def get_jobs_for_asset(asset_name=None, category=None, state=None):
    """ Retrieve `generator iterator <https://docs.python.org/3/glossary.html#term-generator-iterator>`_ of dicts
    describing all jobs run on this asset sorted with most recently created first.

    Job dict attributes. **Note** Attributes whose values are `None` are not included in returned dicts:
        - category (:py:class:`str`)
        - clientResourceId (:py:class:`str`)
        - completedAt (:py:class:`~datetime.datetime`)
        - cost (:py:class:`int`)
        - creator (:py:class:`str`) The user creating the job (previously ``user``)
        - currencyType (:py:class:`str`)
        - deadlineAt (:py:class:`~datetime.datetime`)
        - inputFileLabels (:py:class:`str`)
        - jobUuid (:py:class:`str`)
        - owner (:py:class:`str`) The user performing the job (only found on external jobs)
        - percentComplete (:py:class:`int`)
        - preset (:py:class:`str`)
        - provider (:py:class:`str`)
        - queuedAt (:py:class:`~datetime.datetime`)
        - rule (:py:class:`str`)
        - startedAt (:py:class:`~datetime.datetime`)
        - status (:py:class:`str`)
        - user (:py:class:`str`) (deprecated)

    :param asset_name: The name of the asset to retreive jobs for, defaults to the current supply chain's asset
    :type asset_name: str, optional
    :param category: The type of job to filter for. One or more of 'Analyze', 'Evaluate', 'ExternalJob', 'Export', 'QC', 'Transform'. Defaults to all categories
    :type category: str or list[str], optional
    :param state: The state of the job to filter for. One or more of 'Active', 'Cancelled', 'Complete', 'Error', 'Hold', 'Queued', 'Rescheduled', 'Retried', 'Skipped', 'Restoring', 'Salvaged'. Defaults to all states
    :type state: str or list[str], optional

    Usage:

    >>> yak_jobs = jobs.get_jobs_for_asset()
    >>> next(yak_jobs)
    {'category': 'Evaluate', 'queuedAt': datetime.datetime(...), ...}
    """
    assetId = _getAssetByName(asset_name) if asset_name else context(ASSET_ID)
    if not assetId:
        raise exceptions.NotFound('Asset')

    valid_categories = ('Analyze', 'Evaluate', 'ExternalJob', 'Export', 'QC', 'Transform')

    if category:
        category = [category] if not isinstance(category, list) else category
        for c in category:
            if c not in valid_categories:
                raise ValueError(f'invalid category {c}')
    else:
        category = valid_categories

    valid_states = ('Active', 'Cancelled', 'Complete', 'Error', 'Hold', 'Queued', 'Rescheduled', 'Retried', 'Skipped', 'Restoring', 'Salvaged')
    if state:
        state = [state] if not isinstance(state, list) else state
        for s in state:
            if s not in valid_states:
                raise ValueError(f'invalid state {s}')

    page = 1
    pageSize = 100

    # Attributes we are interested in
    items = ('category', 'queuedAt', 'startedAt', 'completedAt', 'cost', 'currencyType', 'status', 'percentComplete',
             'jobUuid', 'workflowUuid', 'baseWorkflowUuid', 'deadlineAt', 'inputFileLabels', 'clientResourceId')
    # we want the 'name' of these attributes
    itemNames = ('preset', 'provider', 'rule', 'user', 'owner')
    # For now, we filter for all of these event categories involving the asset
    filter = {'movieId': assetId, 'category': category}
    if state:
        filter['state']= state
    filter = json.dumps(filter)
    sort = json.dumps({'id':'desc'})

    while True:
        params = {
            'count': pageSize,
            'filter': filter,
            'offset': (page - 1) * pageSize,
            'page': page,
            'verbose': True,
            'sorting': sort
        }

        events = _getSession().get('v1.0/event', params=params).json()['data']

        if not events:
            return
        else:
            page += 1

        # convert each event to the dict we want
        for event in events:
            job = {}
            for item in items:
                itemVal = event.get(item)
                if item in ('queuedAt', 'startedAt', 'completedAt', 'deadlineAt'):
                    job[item] = _toDatetime(itemVal)
                elif itemVal is not None:
                    job[item] = itemVal
            for itemName in itemNames:
                itemVal = (event.get(itemName) or {}).get('name')
                if itemVal is not None:
                    job[itemName] = itemVal
                    if itemName == 'user':
                        job['creator'] = itemVal

            yield job


# TODO what is the use case for this function vs getting the IDs like can you say give me the job reports

# TODO this must return a PRESIGNED URL
# TODO what happens if you find more than one and documents?
#   switch to specify a jobUuid so we don't have to worry about there is more than one output
def get_job_report(provider_type, label, report_format, preset_name=None, asset_name=None):
    """ Retrieve a job report. Reports are generated by various analyze and QC jobs.

    :param provider_type: Provider type name that generated the report. Use one of: 'SdviAnalyze', 'Aurora', 'Baton',
        'BingeWatching', 'CloudQC', 'ClamAv', 'FuseIQTextless', 'FuseIQVideoHashing', 'Photon', 'Rekognition',
        'SdviSimpleQc', 'Transcribe', 'VideoIndexer', 'VideoIntelligence', 'Vidchecker', 'VodMonitor'
    :type provider_type: str
    :param label: Input file label used by the report generating job
    :type label: str
    :param report_format: Format of the report. Use one of: 'summary', 'raw'
    :type report_format: str
    :param preset_name: Name of the preset used by the job that generated the report. Defaults to None
    :type preset_name: str, optional
    :param asset_name: Name of the asset associated to the job that generated the report. Defaults to the asset
        associated with the current supply chain
    :type asset_name: str, optional

    Usage:

    >>> jobs.get_job_report('SdviAnalyze', 'Yak', 'raw')
    b'...<Report Contents>...'
    """
    asset_id = context(ASSET_ID)

    if asset_name:
        asset_id = _session._getAssetByName(asset_name)

    if not asset_id:
        raise exceptions.NotFound(f'Asset {asset_name}')

    params = {
        'assetId': asset_id,
        'inputFileLabel': label,
        'providerType': provider_type,
        'reportFormat': report_format,
        'presetName': preset_name if preset_name else None
    }
    return _getSession().get(f'v1.0/jobs/report', params=params).content


def cancel_job(job_uuid):
    """ Cancels the given job, identified by UUID

    :param job_uuid: identifier of the job to be cancelled
    :type job_uuid: str
    """
    if not isinstance(job_uuid, str):
        raise TypeError(f"invalid type for job_uuid: {type(job_uuid).__name__}, expected: str")

    try:
        # get the job and use it's `cancel` link
        job = _getSession().get(f'v2/jobs/{job_uuid}').json()['data']

        return _getSession().post(job['links']['cancel'])
    except exceptions.RallyApiError as err:
        if err.code == 404:
            raise exceptions.NotFound(f'job {job_uuid}')
        raise
    except Exception as err:
        raise exceptions.RallyError(f'cannot cancel job: {err.__class__.__name__}: {err}')
