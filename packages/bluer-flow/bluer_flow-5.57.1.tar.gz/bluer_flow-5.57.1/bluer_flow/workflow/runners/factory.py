from typing import Dict

from bluer_flow.workflow.runners import RunnerType
from bluer_flow.workflow.runners.local import LocalRunner
from bluer_flow.workflow.runners.localflow.runner import LocalFlowRunner
from bluer_flow.workflow.runners.generic import GenericRunner

runner_class: Dict[RunnerType, GenericRunner] = {
    RunnerType.GENERIC: GenericRunner,
    RunnerType.LOCAL: LocalRunner,
    RunnerType.LOCALFLOW: LocalFlowRunner,
}
