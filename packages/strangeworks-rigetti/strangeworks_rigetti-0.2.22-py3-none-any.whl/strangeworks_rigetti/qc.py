import strangeworks
from pyquil import Program
from pyquil.api import QuantumComputer
from strangeworks.core.client.resource import Resource
from strangeworks.core.errors.error import StrangeworksError

import strangeworks_rigetti
from strangeworks_rigetti.result import StrangeworksExecutionResult


class QuantumComputer(QuantumComputer):
    def __init__(self, ogc: QuantumComputer, as_qvm: bool, *args, **kwargs):
        self.as_qvm = "True" if as_qvm else "False"

        super().__init__(
            name=ogc.name,
            qam=ogc.qam,
            compiler=ogc.compiler,
        )

    def run(
        self, program, circuit_type=None, shots: int = 1
    ) -> StrangeworksExecutionResult:
        resource: Resource = None
        if isinstance(program, Program):
            # product: rigetti
            payload = self.__serialize_program(program, circuit_type)
            resource = strangeworks.get_resource_for_product(
                strangeworks_rigetti.RIGETTI_PRODUCT_SLUG
            )
            endpoint = "jobs"
        elif isinstance(program, dict):
            # product: rigetti-kernel-method
            payload = program
            payload["circuit_type"] = circuit_type
            endpoint = "kernel"
            resource = strangeworks.get_resource_for_product(
                strangeworks_rigetti.KERNEL_METHOD_PRODUCT_SLUG
            )

            if "pixels" in program:
                # product: rigetti-qnn
                resource = strangeworks.get_resource_for_product(
                    strangeworks_rigetti.KERNEL_METHOD_PRODUCT_SLUG
                )
                endpoint = "qnn"

        else:
            raise StrangeworksError.invalid_argument(
                "must pass a Program to compile & execute with Rigetti"
            )

        payload["as_qvm"] = self.as_qvm

        results = strangeworks.execute(
            res=resource,
            payload=payload,
            endpoint=endpoint,
        )

        if isinstance(program, dict):
            return results

        return results  # StrangeworksExecutionResult.from_json(results)

    def __serialize_program(self, p: Program, circuit_type) -> dict:
        d = self.program_to_json(p)
        d["as_qvm"] = self.as_qvm
        d["circuit_type"] = circuit_type
        return d

    def program_to_json(self, prg: Program) -> dict:
        return {
            "target": self.name,
            "circuit": prg.out(),
            "shots": prg.num_shots,
        }
