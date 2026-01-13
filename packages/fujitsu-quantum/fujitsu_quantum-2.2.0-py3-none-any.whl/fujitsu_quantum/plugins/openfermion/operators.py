# (C) 2024 Fujitsu Limited
from openfermion.ops.operators import QubitOperator

from fujitsu_quantum.types import Operator


def to_fqc_operator(qubit_operator: QubitOperator, ignore_small_coef: bool = True, small_coef_tol: float = 1e-8)\
        -> Operator:
    """Converts an OpenFermion QubitOperator to an operator list compatible with the 'operator' parameter of
    Fujitsu Quantum Cloud Web APIs.
    """

    operator: Operator = []
    for term, coef in sorted(qubit_operator.terms.items()):
        if ignore_small_coef and qubit_operator._issmall(coef, small_coef_tol):
            continue

        pauli_index_list = []
        for factor in term:
            index, action = factor
            action_str = qubit_operator.action_strings[qubit_operator.actions.index(action)]
            pauli_index_list.append(f'{action_str} {index}')

        if not pauli_index_list:
            paulis_str = 'I'
        else:
            paulis_str = ' '.join(pauli_index_list)

        operator.append((paulis_str, coef))

    return operator
