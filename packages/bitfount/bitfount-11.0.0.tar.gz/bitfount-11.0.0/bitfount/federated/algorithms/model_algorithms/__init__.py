"""Algorithms for remote/federated model training on data."""

from __future__ import annotations

from bitfount.federated.algorithms.model_algorithms import post_processing_utils
from bitfount.federated.algorithms.model_algorithms.base import (
    BaseModelAlgorithmFactory,
)
from bitfount.federated.algorithms.model_algorithms.evaluate import (
    ModelEvaluation,
)
from bitfount.federated.algorithms.model_algorithms.federated_training import (
    FederatedModelTraining,
)
from bitfount.federated.algorithms.model_algorithms.inference import (
    ModelInference,
)
from bitfount.federated.algorithms.model_algorithms.post_processing_utils import *  # noqa: F403
from bitfount.federated.algorithms.model_algorithms.train_and_evaluate import (
    ModelTrainingAndEvaluation,
)

__all__: list[str] = [
    "BaseModelAlgorithmFactory",
    "FederatedModelTraining",
    "ModelEvaluation",
    "ModelInference",
    "ModelTrainingAndEvaluation",
]

__all__.extend(post_processing_utils.__all__)


__pdoc__ = {}
# See top level `__init__.py` for an explanation
for _obj in __all__:
    __pdoc__[_obj] = False
