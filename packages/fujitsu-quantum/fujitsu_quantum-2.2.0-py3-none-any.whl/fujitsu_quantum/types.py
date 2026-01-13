import numbers
from typing import Union, Any, Optional, TypeAlias

# Avoid importing numpy just for type checking to minimize the dependent libraries of this SDK
# (e.g., from numpy import integer, floating, inexact).
Integer: TypeAlias = Union[numbers.Integral, 'numpy.integer']
RealNumber: TypeAlias = Union[numbers.Real, 'numpy.integer', 'numpy.floating']
Number: TypeAlias = Union[numbers.Number, 'numpy.integer', 'numpy.inexact']
ParameterValues: TypeAlias = Union[list[Union[list[RealNumber], 'numpy.typing.NDArray']], 'numpy.typing.NDArray']  # The rightmost type means a two-dimensional numpy.ndarray.
"""A sequence of sequences (two-dimensional array)."""
QubitAllocation: TypeAlias = Union[dict[str, Integer], list[Integer]]

# the operator type used in the SDK
Operator: TypeAlias = list[tuple[str, numbers.Number]]
"""The type of operators used for estimation tasks.
E.g., [('I', 1.2), ('X 0 Y 2 Z 5', 1.2 + 0.5j), ('X 3 X 4', -2.5 + 1.2j)]
"""

# the operator type used in the Web API
APIOperator: TypeAlias = list[list[Union[str, list[RealNumber]]]]  # if numpy installed, list[list[Union[str, list[Union[float, numpy.floating]]]]]

QuantumCircuit: TypeAlias = 'qiskit.circuit.quantumcircuit.QuantumCircuit'

# type converters

def to_api_operator(sdk_operator: Optional[Union[Operator, list[Operator], APIOperator, list[APIOperator]]])\
        -> Optional[Union[APIOperator, list[APIOperator]]]:

    if (sdk_operator is None) or (not is_sdk_operator(sdk_operator)):
        # no conversion is needed
        return sdk_operator  # noqa

    if is_single_value('operator', sdk_operator):
        return to_api_single_operator(sdk_operator)

    return [to_api_single_operator(one_sdk_op) for one_sdk_op in sdk_operator]  # noqa


def to_api_single_operator(sdk_operator: Operator) -> APIOperator:
    return [[pauli_and_coef[0], [pauli_and_coef[1].real, pauli_and_coef[1].imag]] for pauli_and_coef in sdk_operator]


def to_sdk_operator(api_operator: Optional[Union[APIOperator, list[APIOperator], Operator, list[Operator]]])\
        -> Optional[Union[Operator, list[Operator]]]:

    if api_operator is None or is_sdk_operator(api_operator):
        # no conversion is needed
        return api_operator

    if is_single_value('operator', api_operator):
        return to_sdk_single_operator(api_operator)

    return [to_sdk_single_operator(one_api_op) for one_api_op in api_operator]  # noqa


def to_sdk_single_operator(api_operator: APIOperator) -> Operator:
    operator = []

    for pauli_and_coef in api_operator:
        if pauli_and_coef[1][1] == 0:
            # the coefficient is either an int or float value
            coef = pauli_and_coef[1][0]
        else:
            # the coefficient is a complex value
            coef = complex(pauli_and_coef[1][0], pauli_and_coef[1][1])

        operator.append((pauli_and_coef[0], coef))

    return operator


def is_sdk_operator(operator) -> bool:
    if is_single_value('operator', operator):
        return isinstance(operator[0], tuple)

    return isinstance(operator[0][0], tuple)


def to_single_value(param_name: str, value: Any) -> Any:
    if is_single_value(param_name, value):
        return value

    return value[0]


def is_single_value(param_name: str, value: Any) -> bool:
    if param_name == 'code':
        # str for OpenQASM code, bytes for QPY data
        return isinstance(value, (str, bytes))

    if param_name == 'n_shots':
        return isinstance(value, int)

    if param_name == 'operator':
        # the below expression can handle both the API and SDK operator formats
        return isinstance(value, list) and len(value) > 0 and isinstance(value[0][0], str)

    if param_name == 'parameter_values':
        return (isinstance(value, list)
                and len(value) > 0 and isinstance(value[0], list)
                and len(value[0]) > 0 and isinstance(value[0][0], (int, float)))

    if param_name == 'qubit_allocation':
        return (isinstance(value, dict)
                or (isinstance(value, list) and len(value) > 0 and isinstance(value[0], int)))

    return False


def single_to_multiple_values(param_values: dict) -> tuple[dict, list]:
    result = {}
    converted_param_names = []
    for param_name, value in param_values.items():
        if is_single_value(param_name, value):
            result[param_name] = [value]
            converted_param_names.append(param_name)
        else:
            result[param_name] = value

    return result, converted_param_names
