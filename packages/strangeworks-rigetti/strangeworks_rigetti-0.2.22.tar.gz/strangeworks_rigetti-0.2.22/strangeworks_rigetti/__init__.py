"""Strangeworks Rigetti SDK"""

import importlib.metadata

from .strange import get_qc, list_quantum_computers
from .upload_input_file import upload_input_file

__version__ = importlib.metadata.version("strangeworks-rigetti")

list_quantum_computers = list_quantum_computers
get_qc = get_qc
upload_input_file = upload_input_file

RIGETTI_PRODUCT_SLUG = "rigetti"
KERNEL_METHOD_PRODUCT_SLUG = "rigetti-kernel-method"
QNN_PRODUCT_SLUG = "rigetti-qnn"
