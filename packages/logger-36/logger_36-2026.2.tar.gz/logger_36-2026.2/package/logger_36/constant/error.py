"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

GPU_LOGGING_ERROR = (
    "GPU details cannot be logged because the Tensorflow and/or Tensorrt package(s) "
    "(https://www.tensorflow.org/, https://developer.nvidia.com/tensorrt)"
    "is/are not installed or not importable."
)

MEMORY_MEASURE_ERROR = (
    "Memory usage cannot be shown because the Psutil package "
    "(https://psutil.readthedocs.io/en/latest/)"
    "is not installed or not importable."
)

MISSING_RICH_MESSAGE = (
    "The Rich console handler is not available because the Rich package "
    "(https://rich.readthedocs.io/en/stable/) "
    "is not installed or not importable. "
    "Falling back to the raw console."
)

CANNOT_SAVE_RECORDS = "Cannot save logging records"
