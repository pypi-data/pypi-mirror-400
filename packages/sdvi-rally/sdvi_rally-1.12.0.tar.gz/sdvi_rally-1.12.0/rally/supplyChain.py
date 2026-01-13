""" Rally Supply Chain support.

Provides management of Rally supply chains

Import example:

>>> from rally import supplyChain
"""
__all__ = [
    'SupplyChainStep',
    'SupplyChainSplit',
    'SupplyChainSequence',
    'SupplyChainCancel',
    'start_new_supply_chain',
    'set_scheduled_supply_chain',
    'get_scheduled_supply_chain',
    'delete_scheduled_supply_chain',
    'create_supply_chain_marker',
    'get_supply_chain_metadata',
    'set_supply_chain_metadata',
    'update_supply_chain_metadata'
]
import datetime
import functools
import threading
import time
import re
import uuid

from rally import exceptions
from rally._utils import _datetimeToTimestamp, _datetimeToPosixTimestamp, _posixToDatetime
from rally.context import context, ASSET_ID, BASE_ASSET_ID, JOB_UUID, ORG_ID, USER_ID, WORKFLOW_BASE_ID, WORKFLOW_ID, \
    WORKFLOW_RULE_ID, WORKFLOW_PARENT_ID
from ._session import _getSession, _getAssetByName

_local = threading.local()


class SupplyChainStep:
    """ A step in a supply chain. Return an instance of this class for the next step in the supply chain

    :param name: The name of the supply chain step
    :type name: str
    :param dynamic_preset_data: Dynamic preset data passed to the supply chain step. Defaults to `None`
    :type dynamic_preset_data: dict, optional
    :param fail_step_name: Setting this argument makes this SupplyChainStep a conditional when part of a
        SupplyChainSequence. The `fail_step_name` step will be executed instead of `name` when the immediately preceding
        step in the sequence fails.
        Notes:

        - Setting `fail_step_name` has no effect outside of a SupplyChainSequence.
        - Executing the fail step will only consider `fail_step_name`, `fail_step_provider_filter`, `dynamic_preset_data`
          and `priority` as all other arguments given here will be ignored.
        - Subsequent steps in the sequence will still be executed after a fail step, unless of course the fail step
          returns something such as a step name or empty string.
        - The `fail_step_name` value may also include an override preset name when formatted like `step_name::preset_name`
    :type fail_step_name: str, optional
    :param preset: Overrides the step's preset with the preset of this name. Defaults to `None`
    :type preset: str, optional
    :param priority: Job priority for remainder of the supply chain, defaults to `None` (meaning that the supply chain's
        priority will not be changed). String values must be one of (shown ranked from greatest to least urgency):

        - `urgent`
        - `high`
        - `med_high`
        - `normal`
        - `med_low`
        - `low`
        - `background`
    :type priority:  int or str, optional
    :param supply_chain_deadline: SupplyChain deadline override for remainder of the supply chain.  Defaults to `None`
    :type supply_chain_deadline: a timezone-aware :py:class:`~datetime.datetime`, optional
    :param step_deadline: SupplyChain deadline override for the supply chain step.  Defaults to `None`
    :type step_deadline: a timezone-aware :py:class:`~datetime.datetime`, optional
    :param provider_filter: Provider tag for the supply chain step.  Constrains provider used to those tagged with this
        TagName.  Defaults to not constraining the provider
    :type provider_filter: str, optional
    :param retry_policy: Job retry policy for remainder of the supply chain.  Must be a list of non-negative ints where
        each int is retry hold time in seconds. A value of `0` means to hold indefinitely.  Defaults to the existing
        retry policy
    :type retry_policy: list(int), optional
    :param step_deadline_lic_only: Deadline for restricting to licensed managed providers.  Specified either as a
       datetime as an absolute date, a timedelta as an offset before the normal job deadline, or as an integer number
       of hours as an offset before the normal job deadline.  Note, this deadline is ignored for jobs with priority
       higher than Normal.
    :type step_deadline_lic_only: :py:class:`~datetime.datetime`, :py:class:`~datetime.timedelta` or int, optional
    :param concurrency_tag: Job concurrency tag. The tag must be a string ending in two digits. For example Tag02.
       The tag limits maximum concurrency of active Export jobs with the same tag. The limit is the trailing two digits.
       A tag like Tag02 will limit the number of active jobs with this tag to two. Max concurrency_tag length is 50 characters.
    :type concurrency_tag: str, optional
    :param pacing_tag: Job pacing tag. The purpose is to limit the number of Export jobs run per unit of time. The tag
        specifies a pacing limit where the limit is of the form JobCount jobs per TimeUnit window of time. For example a
        limit of ten jobs per one day. The limit is applied on jobs having the same pacing_tag and is applied when starting
        a job. The tag must be a string with a maximum length of 64 characters and is of the form: `name%TimeUnit%JobCount`
        and must meet the following regex:`^[a-zA-Z\\\\d_-]+%[1-9]\\\\d* (minute|hour|day)%[1-9]\\\\d?$`. Name can be any string,
        TimeUnit species the unit of time in minute, hour or day and JobCount must be <= 20. The following tag would
        impose the pacing limit in the example above: `foo_test%1 day%10`.
    :type pacing_tag: str, optional
    :param wait_until: Job future scheduling. The job will not run until after this time. Date must be less than 93 days
        in the future.
    :type wait_until: a timezone-aware :py:class:`~datetime.datetime`, optional
    :param wait_file_labels: The job will not run until these files exist, or until after wait_file_until. A maximum of
        10 lables can be specified. Note that when the job runs due to wait_file_until expiration then all the specified
        files may not exist.
    :type wait_file_labels: list(str), optional
    :param wait_file_until: Only wait until this time for wait_file_labels to exist. Date must be less than 10 days in
        the future.
    :type wait_file_until: a timezone-aware :py:class:`~datetime.datetime`, optional, reguired along with wait_file_labels
    :param submit_on_hold: A flag indicating submit the job in the Hold state rather than the Queued state.
    :type submit_on_hold: bool, optional
    :param job_metadata: A string to be set as the job's metadata. This info is optionally added to job usgage reports. Limited to 2K.
    :type job_metadata: str, optional
    :param concur_eval: When True allows this evaulute job to run concurrently with other eval jobs for this asset.
        Note: you generally do NOT want to set this option. As such, this option must be enabled in the silo otherwise
        this setting is ignored. Please contact SDVI support to enable.
    :type concur_eval: bool, optional
    :param fail_step_provider_filter: Provider tag for the fail step supply chain step. Constrains provider used to
        those tagged with this TagName. Defaults to not constraining the provider.
    :type fail_step_provider_filter: str, optional

    Usage:

    >>> my_step = supplyChain.SupplyChainStep('my_step')
    """

    def __init__(self, name, dynamic_preset_data=None, preset=None, priority=None, supply_chain_deadline=None,
                 step_deadline=None, provider_filter=None, retry_policy=None, step_deadline_lic_only=None,
                 fail_step_name=None, concurrency_tag=None, pacing_tag=None, wait_until=None, wait_file_labels=None,
                 wait_file_until=None, submit_on_hold=None, job_metadata=None, concur_eval=None,
                 fail_step_provider_filter=None):
        self.stepName = name
        self.dynamicPresetData = dynamic_preset_data
        self.presetName = preset
        self.workflowJobPriority = _get_job_priority(priority)
        self.movieDeadline = _datetimeToTimestamp(supply_chain_deadline) if supply_chain_deadline else None
        self.movieDeadlineNextStep = _datetimeToTimestamp(step_deadline) if step_deadline else None
        self.workflowJobRetryPolicy = retry_policy
        self.deadlineLicOnly = step_deadline_lic_only
        self.providerTag = provider_filter
        self.concurrencyTag = concurrency_tag
        self.pacingTag = pacing_tag
        self.waitUntil = int(_datetimeToPosixTimestamp(wait_until)) if wait_until else None
        self.submitOnHold = True if submit_on_hold else None
        self.concurEval = True if concur_eval else None
        if wait_file_labels:
            if not context(ASSET_ID):
                raise exceptions.NotFound('asset')
            assert isinstance(wait_file_until, datetime.datetime), 'must specify wait_file_until along with wait_file_labels'
            assert isinstance(wait_file_labels, list) and len(wait_file_labels) <= 10,\
                'wait_file_labels must be a list of at most 10 entries'
            nowPlus10Days = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=10)
            assert wait_file_until < nowPlus10Days, 'wait_file_until must be within 10 days of now'
            self.waitFile = {'assetId': context(ASSET_ID),
                             'labels': wait_file_labels,
                             'until': int(_datetimeToPosixTimestamp(wait_file_until))}
        if job_metadata:
            assert isinstance(job_metadata, str) and len(job_metadata) <= 2000, 'job_metadata must be a string of length <= 2000'
            self.jobMetadata = job_metadata

        if self.waitUntil:
            nowPlus93Days = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=93)
            assert self.waitUntil < nowPlus93Days.timestamp(), 'wait_until must be within 93 days of now'

        if fail_step_name:
            if isinstance(fail_step_name, str):
                self.failStepName = fail_step_name
                self.failStepProviderFilter = fail_step_provider_filter
            else:
                raise TypeError(f"invalid type for step: {type(fail_step_name).__name__}, expected: str")

        if isinstance(self.deadlineLicOnly, (int, float)):
            # convert from hours to mS
            # a negative value indicates a relative time before job deadline
            self.deadlineLicOnly = 0 - max(int(self.deadlineLicOnly * 60 * 60 * 1000), 0)
        elif isinstance(self.deadlineLicOnly, datetime.timedelta):
            # convert to number of hours for next conversion
            self.deadlineLicOnly = 0 - max(int(self.deadlineLicOnly.total_seconds() * 1000), 0)
        elif isinstance(self.deadlineLicOnly, datetime.datetime):
            # convert from hours to mS
            # a positive value indicates an absolute time
            self.deadlineLicOnly = _datetimeToTimestamp(self.deadlineLicOnly)

        if concurrency_tag and (len(concurrency_tag) > 50 or not re.match(r'.*\d{2}$', concurrency_tag)
                                or concurrency_tag.endswith('00')):
            raise TypeError(f'invalid concurrency_tag {concurrency_tag}')

        if pacing_tag:
            tagCheck = re.match(r'^[a-zA-Z\d_-]+%([1-9]\d*) (minute|hour|day)%([1-9]\d?)$', pacing_tag)
            jobCnt = int(tagCheck[3]) if tagCheck else 0
            if len(pacing_tag) > 64 or not tagCheck or jobCnt > 20:
                raise TypeError(f'invalid pacing_tag {pacing_tag}')

    def _toJson(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}


class _SupplyChainMixin:
    def _validateStep(self, step):
        if isinstance(step, str):
            return SupplyChainStep(step)

        validTypes = (SupplyChainStep,) if isinstance(self, SupplyChainSequence) else\
            (SupplyChainStep, SupplyChainSequence)

        if not isinstance(step, validTypes):
            raise TypeError(f"invalid type for step: {type(step).__name__}, expected:"
                            f" str, {', '.join([x.__name__ for x in validTypes])}")

        return step


class SupplyChainSplit(_SupplyChainMixin):
    """ An object to represent a split in a supply chain. Return this object to create a split in the supply chain.

    :param resume_step: Optional step to resume when split paths complete
    :type resume_step: str, :class:`~rally.supplyChain.SupplyChainStep`, or :class:`~rally.supplyChain.SupplyChainSequence`
    """
    def __init__(self, resume_step=None):
        self.resumeStep = [self._validateStep(resume_step)] if resume_step else []
        self.splitSteps = []

    def add_split(self, step, run_async=False):
        """ Add a split step.

        :param step: Initial supply chain step of a split in the parent supply chain.
        :type step: str, :class:`~rally.supplyChain.SupplyChainStep` or :class:`~rally.supplyChain.SupplyChainSequence`
        :param run_async: Set true to make this split path asynchronous.
        :type run_async: :boolean:

        Usage:

        >>> my_split = supplyChain.SupplyChainSplit('step_to_resume')
        >>> my_split.add_split('step_to_split', run_async=True)
        """
        self.splitSteps.append({'isNewChildWorkflow': True, 'async': run_async, 'wfId': str(uuid.uuid4()),
                                'stepName': self._validateStep(step)})

    def _toJson(self):
        if not self.splitSteps:
            raise Exception('invalid SupplyChainSplit, no splits')
        if all([split.get('async') for split in self.splitSteps]):
            raise Exception('all paths of a split cannot be async')
        return self.splitSteps + self.resumeStep


class SupplyChainSequence(_SupplyChainMixin):
    """
    An object to represent a sequence in a supply chain. Return this object to specify a list of next steps
    in the supply chain. Note that each evaluate type step in the sequence should return nothing so that the next step in the
    sequence is executed. Returning anything other than nothing (None) will cause all subsequent steps in the sequence
    to be ignored. For instance, returning a step name will result in jumping out of the sequence into the specified step.
    Returning an empty string can be used to simply ignore the remaining steps.

    """
    def __init__(self):
        self.steps = []

    def add_step(self, step):
        """ Add a step the to sequence.

        :param step: Supply chain step
        :type step: str or :class:`~rally.supplyChain.SupplyChainStep`

        Usage:

        >>> my_sequence = supplyChain.SupplyChainSequence()
        >>> my_sequence.add_step('next_step')
        """
        self.steps.append(self._validateStep(step))

    def _toJson(self):
        if not self.steps:
            raise Exception('invalid SupplyChainSequence, no steps')
        return [x._toJson() for x in self.steps]


class SupplyChainCancel(_SupplyChainMixin):
    """
    Cancels all running and scheduled jobs associated with this supply chain. Supply chain continues at the
    specified SupplyChainStep.

    :param resume_step:
    :type resume_step: str, :class:`~rally.supplyChain.SupplyChainStep` or :class:`~rally.supplyChain.SupplyChainSequence`:

    Usage:

    >>> supplyChain.SupplyChainCancel('step_to_run_after_cancel')
    """
    def __init__(self, resume_step):
        self.resumeStep = self._validateStep(resume_step)

    def _toJson(self):
        return {'cancelAllSubWorkflowsAndResumeAtStep': self.resumeStep}


def start_new_supply_chain(asset, step, dynamic_preset_data=None, preset_name=None, supply_chain_job_priority=None,
                           deadline=None, supply_chain_deadline_step_name=None, retry_policy=None,
                           client_resource_id=None):
    """ Start a new supply chain on the specified asset.

    :param asset: Name of the asset.  The asset is created if it does not already exist.
    :type asset: str
    :param step: First step to execute in the new supply chain. If is :class:`~rally.supplyChain.SupplyChainStep` then
        the following member fields on the first step will get used to start the supply chain: name, provider_filter,
        concurrency_tag, pacing_tag, wait_until, wait_file_label/ wait_file_until. All other member fields are ignored.
    :type step: str or :class:`~rally.supplyChain.SupplyChainStep`
    :param dynamic_preset_data: Dynamic preset data passed to the first step.  Defaults to no preset data
    :type dynamic_preset_data: dict, optional
    :param preset_name: First step preset name override. Defaults to preset defined by the step definition
    :type preset_name: str, optional
    :param supply_chain_job_priority: Job priority override for _all_ steps in the supply chain.  Defaults to preserving
        existing priorities.  String values must be one of (shown ranked from greatest to least urgency):

        - `urgent`
        - `high`
        - `med_high`
        - `normal`
        - `med_low`
        - `low`
        - `background`
    :type supply_chain_job_priority: int or str, optional
    :param deadline: Supply chain deadline time.  Defaults to no deadline
    :type deadline: a timezone-aware :py:class:`~datetime.datetime`, optional
    :param supply_chain_deadline_step_name: Name of the first step to execute in another supply chain.  This step is
        provided with dynamicPresetData containing the following keys:

        - 'baseWorkflowId'
        - 'workflowId'
        - 'deadlineTime'
        - 'alertTime'

        This new SupplyChain is created and started only when the deadline is reached.  It is not created or started
        if the original SupplyChain finishes before the deadline or if the supply-chain_deadline_time and/or the
        supply_chain_deadline_step_name is removed.  Note it is possible this new SupplyChain could run after the
        original SupplyChain finishes if the finish time is near the deadline time.  Defaults to `None` (meaning no new
        SupplyChain or SupplyChainStep is created upon reaching the deadline).
    :type supply_chain_deadline_step_name: str, optional
    :param retry_policy: Job retry policy override for _all_ steps in the supply chain.  Must be a list of non-negative
        ints where each int is retry hold time in seconds.  A value of `0` means indefinite hold.  Defaults to no override.
    :type retry_policy: list(int), optional
    :param client_resource_id: An identifier for the SupplyChain that is meaningful to the creator.  This identifier
        will be by default applied to all jobs in the SupplyChain and to descendent SupplyChains
    :type client_resource_id: str, optional

    Usage:

    >>> supplyChain.start_new_supply_chain('Yeti Corps Asset', 'VanguardStep')
    """
    if isinstance(step, (str, SupplyChainStep)):
        step = step if isinstance(step, str) else step._toJson()
    else:
        raise TypeError(f"invalid type for step: {type(step).__name__}, expected: str or SupplyChainStep")

    payload = {'assetName': asset,
               'firstStep': step,
               'dynamicPresetData': dynamic_preset_data,
               'presetName': preset_name,
               'jobPriority': _get_job_priority(supply_chain_job_priority),
               'jobRetryPolicy': retry_policy,
               'deadlineTime': _datetimeToTimestamp(deadline) if deadline else None,
               'deadlineStepName': supply_chain_deadline_step_name,
               'fromWfRuleId': context(WORKFLOW_RULE_ID),
               'clientResourceId': client_resource_id}

    if not context(ASSET_ID):
        payload['jobUuidForMovieId'] = context(JOB_UUID)

    payload['startOrigin'] = f'Eval2_{context(JOB_UUID)}'

    s = _getSession()
    s.post('v1.0/workflow/new', json=payload)


def set_scheduled_supply_chain(step, creation_delay=None, deadline_delay=None, idle_delay=None, date_after=None):
    """ Set a scheduled supply chain for a given asset. The specified supply chain will start when all the specified start
    criteria are met. There is at most one scheduled supply chain per asset. An existing scheduled supply chain for this
    asset will be replaced by this one. Execution of the supply chain removes the scheduled supply chain entry.

    .. note::
       At least one but any or all of 'creation_delay', 'deadline_delay', 'idle_delay', or 'date_after' can be specified

    .. warning::
        The asset’s current deadline is captured when setting the scheduled supply chain. Later changing the asset’s
        deadline to an earlier time may cause the sypply chain to never run.

    :param step: the name of the supply chain step to execute when the schedule condition is met
    :type step: str, :class:`~rally.supplyChain.SupplyChainStep`
    :param creation_delay: the number of days after creation of the asset to trigger execution, defaults to not executing based on creation date
    :type creation_delay: int, optional
    :param deadline_delay: the number of days after the asset's deadline that the scheduled supply chain is executed, defaults to not executing based on deadline
    :type deadline_delay: int, optional
    :param idle_delay: the number of days of asset inactivity before running the scheduled supply chain, defaults to not executing based on idle time
    :type idle_delay: int, optional
    :param date_after: a timezone-aware :py:class:`datetime.datetime` on which to execute scheduled supply chain, defaults to not executing based on a date.
        Date must be less than 93 days in the future.
    :type date_after: str, optional

    Usage:

    >>> supplyChain.set_scheduled_supply_chain('yak_delete', idle_delay=2)

    """
    # Validate inputs
    if not context(ASSET_ID):
        raise exceptions.NotFound('asset')

    if creation_delay:
        assert isinstance(creation_delay, int), 'creation_delay must be int'
    if deadline_delay:
        assert isinstance(deadline_delay, int), 'deadline_delay must be int'
    if idle_delay:
        assert isinstance(idle_delay, int), 'idle_delay must be int'

    date_after_int = int(_datetimeToPosixTimestamp(date_after)) if date_after else None
    if date_after_int:
        nowPlus93Days = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=93)
        assert date_after_int < nowPlus93Days.timestamp(), 'date_after must be within 93 days of now'

    payload = {
        'stepName': step.stepName if isinstance(step, SupplyChainStep) else step,
        'creationDelay': creation_delay if creation_delay else None,
        'deadlineDelay': deadline_delay if deadline_delay else None,
        'idleDelay': idle_delay if idle_delay else None,
        'dateAfter': date_after_int,
    }

    _getSession().post(f'v1.0/scheduledWorkflow/{context(ASSET_ID)}', json=payload)


def get_scheduled_supply_chain(asset_name=None):
    """ Return a dict containing a representation of an asset's scheduled supply chain.
    Note that attributes whose values are `None` are not included in the return

    Scheduled Supply Chain dict attributes:
        - asset_id (:py:class:`int`)
        - creation_delay, days: (:py:class:`int`)
        - deadline_delay, days: (:py:class:`int`)
        - idle_delay, days: (:py:class:`int`)
        - date_after, date: (:py:class:`datetime.datetime`)
        - step_name: (:py:class:`str`)

    :param asset_name: the name of the asset, defaults to this asset
    :type asset_name: str, optional

    Usage:

    >>> supplyChain.get_scheduled_supply_chain()
    {'asset_id': 1, 'idle_delay': 2, 'step_name': 'yak_delete',...}

    """
    asset_id = _getAssetByName(asset_name) if asset_name else context(ASSET_ID)
    if not asset_id:
        raise exceptions.NotFound(asset_name or 'asset')

    try:
        resp = _getSession().get(f'v1.0/scheduledWorkflow/{asset_id}')
        res = {}
        # Remove None values and Convert unix date to tz-aware datetime
        for key, value in resp.json().items():
            if value is not None:
                if key == 'date_after':
                    res[key] = _posixToDatetime(value)
                else:
                    res[key] = value
        return res
    except exceptions.RallyApiError as e:
        if e.code == 404:
            raise exceptions.NotFound(asset_name or 'asset')
        raise

def delete_scheduled_supply_chain():
    """ Deletes the scheduled supply chain for a given asset.

    Usage:

    >>> supplyChain.delete_scheduled_supply_chain()

    """
    # Validate inputs
    if not context(ASSET_ID):
        raise exceptions.NotFound('asset')

    _getSession().delete(f'v1.0/scheduledWorkflow/{context(ASSET_ID)}')

def create_supply_chain_marker(description, icon, color):
    """
    Create a supply chain marker.

    :param description: Text description to be displayed with the marker, max 50 characters.
    :type description: str
    :param icon: Name for the icon to be used as the marker.
    :type icon: str
    :param color: the icon color, one of:

        - 'pass': equivalent to `green`
        - 'fail': equivalent to `red`
        - a hex value (`#xxxxxx`), or
        - a web color name
    :type color: str

    Usage:

    >>> supplyChain.create_supply_chain_marker('Yeti-Marker', 'fa-thumb-tack', 'burlywood')

    .. seealso::
        `Font Awesome <https://fontawesome.com/icons?d=gallery&s=regular>`_ documentation for available icons

        `Color keyword <https://developer.mozilla.org/en-US/docs/Web/CSS/color_value>`_ MDN documentation
    """
    description = description or ''

    if len(description) > 50:
        raise ValueError('description must be < 51 characters')
    if not isinstance(color, str):
        raise TypeError('color argument must be a string')

    payload = {
        'success': False if color.lower() == 'fail' else True,
        'desc': description,
        'icon': icon,
        'color': None if color.lower() in ('pass', 'fail') else color,
        'userId': context(USER_ID),
        'orgId': context(ORG_ID),
        'jobId': context(JOB_UUID),
        'assetId': context(ASSET_ID),
        'assetBaseId': context(BASE_ASSET_ID),
        'wfRuleId': context(WORKFLOW_RULE_ID),
        'wfId': context(WORKFLOW_ID),
        'wfBaseId': context(WORKFLOW_BASE_ID),
        'wfParentId': context(WORKFLOW_PARENT_ID),
    }

    s = _getSession()
    s.post('v1.0/workflow/marker', json=payload)


@functools.lru_cache()
def get_supply_chain_metadata(name=None):
    """ Return a dict containing an Asset's SupplyChain metadata. Raises a :class:`~rally.exceptions.NotFound` if the
    asset does not exist.

    :param name: the asset name, defaults to this Asset
    :type name: str, optional

    Usage:

    >>> supplyChain.get_supply_chain_metadata()
    {'spam': 'eggs', 'yaks': 5}
    """
    assetId = _getAssetByName(name) if name else context(ASSET_ID)
    if not assetId:
        raise exceptions.NotFound(name or 'asset')

    # wait at least 300ms before attempting to read after write
    # this reduces the odds of getting stale data significantly
    if hasattr(_local, 'lastWrite'):
        wait = 0.300 - (time.time() - _local.lastWrite)
        if wait > 0:
            time.sleep(wait)

    resp = _getSession().get(f'v2/supplyChainMetadata/{assetId}')

    return resp.json()['data']['attributes']['metadata']


# TODO limit size
def set_supply_chain_metadata(metadata):
    """ Set an Asset's SupplyChain metadata. Note this will replace any existing metadata

    .. warning::
        Altering supply chain metadata can seriously impact the function of a supply chain. Proceed at your own risk.

    :param metadata: metadata to set on the Asset
    :type metadata: dict

    Usage:

    >>> supplyChain.set_supply_chain_metadata({'spam': 'eggs'})
    """
    assetId = context(ASSET_ID)
    if not assetId:
        raise exceptions.NotFound('asset')

    _getSession().put(f'v1.0/movie/{assetId}/workflowMetadata2', json={'metadata': metadata})
    _local.lastWrite = time.time()
    get_supply_chain_metadata.cache_clear()


def update_supply_chain_metadata(metadata):
    """ Update an Asset's SupplyChain with the supplied metadata
    The update is similar to python dict method update() except that the supplied metadata must be a dict.

    :type metadata: dict
    :param metadata: metadata to update the Asset supply chain metadata

    Usage:

    >>> supplyChain.update_supply_chain_metadata({'spam': 'eggs'})
    """
    if not isinstance(metadata, dict):
        raise TypeError('metadata must be of type dict')

    assetId = context(ASSET_ID)
    if not assetId:
        raise exceptions.NotFound('asset')

    _getSession().put(f'v1.0/movie/{assetId}/workflowMetadata2', json={'metadata': metadata}, params={'replace': 'dictUpdate'})
    _local.lastWrite = time.time()
    get_supply_chain_metadata.cache_clear()


def _get_job_priority(priority):
    priority_map = {
        'urgent': 'PriorityUrgent',
        'high': 'PriorityHigh',
        'med_high': 'PriorityMedHigh',
        'normal': 'PriorityNorm',
        'med_low': 'PriorityMedLow',
        'low': 'PriorityLow',
        'background': 'PriorityBackground'
    }

    if isinstance(priority, (int, type(None))):
        return priority
    # Normalize str priorities into something the API can understand (PascalCase `urgent` => `PriorityUrgent`)
    try:
        return priority_map[priority.lower()]
    except KeyError:
        raise ValueError(f'{priority} is not a valid priority')
