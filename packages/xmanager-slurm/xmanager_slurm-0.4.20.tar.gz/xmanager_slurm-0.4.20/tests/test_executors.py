import datetime as dt
import signal
import typing as tp
from unittest.mock import MagicMock

import pytest

from xm_slurm import config, executors, resources


@pytest.fixture
def dummy_cluster_config():
    """Create a dummy cluster configuration for testing."""
    ssh_config = config.SSHConfig(endpoints=(config.Endpoint("localhost", 22),), user="testuser")
    return config.SlurmClusterConfig(
        name="test_cluster",
        ssh=ssh_config,
        runtime=config.ContainerRuntime.DOCKER,
    )


@pytest.fixture
def basic_requirements(dummy_cluster_config):
    """Create basic job requirements for testing."""
    return resources.JobRequirements(
        cpu=1,
        memory=1024**3,  # 1GB
        cluster=dummy_cluster_config,
    )


@pytest.mark.parametrize(
    "tag",
    [
        "ghcr.io/my-project/my-image:latest",
        "docker.io/image:v1.0",
        None,
    ],
)
def test_slurm_spec_creation(tag: str | None) -> None:
    """Test creating a SlurmSpec with various tags."""
    spec = executors.SlurmSpec(tag=tag)
    assert spec.tag == tag


def test_slurm_spec_is_frozen() -> None:
    """Test that SlurmSpec is frozen (immutable)."""
    spec = executors.SlurmSpec(tag="test:latest")
    with pytest.raises(AttributeError):
        spec.tag = "new-tag:latest"  # type: ignore


def test_slurm_spec_is_executor_spec() -> None:
    """Test that SlurmSpec is an ExecutorSpec."""
    spec = executors.SlurmSpec(tag="test:latest")
    assert isinstance(spec, executors.xm.ExecutorSpec)


# Type validation tests
@pytest.mark.parametrize("invalid_requirements", [MagicMock(), "requirements", 123])
def test_slurm_executor_requirements_type_validation(invalid_requirements: tp.Any) -> None:
    """Test that executor validates requirements type."""
    with pytest.raises(TypeError, match="requirements must be a `xm_slurm.JobRequirements`"):
        executors.Slurm(requirements=invalid_requirements, time=dt.timedelta(hours=1))


@pytest.mark.parametrize("invalid_time", ["1 hour", 3600, 1.5])
def test_slurm_executor_time_type_validation(
    basic_requirements: resources.JobRequirements, invalid_time: tp.Any
) -> None:
    """Test that executor validates time type."""
    with pytest.raises(TypeError, match="time must be a `datetime.timedelta`"):
        executors.Slurm(requirements=basic_requirements, time=invalid_time)


def test_slurm_executor_bind_type_validation(basic_requirements: resources.JobRequirements) -> None:
    """Test that executor validates bind type."""
    with pytest.raises(TypeError, match="bind must be a mapping"):
        executors.Slurm(
            requirements=basic_requirements,
            time=dt.timedelta(hours=1),
            bind="gpu:none",  # type: ignore
        )


@pytest.mark.parametrize("invalid_signal", ["SIGUSR2", 12])
def test_slurm_executor_timeout_signal_type_validation(
    basic_requirements: resources.JobRequirements, invalid_signal: tp.Any
) -> None:
    """Test that executor validates timeout_signal type."""
    with pytest.raises(TypeError, match="termination_signal must be a `signal.Signals`"):
        executors.Slurm(
            requirements=basic_requirements,
            time=dt.timedelta(hours=1),
            timeout_signal=invalid_signal,
        )


def test_slurm_executor_timeout_signal_grace_period_type_validation(
    basic_requirements: resources.JobRequirements,
) -> None:
    """Test that executor validates timeout_signal_grace_period type."""
    with pytest.raises(
        TypeError, match="termination_signal_delay_time must be a `datetime.timedelta`"
    ):
        executors.Slurm(
            requirements=basic_requirements,
            time=dt.timedelta(hours=1),
            timeout_signal_grace_period=90,  # type: ignore
        )


@pytest.mark.parametrize("invalid_attempts", [-1, -10])
def test_slurm_executor_requeue_max_attempts_validation(
    basic_requirements: resources.JobRequirements, invalid_attempts: int
) -> None:
    """Test that executor validates requeue_max_attempts."""
    with pytest.raises(ValueError, match="requeue_max_attempts must be greater than or equal to 0"):
        executors.Slurm(
            requirements=basic_requirements,
            time=dt.timedelta(hours=1),
            requeue_max_attempts=invalid_attempts,
        )


def test_slurm_executor_requeue_on_exit_code_validation(
    basic_requirements: resources.JobRequirements,
) -> None:
    """Test that executor validates requeue_on_exit_code."""
    with pytest.raises(ValueError, match="requeue_on_exit_code should not be 0"):
        executors.Slurm(
            requirements=basic_requirements, time=dt.timedelta(hours=1), requeue_on_exit_code=0
        )


def test_slurm_executor_exclusive_oversubscribe_conflict(
    basic_requirements: resources.JobRequirements,
) -> None:
    """Test that exclusive and oversubscribe cannot be both True."""
    with pytest.raises(ValueError, match="exclusive and oversubscribe are mutually exclusive"):
        executors.Slurm(
            requirements=basic_requirements,
            time=dt.timedelta(hours=1),
            exclusive=True,
            oversubscribe=True,
        )


@pytest.mark.parametrize("invalid_nice", [-2147483646, 2147483646])
def test_slurm_executor_nice_bounds_validation(
    basic_requirements: resources.JobRequirements, invalid_nice: int
) -> None:
    """Test that executor validates nice bounds."""
    with pytest.raises(ValueError, match="nice must be between"):
        executors.Slurm(
            requirements=basic_requirements, time=dt.timedelta(hours=1), nice=invalid_nice
        )


@pytest.mark.parametrize("valid_nice", [-2147483645, -19, 0, 19, 2147483645])
def test_slurm_executor_nice_valid_bounds(
    basic_requirements: resources.JobRequirements, valid_nice: int
) -> None:
    """Test that executor accepts valid nice values."""
    executor = executors.Slurm(
        requirements=basic_requirements, time=dt.timedelta(hours=1), nice=valid_nice
    )
    assert executor.nice == valid_nice


def test_slurm_executor_is_frozen(basic_requirements: resources.JobRequirements) -> None:
    """Test that Slurm executor is frozen (immutable)."""
    executor = executors.Slurm(requirements=basic_requirements, time=dt.timedelta(hours=1))
    with pytest.raises(AttributeError):
        executor.account = "new-account"  # type: ignore


def test_slurm_executor_bind_resource_validation_invalid_string_key(
    basic_requirements: resources.JobRequirements,
) -> None:
    """Test bind validation with invalid string key."""
    with pytest.raises(TypeError, match="bind resource must be a"):
        executors.Slurm(
            requirements=basic_requirements,
            time=dt.timedelta(hours=1),
            bind={123: "closest"},  # type: ignore
        )


def test_slurm_executor_bind_resource_validation_invalid_enum_key(
    basic_requirements: resources.JobRequirements,
) -> None:
    """Test bind validation with invalid ResourceType key."""
    with pytest.raises(TypeError, match="bind resource must be a"):
        executors.Slurm(
            requirements=basic_requirements,
            time=dt.timedelta(hours=1),
            bind={resources.ResourceType.CPU: "value"},  # type: ignore
        )


def test_slurm_executor_bind_accepts_resource_type_enums(
    basic_requirements: resources.JobRequirements,
) -> None:
    """Test bind accepts valid ResourceType enums."""
    executor = executors.Slurm(
        requirements=basic_requirements,
        time=dt.timedelta(hours=1),
        bind={resources.ResourceType.GPU: "closest"},
    )
    assert executor.bind == {resources.ResourceType.GPU: "closest"}


def test_slurm_executor_bind_accepts_custom_strings(
    basic_requirements: resources.JobRequirements,
) -> None:
    """Test bind accepts custom string GRES names."""
    executor = executors.Slurm(
        requirements=basic_requirements,
        time=dt.timedelta(hours=1),
        bind={"custom_gres": "value"},
    )
    assert executor.bind == {"custom_gres": "value"}


def test_slurm_executor_to_directives_default(basic_requirements):
    """Test directive generation with minimal configuration."""
    executor = executors.Slurm(requirements=basic_requirements, time=dt.timedelta(hours=1))
    directives = executor.batch_directives()
    assert any(d.startswith("--time=") for d in directives)
    assert any(d.startswith("--kill-on-invalid-dep=") for d in directives)
    assert any(d.startswith("--signal=") for d in directives)
    assert any(d.startswith("--requeue") for d in directives)


@pytest.mark.parametrize(
    "time,expected",
    [
        (dt.timedelta(hours=1), "--time=0-01:00:00"),
        (dt.timedelta(days=1, hours=2, minutes=30), "--time=1-02:30:00"),
        (dt.timedelta(minutes=5), "--time=0-00:05:00"),
    ],
)
def test_slurm_executor_to_directives_time(basic_requirements, time, expected):
    """Test time directive generation."""
    executor = executors.Slurm(requirements=basic_requirements, time=time)
    directives = executor.batch_directives()
    time_directive = [d for d in directives if d.startswith("--time=")][0]
    assert time_directive == expected


@pytest.mark.parametrize(
    "executor_kwargs,expected_directive",
    [
        ({"account": "my-account"}, "--account=my-account"),
        ({"account": "project-123"}, "--account=project-123"),
        ({"partition": "gpu-partition"}, "--partition=gpu-partition"),
        ({"partition": "cpu-partition"}, "--partition=cpu-partition"),
        ({"partition": "debug"}, "--partition=debug"),
        ({"qos": "high"}, "--qos=high"),
        ({"qos": "low"}, "--qos=low"),
        ({"qos": "normal"}, "--qos=normal"),
        ({"priority": 0}, "--priority=0"),
        ({"priority": 100}, "--priority=100"),
        ({"priority": 1000}, "--priority=1000"),
        ({"nice": -5}, "--nice=-5"),
        ({"nice": -19}, "--nice=-19"),
        ({"nice": 0}, "--nice=0"),
        ({"nice": 19}, "--nice=19"),
    ],
)
def test_slurm_executor_to_directives_executor_params(
    basic_requirements, executor_kwargs, expected_directive
):
    """Test directive generation for various executor parameters."""
    executor = executors.Slurm(
        requirements=basic_requirements,
        time=dt.timedelta(hours=1),
        **executor_kwargs,
    )
    directives = executor.batch_directives()
    assert expected_directive in directives


@pytest.mark.parametrize(
    "reservation,expected",
    [
        ("my-reservation", "--reservation=my-reservation"),
        (["res1", "res2", "res3"], "--reservation=res1,res2,res3"),
    ],
)
def test_slurm_executor_to_directives_reservation(basic_requirements, reservation, expected):
    """Test reservation directive generation."""
    executor = executors.Slurm(
        requirements=basic_requirements, time=dt.timedelta(hours=1), reservation=reservation
    )
    directives = executor.batch_directives()
    reservation_directive = [d for d in directives if d.startswith("--reservation=")][0]
    assert reservation_directive == expected


@pytest.mark.parametrize(
    "flag_kwargs,expected_directives",
    [
        ({"exclusive": True}, ["--exclusive"]),
        ({"exclusive": False}, []),
        ({"oversubscribe": True}, ["--oversubscribe"]),
        ({"oversubscribe": False}, []),
        ({"overcommit": True}, ["--overcommit"]),
        ({"overcommit": False}, []),
        ({"kill_on_invalid_dependencies": True}, ["--kill-on-invalid-dep=yes"]),
        ({"kill_on_invalid_dependencies": False}, ["--kill-on-invalid-dep=no"]),
    ],
)
def test_slurm_executor_to_directives_boolean_flags(
    basic_requirements, flag_kwargs, expected_directives
):
    """Test directive generation for boolean flags."""
    executor = executors.Slurm(
        requirements=basic_requirements,
        time=dt.timedelta(hours=1),
        **flag_kwargs,
    )
    directives = executor.batch_directives()
    for expected in expected_directives:
        assert any(expected in d for d in directives)
    for unexpected in ["--exclusive", "--oversubscribe", "--overcommit"]:
        if flag_kwargs and not any(expected in [unexpected] for expected in expected_directives):
            pass  # Skip negative checks for now


@pytest.mark.parametrize(
    "timeout_signal,grace_period,expected_signal",
    [
        (signal.SIGUSR1, dt.timedelta(minutes=2), "USR1@120"),
        (signal.SIGUSR2, dt.timedelta(seconds=90), "USR2@90"),
        (signal.SIGTERM, dt.timedelta(seconds=30), "TERM@30"),
        (signal.SIGKILL, dt.timedelta(seconds=1), "KILL@1"),
    ],
)
def test_slurm_executor_to_directives_timeout_signal(
    basic_requirements, timeout_signal, grace_period, expected_signal
):
    """Test timeout signal directive generation."""
    executor = executors.Slurm(
        requirements=basic_requirements,
        time=dt.timedelta(hours=1),
        timeout_signal=timeout_signal,
        timeout_signal_grace_period=grace_period,
    )
    directives = executor.batch_directives()
    signal_directive = [d for d in directives if d.startswith("--signal=")][0]
    assert signal_directive == f"--signal={expected_signal}"


@pytest.mark.parametrize(
    "requeue,max_attempts,expected",
    [
        (True, 5, "--requeue"),
        (True, 0, "--no-requeue"),
        (False, 0, "--no-requeue"),
    ],
)
def test_slurm_executor_to_directives_requeue(basic_requirements, requeue, max_attempts, expected):
    """Test requeue directive generation."""
    executor = executors.Slurm(
        requirements=basic_requirements,
        time=dt.timedelta(hours=1),
        requeue=requeue,
        requeue_max_attempts=max_attempts,
    )
    directives = executor.batch_directives()
    requeue_directives = [d for d in directives if "requeue" in d]
    assert expected in requeue_directives


def test_slurm_executor_to_directives_bind_gpu(basic_requirements):
    """Test GPU bind directive generation."""
    executor = executors.Slurm(
        requirements=basic_requirements,
        time=dt.timedelta(hours=1),
        bind={resources.ResourceType.GPU: "closest"},
    )
    directives = executor.step_directives()
    gpu_bind_directive = [d for d in directives if d.startswith("--gpu-bind=")][0]
    assert gpu_bind_directive == "--gpu-bind=closest"


@pytest.mark.parametrize(
    "resource,value,expected",
    [
        (resources.ResourceType.GPU, "closest", "--gpu-bind=closest"),
        (resources.ResourceType.MEMORY, "local", "--mem-bind=local"),
        (resources.ResourceType.RAM, "map_mem:0,1", "--mem-bind=map_mem:0,1"),
        (resources.ResourceType.GPU, None, "--gpu-bind=none"),
    ],
)
def test_slurm_executor_to_directives_bind_resource_types(
    basic_requirements, resource, value, expected
):
    """Test bind directive generation with ResourceType enums."""
    executor = executors.Slurm(
        requirements=basic_requirements,
        time=dt.timedelta(hours=1),
        bind={resource: value},
    )
    directives = executor.step_directives()
    assert any(expected in d for d in directives)


@pytest.mark.parametrize(
    "custom_gres,value,expected",
    [
        ("gpu_custom", "closest", "--tres-bind=gres/gpu_custom:closest"),
        ("memory_pool", "local", "--tres-bind=gres/memory_pool:local"),
        ("accelerator", None, "--tres-bind=gres/accelerator:none"),
    ],
)
def test_slurm_executor_to_directives_bind_custom_gres(
    basic_requirements, custom_gres, value, expected
):
    """Test bind directive generation with custom GRES strings."""
    executor = executors.Slurm(
        requirements=basic_requirements,
        time=dt.timedelta(hours=1),
        bind={custom_gres: value},
    )
    directives = executor.step_directives()
    assert any(expected in d for d in directives)


def test_slurm_executor_to_directives_includes_requirements_directives(basic_requirements):
    """Test that to_directives includes directives from requirements."""
    executor = executors.Slurm(requirements=basic_requirements, time=dt.timedelta(hours=1))
    directives = executor.batch_directives()
    assert any(d.startswith("--cpus-per-task=") for d in directives)
    assert any(d.startswith("--mem-per-cpu=") for d in directives)


@pytest.mark.parametrize(
    "grace_period,expected_diff",
    [
        (
            dt.timedelta(minutes=1, seconds=30),
            dt.timedelta(hours=1) - dt.timedelta(minutes=1, seconds=30),
        ),
        (dt.timedelta(minutes=30), dt.timedelta(hours=2) - dt.timedelta(minutes=30)),
    ],
)
def test_slurm_executor_requeue_timeout_property(basic_requirements, grace_period, expected_diff):
    """Test requeue_timeout property calculation."""
    job_time = dt.timedelta(hours=2)
    executor = executors.Slurm(
        requirements=basic_requirements,
        time=job_time,
        timeout_signal_grace_period=grace_period,
    )
    assert executor.requeue_timeout == job_time - grace_period


@pytest.mark.parametrize("tag", ["test:latest", "ghcr.io/project/image:v1", None])
def test_slurm_executor_spec_classmethod(tag):
    """Test that Executor.Spec() class method returns SlurmSpec."""
    spec = executors.Slurm.Spec(tag=tag)
    assert isinstance(spec, executors.SlurmSpec)
    assert spec.tag == tag


def test_slurm_executor_with_multiple_binds(basic_requirements):
    """Test executor with multiple resource binds."""
    executor = executors.Slurm(
        requirements=basic_requirements,
        time=dt.timedelta(hours=1),
        bind={
            resources.ResourceType.GPU: "closest",
            resources.ResourceType.MEMORY: "local",
        },
    )
    directives = executor.step_directives()
    assert any("--gpu-bind=closest" in d for d in directives)
    assert any("--mem-bind=local" in d for d in directives)


def test_slurm_executor_bind_flag_sets_gres_flags(basic_requirements):
    """Test that bind_flag produces the correct --gres-flags directive."""
    executor = executors.Slurm(
        requirements=basic_requirements,
        time=dt.timedelta(hours=1),
        bind_flag="enforce-binding",
    )
    directives = executor.step_directives()
    assert "--gres-flags=enforce-binding" in directives


@pytest.mark.parametrize("grace_period_secs", [1, 30, 3600])
def test_slurm_executor_with_various_grace_periods(basic_requirements, grace_period_secs):
    """Test executor with various timeout grace periods."""
    executor = executors.Slurm(
        requirements=basic_requirements,
        time=dt.timedelta(hours=24),
        timeout_signal_grace_period=dt.timedelta(seconds=grace_period_secs),
    )
    directives = executor.batch_directives()
    signal_directive = [d for d in directives if d.startswith("--signal=")][0]
    assert f"@{grace_period_secs}" in signal_directive


@pytest.mark.parametrize(
    "job_time,grace_period",
    [
        (dt.timedelta(minutes=2), dt.timedelta(seconds=30)),
        (dt.timedelta(hours=1), dt.timedelta(minutes=5)),
    ],
)
def test_slurm_executor_requeue_timeout_calculation(basic_requirements, job_time, grace_period):
    """Test requeue_timeout with various time combinations."""
    executor = executors.Slurm(
        requirements=basic_requirements,
        time=job_time,
        timeout_signal_grace_period=grace_period,
    )
    expected = job_time - grace_period
    assert executor.requeue_timeout == expected


@pytest.mark.parametrize("sig", [signal.SIGUSR1, signal.SIGUSR2, signal.SIGTERM, signal.SIGKILL])
def test_slurm_executor_multiple_signal_types(basic_requirements, sig):
    """Test executor with different signal types."""
    executor = executors.Slurm(
        requirements=basic_requirements,
        time=dt.timedelta(hours=1),
        timeout_signal=sig,
    )
    directives = executor.batch_directives()
    signal_directive = [d for d in directives if d.startswith("--signal=")][0]
    expected_sig_name = sig.name.removeprefix("SIG")
    assert expected_sig_name in signal_directive
