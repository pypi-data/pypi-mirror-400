import contextlib
from rally._vendored import certifi
import importlib.util
import json
import os
import re
from json import JSONDecodeError

import click
from urllib.parse import urlparse, urlunparse

from rally import asset
from rally import context
from rally.context import _ENV_API_TOKEN, _ENV_API_URL, _ENV_CONTEXT

help_text = """\
Rally CLI - execute Decision Engine presets locally

Please set the following environment variables:

\b
    {prefix}{cmd} RALLY_URL=https://silo.sdvi.com
    {prefix}{cmd} RALLY_API_TOKEN=<your API token>
    {prefix}rally run preset.py
""".format(
    cmd="export" if os.name == "posix" else "set",
    prefix="$ " if os.name == "posix" else "> ",
)


@click.group(help=help_text)
def cmd():
    pass


@cmd.command()
@click.argument('preset', type=str)
@click.option('--asset', '-a', type=str, default=None,
              help='specify an asset to run on')
@click.option('--dpd', '-d', default=None,
              help='specify Dynamic Preset Data as a JSON string or a JSON filename')
def run(preset, asset, dpd):
    """ Runs the eval_main function in the given preset python file

    :param preset: Required. The name of a preset file to run, must contain an `eval_main` function.
    """
    validate_environment()
    eval_context = make_context(asset, dpd)

    # import the user preset as a module
    spec = importlib.util.spec_from_file_location('preset', preset)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    userScript = module.eval_main
    args = (eval_context,) if userScript.__code__.co_argcount == 1 else tuple()

    try:
        return userScript(*args)
    except IOError as err:
        if 'Could not find a suitable TLS CA certificate bundle' in str(err):
            os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
            return userScript(*args)
        else:
            raise err


def validate_environment():
    """ Ensures required environment variables are set """
    apiToken = os.environ.get(_ENV_API_TOKEN)
    rallyUrl = os.environ.get(_ENV_API_URL)

    assert apiToken, f"{_ENV_API_TOKEN} must be set in your environment"

    url_help = f"{_ENV_API_URL} must be set to 'https://<silo>.sdvi.com' in your environment"
    assert rallyUrl, url_help
    url_parts = urlparse(rallyUrl)
    # Ensure sdvi.com silo; permit custom port numbers
    assert re.compile(r'.*\.sdvi\.com(:[0-9]*)?$').match(url_parts.netloc), f"{url_help}, but found '{rallyUrl}'"
    # Apply standard /api path unless user provided something different
    path = 'api' if re.compile('/*').fullmatch(url_parts.path) else url_parts.path
    # Strip query params, etc because subsequent use of the URL will blindly assume path pieces can be appended.
    os.environ[_ENV_API_URL] = urlunparse((url_parts.scheme, url_parts.netloc, path, '', '', ''))

    # Rally can cope with missing keys in this dict, but cannot cope with `None`. Set this env var to an empty dict
    # to avoid AttributeErrors when accessing _ENV_CONTEXT.
    # This validation is unneeded outside the CLI, as eval2 provider creates this variable during bootstrap.
    if not os.environ.get(_ENV_CONTEXT):
        os.environ[_ENV_CONTEXT] = json.dumps({})


def make_context(asset_name, dynamic_preset_data):
    """ The actual context of eval2 jobs run inside a workflow will contain several more attributes set in the connector
    the following are supported by the CLI:

    'assetName',
    'assetId',
    'dynamicPresetData'
    'rallyUrl'
    """
    dynamicPresetData = None
    if dynamic_preset_data:
        with contextlib.suppress(FileNotFoundError):
            with open(dynamic_preset_data) as f:
                dynamicPresetData = json.load(f)

        if not dynamicPresetData:
            try:
                dynamicPresetData = json.loads(dynamic_preset_data)
            except JSONDecodeError as err:
                raise ValueError('dynamic preset data must be a JSON file or JSON string') from err

    ctx = {'assetName': asset_name,
           'assetId': asset._getAssetByName(asset_name) if asset_name else None,
           'dynamicPresetData': dynamicPresetData,
           'rallyUrl': os.environ[_ENV_API_URL]}

    os.environ[_ENV_CONTEXT] = json.dumps(ctx)

    # asset._getAssetByName only depends on the API token and URL, but will have the side effect of having loaded
    # and cached the context. Force it to reload on next use so updated context will get read.
    context._refresh()

    return ctx
