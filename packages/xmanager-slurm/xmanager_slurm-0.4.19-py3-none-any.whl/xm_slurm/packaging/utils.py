import collections
import logging
import typing as tp

from xmanager import xm

from xm_slurm.packaging.registry import IndexedContainer

T = tp.TypeVar("T")
P = tp.ParamSpec("P")
ReturnT = tp.TypeVar("ReturnT")

logger = logging.getLogger(__name__)


def collect_executors_by_executable(
    targets: tp.Sequence[IndexedContainer[xm.Packageable]],
) -> dict[xm.ExecutableSpec, set[xm.ExecutorSpec]]:
    executors_by_executable = collections.defaultdict(set)
    for target in targets:
        executors_by_executable[target.value.executable_spec].add(target.value.executor_spec)
    return executors_by_executable
