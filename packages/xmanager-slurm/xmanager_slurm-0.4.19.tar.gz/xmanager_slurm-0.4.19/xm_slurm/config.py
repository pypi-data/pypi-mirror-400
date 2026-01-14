import dataclasses
import enum
import functools
import json
import os
import pathlib
import typing as tp

import asyncssh
from xmanager import xm


class ContainerRuntime(enum.Enum):
    """The container engine to use."""

    SINGULARITY = enum.auto()
    APPTAINER = enum.auto()
    DOCKER = enum.auto()
    PODMAN = enum.auto()

    @classmethod
    def from_string(
        cls, runtime: tp.Literal["singularity", "apptainer", "docker", "podman"]
    ) -> "ContainerRuntime":
        return {
            "singularity": cls.SINGULARITY,
            "apptainer": cls.APPTAINER,
            "docker": cls.DOCKER,
            "podman": cls.PODMAN,
        }[runtime]

    def __str__(self):
        if self is self.SINGULARITY:
            return "singularity"
        elif self is self.APPTAINER:
            return "apptainer"
        elif self is self.DOCKER:
            return "docker"
        elif self is self.PODMAN:
            return "podman"
        else:
            raise NotImplementedError


class Endpoint(tp.NamedTuple):
    hostname: str
    port: int | None

    def __str__(self) -> str:
        if self.port is None or self.port == asyncssh.DEFAULT_PORT:
            return self.hostname
        return f"[{self.hostname}]:{self.port}"


class PublicKey(tp.NamedTuple):
    algorithm: str
    key: str


@dataclasses.dataclass
class SSHConfig:
    endpoints: tuple[Endpoint, ...]
    public_key: PublicKey | None = None
    user: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.endpoints, tuple):
            raise TypeError(f"endpoints must be a tuple, not {type(self.endpoints)}")
        if len(self.endpoints) == 0:
            raise ValueError("endpoints must be a non-empty tuple")
        if not all(isinstance(endpoint, Endpoint) for endpoint in self.endpoints):
            raise TypeError(f"endpoints must be a tuple of strings, not {type(self.endpoints)}")

        if not isinstance(self.user, str | None):
            raise TypeError(f"user must be a string or None, not {type(self.user)}")
        if not isinstance(self.public_key, PublicKey | None):
            raise TypeError(
                f"public_key must be a SSHPublicKey or None, not {type(self.public_key)}"
            )

    @functools.cached_property
    def known_hosts(self) -> asyncssh.SSHKnownHosts | None:
        if self.public_key is None:
            return None

        known_hosts = []
        for endpoint in self.endpoints:
            known_hosts.append(f"{endpoint!s} {self.public_key.algorithm} {self.public_key.key}")

        return asyncssh.SSHKnownHosts("\n".join(known_hosts))

    def serialize(self):
        return json.dumps({
            "endpoints": tuple(tuple(endpoint) for endpoint in self.endpoints),
            "public_key": tuple(self.public_key),
            "user": self.user,
        })

    @classmethod
    def deserialize(cls, data):
        data = json.loads(data)
        return cls(
            endpoints=tuple(Endpoint(*endpoint) for endpoint in data["endpoints"]),
            public_key=PublicKey(*data["public_key"]) if data["public_key"] else None,
            user=data["user"],
        )

    def __hash__(self):
        return hash((
            type(self),
            *(tuple(endpoint) for endpoint in self.endpoints),
            self.public_key,
            self.user,
        ))


@dataclasses.dataclass(frozen=True, kw_only=True)
class SlurmClusterConfig:
    name: str

    ssh: SSHConfig

    # Job submission directory
    cwd: str | None = None

    # Additional scripting
    prolog: str | None = None
    epilog: str | None = None

    # Job scheduling
    account: str | None = None
    partition: str | None = None
    qos: str | None = None

    # If true, a reverse proxy is initiated via the submission host.
    proxy: tp.Literal["submission-host"] | str | None = None

    runtime: ContainerRuntime

    # Environment variables
    host_environment: tp.Mapping[str, str] = dataclasses.field(default_factory=dict)
    container_environment: tp.Mapping[str, str] = dataclasses.field(default_factory=dict)

    # Mounts
    mounts: tp.Mapping[os.PathLike[str] | str, os.PathLike[str] | str] = dataclasses.field(
        default_factory=dict
    )

    # Resource mapping
    resources: tp.Mapping["xm_slurm.ResourceType", str] = dataclasses.field(default_factory=dict)  # type: ignore # noqa: F821

    features: tp.Mapping["xm_slurm.FeatureType", str] = dataclasses.field(default_factory=dict)  # type: ignore # noqa: F821

    # Function to validate the Slurm executor config
    validate: tp.Callable[[xm.Job], None] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.ssh, SSHConfig):
            raise TypeError(f"ssh must be a SlurmSSHConfig, not {type(self.ssh)}")
        for src, dst in self.mounts.items():
            if not isinstance(src, (str, os.PathLike)):
                raise TypeError(
                    f"Mount source must be a string or path-like object, not {type(src)}"
                )
            if not isinstance(dst, (str, os.PathLike)):
                raise TypeError(
                    f"Mount destination must be a string or path-like object, not {type(dst)}"
                )

            if not pathlib.Path(src).is_absolute():
                raise ValueError(f"Mount source must be an absolute path: {src}")
            if not pathlib.Path(dst).is_absolute():
                raise ValueError(f"Mount destination must be an absolute path: {dst}")

    def __hash__(self):
        return hash((
            type(self),
            self.ssh,
            self.cwd,
            self.prolog,
            self.epilog,
            self.account,
            self.partition,
            self.qos,
            self.proxy,
            self.runtime,
            frozenset(self.host_environment.items()),
            frozenset(self.container_environment.items()),
        ))
