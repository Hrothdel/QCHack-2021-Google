from typing import List, Tuple

import numpy as np
import cirq

def matrix_to_sycamore_operations(
    target_qubits: List[cirq.GridQubit], matrix: np.ndarray
) -> Tuple[cirq.OP_TREE, List[cirq.GridQubit]]:
    """A method to convert a unitary matrix to a list of Sycamore operations.

    This method will return a list of `cirq.Operation`s using the qubits and (optionally) ancilla
    qubits to implement the unitary matrix `matrix` on the target qubits `qubits`.
    The operations are also supported by `cirq.google.gate_sets.SYC_GATESET`.

    Args:
        target_qubits: list of qubits the returned operations will act on. The qubit order defined by the list
            is assumed to be used by the operations to implement `matrix`.
        matrix: a matrix that is guaranteed to be unitary and of size (2**len(qs), 2**len(qs)).
    Returns:
        A tuple of operations and ancilla qubits allocated.
            Operations: In case the matrix is supported, a list of operations `ops` is returned.
                `ops` acts on `qs` qubits and for which `cirq.unitary(ops)` is equal to `matrix` up
                 to certain tolerance. In case the matrix is not supported, it might return NotImplemented to
                 reduce the noise in the judge output.
            Ancilla qubits: In case ancilla qubits are allocated a list of ancilla qubits. Otherwise
                an empty list.
        .
    """

    gate = getGate(matrix)
    if gate != None:
        operation = gate.on(*target_qubits)

        converter = cirq.google.ConvertToSycamoreGates()
        converted = converter.convert(operation)
        circuit = cirq.Circuit(converted)

        #optimized = cirq.google.optimized_for_sycamore(circuit)

        return circuit, []
    else:
        return NotImplemented, []

def getGate(matrix):
    qubit_number = int(np.log2(len(matrix)))
    identity = cirq.IdentityGate(qubit_number)

    if np.array_equal(matrix, identity._unitary_()):
        return identity
    if qubit_number == 2:
        gates = [cirq.CNOT,
                cirq.CX,
                cirq.CZ,
                cirq.SWAP,
                cirq.ISWAP,
                cirq.google.SYC]

        for gate in gates:
            if np.array_equal(gate._unitary_(), matrix):
                return gate
    if qubit_number == 3:
        gates = [cirq.CCNOT,
                cirq.CCX,
                cirq.CCZ,
                cirq.CSWAP,
                cirq.FREDKIN]

        for gate in gates:
            if np.array_equal(gate._unitary_(), matrix):
                return gate

    if qubit_number < 3:
        return cirq.MatrixGate(matrix)

    return None
