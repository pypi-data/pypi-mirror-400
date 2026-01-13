# (C) 2024 Fujitsu Limited

from __future__ import annotations

import typing
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from os import PathLike
from pprint import pformat
from typing import Any, Optional, Union
from uuid import UUID

from fujitsu_quantum.api.api import get_task
from fujitsu_quantum.storage import StorageService, resolve_raw_ref
from fujitsu_quantum.types import QubitAllocation

if typing.TYPE_CHECKING:
    from fujitsu_quantum.tasks import Task


class Result:

    def __init__(self, task: Task, outputs: dict[str, Any]):
        self._task = task

        self._message: Optional[str] = outputs.get('message', None)

        self._execution_result: Optional[list[ExecutionResult]] = None
        self._transpilation_result: Optional[list[TranspilationResult]] = None
        self._hybrid_result_s3_url: Optional[str] = None

        if 'result' in outputs:
            if self._task.type == 'hybrid':
                self._hybrid_result_s3_url = outputs['result'].get('ref', None)
            else:
                result: dict = resolve_raw_ref('result', outputs['result'], {})

                trans_result: Optional[list] = result.get('transpilation', None)
                if trans_result is None:
                    self._transpilation_result = None
                else:
                    self._transpilation_result = [TranspilationResult.from_dict(one_trans_result) for one_trans_result in trans_result]

                if self._transpilation_result is None:
                    id_to_trans_result = None
                else:
                    id_to_trans_result = { tr.id: tr for tr in self._transpilation_result }

                exec_result: Optional[list] = result.get('execution', None)
                if exec_result is None:
                    self._execution_result = None
                else:
                    self._execution_result = [ExecutionResult(one_exec_result, id_to_trans_result) for one_exec_result in exec_result]

    def save(self, dir_path: Union[str, PathLike]):
        if self._hybrid_result_s3_url is None:
            raise ValueError('There is no result data.')

        def get_fresh_result_s3_url():
            outputs: dict = get_task(self.task_id, {'outputs'})['outputs']
            if not ('result' in outputs and 'ref' in outputs['result']):
                raise ValueError('There is no result data.')
            return outputs['result']['ref']

        StorageService._download_hybrid_program_result(self._hybrid_result_s3_url, dir_path, get_fresh_result_s3_url)

    def __getitem__(self, item):
        if self._execution_result is None:
            raise IndexError('There are no execution results.')

        if len(self._execution_result) == 1:
            return self._execution_result[0][item]

        return self._execution_result[item]

    @property
    def task(self) -> Task:
        return self._task

    @property
    def task_id(self) -> UUID:
        return self._task.task_id

    @property
    def task_status(self) -> Task.Status:
        return self._task.status

    @property
    def message(self) -> Optional[str]:
        return self._message

    @property
    def counts(self) -> dict[str, int]:
        return self[0].counts

    @property
    def quasi_probabilities(self) -> Optional[dict[str, float]]:
        return self[0].quasi_probabilities

    @property
    def exp_val(self) -> Optional[complex]:
        return self[0].exp_val

    @property
    def var(self) -> Optional[complex]:
        return self[0].var

    @property
    def fidelity_alerts(self) -> Optional[str]:
        return self[0].fidelity_alerts

    @property
    def transpilation(self) -> Optional[TranspilationResult]:
        return self[0].transpilation

    @property
    def time_profile(self) -> dict[str, datetime]:
        return self[0].time_profile

    @property
    def all_transpilation_results(self) -> Optional[list[TranspilationResult]]:
        return self._transpilation_result

    def to_dict(self) -> dict[str, Any]:
        return {
            'message': self._message,
            'execution_result': [er.to_dict() for er in self._execution_result] if self._execution_result is not None else None,
            'transpilation_result': [tr.to_dict() for tr in self._transpilation_result] if self._transpilation_result is not None else None,
        }

    def __str__(self):
        return pformat(self.to_dict())

    def __len__(self) -> int:
        if self._execution_result is None:
            raise ValueError('There are no execution results.')

        if len(self._execution_result) == 1:
            return len(self._execution_result[0])

        return len(self._execution_result)

    def __iter__(self):
        if self._execution_result is None:
            raise ValueError('There are no execution results.')

        if len(self._execution_result) == 1:
            return iter(self._execution_result[0])

        return iter(self._execution_result)


@dataclass
class TranspilationResult:
    id: int
    transpiled_program: Optional[str]
    qubit_allocation: Optional[QubitAllocation]
    n_op_groups: Optional[int]
    time_profile: dict[str, datetime]

    @staticmethod
    def from_dict(result: dict[str, Any]):
        return TranspilationResult(
            id=result['id'],
            transpiled_program=result.get('transpiledCode', None),
            qubit_allocation=result.get('qubitAllocation', None),
            n_op_groups=result.get('nOpGroups', None),
            time_profile={
                'transpilation_start': datetime.strptime(result['start'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc),
                'transpilation_end': datetime.strptime(result['end'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc),
            }
        )

    def to_dict(self):
        return asdict(self)

    def __str__(self):
        return pformat(self.to_dict())


class ExecutionResult:

    @dataclass
    class OneResult:
        """An execution result for a single set of parameter values."""
        data: ResultData
        fidelity_alerts: Optional[str]
        transpilation: Optional[TranspilationResult]
        time_profile: dict[str, datetime]

        @property
        def counts(self) -> Optional[dict[str, int]]:
            return self.data.counts

        @property
        def quasi_probabilities(self) -> Optional[dict[str, float]]:
            return self.data.quasi_probabilities

        @property
        def exp_val(self) -> Optional[complex]:
            return self.data.exp_val

        @property
        def var(self) -> Optional[complex]:
            return self.data.var

    def __init__(self, result: dict[str, Any], id_to_transpilation_result: Optional[dict[int, TranspilationResult]]):
        # Each element of the data corresponds to the execution result for each parameter-values.
        result_data_list = [ResultData(one_data) for one_data in result['data']]
        fidelity_alerts = result.get('fidelityAlerts', None)
        transpilation_result = id_to_transpilation_result[result['transpilation']] if id_to_transpilation_result is not None else None
        time_profile: dict[str, datetime] = {
            "execution_start": datetime.strptime(result['start'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc),
            "execution_end": datetime.strptime(result['end'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc),
        }

        self._all_results: list[ExecutionResult.OneResult]\
            = [ExecutionResult.OneResult(data=data, fidelity_alerts=fidelity_alerts, transpilation=transpilation_result, time_profile=time_profile)
               for data in result_data_list]

    def __getitem__(self, item):
        return self._all_results[item]

    @property
    def counts(self) -> Optional[dict[str, int]]:
        return self[0].data.counts

    @property
    def quasi_probabilities(self) -> Optional[dict[str, float]]:
        return self[0].data.quasi_probabilities

    @property
    def exp_val(self) -> Optional[complex]:
        return self[0].data.exp_val

    @property
    def var(self) -> Optional[complex]:
        return self[0].data.var

    @property
    def fidelity_alerts(self) -> Optional[str]:
        return self[0].fidelity_alerts

    @property
    def time_profile(self) -> dict[str, datetime]:
        return self[0].time_profile

    @property
    def transpilation(self) -> TranspilationResult:
        return self[0].transpilation

    def to_dict(self):
        return {
            'data': [result.data.to_dict() for result in self._all_results],
            'transpilation_result_id': self[0].transpilation.id if self[0].transpilation is not None else None,
            'time_profile': self[0].time_profile,
        }

    def __str__(self):
        return pformat(self.to_dict())

    def __len__(self) -> int:
        return len(self._all_results)

    def __iter__(self):
        return iter(self._all_results)


class ResultData:
    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def counts(self) -> Optional[dict[str, int]]:
        return self._data.get('counts', None)

    @property
    def quasi_probabilities(self) -> Optional[dict[str, float]]:
        return self._data.get('quasiProbabilities', None)

    @property
    def exp_val(self) -> Optional[complex]:
        exp_val: Optional[list] = self._data.get('expVal', None)
        if exp_val is None:
            return None

        return complex(exp_val[0], exp_val[1])

    @property
    def var(self) -> Optional[complex]:
        var: Optional[list] = self._data.get('var', None)
        if var is None:
            return None

        return complex(var[0], var[1])

    def to_dict(self):
        return self._data

    def __str__(self):
        return str(self._data)
