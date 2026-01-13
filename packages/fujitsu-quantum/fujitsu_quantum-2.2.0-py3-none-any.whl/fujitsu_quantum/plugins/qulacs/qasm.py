# (C) 2024 Fujitsu Limited

import cmath
from typing import Union

from qulacs import ParametricQuantumCircuit, QuantumCircuit

_gate_map_1q = {
    'X': 'x',
    'Y': 'y',
    'Z': 'z',
    'H': 'h',
    'S': 's',
    'Sdag': 'sdg',
    'T': 't',
    'Tdag': 'tdg',
    'sqrtX': 'sx',
    'sqrtXdag': 'sxdg',
    'sqrtY': 'sy',
    'sqrtYdag': 'sydg',
    'I': 'id',
}

_gate_map_controlled_2q = {
    'CNOT': 'cx',
    'CZ': 'cz',
}

_gate_map_2q = {
    'SWAP': 'swap',
}

_gate_map_rotation_x_1q = {
    'X-rotation': 'rx',
    'ParametricRX': 'rx',
}

_gate_map_rotation_y_1q = {
    'Y-rotation': 'ry',
    'ParametricRY': 'ry',
}

_gate_map_rotation_z_1q = {
    'Z-rotation': 'rz',
    'ParametricRZ': 'rz',
}


def to_qasm(circuit: Union[QuantumCircuit, ParametricQuantumCircuit]) -> str:
    """Converts a Qulacs circuit to OpenQASM 3 code. The given circuit must consist of only the following gates:
    X, Y, Z, H, S, Sdag, T, Tdag, sqrtX, sqrtXdag, sqrtY, sqrtYdag, I, CNOT, CZ, SWAP, RX, RY, RZ,
    ParametricRX, ParametricRY, ParametricRZ."""

    qasm_lines = ['OPENQASM 3;', 'include "stdgates.inc";', f'qubit[{circuit.get_qubit_count()}] q;',
                  'gate sxdg _gate_q_0 {', '  s _gate_q_0;', '  h _gate_q_0;', '  s _gate_q_0;', '}',
                  'gate sy _gate_q_0 {', '  ry(pi/2) _gate_q_0;', '  gphase(pi/4);', '}',
                  'gate sydg _gate_q_0 {', '  ry(-pi/2) _gate_q_0;', '  gphase(7*pi/4);', '}', ]

    for gate_i in range(circuit.get_gate_count()):
        gate = circuit.get_gate(gate_i)
        control_indices = gate.get_control_index_list()
        target_indices = gate.get_target_index_list()
        gate_name = gate.get_name()

        if gate_name in _gate_map_1q:
            qasm_lines.append(f'{_gate_map_1q[gate_name]} q[{target_indices[0]}];')
        elif gate_name in _gate_map_controlled_2q:
            qasm_lines.append(f'{_gate_map_controlled_2q[gate_name]} q[{control_indices[0]}], q[{target_indices[0]}];')
        elif gate_name in _gate_map_2q:
            qasm_lines.append(f'{_gate_map_2q[gate_name]} q[{target_indices[0]}], q[{target_indices[1]}];')
        elif gate_name in _gate_map_rotation_x_1q:
            matrix = gate.get_matrix()
            angle = cmath.phase(matrix[0][0] - matrix[1][0]) * 2
            qasm_lines.append(f'{_gate_map_rotation_x_1q[gate_name]}({angle}) q[{target_indices[0]}];')
        elif gate_name in _gate_map_rotation_y_1q:
            matrix = gate.get_matrix()
            angle = cmath.phase(matrix[0][0] + matrix[1][0] * 1j) * 2
            qasm_lines.append(f'{_gate_map_rotation_y_1q[gate_name]}({angle}) q[{target_indices[0]}];')
        elif gate_name in _gate_map_rotation_z_1q:
            matrix = gate.get_matrix()
            angle = cmath.phase(matrix[1][1]) * 2
            qasm_lines.append(f'{_gate_map_rotation_z_1q[gate_name]}({angle}) q[{target_indices[0]}];')
        else:
            raise ValueError(f'The given circuit includes {gate_name} gate, but '
                             f'{gate_name} cannot be converted to OpenQASM code.')

    qasm_str = '\n'.join(qasm_lines)
    return qasm_str
