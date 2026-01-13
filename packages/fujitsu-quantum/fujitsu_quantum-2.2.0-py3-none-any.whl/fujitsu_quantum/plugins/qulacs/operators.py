# (C) 2024 Fujitsu Limited

from qulacs import GeneralQuantumOperator

from fujitsu_quantum.types import Operator


def to_fqc_operator(operator: GeneralQuantumOperator) -> Operator:
    """Converts a Qulacs GeneralQuantumOperator to an operator list compatible with the 'operator' parameter of
    Fujitsu Quantum Cloud Web APIs.
    """
    operator_list: Operator = []
    for ti in range(operator.get_term_count()):
        term = operator.get_term(ti)
        pauli_str = term.get_pauli_string()
        if not pauli_str:
            pauli_str = 'I'

        coef = term.get_coef()
        operator_list.append((pauli_str, coef))

    return operator_list
