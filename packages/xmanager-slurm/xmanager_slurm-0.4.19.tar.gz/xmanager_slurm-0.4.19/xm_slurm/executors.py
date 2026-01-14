import collections.abc
import dataclasses
import datetime as dt
import signal
import typing as tp

from xmanager import xm

from xm_slurm import resources, utils

ResourceBindType = tp.Literal[
    resources.ResourceType.GPU,
    resources.ResourceType.MEMORY,
    resources.ResourceType.RAM,
]


@dataclasses.dataclass(frozen=True, kw_only=True)
class SlurmSpec(xm.ExecutorSpec):
    """Slurm executor specification that describes the location of the container runtime.

    Args:
        tag: The Image URI to push and pull the container image from.
            For example, using the GitHub Container Registry: `ghcr.io/my-project/my-image:latest`.
    """

    tag: str | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Slurm(xm.Executor):
    """Slurm Executor describing the runtime environment.

    Args:
        requirements: The requirements for the job.
        time: The maximum time to run the job.
        switches: Maximum count of leaf switches desired for the job allocation.
        switches_grace_period: Maximum time to wait for that number of switches.
        bind: How to bind tasks to resource (memory, GPU, or generic resource).
        bind_flag: Generic resource task binding options.
        account: The account to charge the job to.
        partition: The partition to run the job in.
        qos: The quality of service to run the job with.
        priority: The priority of the job.
        reservation: Allocate resources for the job from the named reservation.
        exclusive: Allow sharing nodes with other running jobs.
        oversubscribe: Allow over-subscribing resources with other running jobs.
        overcommit: Allow sharing of allocated resources as if only one task per was requested.
        nice: Run the job with an adjusted scheduling priority.
        kill_on_invalid_dependencies: Whether to kill the job if it has invalid dependencies.
        timeout_signal: The signal to send to the job when it runs out of time.
        timeout_signal_grace_period: The time to wait before sending `timeout_signal`.
        requeue: Whether or not the job is eligible for requeueing.
        requeue_on_exit_code: The exit code that triggers requeueing.
        requeue_max_attempts: The maximum number of times to attempt requeueing.

    """

    # Job requirements
    requirements: resources.JobRequirements
    time: dt.timedelta
    bind: tp.Mapping[ResourceBindType | str, str | None] | None = None
    bind_flag: str | None = None

    # Placement
    account: str | None = None
    partition: str | None = None
    qos: str | None = None
    priority: int | None = None
    reservation: str | tp.Iterable[str] | None = None
    exclusive: bool = False
    oversubscribe: bool = False
    overcommit: bool = False
    nice: int | None = None

    # Job dependency handling
    kill_on_invalid_dependencies: bool = True

    # Job rescheduling
    timeout_signal: signal.Signals = signal.SIGUSR2
    timeout_signal_grace_period: dt.timedelta = dt.timedelta(seconds=90)

    requeue: bool = True  # Is this job ellible for requeueing?
    requeue_on_exit_code: int = 42  # The exit code that triggers requeueing
    requeue_on_timeout: bool = True  # Should the job requeue upon timeout minus the grace period
    requeue_max_attempts: int = 5  # How many times to attempt requeueing

    @property
    def requeue_timeout(self) -> dt.timedelta:
        return self.time - self.timeout_signal_grace_period

    def __post_init__(self) -> None:
        if not isinstance(self.requirements, resources.JobRequirements):
            raise TypeError(
                f"requirements must be a `xm_slurm.JobRequirements`, got {type(self.requirements)}. "
                "If you're still using `xm.JobRequirements`, please update to `xm_slurm.JobRequirements`."
            )
        if not isinstance(self.time, dt.timedelta):
            raise TypeError(f"time must be a `datetime.timedelta`, got {type(self.time)}")
        if self.bind is not None:
            if not isinstance(self.bind, collections.abc.Mapping):
                raise TypeError(f"bind must be a mapping, got {type(self.bind)}")
            for resource, value in self.bind.items():
                if resource not in (
                    resources.ResourceType.GPU,
                    resources.ResourceType.MEMORY,
                    resources.ResourceType.RAM,
                ) and not isinstance(resource, str):
                    raise TypeError(
                        f"bind resource must be a {resources.ResourceType.GPU.name}, {resources.ResourceType.MEMORY.name}, or {resources.ResourceType.RAM.name}, got {type(resource)}"
                    )
                if value is not None and not isinstance(value, str):
                    raise TypeError(f"bind value must be None or a string, got {type(value)}")
        if self.bind_flag is not None and not isinstance(self.bind_flag, str):
            raise TypeError(f"bind_flag must be a string, got {type(self.bind_flag)}")

        if not isinstance(self.timeout_signal, signal.Signals):
            raise TypeError(
                f"termination_signal must be a `signal.Signals`, got {type(self.timeout_signal)}"
            )
        if not isinstance(self.timeout_signal_grace_period, dt.timedelta):
            raise TypeError(
                f"termination_signal_delay_time must be a `datetime.timedelta`, got {type(self.timeout_signal_grace_period)}"
            )
        if self.requeue_max_attempts < 0:
            raise ValueError(
                f"requeue_max_attempts must be greater than or equal to 0, got {self.requeue_max_attempts}"
            )
        if self.requeue_on_exit_code == 0:
            raise ValueError("requeue_on_exit_code should not be 0 to avoid unexpected behavior.")
        if self.exclusive and self.oversubscribe:
            raise ValueError("exclusive and oversubscribe are mutually exclusive.")
        if self.nice is not None and not (-2147483645 <= self.nice <= 2147483645):
            raise ValueError(f"nice must be between -2147483645 and 2147483645, got {self.nice}")

    @classmethod
    def Spec(cls, tag: str | None = None) -> SlurmSpec:
        return SlurmSpec(tag=tag)

    def batch_directives(self) -> list[str]:
        # Job requirements
        directives = self.requirements.batch_directives()

        # Time
        directives.append(f"--time={utils.timestr_from_timedelta(self.time)}")

        # Job dependency handling
        directives.append(
            f"--kill-on-invalid-dep={'yes' if self.kill_on_invalid_dependencies else 'no'}"
        )

        # Placement
        if self.account is not None:
            directives.append(f"--account={self.account}")
        if self.partition is not None:
            directives.append(f"--partition={self.partition}")
        if self.qos is not None:
            directives.append(f"--qos={self.qos}")
        if self.priority is not None:
            directives.append(f"--priority={self.priority}")
        if self.reservation is not None:
            match self.reservation:
                case str():
                    directives.append(f"--reservation={self.reservation}")
                case collections.abc.Iterable():
                    directives.append(f"--reservation={','.join(self.reservation)}")
                case _:
                    raise ValueError(f"Invalid reservation type: {type(self.reservation)}")
        if self.exclusive:
            directives.append("--exclusive")
        if self.oversubscribe:
            directives.append("--oversubscribe")
        if self.overcommit:
            directives.append("--overcommit")
        if self.nice is not None:
            directives.append(f"--nice={self.nice}")

        # Job rescheduling
        directives.append(
            f"--signal={self.timeout_signal.name.removeprefix('SIG')}@{self.timeout_signal_grace_period.seconds}"
        )
        if self.requeue is not None and self.requeue_max_attempts > 0:
            directives.append("--requeue")
        else:
            directives.append("--no-requeue")

        return directives

    def step_directives(self) -> list[str]:
        directives = self.requirements.step_directives()

        # Resource binding
        if self.bind is not None:
            for resource, value in self.bind.items():
                if value is None:
                    value = "none"
                match resource:
                    case resources.ResourceType.MEMORY | resources.ResourceType.RAM:
                        directives.append(f"--mem-bind={value}")
                    case resources.ResourceType.GPU:
                        directives.append(f"--gpu-bind={value}")
                    case str():
                        directives.append(f"--tres-bind=gres/{resource}:{value}")
                    case _:
                        raise ValueError(f"Unsupported resource type {resource!r} for binding.")

        if self.bind_flag is not None:
            directives.append(f"--gres-flags={self.bind_flag}")

        return directives
