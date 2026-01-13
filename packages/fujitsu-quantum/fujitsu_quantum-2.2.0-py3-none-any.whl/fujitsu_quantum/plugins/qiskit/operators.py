from qiskit.quantum_info import SparsePauliOp

from fujitsu_quantum.types import Operator


def to_fqc_operator(qiskit_op: SparsePauliOp) -> Operator:
    """Converts the given SparsePauliOp object to an operator object for submit_estimation_task(...).

    Args:
        qiskit_op (SparsePauliOp): a SparsePauliOp object to convert.

    Returns:
        Operator: an Operator object for submit_estimation_task(...).
    """
    paulis_api_str = [_to_sparse_pauli_label(pauli.to_label()) for pauli in qiskit_op.paulis]

    return [(pauli, complex(coef.real, coef.imag)) for pauli, coef in zip(paulis_api_str, qiskit_op.coeffs)]


def _to_sparse_pauli_label(pauli_label: str) -> str:
    """Converts the given pauli label (e.g., 'IXYIIZ' (little-endian)) to a sparse pauli label (e.g., 'Z 0 Y 3 X 4')."""
    sparse_pauli_label = ''
    for i, pauli_str in enumerate(reversed(pauli_label)):
        # omit 'I'
        sparse_pauli_label += (pauli_str + ' ' + str(i) + ' ') if pauli_str != 'I' else ''

    sparse_pauli_label = sparse_pauli_label[:-1]  # delete the last space

    if sparse_pauli_label == '':
        # In a case where the given pauli label consists of 'I's only (e.g., 'IIIIII')
        sparse_pauli_label = 'I'

    return sparse_pauli_label
