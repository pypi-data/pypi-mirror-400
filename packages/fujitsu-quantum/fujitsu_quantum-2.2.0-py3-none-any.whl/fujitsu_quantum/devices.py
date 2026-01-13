# (C) 2024 Fujitsu Limited

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from os import PathLike
from pprint import pformat
from typing import Any, Dict, List, Optional, Union

from fujitsu_quantum.api.api import get_device, get_devices
from fujitsu_quantum.storage import ObjectReference
from fujitsu_quantum.tasks import Task
from fujitsu_quantum.types import Integer, Operator, ParameterValues, QuantumCircuit, QubitAllocation


class Device:

    class Type(str, Enum):
        # Note: the string literal 'QPU' is hard-coded in Tasks._is_qpu(...) to avoid a circular import.
        # If you change the literal 'QPU', you also need to change the hard-coded literal in the method.
        QPU = 'QPU'
        SIMULATOR = 'simulator'

    class Status(str, Enum):
        available = 'available'
        reserved = 'reserved'
        maintenance = 'maintenance'
        stopped = 'stopped'

    def __init__(self, device_info: Dict[str, Any]):
        self._init_attributes(device_info)

    def _init_attributes(self, device_info):
        self._device_id: str = device_info['deviceId']
        self._device_type: Device.Type = Device.Type(device_info['deviceType'])
        self._status: Device.Status = Device.Status(device_info['status'])
        until_str: Optional[str] = device_info.get('until', None)
        if until_str is not None:
            self._until: Optional[datetime] = datetime.strptime(until_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        else:
            self._until = None
        self._n_pending_tasks: int = device_info['nPendingTasks']
        self._n_qubits: int = device_info['nQubits']
        self._basis_gates: List[str] = device_info['basisGates']
        self._supported_instructions: List[str] = device_info['supportedInstructions']
        self._description: str = device_info['description']
        self._description_heading: str = device_info['descriptionHeading']
        self._notice: Optional[str] = device_info.get('notice', None)
        self._notice_heading: Optional[str] = device_info.get('noticeHeading', None)
        self._n_nodes: Optional[int] = device_info.get('nNodes', None)
        self._calibration: Optional[dict] = device_info.get('calibrationData', None)
        self._fetched_at: datetime = device_info['fetchedAt']
        self._str = {k: v for k, v in device_info.items() if v is not None}

    def __str__(self) -> str:
        return pformat(self._str)

    def reload(self):
        """Retrieves the latest information of the device from the cloud, then updates the attributes of this object."""
        resp: dict = get_device(self._device_id)
        resp.update({'fetchedAt': datetime.now(timezone.utc)})
        self._init_attributes(resp)

    @property
    def fetched_at(self) -> datetime:
        return self._fetched_at

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def device_type(self) -> Type:
        return self._device_type

    @property
    def status(self) -> Status:
        return self._status

    @property
    def until(self) -> Optional[datetime]:
        return self._until

    @property
    def n_pending_tasks(self) -> int:
        return self._n_pending_tasks

    @property
    def n_qubits(self) -> int:
        return self._n_qubits

    @property
    def basis_gates(self) -> List[str]:
        return self._basis_gates

    @property
    def supported_instructions(self) -> List[str]:
        return self._supported_instructions

    @property
    def description(self) -> str:
        return self._description

    @property
    def description_heading(self) -> str:
        return self._description_heading

    @property
    def notice(self) -> Optional[str]:
        return self._notice

    @property
    def notice_heading(self) -> Optional[str]:
        return self._notice_heading

    @property
    def n_nodes(self) -> Optional[int]:
        return self._n_nodes

    @property
    def calibration(self):
        # TODO will be supported in future versions
        return None

    def submit_sampling_task(self,
                             program: Union[str, list[str], QuantumCircuit, list[QuantumCircuit], ObjectReference],
                             n_shots: Union[Integer, list[Integer], 'numpy.typing.NDArray', ObjectReference] = Task.DEFAULT_SHOTS,
                             parameter_values: Optional[Union[ParameterValues, list[ParameterValues], 'numpy.typing.NDArray', ObjectReference]] = None,
                             name: Optional[str] = None,
                             note: Optional[str] = None,
                             skip_transpilation: bool = False,
                             seed_transpilation: Optional[int] = None,
                             transpilation_options: Optional[Dict[str, Any]] = None,
                             qubit_allocation: Optional[Union[QubitAllocation, list[QubitAllocation], ObjectReference]] = None,
                             ro_error_mitigation: Optional[Union[Task.ROErrorMitigation, str]] = None,
                             n_nodes: Optional[int] = None,
                             n_per_node: Optional[int] = None,
                             seed_simulation: Optional[int] = None,
                             include_transpilation_result: bool = False,
                             timeout: Optional[int] = None,
                             **extra_config) -> Task:

        return Task.submit(self,
                           task_type=Task.Type.SAMPLING,
                           program=program,
                           n_shots=n_shots,
                           parameter_values=parameter_values,
                           name=name,
                           note=note,
                           skip_transpilation=skip_transpilation,
                           seed_transpilation=seed_transpilation,
                           transpilation_options=transpilation_options,
                           qubit_allocation=qubit_allocation,
                           ro_error_mitigation=ro_error_mitigation,
                           n_nodes=n_nodes,
                           n_per_node=n_per_node,
                           seed_simulation=seed_simulation,
                           estimation_dop=None,
                           include_transpilation_result=include_transpilation_result,
                           timeout=timeout,
                           **extra_config)

    def submit_estimation_task(self,
                               program: Union[str, list[str], QuantumCircuit, list[QuantumCircuit], ObjectReference],
                               operator: Union[Operator, list[Operator], ObjectReference],
                               method: Union[Task.EstimationMethod, str] = Task.EstimationMethod.SAMPLING,
                               n_shots: Optional[Union[Integer, list[Integer], 'numpy.typing.NDArray', ObjectReference]] = None,
                               parameter_values: Optional[Union[ParameterValues, list[ParameterValues], 'numpy.typing.NDArray', ObjectReference]] = None,
                               name: Optional[str] = None,
                               note: Optional[str] = None,
                               skip_transpilation: bool = False,
                               seed_transpilation: Optional[int] = None,
                               transpilation_options: Optional[Dict[str, Any]] = None,
                               qubit_allocation: Optional[Union[QubitAllocation, list[QubitAllocation], ObjectReference]] = None,
                               ro_error_mitigation: Optional[Union[Task.ROErrorMitigation, str]] = None,
                               n_nodes: Optional[int] = None,
                               n_per_node: Optional[int] = None,
                               seed_simulation: Optional[int] = None,
                               estimation_dop: Optional[Union[int, str]] = None,
                               include_transpilation_result: bool = False,
                               timeout: Optional[int] = None,
                               **extra_config) -> Task:

        return Task.submit(self,
                           task_type=Task.Type.ESTIMATION,
                           program=program,
                           operator=operator,
                           method=method,
                           n_shots=n_shots,
                           parameter_values=parameter_values,
                           name=name,
                           note=note,
                           skip_transpilation=skip_transpilation,
                           seed_transpilation=seed_transpilation,
                           transpilation_options=transpilation_options,
                           qubit_allocation=qubit_allocation,
                           ro_error_mitigation=ro_error_mitigation,
                           n_nodes=n_nodes,
                           n_per_node=n_per_node,
                           seed_simulation=seed_simulation,
                           estimation_dop=estimation_dop,
                           include_transpilation_result=include_transpilation_result,
                           timeout=timeout,
                           **extra_config)

    def submit_hybrid_task(self,
                           program_paths: list[Union[str, PathLike]],
                           config_path: Union[str, PathLike],
                           name: Optional[str] = None,
                           note: Optional[str] = None,
                           timeout: Optional[int] = None,
                           **extra_config) -> Task:

        return Task.submit(self,
                           task_type=Task.Type.HYBRID,
                           program=program_paths,
                           name=name,
                           note=note,
                           task_config_path=config_path,
                           timeout=timeout,
                           **extra_config)


class DeviceIterator:
    def __init__(self, device_info_list: list[dict]):
        self._devices = [Device(dev) for dev in device_info_list]
        self._devices_iter = iter(self._devices)

    def __iter__(self) -> DeviceIterator:
        return self

    def __next__(self) -> Device:
        return next(self._devices_iter)


class Devices:
    @staticmethod
    def list() -> list[Device]:
        return list(Devices.iter())

    @staticmethod
    def iter() -> DeviceIterator:
        resp: list = get_devices()
        fetch_time = datetime.now(timezone.utc)
        for device_info in resp:
            device_info.update({'fetchedAt': fetch_time})
        return DeviceIterator(resp)

    @staticmethod
    def get(device_id: str) -> Device:
        resp: dict = get_device(device_id)
        resp.update({'fetchedAt': datetime.now(timezone.utc)})
        return Device(resp)
