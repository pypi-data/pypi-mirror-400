import dataclasses
import enum
import typing as tp


class ExperimentUnitRole(enum.Enum):
    WORK_UNIT = enum.auto()
    AUX_UNIT = enum.auto()


@dataclasses.dataclass(kw_only=True, frozen=True)
class ExperimentPatch:
    title: str | None = None
    description: str | None = None
    note: str | None = None
    tags: list[str] | None = None


@dataclasses.dataclass(kw_only=True, frozen=True)
class SlurmJob:
    name: str
    slurm_job_id: str
    slurm_ssh_config: str


@dataclasses.dataclass(kw_only=True, frozen=True)
class Artifact:
    name: str
    uri: str


@dataclasses.dataclass(kw_only=True, frozen=True)
class ConfigArtifact:
    name: tp.Literal["GRAPHVIZ", "PYTHON"]
    uri: str


@dataclasses.dataclass(kw_only=True, frozen=True)
class ExperimentUnit:
    identity: str
    args: str | None = None
    jobs: list[SlurmJob] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(kw_only=True, frozen=True)
class ExperimentUnitPatch:
    identity: str | None = None
    args: str | None = None


@dataclasses.dataclass(kw_only=True, frozen=True)
class WorkUnit(ExperimentUnit):
    wid: int
    artifacts: list[Artifact] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(kw_only=True, frozen=True)
class WorkUnitPatch(ExperimentUnitPatch):
    wid: int


@dataclasses.dataclass(kw_only=True, frozen=True)
class Experiment:
    title: str
    description: str | None
    note: str | None
    tags: list[str] | None

    work_units: list[WorkUnit] = dataclasses.field(default_factory=list)
    artifacts: list[Artifact] = dataclasses.field(default_factory=list)
