import collections
import logging
import typing as tp

from xmanager import xm

from xm_slurm.console import console
from xm_slurm.executors import SlurmSpec
from xm_slurm.packaging import registry

IndexedContainer = registry.IndexedContainer

logger = logging.getLogger(__name__)


def package(
    packageables: tp.Sequence[xm.Packageable],
) -> list[xm.Executable]:
    """
    Takes as input a list of packageables and returns a mapping of
    `DockerTarget`'s to the latest digest of that image.
    """
    # Docker targets to be collected.
    # These are a mapping from `DockerTarget` to the latest digest of the image.
    targets_by_type = collections.defaultdict[
        tp.Type[xm.ExecutableSpec], list[IndexedContainer[xm.Packageable]]
    ](list)

    # Collect dockerfiles that need to be built locally
    for index, packageable in enumerate(packageables):
        if not isinstance(packageable.executor_spec, SlurmSpec):
            raise ValueError(
                f"Unsupported executor spec for packageable: {packageable}."
                "xm_slurm only supports `xm_slurm.SlurmSpec`."
            )
        targets_by_type[type(packageable.executable_spec)].append(
            IndexedContainer[xm.Packageable](index, packageable)
        )

    targets: list[IndexedContainer[xm.Executable]] = []
    # TODO(jfarebro): Could make this async as well...?
    with console.status("[magenta] :package: Packaging executables..."):
        for executable_spec_type, targets_for_type in targets_by_type.items():
            logger.info(
                f"Packaging {len(targets_for_type)} {executable_spec_type.__name__} target{'s' if len(targets_for_type) > 1 else ''}."
            )
            targets.extend(registry.route(executable_spec_type, targets_for_type))

    console.print(
        f"[magenta]:package: Finished packaging [bold]{len(targets)} executable"
        f"{'s' if len(targets) > 1 else ''}[/bold]."
    )

    assert len(targets) == len(packageables), "Number of targets must match packageables"
    targets = sorted(targets, key=lambda t: t.index)
    return [target.value for target in targets]
