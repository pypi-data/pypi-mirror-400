import builtins
import collections.abc
import datetime as dt
import enum
import itertools
import math
import re
import typing as tp

from xm_slurm import config, utils


class ResourceType(enum.IntEnum):
    CPU = 1

    MEMORY = 2
    RAM = 2

    EPHEMERAL_STORAGE = 3
    DISK = 3

    GPU = 1000
    RTX8000 = 1001
    P4 = 1010

    P100 = 1011
    P100_16GIB = 1012

    V100 = 1020
    V100_32GIB = 1021

    A100 = 1030
    A100_80GIB = 1031
    A5000 = 1032
    A6000 = 1033

    H100 = 1040
    L40S = 1041


AcceleratorType = set([
    ResourceType.RTX8000,
    ResourceType.P4,
    ResourceType.P100,
    ResourceType.P100_16GIB,
    ResourceType.V100,
    ResourceType.V100_32GIB,
    ResourceType.A100,
    ResourceType.A100_80GIB,
    ResourceType.A5000,
    ResourceType.A6000,
    ResourceType.H100,
    ResourceType.L40S,
])

assert AcceleratorType | {
    ResourceType.CPU,
    ResourceType.MEMORY,
    ResourceType.DISK,
    ResourceType.GPU,
} == set(ResourceType.__members__.values()), "Resource types are not exhaustive."


class FeatureType(enum.IntEnum):
    NVIDIA_MIG = 1
    NVIDIA_NVLINK = 2


class InvalidTopologyError(Exception):
    """An unrecognized topology has been provided."""


TOPOLOGY_REGEX = re.compile(r"^(?P<dims>[\d]+(?:x[\d]+)*)$")


class Topology:
    mesh: str
    dimensions: list[int]
    switches: int | None
    switches_grace_period: dt.timedelta | None

    def __init__(
        self,
        mesh: str,
        /,
        *,
        switches: int | None = None,
        switches_grace_period: dt.timedelta | None = None,
    ):
        mesh_match = TOPOLOGY_REGEX.fullmatch(mesh)
        if not mesh_match:
            raise InvalidTopologyError(f"Invalid topology mesh: {mesh!r}.")

        self.mesh = mesh
        self.dimensions = list(map(int, mesh_match.group("dims").split("x")))
        if switches is not None:
            assert (
                isinstance(switches, int) and switches > 0
            ), "Switches must be a positive integer."
        self.switches = switches
        if switches_grace_period is not None:
            assert isinstance(
                switches_grace_period, dt.timedelta
            ), "Switches grace period must be a `datetime.timedelta`."
        self.switches_grace_period = switches_grace_period

    @property
    def chip_count(self) -> int:
        return math.prod(self.dimensions)

    @property
    def ndim(self) -> int:
        return len(self.dimensions)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Topology):
            return False
        return (
            self.mesh == other.mesh
            and self.switches == other.switches
            and self.switches_grace_period == other.switches_grace_period
        )

    def __hash__(self) -> int:
        return hash((self.mesh, self.switches, self.switches_grace_period))


ResourceQuantity = int | float | Topology


def _parse_resource_quantity(
    resource_name: ResourceType | str, value: ResourceQuantity
) -> tuple[float, Topology | None]:
    if isinstance(resource_name, ResourceType):
        resource_name = resource_name.name
    match value:
        case Topology() as topology:
            return topology.chip_count, topology
        case builtins.str() as topology_str if (
            "x" in topology_str and TOPOLOGY_REGEX.fullmatch(topology_str) is not None
        ):
            topology = Topology(topology_str)
            return topology.chip_count, topology
        case builtins.str() as num_str:
            try:
                value = float(num_str)
                return int(value) if value.is_integer() else value, None
            except ValueError as e:
                raise ValueError(
                    f"Couldn't parse resource quantity for {resource_name}. "
                    f"{num_str!r} was given."
                ) from e
        case int() | float():
            return value, None
        case _:
            raise ValueError(f"Invalid resource quantity: {value!r} for {resource_name!r}.")


class JobRequirements:
    replicas: int
    location: str | None
    accelerator: ResourceType | None
    topology: Topology | None
    cluster: config.SlurmClusterConfig

    def __init__(
        self,
        *,
        resources: tp.Mapping[ResourceType | str, ResourceQuantity] | None = None,
        replicas: int | None = None,
        location: str | tp.Iterable[str] | None = None,
        cluster: config.SlurmClusterConfig,
        **kw_resources: ResourceQuantity,
    ):
        if isinstance(location, collections.abc.Iterable) and not isinstance(location, str):
            location = ",".join(location)
        self.location = location

        self.accelerator = None
        self.topology = None
        self.cluster = cluster

        if resources is None:
            resources = {}

        self.task_requirements: dict[ResourceType | str, ResourceQuantity] = {}
        for resource_name, value in itertools.chain(resources.items(), kw_resources.items()):
            quantity, topology = _parse_resource_quantity(resource_name, value)
            match resource_name:
                case str() if resource_name.upper() in ResourceType.__members__:
                    resource = ResourceType[resource_name.upper()]
                case ResourceType():
                    resource = resource_name
                case str():
                    resource = resource_name

            if (
                resource in AcceleratorType
                or resource == ResourceType.GPU
                or (isinstance(resource, str) and resource.startswith("gpu"))
            ):
                if self.accelerator is not None:
                    raise ValueError("Accelerator already set.")
                self.accelerator = resource  # type: ignore
                self.topology = topology
            elif topology is not None:
                raise ValueError(
                    f"A topology was specified for a non-accelerator resource: {resource_name!r}."
                )

            if resource in self.task_requirements:
                raise ValueError(f"{resource} has been specified twice.")
            self.task_requirements[resource] = quantity

        if self.topology is not None and self.topology.ndim > 2:
            raise ValueError("Topologies with more than 2 dimensions are not supported.")

        if (
            self.accelerator is not None
            and self.topology is not None
            and len(self.topology.dimensions) == 2
        ):
            if replicas is not None and replicas != self.topology.dimensions[1]:
                raise ValueError(
                    f"For multihost GPUs with topology {self.topology}, replicas should"
                    f"be either None or {self.topology.dimensions[1]}. Found: "
                    f"{replicas}"
                )
            replicas = self.topology.dimensions[1]

        if replicas is not None and replicas <= 0:
            raise ValueError(f"Replicas must be a positive integer, got {replicas!r}")
        self.replicas = replicas or 1

    def batch_directives(self) -> list[str]:
        directives = []

        for resource, value in self.task_requirements.items():
            match resource:
                case ResourceType.EPHEMERAL_STORAGE | ResourceType.DISK:
                    assert isinstance(
                        value, int
                    ), f"Disk space must be an integer, got {type(value)!r}"
                    directives.append(f"--tmp={math.ceil(value / 2**20)}M")
                case ResourceType.MEMORY | ResourceType.RAM:
                    num_cpus = self.task_requirements.get(ResourceType.CPU, 1)
                    assert isinstance(
                        value, (int, float)
                    ), f"Memory must be an integer or float, got {type(value)!r}"
                    assert isinstance(
                        num_cpus, int
                    ), f"CPU must be an integer, got {type(num_cpus)!r}"
                    directives.append(f"--mem-per-cpu={math.ceil(value / num_cpus / 2**20)}M")
                case ResourceType.CPU:
                    assert isinstance(value, int), f"CPU must be an integer, got {type(value)!r}"
                    directives.append(f"--cpus-per-task={value}")
                case ResourceType.GPU:
                    assert isinstance(value, int), f"GPU must be an integer, got {type(value)!r}"
                    directives.append(f"--gpus={value}")
                case ResourceType() if resource in AcceleratorType:
                    assert isinstance(
                        value, int
                    ), f"Accelerator must be an integer, got {type(value)!r}"
                    resource_type = self.cluster.resources.get(resource, None)
                    if resource_type is None:
                        raise ValueError(
                            f"Cluster {self.cluster.name} does not map resource type {resource!r}."
                        )
                    directives.append(f"--gpus={resource_type}:{value}")
                case str():
                    directives.append(f"--gres={resource}:{value}")

        if self.location:
            assert isinstance(
                self.location, str
            ), f"Location must be a string, got {type(self.location)!r}"
            directives.append(f"--nodelist={self.location}")

        assert (
            isinstance(self.replicas, int) and self.replicas > 0
        ), f"Replicas must be a positive integer, got {self.replicas!r}"
        directives.append(f"--ntasks={self.replicas}")

        if self.topology is not None:
            assert self.accelerator is not None, "Accelerator must be set."
            match self.accelerator:
                case ResourceType.GPU:
                    directives.append(f"--gpus-per-task={self.topology.dimensions[0]}")
                case ResourceType() if self.accelerator in AcceleratorType:
                    resource_type = self.cluster.resources[self.accelerator]
                    directives.append(
                        f"--gpus-per-task={resource_type}:{self.topology.dimensions[0]}"
                    )

            if self.topology.switches is not None:
                switches_timeout = (
                    f"@{utils.timestr_from_timedelta(self.topology.switches_grace_period)}"
                    if self.topology.switches_grace_period is not None
                    else ""
                )
                directives.append(f"--switches={self.topology.switches}{switches_timeout}")

        return directives

    def step_directives(self) -> list[str]:
        return []

    def replace(
        self,
        replicas: int | None = None,
        location: str | None = None,
        cluster: config.SlurmClusterConfig | None = None,
        **kw_resources: ResourceQuantity,
    ) -> "JobRequirements":
        # Merge kw_resources into existing task_requirements, removing conflicting enum keys
        merged_resources = dict(self.task_requirements)

        # Remove ResourceType keys that will be overridden by string keys in kw_resources
        for key in list(merged_resources.keys()):
            if isinstance(key, ResourceType) and any(
                ResourceType[name.upper()] == key
                for name in kw_resources
                if name.upper() in ResourceType.__members__
            ):
                del merged_resources[key]

        merged_resources.update(kw_resources)  # type: ignore

        return JobRequirements(
            resources=merged_resources,
            replicas=replicas if replicas is not None else self.replicas,
            location=location if location is not None else self.location,
            cluster=cluster if cluster is not None else self.cluster,
        )

    def __repr__(self) -> str:
        args = []

        for resource, value in self.task_requirements.items():
            if isinstance(resource, ResourceType):
                resource = resource.name
            args.append(f"{resource.lower()}={value!r}")

        if self.replicas != 1:
            args.append(f"replicas={self.replicas!r}")

        if self.cluster is not None:
            args.append(f"cluster={self.cluster!r}")

        return f'xm_slurm.JobRequirements({", ".join(args)})'
