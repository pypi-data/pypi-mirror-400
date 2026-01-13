"""Protocols related to EHR interactions."""

from bitfount.federated.protocols.ehr.data_extraction_protocol_charcoal import (
    DataExtractionProtocolCharcoal,
)
from bitfount.federated.protocols.ehr.nextgen_search_protocol import (
    NextGenSearchProtocol,
)

__all__: list[str] = [
    "DataExtractionProtocolCharcoal",
    "NextGenSearchProtocol",
]

# See top level `__init__.py` for an explanation
__pdoc__ = {"data_extraction_protocol_charcoal": False}
for _obj in __all__:
    __pdoc__[_obj] = False
