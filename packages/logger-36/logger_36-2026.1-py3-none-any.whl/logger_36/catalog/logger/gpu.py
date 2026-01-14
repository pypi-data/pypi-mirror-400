"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import sys as s

from logger_36.constant.error import GPU_LOGGING_ERROR
from logger_36.instance.logger import L
from logger_36.type.logger import logger_t

try:
    import tensorflow as tsfl  # noqa
    import tensorrt as tsrt  # noqa
except ModuleNotFoundError:
    tsfl = tsrt = None
    _GPU_LOGGING_ERROR = GPU_LOGGING_ERROR
else:
    _GPU_LOGGING_ERROR = None


def LogGPURelatedDetails(*, logger: logger_t = L) -> None:
    """"""
    global _GPU_LOGGING_ERROR

    if None in (tsfl, tsrt):
        if _GPU_LOGGING_ERROR is not None:
            s.__stderr__.write(_GPU_LOGGING_ERROR + "\n")
            _GPU_LOGGING_ERROR = None
        return

    system_details = tsfl.sysconfig.get_build_info()
    logger.info(
        f"GPU-RELATED DETAILS\n"
        f"                GPUs: {tsfl.config.list_physical_devices('GPU')}\n"
        f"                CPUs: {tsfl.config.list_physical_devices('CPU')}\n"
        f"                Cuda: {system_details['cuda_version']}\n"
        f"               CuDNN: {system_details['cudnn_version']}\n"
        f"          Tensorflow: {tsfl.version.VERSION}\n"
        f"    Tensorflow Build: {tsfl.sysconfig.get_build_info()}\n"
        f"            TensorRT: {tsrt.__version__}"
    )
