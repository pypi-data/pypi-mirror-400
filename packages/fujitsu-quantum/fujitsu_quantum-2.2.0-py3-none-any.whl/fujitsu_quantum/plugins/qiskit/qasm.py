from qiskit import QuantumCircuit, qasm3, transpile


# For the OpenQASM 3 standard gates definition, see qiskit.qasm3.STDGATES_INC_GATES
_qasm3_standard_gates = [
    'p', 'x', 'y', 'z', 'h', 's', 'sdg', 't', 'tdg', 'sx', 'rx', 'ry', 'rz',
    'cx', 'cy', 'cz', 'cp', 'crx', 'cry', 'crz', 'ch', 'swap', 'ccx', 'cswap', 'cu',
    'id',
    # 'u'  # 'u' gate is excluded because qasm3.loads_experimental cannot load it.
]


def to_qasm(circuit: QuantumCircuit) -> str:
    """Convert a quantum circuit to its OpenQASM 3 representation.

    qiskit.qasm3.dumps produces invalid custom gate definitions for some cases.
    As a workaround, this function transpiles the circuit to use only standard gates before conversion.

    Args:
        circuit: The quantum circuit to convert.

    Returns:
        str: The OpenQASM 3 representation of the circuit.
    """

    # There is a bug that qasm3.dumps outputs invalid custom gate definitions for some cases.
    # As a workaround, we transpile the circuit so that it only uses standard gates to avoid custom gate definitions.
    transpiled_circ = transpile(circuit, basis_gates=_qasm3_standard_gates, optimization_level=0)
    return qasm3.dumps(transpiled_circ, disable_constants=True)
