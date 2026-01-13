"""Protocols for remote/federated model training on data."""

from __future__ import annotations

from bitfount.federated.protocols.model_protocols.federated_averaging import (
    FederatedAveraging,
)
from bitfount.federated.protocols.model_protocols.inference_csv_report import (
    InferenceAndCSVReport,
)
from bitfount.federated.protocols.model_protocols.inference_csv_report_for_modeller import (  # noqa: E501
    InferenceAndReturnCSVReport,
)
from bitfount.federated.protocols.model_protocols.inference_image_output import (
    InferenceAndImageOutput,
)
from bitfount.federated.protocols.model_protocols.instrumented_inference_csv_report import (  # noqa: E501
    InstrumentedInferenceAndCSVReport,
)

__all__: list[str] = [
    "FederatedAveraging",
    "InferenceAndCSVReport",
    "InferenceAndReturnCSVReport",
    "InferenceAndImageOutput",
    "InstrumentedInferenceAndCSVReport",
]

# See top level `__init__.py` for an explanation
__pdoc__ = {}
for _obj in __all__:
    __pdoc__[_obj] = False
