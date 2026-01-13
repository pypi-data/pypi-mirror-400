""" Support for new or experimental features. These features may be moved into other sub-modules as their behaviors
 are finalized

Importing the experimental module:

>>> from rally.experimental import <feature> [as <alias>]

.. warning::

    **DEPRECATION WARNING**: `rally.experimental.asset_status` methods will be removed from the experimental submodule in a future release. These methods are available in the `asset` submodule.

"""
from rally.experimental.asset_status import *
