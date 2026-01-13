import base64
import pickle
from typing import List, Optional

import strangeworks
from pyquil.api._qam import QAMExecutionResult
from qcs_sdk import QCSClient

import strangeworks_rigetti

from .qc import QuantumComputer
from .result import StrangeworksExecutionResult


def list_quantum_computers() -> List[str]:
    backends = strangeworks.backends(product_slugs=["rigetti"])
    return backends


def get_qc(
    name: str = "WavefunctionSimulator",
    as_qvm: Optional[bool] = None,
    noisy: Optional[bool] = None,
    compiler_timeout: float = 10.0,
    execution_timeout: float = 10.0,
    client_configuration: Optional[QCSClient] = None,
    **kwargs,
) -> QuantumComputer:
    """Get quantum computer.

    Parameters
    ----------
    name: str
        name of computer. Defaults to "WavefunctionSimulator"
    as_qvm: bool
        used to determine if the job is to be run using the quantum virtual machine.
        If it is True, the run method will use the simulator for free. If it is False,
        the job is run on Rigetti hardware and will incur a cost.

    Returns
    -------
    : QuantumComputer
        QuantumComputer object
    """
    # TODO: get_backend asks for a slug not name, so for now we do this:
    ogc = strangeworks.client.get_backends(
        product_slugs=[
            strangeworks_rigetti.RIGETTI_PRODUCT_SLUG,
            strangeworks_rigetti.KERNEL_METHOD_PRODUCT_SLUG,
            strangeworks_rigetti.QNN_PRODUCT_SLUG,
        ]
    )
    my_backend = None
    for b in ogc:
        if name == "WavefunctionSimulator":
            my_backend = b
            break
        if b.remote_backend_id == name:
            my_backend = b
            break

    if my_backend is not None:
        my_backend.qam = StrangeworksExecutionResult()
        my_backend.compiler = None

    return QuantumComputer(my_backend, as_qvm=as_qvm)


def execution_from_result(response: dict) -> QAMExecutionResult:
    pickled_res = response["pickled_result"]
    pickle_bytes = base64.b64decode(pickled_res)
    return pickle.loads(pickle_bytes)
