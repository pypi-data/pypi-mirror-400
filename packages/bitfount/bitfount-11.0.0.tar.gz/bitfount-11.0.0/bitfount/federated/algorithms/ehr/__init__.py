"""Algorithms for Electronic Health Records (EHR) data.

This package contains implementations of algorithms specifically designed for working
with Electronic Health Records (EHR) data.
"""

from bitfount.federated.algorithms.ehr.ehr_base_algorithm import (
    BaseEHRWorkerAlgorithm,
    PatientDetails,
    QuerierType,
)
from bitfount.federated.algorithms.ehr.ehr_patient_info_download_algorithm import (
    EHRPatientInfoDownloadAlgorithm,
)
from bitfount.federated.algorithms.ehr.ehr_patient_query_algorithm import (
    EHRPatientQueryAlgorithm,
    PatientQueryResults,
)
from bitfount.federated.algorithms.ehr.image_selection_algorithm import (
    ImageSelectionAlgorithm,
)
from bitfount.federated.algorithms.ehr.patient_id_exchange_algorithm import (
    PatientIDExchangeAlgorithm,
)

__all__ = [
    "BaseEHRWorkerAlgorithm",
    "EHRPatientInfoDownloadAlgorithm",
    "EHRPatientQueryAlgorithm",
    "ImageSelectionAlgorithm",
    "PatientDetails",
    "PatientIDExchangeAlgorithm",
    "PatientQueryResults",
    "QuerierType",
]

__pdoc__ = {}
# See top level `__init__.py` for an explanation
for _obj in __all__:
    __pdoc__[_obj] = False
