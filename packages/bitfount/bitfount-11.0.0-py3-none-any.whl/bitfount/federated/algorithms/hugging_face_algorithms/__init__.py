"""Algorithms for remote Hugging Face models."""

from __future__ import annotations

from bitfount.federated.algorithms.hugging_face_algorithms.hugging_face_image_classification import (  # noqa: E501
    HuggingFaceImageClassificationInference,
)
from bitfount.federated.algorithms.hugging_face_algorithms.hugging_face_image_segmentation import (  # noqa: E501
    HuggingFaceImageSegmentationInference,
)
from bitfount.federated.algorithms.hugging_face_algorithms.hugging_face_perplexity import (  # noqa: E501
    HuggingFacePerplexityEvaluation,
)
from bitfount.federated.algorithms.hugging_face_algorithms.hugging_face_text_classification import (  # noqa: E501
    HuggingFaceTextClassificationInference,
)
from bitfount.federated.algorithms.hugging_face_algorithms.hugging_face_text_generation import (  # noqa: E501
    HuggingFaceTextGenerationInference,
)
from bitfount.federated.algorithms.hugging_face_algorithms.timm_fine_tuning import (
    TIMMFineTuning,
)
from bitfount.federated.algorithms.hugging_face_algorithms.timm_inference import (
    TIMMInference,
)
from bitfount.federated.algorithms.hugging_face_algorithms.utils import (
    TIMMTrainingConfig,
    get_device_for_model,
    train_one_epoch,
    validate,
)

__all__ = [
    "HuggingFaceImageClassificationInference",
    "HuggingFaceImageSegmentationInference",
    "HuggingFacePerplexityEvaluation",
    "HuggingFaceTextClassificationInference",
    "HuggingFaceTextGenerationInference",
    "TIMMFineTuning",
    "TIMMInference",
    "TIMMTrainingConfig",
    "get_device_for_model",
    "train_one_epoch",
    "validate",
]

# Hide hugging face algorithms subpackage from pdoc-generated documentation
__pdoc__ = {}
# See top level `__init__.py` for an explanation
for _obj in __all__:
    __pdoc__[_obj] = False
