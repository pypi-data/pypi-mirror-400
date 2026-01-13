""" Rally User Defined Connector support.

A user defined connector is a Rally connector supplied by a user. It is a python script executed in the context of
a job for a user defined provider type. It runs in a fashion vary similar to a Decision Engine script in that it
has access to all the Classes and functions in the Rally module. Classes and functions in this file are specific
to user defined connector support and are not generally useful in a Decision Engine script.

Other differences between a User Defined Connector and a Decision Engine include the entry point name and extra
attributes in the context dictionary passed to the entry point. The entry point name for a User Defined Connector
is connector_main. Two extra context attributes include `presetProviderPreset` which contains the Provider Preset
portion of the job preset and `presetRallyConfig` which contains the Rally Config portion of the job preset.

Another difference between a User Defined Connector and a Decision Engine job is that User Defined Connector jobs are
either Transform or QC type jobs and therefore their returns are not parsed like Decision Engine jobs. Return values in
User Defined Connectors are used to handle job artifacts and output. This means that SupplyChainSteps and return values
can not be used to control supply chains. You must use next step in workflow rules like you would for other Transform
or QC jobs.

Note: Rally QC Jobs require an input by default. If you want to run a User Defined Connector QC job without defining an
input file then you will need to add an empty inputSpec to the preset's RallyConfig.

Preset example:

def connector_main(context):
    print('my preset', context['presetProviderPreset']
    return

Import example:

>>> from rally import userDefinedConnector
"""
__all__ = [
    'OutputArtifactUrl',
    'OutputArtifactBytes',
    'report_progress'
]
import base64
import signal
import sys

class OutputArtifact:
    """ Base class for various output artifacts
    """

    def _toJson(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}


class OutputArtifactUrl(OutputArtifact):
    """ An output artifact referenced by url, ex: s3://my_bucket/my_key

    Return an instance (or list) of this class for an output artifact in cloud storage.
    The url scheme must be one of: s3, gs, az, ac for Amazon, Google, Azure, Alibaba respectively.
    The url will be matched against outputSpec tokens to determine how to update asset inventory.

    :param url: Url for the output artifact.
    :type url: str
    """

    def __init__(self, url):
        self.url = url
        self.artifactType = 'RemoteMediaArtifact'


class OutputArtifactBytes(OutputArtifact):
    """ An output artifact as a sequence of bytes

    Return an instance (or list) of this class for an output artifact as a sequence of bytes.
    The filename will be matched against outputSpec tokens to determine where to store the file and how to update
    asset inventory.

    :param data: Sequence of bytes for the output artifact.
    :type data: bytes
    :param filename: Name of file for the sequence of bytes
    :type filename: str
    """

    def __init__(self, data, filename):
        self.dataBase64 = base64.b64encode(data).decode()
        self.filename = filename
        self.artifactType = 'ArtifactStream'


def report_progress(progress):
    """ Report job progress

    This function should be called about every 30-60 seconds but must be called at least every 5 minutes. Otherwise,
    the job will be considered dead and will be terminated. This function must also report progress changes (decreasing
    values ignored) every 15 minutes (configurable per provider) or the job will be considered dead and will be terminated.
    This function will raise Exception('cancelled') if the job has been cancelled. Two minutes after job cancellation
    the job will be terminated if not exited sooner. Note that report_progress must be called more often than every two
    minutes to guarantee getting this exception after job cancellation.

    :param progress: Job progress, [0-100]
    :type progress: int, or float

    Usage:

    >>> userDefinedConnector.report_progress(42)
    """
    assert isinstance(progress, (int, float)), 'progress must be an int or float'
    assert 0 <= progress <= 100, 'progress must be [0-100]'

    if cancelled:
        raise Exception('cancelled')

    print(f'__progress__:{int(progress * 1000)}', file=sys.stderr, flush=True)


cancelled = False

def _handleSigTerm(*_):
    global cancelled
    cancelled = True

signal.signal(signal.SIGTERM, _handleSigTerm)
