"""Manages the federated communication and training of models.

Federated algorithm plugins can also be imported from this package.
"""

from __future__ import annotations

from bitfount.federated import (
    aggregators,
    algorithms,
    authorisation_checkers,
    background_file_counter,
    early_stopping,
    encryption,
    exceptions,
    helper,
    keys_setup,
    logging,
    mixins,
    model_reference,
    modeller,
    monitoring,
    pod,
    pod_response_message,
    pod_vitals,
    privacy,
    protocols,
    schema_management,
    secure,
    task_requests,
    transport,
    types,
    utils,
    worker,
)
from bitfount.federated.aggregators import *  # noqa: F403
from bitfount.federated.algorithms import *  # noqa: F403
from bitfount.federated.authorisation_checkers import *  # noqa: F403
from bitfount.federated.background_file_counter import *  # noqa: F403
from bitfount.federated.early_stopping import *  # noqa: F403
from bitfount.federated.encryption import *  # noqa: F403
from bitfount.federated.exceptions import *  # noqa: F403
from bitfount.federated.helper import *  # noqa: F403
from bitfount.federated.keys_setup import *  # noqa: F403
from bitfount.federated.logging import *  # noqa: F403
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.mixins import *  # noqa: F403
from bitfount.federated.model_reference import *  # noqa: F403
from bitfount.federated.modeller import *  # noqa: F403
from bitfount.federated.monitoring import *  # noqa: F403
from bitfount.federated.pod import *  # noqa: F403
from bitfount.federated.pod_response_message import *  # noqa: F403
from bitfount.federated.pod_vitals import *  # noqa: F403
from bitfount.federated.privacy import *  # noqa: F403
from bitfount.federated.protocols import *  # noqa: F403
from bitfount.federated.schema_management import *  # noqa: F403
from bitfount.federated.secure import *  # noqa: F403
from bitfount.federated.task_requests import *  # noqa: F403
from bitfount.federated.transport import *  # noqa: F403
from bitfount.federated.types import *  # noqa: F403
from bitfount.federated.utils import *  # noqa: F403
from bitfount.federated.worker import *  # noqa: F403

_logger = _get_federated_logger(__name__)

__all__: list[str] = []

# Protocols and algorithms are imported from their own respective subpackages because
# of how we handle plugins for these components.
__all__.extend(aggregators.__all__)
__all__.extend(algorithms.__all__)
__all__.extend(authorisation_checkers.__all__)
__all__.extend(background_file_counter.__all__)
__all__.extend(early_stopping.__all__)
__all__.extend(encryption.__all__)
__all__.extend(exceptions.__all__)
__all__.extend(helper.__all__)
__all__.extend(keys_setup.__all__)
__all__.extend(logging.__all__)
__all__.extend(mixins.__all__)
__all__.extend(model_reference.__all__)
__all__.extend(modeller.__all__)
__all__.extend(monitoring.__all__)
__all__.extend(pod.__all__)
__all__.extend(pod_response_message.__all__)
__all__.extend(pod_vitals.__all__)
__all__.extend(privacy.__all__)
__all__.extend(protocols.__all__)
__all__.extend(schema_management.__all__)
__all__.extend(secure.__all__)
__all__.extend(task_requests.__all__)
__all__.extend(transport.__all__)
__all__.extend(types.__all__)
__all__.extend(utils.__all__)
__all__.extend(worker.__all__)

# See top level `__init__.py` for an explanation
__pdoc__ = {}
for _obj in __all__:
    __pdoc__[_obj] = False
