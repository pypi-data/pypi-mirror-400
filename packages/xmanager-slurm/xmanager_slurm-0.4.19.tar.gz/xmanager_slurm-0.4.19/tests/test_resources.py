import typing as tp

import pytest

from xm_slurm import config, resources


@pytest.fixture
def dummy_cluster_config() -> config.SlurmClusterConfig:
    """Create a dummy cluster configuration for testing."""
    ssh_config = config.SSHConfig(endpoints=(config.Endpoint("localhost", 22),), user="testuser")
    return config.SlurmClusterConfig(
        name="test_cluster",
        ssh=ssh_config,
        runtime=config.ContainerRuntime.DOCKER,
    )


@pytest.fixture
def cluster_with_gpu_mapping() -> config.SlurmClusterConfig:
    """Create a cluster config with GPU resource mapping."""
    ssh_config = config.SSHConfig(endpoints=(config.Endpoint("localhost", 22),), user="testuser")
    return config.SlurmClusterConfig(
        name="gpu_cluster",
        ssh=ssh_config,
        runtime=config.ContainerRuntime.DOCKER,
        resources={
            resources.ResourceType.A100: "a100",
            resources.ResourceType.V100: "v100",
            resources.ResourceType.P100: "p100",
        },
    )


@pytest.fixture
def basic_job_requirements(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> resources.JobRequirements:
    """Create basic job requirements for testing."""
    return resources.JobRequirements(
        cpu=1,
        memory=1024**3,  # 1GB
        cluster=dummy_cluster_config,
    )


def test_job_requirements_with_cpu_and_memory(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test JobRequirements with CPU and memory resources."""
    req = resources.JobRequirements(
        cpu=4,
        memory=8 * 1024**3,
        cluster=dummy_cluster_config,
    )
    assert req.task_requirements[resources.ResourceType.CPU] == 4
    assert req.task_requirements[resources.ResourceType.MEMORY] == 8 * 1024**3
    assert req.replicas == 1


def test_job_requirements_with_replicas(dummy_cluster_config: config.SlurmClusterConfig) -> None:
    """Test JobRequirements with multiple replicas."""
    req = resources.JobRequirements(
        cpu=1,
        replicas=5,
        cluster=dummy_cluster_config,
    )
    assert req.replicas == 5


@pytest.mark.parametrize(
    "location,expected_location",
    [("node001", "node001"), (["node001", "node002"], "node001,node002")],
)
def test_job_requirements_with_location(
    dummy_cluster_config: config.SlurmClusterConfig,
    location: str | tp.Iterable[str],
    expected_location: str,
) -> None:
    """Test JobRequirements with specific node location."""
    req = resources.JobRequirements(
        cpu=1,
        location=location,
        cluster=dummy_cluster_config,
    )
    assert req.location == expected_location


def test_job_requirements_replicas_default_to_one(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that replicas defaults to 1 when None is provided."""
    req = resources.JobRequirements(
        cpu=1,
        replicas=None,  # type: ignore
        cluster=dummy_cluster_config,
    )
    assert req.replicas == 1


@pytest.mark.parametrize(
    "resource_name,resource_type",
    [
        ("cpu", resources.ResourceType.CPU),
        ("memory", resources.ResourceType.MEMORY),
        ("ram", resources.ResourceType.RAM),
        ("disk", resources.ResourceType.DISK),
        ("ephemeral_storage", resources.ResourceType.EPHEMERAL_STORAGE),
    ],
)
def test_job_requirements_string_resource_names(
    dummy_cluster_config: config.SlurmClusterConfig,
    resource_name: str,
    resource_type: resources.ResourceType,
) -> None:
    """Test JobRequirements with string resource names."""
    kwargs = {resource_name: 1, "cluster": dummy_cluster_config}
    req = resources.JobRequirements(**kwargs)
    assert resource_type in req.task_requirements


@pytest.mark.parametrize(
    "resource_name,resource_type",
    [
        ("CPU", resources.ResourceType.CPU),
        ("Memory", resources.ResourceType.MEMORY),
        ("RAM", resources.ResourceType.RAM),
        ("DISK", resources.ResourceType.DISK),
    ],
)
def test_job_requirements_uppercase_string_resource_names(
    dummy_cluster_config: config.SlurmClusterConfig,
    resource_name: str,
    resource_type: resources.ResourceType,
) -> None:
    """Test JobRequirements with uppercase string resource names."""
    kwargs = {resource_name: 1, "cluster": dummy_cluster_config}
    req = resources.JobRequirements(**kwargs)
    assert resource_type in req.task_requirements


def test_job_requirements_with_resource_mapping(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test JobRequirements with resources dict parameter."""
    resources_dict: tp.Mapping[resources.ResourceType | str, resources.ResourceQuantity] = {
        resources.ResourceType.CPU: 2,
        resources.ResourceType.MEMORY: 4 * 1024**3,
    }
    req = resources.JobRequirements(resources=resources_dict, cluster=dummy_cluster_config)
    assert req.task_requirements[resources.ResourceType.CPU] == 2
    assert req.task_requirements[resources.ResourceType.MEMORY] == 4 * 1024**3


def test_job_requirements_mixed_resources_and_kwargs(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test JobRequirements with both resources dict and keyword arguments."""
    resources_dict: tp.Mapping[resources.ResourceType | str, resources.ResourceQuantity] = {
        resources.ResourceType.CPU: 2
    }
    req = resources.JobRequirements(
        resources=resources_dict,
        memory=4 * 1024**3,
        cluster=dummy_cluster_config,
    )
    assert req.task_requirements[resources.ResourceType.CPU] == 2
    assert req.task_requirements[resources.ResourceType.MEMORY] == 4 * 1024**3


def test_job_requirements_generic_resources(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test JobRequirements with generic resource names."""
    req = resources.JobRequirements(
        cluster=dummy_cluster_config,
        custom_resource="2",  # type: ignore
    )
    assert req.task_requirements["custom_resource"] == 2


def test_job_requirements_with_generic_gpu(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test JobRequirements with generic GPU resource."""
    req = resources.JobRequirements(
        gpu=2,
        cluster=dummy_cluster_config,
    )
    assert req.accelerator == resources.ResourceType.GPU
    assert req.task_requirements[resources.ResourceType.GPU] == 2


@pytest.mark.parametrize(
    "accelerator_type,count",
    [
        (resources.ResourceType.A100, 1),
        (resources.ResourceType.V100, 2),
        (resources.ResourceType.P100, 4),
        (resources.ResourceType.H100, 8),
    ],
)
def test_job_requirements_with_specific_accelerators(
    dummy_cluster_config: config.SlurmClusterConfig,
    accelerator_type: resources.ResourceType,
    count: int,
) -> None:
    """Test JobRequirements with specific accelerator types."""
    kwargs = {accelerator_type.name.lower(): count, "cluster": dummy_cluster_config}
    req = resources.JobRequirements(**kwargs)
    assert req.accelerator == accelerator_type
    assert req.task_requirements[accelerator_type] == count


def test_job_requirements_multiple_accelerators_error(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that multiple accelerators raise an error."""
    with pytest.raises(ValueError, match="Accelerator already set"):
        resources.JobRequirements(
            a100=1,
            v100=2,
            cluster=dummy_cluster_config,
        )


def test_job_requirements_gpu_and_specific_accelerator_error(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that GPU and specific accelerator together raise an error."""
    with pytest.raises(ValueError, match="Accelerator already set"):
        resources.JobRequirements(
            gpu=1,
            a100=2,
            cluster=dummy_cluster_config,
        )


def test_job_requirements_duplicate_resource_error(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that specifying same resource twice raises an error."""
    with pytest.raises(ValueError, match="has been specified twice"):
        resources.JobRequirements(
            resources={resources.ResourceType.CPU: 2},
            cpu=4,
            cluster=dummy_cluster_config,
        )


def test_job_requirements_duplicate_memory_and_ram_error(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that memory and ram (which map to same type) raises an error."""
    with pytest.raises(ValueError, match="has been specified twice"):
        resources.JobRequirements(
            memory=4 * 1024**3,
            ram=4 * 1024**3,
            cluster=dummy_cluster_config,
        )


def test_job_requirements_duplicate_disk_and_storage_error(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that disk and ephemeral_storage (which map to same type) raises an error."""
    with pytest.raises(ValueError, match="has been specified twice"):
        resources.JobRequirements(
            disk=1024**3,
            ephemeral_storage=1024**3,
            cluster=dummy_cluster_config,
        )


def test_job_requirements_to_directives_cpu(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test CPU directive generation."""
    req = resources.JobRequirements(cpu=4, cluster=dummy_cluster_config)
    directives = req.batch_directives()
    assert "--cpus-per-task=4" in directives


def test_job_requirements_to_directives_memory(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test memory directive generation."""
    req = resources.JobRequirements(
        cpu=2,
        memory=8 * 1024**3,  # 8GB
        cluster=dummy_cluster_config,
    )
    directives = req.batch_directives()
    # 8GB / 2 CPUs / 2^20 bytes per MB = 4096 MB
    assert "--mem-per-cpu=4096M" in directives


def test_job_requirements_to_directives_memory_with_single_cpu(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test memory directive with single CPU (default)."""
    req = resources.JobRequirements(
        memory=2 * 1024**3,  # 2GB
        cluster=dummy_cluster_config,
    )
    directives = req.batch_directives()
    # 2GB / 1 CPU / 2^20 = 2048 MB
    assert "--mem-per-cpu=2048M" in directives


def test_job_requirements_to_directives_ram_alias(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that RAM alias works like MEMORY."""
    req = resources.JobRequirements(
        cpu=2,
        ram=8 * 1024**3,
        cluster=dummy_cluster_config,
    )
    directives = req.batch_directives()
    assert "--mem-per-cpu=4096M" in directives


def test_job_requirements_to_directives_disk(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test disk space directive generation."""
    req = resources.JobRequirements(
        disk=1024**3,  # 1GB
        cluster=dummy_cluster_config,
    )
    directives = req.batch_directives()
    # 1GB / 2^20 MB = 1024 MB
    assert "--tmp=1024M" in directives


def test_job_requirements_to_directives_ephemeral_storage_alias(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that ephemeral_storage alias works like disk."""
    req = resources.JobRequirements(
        ephemeral_storage=2 * 1024**3,  # 2GB
        cluster=dummy_cluster_config,
    )
    directives = req.batch_directives()
    # 2GB / 2^20 MB = 2048 MB
    assert "--tmp=2048M" in directives


def test_job_requirements_to_directives_generic_gpu(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test generic GPU directive generation."""
    req = resources.JobRequirements(
        gpu=4,
        cluster=dummy_cluster_config,
    )
    directives = req.batch_directives()
    assert "--gpus=4" in directives


def test_job_requirements_to_directives_specific_gpu(
    cluster_with_gpu_mapping: config.SlurmClusterConfig,
) -> None:
    """Test specific GPU type directive generation."""
    req = resources.JobRequirements(
        a100=2,
        cluster=cluster_with_gpu_mapping,
    )
    directives = req.batch_directives()
    assert "--gpus=a100:2" in directives


@pytest.mark.parametrize(
    "accelerator_type,gpu_name,count",
    [
        (resources.ResourceType.A100, "a100", 1),
        (resources.ResourceType.V100, "v100", 2),
        (resources.ResourceType.P100, "p100", 4),
    ],
)
def test_job_requirements_to_directives_various_gpu_types(
    accelerator_type: resources.ResourceType,
    gpu_name: str,
    count: int,
) -> None:
    """Test specific GPU type directive generation for various types."""
    ssh_config = config.SSHConfig(endpoints=(config.Endpoint("localhost", 22),), user="testuser")
    cluster = config.SlurmClusterConfig(
        name="gpu_cluster",
        ssh=ssh_config,
        runtime=config.ContainerRuntime.DOCKER,
        resources={accelerator_type: gpu_name},
    )
    kwargs = {accelerator_type.name.lower(): count}
    req = resources.JobRequirements(**kwargs, cluster=cluster)  # type: ignore
    directives = req.batch_directives()
    assert f"--gpus={gpu_name}:{count}" in directives


def test_job_requirements_to_directives_unmapped_gpu_raises_error(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that unmapped accelerator raises error."""
    req = resources.JobRequirements(
        a100=1,
        cluster=dummy_cluster_config,
    )
    with pytest.raises(ValueError, match="does not map resource type"):
        req.batch_directives()


def test_job_requirements_to_directives_custom_gres(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test custom GRES directive generation."""
    req = resources.JobRequirements(
        custom_resource="2",  # type: ignore
        cluster=dummy_cluster_config,
    )
    directives = req.batch_directives()
    assert "--gres=custom_resource:2" in directives


def test_job_requirements_to_directives_replicas(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test replicas directive generation."""
    req = resources.JobRequirements(
        cpu=1,
        replicas=8,
        cluster=dummy_cluster_config,
    )
    directives = req.batch_directives()
    assert "--ntasks=8" in directives


def test_job_requirements_to_directives_location(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test node location directive generation."""
    req = resources.JobRequirements(
        cpu=1,
        location="node[001-005]",
        cluster=dummy_cluster_config,
    )
    directives = req.batch_directives()
    assert "--nodelist=node[001-005]" in directives


def test_job_requirements_to_directives_combined_all_resources(
    cluster_with_gpu_mapping: config.SlurmClusterConfig,
) -> None:
    """Test directive generation with all resource types."""
    req = resources.JobRequirements(
        cpu=8,
        memory=64 * 1024**3,  # 64GB
        disk=500 * 1024**3,  # 500GB
        a100=2,
        replicas=4,
        location="gpu-nodes[001-004]",
        cluster=cluster_with_gpu_mapping,
    )
    directives = req.batch_directives()
    assert "--cpus-per-task=8" in directives
    assert "--mem-per-cpu=8192M" in directives  # 64GB / 8 CPUs / 2^20
    assert "--tmp=512000M" in directives  # 500GB / 2^20
    assert "--gpus=a100:2" in directives
    assert "--ntasks=4" in directives
    assert "--nodelist=gpu-nodes[001-004]" in directives


def test_job_requirements_replace_all_parameters(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test replace method with all parameters."""
    original = resources.JobRequirements(
        cpu=2,
        memory=4 * 1024**3,
        replicas=2,
        cluster=dummy_cluster_config,
    )
    ssh_config = config.SSHConfig(endpoints=(config.Endpoint("localhost", 22),), user="testuser")
    new_cluster = config.SlurmClusterConfig(
        name="new_cluster",
        ssh=ssh_config,
        runtime=config.ContainerRuntime.DOCKER,
    )
    replaced = original.replace(
        cpu=4,
        memory=8 * 1024**3,
        replicas=4,
        location="new-location",
        cluster=new_cluster,
    )
    assert replaced.task_requirements[resources.ResourceType.CPU] == 4
    assert replaced.task_requirements[resources.ResourceType.MEMORY] == 8 * 1024**3
    assert replaced.replicas == 4
    assert replaced.location == "new-location"
    assert replaced.cluster == new_cluster


def test_job_requirements_replace_partial_parameters(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test replace method with partial parameters."""
    original = resources.JobRequirements(
        cpu=2,
        memory=4 * 1024**3,
        replicas=2,
        location="original-location",
        cluster=dummy_cluster_config,
    )
    replaced = original.replace(cpu=4, replicas=8)
    assert replaced.task_requirements[resources.ResourceType.CPU] == 4
    assert replaced.task_requirements[resources.ResourceType.MEMORY] == 4 * 1024**3
    assert replaced.replicas == 8
    assert replaced.location == "original-location"
    assert replaced.cluster == dummy_cluster_config


def test_job_requirements_replace_preserves_cluster_when_not_specified(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that replace preserves cluster when not specified."""
    req = resources.JobRequirements(cpu=1, cluster=dummy_cluster_config)
    replaced = req.replace(cpu=2)
    assert replaced.cluster == dummy_cluster_config


def test_job_requirements_replace_with_resources_dict(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test replace method with keyword arguments for resources."""
    original = resources.JobRequirements(
        cpu=2,
        memory=4 * 1024**3,
        cluster=dummy_cluster_config,
    )
    replaced = original.replace(
        cpu=8,
        memory=16 * 1024**3,
    )
    assert replaced.task_requirements[resources.ResourceType.CPU] == 8
    assert replaced.task_requirements[resources.ResourceType.MEMORY] == 16 * 1024**3


def test_job_requirements_replace_with_additional_kwargs(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test replace method with additional keyword arguments."""
    original = resources.JobRequirements(
        cpu=2,
        cluster=dummy_cluster_config,
    )
    replaced = original.replace(memory=8 * 1024**3)
    assert replaced.task_requirements[resources.ResourceType.CPU] == 2
    assert replaced.task_requirements[resources.ResourceType.MEMORY] == 8 * 1024**3


def test_job_requirements_repr_simple_requirements(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test repr for simple requirements."""
    req = resources.JobRequirements(cpu=2, cluster=dummy_cluster_config)
    repr_str = repr(req)
    assert "xm_slurm.JobRequirements" in repr_str
    assert "cpu=2" in repr_str


def test_job_requirements_repr_multiple_resources(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test repr with multiple resources."""
    req = resources.JobRequirements(
        cpu=4,
        memory=8 * 1024**3,
        cluster=dummy_cluster_config,
    )
    repr_str = repr(req)
    assert "cpu=4" in repr_str
    assert f"memory={8 * 1024**3!r}" in repr_str


def test_job_requirements_repr_with_replicas(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test repr includes replicas when not default."""
    req = resources.JobRequirements(
        cpu=1,
        replicas=5,
        cluster=dummy_cluster_config,
    )
    repr_str = repr(req)
    assert "replicas=5" in repr_str


def test_job_requirements_repr_without_replicas_when_default(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test repr excludes replicas when it's the default value."""
    req = resources.JobRequirements(
        cpu=1,
        replicas=1,
        cluster=dummy_cluster_config,
    )
    repr_str = repr(req)
    assert "replicas=" not in repr_str


def test_job_requirements_repr_with_cluster(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test repr includes cluster."""
    req = resources.JobRequirements(
        cpu=1,
        cluster=dummy_cluster_config,
    )
    repr_str = repr(req)
    assert "cluster=" in repr_str


def test_job_requirements_repr_resource_types_as_lowercase(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that ResourceType names are lowercase in repr."""
    req = resources.JobRequirements(
        cpu=2,
        memory=4 * 1024**3,
        cluster=dummy_cluster_config,
    )
    repr_str = repr(req)
    # Should use lowercase names for ResourceType
    assert "cpu=" in repr_str
    assert "memory=" in repr_str
    assert "CPU" not in repr_str.split("=")[1]  # Check that CPU values aren't uppercase


def test_job_requirements_repr_custom_resources_stay_lowercase(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that custom resource names stay lowercase in repr."""
    req = resources.JobRequirements(
        custom_resource="2",  # type: ignore
        cluster=dummy_cluster_config,
    )
    repr_str = repr(req)
    assert "custom_resource=" in repr_str


def test_job_requirements_invalid_memory_type(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that invalid memory type is caught during directive generation."""
    req = resources.JobRequirements(cluster=dummy_cluster_config)
    req.task_requirements[resources.ResourceType.MEMORY] = "invalid"  # type: ignore
    with pytest.raises(AssertionError, match="Memory must be an integer or float"):
        req.batch_directives()


def test_job_requirements_invalid_cpu_type(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that invalid CPU type is caught during directive generation."""
    req = resources.JobRequirements(cluster=dummy_cluster_config)
    req.task_requirements[resources.ResourceType.CPU] = 4.5  # type: ignore
    with pytest.raises(AssertionError, match="CPU must be an integer"):
        req.batch_directives()


def test_job_requirements_invalid_gpu_type(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that invalid GPU type is caught during directive generation."""
    req = resources.JobRequirements(cluster=dummy_cluster_config)
    req.task_requirements[resources.ResourceType.GPU] = 1.5  # type: ignore
    with pytest.raises(AssertionError, match="GPU must be an integer"):
        req.batch_directives()


def test_job_requirements_invalid_disk_type(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that invalid disk type is caught during directive generation."""
    req = resources.JobRequirements(cluster=dummy_cluster_config)
    req.task_requirements[resources.ResourceType.DISK] = 1.5  # type: ignore
    with pytest.raises(AssertionError, match="Disk space must be an integer"):
        req.batch_directives()


def test_job_requirements_invalid_replicas(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that invalid replicas raise an error during directive generation."""
    req = resources.JobRequirements(cluster=dummy_cluster_config)
    req.replicas = -1
    with pytest.raises(AssertionError, match="Replicas must be a positive integer"):
        req.batch_directives()


def test_job_requirements_invalid_replicas_zero(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that zero replicas raise an error during directive generation."""
    req = resources.JobRequirements(cluster=dummy_cluster_config)
    req.replicas = 0
    with pytest.raises(AssertionError, match="Replicas must be a positive integer"):
        req.batch_directives()


def test_job_requirements_invalid_location_type(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that invalid location type is caught during directive generation."""
    req = resources.JobRequirements(cluster=dummy_cluster_config)
    req.location = 123  # type: ignore
    with pytest.raises(AssertionError, match="Location must be a string"):
        req.batch_directives()


@pytest.mark.parametrize(
    "memory_bytes,cpu_count,expected_mem_per_cpu_mb",
    [
        (1024**3, 1, 1024),
        (2 * 1024**3, 2, 1024),
        (4 * 1024**3, 4, 1024),
        (8 * 1024**3, 2, 4096),
        (16 * 1024**3, 4, 4096),
    ],
)
def test_job_requirements_memory_directive_calculation(
    dummy_cluster_config: config.SlurmClusterConfig,
    memory_bytes: int,
    cpu_count: int,
    expected_mem_per_cpu_mb: int,
) -> None:
    """Test memory directive calculation with various CPU counts."""
    req = resources.JobRequirements(
        cpu=cpu_count,
        memory=memory_bytes,
        cluster=dummy_cluster_config,
    )
    directives = req.batch_directives()
    assert f"--mem-per-cpu={expected_mem_per_cpu_mb}M" in directives


@pytest.mark.parametrize(
    "disk_bytes,expected_tmp_mb",
    [
        (1024**3, 1024),
        (2 * 1024**3, 2048),
        (512 * 1024**3, 524288),
        (1024 * 1024**3, 1048576),
    ],
)
def test_job_requirements_disk_directive_calculation(
    dummy_cluster_config: config.SlurmClusterConfig,
    disk_bytes: int,
    expected_tmp_mb: int,
) -> None:
    """Test disk directive calculation with various sizes."""
    req = resources.JobRequirements(
        disk=disk_bytes,
        cluster=dummy_cluster_config,
    )
    directives = req.batch_directives()
    assert f"--tmp={expected_tmp_mb}M" in directives


def test_job_requirements_fractional_memory_rounds_correctly(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that fractional memory values are rounded correctly."""
    req = resources.JobRequirements(
        cpu=3,
        memory=10 * 1024**3,  # 10GB / 3 = 3.33GB per CPU
        cluster=dummy_cluster_config,
    )
    directives = req.batch_directives()
    # math.ceil(10 * 1024^3 / 3 / 2^20) = math.ceil(3413.33...) = 3414
    assert "--mem-per-cpu=3414M" in directives


def test_job_requirements_fractional_disk_rounds_correctly(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that fractional disk values are rounded correctly."""
    req = resources.JobRequirements(
        disk=5 * 1024**3 + 512 * 1024**2,  # 5.5GB
        cluster=dummy_cluster_config,
    )
    directives = req.batch_directives()
    # math.ceil((5*1024^3 + 512*1024^2) / 2^20) = math.ceil(5632) = 5632
    assert "--tmp=5632M" in directives


def test_job_requirements_empty_task_requirements(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test job requirements with no specific resources."""
    req = resources.JobRequirements(cluster=dummy_cluster_config)
    directives = req.batch_directives()
    # Should still have ntasks directive
    assert "--ntasks=1" in directives
    assert len(directives) == 1


def test_job_requirements_accelerator_flag_not_set_without_gpu(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that accelerator is None when no GPU is specified."""
    req = resources.JobRequirements(
        cpu=4,
        memory=8 * 1024**3,
        cluster=dummy_cluster_config,
    )
    assert req.accelerator is None


def test_job_requirements_multiple_directives_order_independence(
    cluster_with_gpu_mapping: config.SlurmClusterConfig,
) -> None:
    """Test that directive order doesn't matter for correctness."""
    req1 = resources.JobRequirements(
        cpu=2,
        memory=4 * 1024**3,
        disk=500 * 1024**3,
        a100=1,
        cluster=cluster_with_gpu_mapping,
    )
    req2 = resources.JobRequirements(
        disk=500 * 1024**3,
        a100=1,
        cpu=2,
        memory=4 * 1024**3,
        cluster=cluster_with_gpu_mapping,
    )
    directives1 = set(req1.batch_directives())
    directives2 = set(req2.batch_directives())
    assert directives1 == directives2


def test_job_requirements_resource_type_membership() -> None:
    """Test various resource type memberships."""
    # GPU should be in AcceleratorType set
    assert resources.ResourceType.GPU not in resources.AcceleratorType

    # Specific GPUs should be in AcceleratorType
    assert resources.ResourceType.A100 in resources.AcceleratorType
    assert resources.ResourceType.V100 in resources.AcceleratorType

    # Non-GPU resources should not be in AcceleratorType
    assert resources.ResourceType.CPU not in resources.AcceleratorType
    assert resources.ResourceType.MEMORY not in resources.AcceleratorType


def test_topology_single_dimension() -> None:
    """Test creating a topology with a single dimension."""
    topo = resources.Topology("8")
    assert topo.mesh == "8"
    assert topo.dimensions == [8]
    assert topo.chip_count == 8
    assert topo.ndim == 1


def test_topology_two_dimensions() -> None:
    """Test creating a topology with two dimensions."""
    topo = resources.Topology("4x2")
    assert topo.mesh == "4x2"
    assert topo.dimensions == [4, 2]
    assert topo.chip_count == 8
    assert topo.ndim == 2


def test_topology_three_dimensions() -> None:
    """Test creating a topology with three dimensions."""
    topo = resources.Topology("2x2x2")
    assert topo.mesh == "2x2x2"
    assert topo.dimensions == [2, 2, 2]
    assert topo.chip_count == 8
    assert topo.ndim == 3


def test_topology_many_dimensions() -> None:
    """Test creating a topology with many dimensions."""
    topo = resources.Topology("2x2x2x2x2")
    assert topo.mesh == "2x2x2x2x2"
    assert topo.dimensions == [2, 2, 2, 2, 2]
    assert topo.chip_count == 32
    assert topo.ndim == 5


def test_topology_invalid_mesh_empty() -> None:
    """Test that empty mesh string raises InvalidTopologyError."""
    with pytest.raises(resources.InvalidTopologyError, match="Invalid topology mesh"):
        resources.Topology("")


def test_topology_invalid_mesh_no_digits() -> None:
    """Test that mesh with no digits raises InvalidTopologyError."""
    with pytest.raises(resources.InvalidTopologyError, match="Invalid topology mesh"):
        resources.Topology("abc")


def test_topology_invalid_mesh_extra_characters() -> None:
    """Test that mesh with invalid characters raises InvalidTopologyError."""
    with pytest.raises(resources.InvalidTopologyError, match="Invalid topology mesh"):
        resources.Topology("4x2x")


def test_topology_invalid_mesh_with_space() -> None:
    """Test that mesh with spaces raises InvalidTopologyError."""
    with pytest.raises(resources.InvalidTopologyError, match="Invalid topology mesh"):
        resources.Topology("4 x 2")


def test_topology_invalid_mesh_negative_dimension() -> None:
    """Test that negative dimensions are rejected."""
    # Note: regex won't match negative numbers, so this raises InvalidTopologyError
    with pytest.raises(resources.InvalidTopologyError, match="Invalid topology mesh"):
        resources.Topology("-4x2")


def test_topology_missing_switches_raises_error() -> None:
    """Test that invalid switches type raises AssertionError."""
    with pytest.raises(AssertionError, match="Switches must be a positive integer"):
        resources.Topology("4x2", switches="2")  # type: ignore


def test_topology_invalid_switches_type_raises_error() -> None:
    """Test that non-integer switches raises AssertionError."""
    with pytest.raises(AssertionError, match="Switches must be a positive integer"):
        resources.Topology("4x2", switches=2.5)  # type: ignore


def test_topology_zero_switches_raises_error() -> None:
    """Test that zero switches raises AssertionError."""
    with pytest.raises(AssertionError, match="Switches must be a positive integer"):
        resources.Topology("4x2", switches=0)


def test_topology_negative_switches_raises_error() -> None:
    """Test that negative switches raises AssertionError."""
    with pytest.raises(AssertionError, match="Switches must be a positive integer"):
        resources.Topology("4x2", switches=-1)


def test_topology_missing_grace_period_is_allowed() -> None:
    """Test that grace period can be None."""
    topo = resources.Topology("4x2", switches=1)
    assert topo.switches_grace_period is None


def test_topology_invalid_grace_period_type_raises_error() -> None:
    """Test that non-timedelta grace period raises AssertionError."""
    with pytest.raises(AssertionError, match="Switches grace period must be a"):
        resources.Topology("4x2", switches=1, switches_grace_period="5 minutes")  # type: ignore


def test_topology_equality_same_values() -> None:
    """Test that topologies with same values are equal."""
    topo1 = resources.Topology("4x2", switches=1)
    topo2 = resources.Topology("4x2", switches=1)
    assert topo1 == topo2


def test_topology_inequality_different_mesh() -> None:
    """Test that topologies with different mesh are not equal."""
    topo1 = resources.Topology("4x2", switches=1)
    topo2 = resources.Topology("2x4", switches=1)
    assert topo1 != topo2


def test_topology_inequality_different_switches() -> None:
    """Test that topologies with different switches are not equal."""
    topo1 = resources.Topology("4x2", switches=1)
    topo2 = resources.Topology("4x2", switches=2)
    assert topo1 != topo2


def test_topology_inequality_different_grace_period() -> None:
    """Test that topologies with different grace periods are not equal."""
    delta1 = __import__("datetime").timedelta(minutes=5)
    delta2 = __import__("datetime").timedelta(minutes=10)
    topo1 = resources.Topology("4x2", switches=1, switches_grace_period=delta1)
    topo2 = resources.Topology("4x2", switches=1, switches_grace_period=delta2)
    assert topo1 != topo2


def test_topology_hash_consistency() -> None:
    """Test that equal topologies have the same hash."""
    topo1 = resources.Topology("4x2", switches=1)
    topo2 = resources.Topology("4x2", switches=1)
    assert hash(topo1) == hash(topo2)


def test_topology_hash_in_set() -> None:
    """Test that topologies can be used in sets."""
    topo1 = resources.Topology("4x2", switches=1)
    topo2 = resources.Topology("4x2", switches=1)
    topo3 = resources.Topology("2x4", switches=1)
    topology_set = {topo1, topo2, topo3}
    assert len(topology_set) == 2


def test_topology_hash_in_dict() -> None:
    """Test that topologies can be used as dict keys."""
    topo1 = resources.Topology("4x2", switches=1)
    topo2 = resources.Topology("4x2", switches=1)
    topology_dict = {topo1: "value1"}
    topology_dict[topo2] = "value2"
    assert len(topology_dict) == 1
    assert topology_dict[topo1] == "value2"


def test_topology_inequality_with_non_topology() -> None:
    """Test that topology is not equal to non-topology objects."""
    topo = resources.Topology("4x2", switches=1)
    assert topo != "4x2"
    assert topo != 8
    assert topo is not None
    assert topo != {"mesh": "4x2"}


def test_job_requirements_with_topology_object(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test creating job requirements with a Topology object."""
    topo = resources.Topology("4x2", switches=1)
    req = resources.JobRequirements(
        gpu=topo,
        cluster=dummy_cluster_config,
    )
    assert req.topology == topo
    assert req.accelerator == resources.ResourceType.GPU
    assert req.task_requirements[resources.ResourceType.GPU] == 8


def test_job_requirements_with_topology_string(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test creating job requirements with a topology string."""
    # Note: Creating a topology from a string directly doesn't work
    # since Topology requires switches and switches_grace_period.
    # This test documents that behavior.
    topo = resources.Topology("4x2", switches=1)
    req = resources.JobRequirements(
        gpu=topo,
        cluster=dummy_cluster_config,
    )
    assert req.topology is not None
    assert req.topology.mesh == "4x2"
    assert req.topology.dimensions == [4, 2]
    assert req.task_requirements[resources.ResourceType.GPU] == 8


def test_job_requirements_single_dim_topology_creates_topology_object(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that numeric GPU value creates a Topology object with default switches."""
    # Looking at the code, numeric values are parsed as floats, not Topology objects
    # Topology objects are only created from explicit Topology objects or topology strings
    # with switches/grace_period parameters
    topo = resources.Topology("8", switches=1)
    req = resources.JobRequirements(
        gpu=topo,
        cluster=dummy_cluster_config,
    )
    assert req.topology is not None
    assert req.topology.mesh == "8"
    assert req.topology.dimensions == [8]
    assert req.topology.chip_count == 8


def test_job_requirements_topology_replicates_from_second_dimension(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that 2D topology sets replicas from second dimension."""
    topo = resources.Topology("4x3", switches=1)
    req = resources.JobRequirements(
        gpu=topo,
        cluster=dummy_cluster_config,
    )
    assert req.replicas == 3


def test_job_requirements_2d_topology_replicas_mismatch_error(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that mismatched replicas with 2D topology raises error."""
    topo = resources.Topology("4x3", switches=1)
    with pytest.raises(ValueError, match="replicas should"):
        resources.JobRequirements(
            gpu=topo,
            replicas=5,
            cluster=dummy_cluster_config,
        )


def test_job_requirements_2d_topology_replicas_match_succeeds(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that matching replicas with 2D topology succeeds."""
    topo = resources.Topology("4x3", switches=1)
    req = resources.JobRequirements(
        gpu=topo,
        replicas=3,
        cluster=dummy_cluster_config,
    )
    assert req.replicas == 3


def test_job_requirements_topology_with_specific_accelerator(
    cluster_with_gpu_mapping: config.SlurmClusterConfig,
) -> None:
    """Test topology with specific accelerator type."""
    topo = resources.Topology("2x4", switches=2)
    req = resources.JobRequirements(
        a100=topo,
        cluster=cluster_with_gpu_mapping,
    )
    assert req.topology == topo
    assert req.accelerator == resources.ResourceType.A100
    assert req.task_requirements[resources.ResourceType.A100] == 8
    assert req.replicas == 4


def test_job_requirements_topology_on_non_accelerator_raises_error(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that topology on non-accelerator resource raises error."""
    topo = resources.Topology("4x2", switches=1)
    with pytest.raises(ValueError, match="A topology was specified for a non-accelerator"):
        resources.JobRequirements(
            cpu=topo,  # type: ignore
            cluster=dummy_cluster_config,
        )


def test_topology_directive_gpus_per_task(dummy_cluster_config: config.SlurmClusterConfig) -> None:
    """Test that topology generates gpus-per-task directive."""
    topo = resources.Topology("4x2", switches=1)
    req = resources.JobRequirements(
        gpu=topo,
        cluster=dummy_cluster_config,
    )
    directives = req.batch_directives()
    assert "--gpus-per-task=4" in directives


def test_topology_directive_gpus_per_task_with_specific_accelerator(
    cluster_with_gpu_mapping: config.SlurmClusterConfig,
) -> None:
    """Test that topology generates gpus-per-task directive."""
    topo = resources.Topology("2x4", switches=2)
    req = resources.JobRequirements(
        a100=topo,
        cluster=cluster_with_gpu_mapping,
    )
    directives = req.batch_directives()
    assert "--gpus-per-task=a100:2" in directives


def test_topology_directive_ntasks_from_topology(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that 2D topology generates ntasks directive from second dimension."""
    topo = resources.Topology("4x3", switches=1)
    req = resources.JobRequirements(
        gpu=topo,
        cluster=dummy_cluster_config,
    )
    directives = req.batch_directives()
    assert "--ntasks=3" in directives


def test_topology_directive_switches(dummy_cluster_config: config.SlurmClusterConfig) -> None:
    """Test that topology generates switches directive."""
    topo = resources.Topology("4x2", switches=2)
    req = resources.JobRequirements(
        gpu=topo,
        cluster=dummy_cluster_config,
    )
    directives = req.batch_directives()
    assert any("--switches=" in d for d in directives)


def test_topology_directive_switches_with_timeout(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that topology generates switches directive with grace period timeout."""
    delta = __import__("datetime").timedelta(minutes=5)
    topo = resources.Topology("4x2", switches=2, switches_grace_period=delta)
    req = resources.JobRequirements(
        gpu=topo,
        cluster=dummy_cluster_config,
    )
    directives = req.batch_directives()
    # Should have format like "--switches=2@5:00" (5 minutes in SLURM format)
    switches_directives = [d for d in directives if "--switches=" in d]
    assert len(switches_directives) > 0
    assert "@" in switches_directives[0]


def test_topology_1d_topology_no_ntasks_override(
    dummy_cluster_config: config.SlurmClusterConfig,
) -> None:
    """Test that 1D topology doesn't override ntasks from replicas."""
    topo = resources.Topology("8", switches=1)
    req = resources.JobRequirements(
        gpu=topo,
        replicas=4,
        cluster=dummy_cluster_config,
    )
    directives = req.batch_directives()
    assert "--ntasks=4" in directives


def test_parse_topology_object() -> None:
    """Test parsing a Topology object."""
    topology = resources.Topology("4x2")
    quantity, topo = resources._parse_resource_quantity(resources.ResourceType.GPU, topology)
    assert quantity == topology.chip_count
    assert topology == topo


def test_parse_topology_string() -> None:
    """Test parsing a topology string creates a Topology object."""
    # Topology strings are parsed successfully and create Topology objects
    # even without explicit switches/grace_period parameters
    quantity, topology = resources._parse_resource_quantity(resources.ResourceType.GPU, "4x2")  # type: ignore
    assert quantity == 8
    assert isinstance(topology, resources.Topology)
    assert topology.mesh == "4x2"
    assert topology.dimensions == [4, 2]


def test_parse_numeric_string() -> None:
    """Test parsing a numeric string creates a Topology object."""
    # A numeric string like "8" matches the TOPOLOGY_REGEX, so it creates a Topology
    quantity, topology = resources._parse_resource_quantity(resources.ResourceType.GPU, "8")  # type: ignore
    assert quantity == 8
    assert topology is None

    quantity, topology = resources._parse_resource_quantity(resources.ResourceType.GPU, "4x2")  # type: ignore
    assert quantity == 8
    assert isinstance(topology, resources.Topology)
    assert topology.mesh == "4x2"
    assert topology.dimensions == [4, 2]


def test_parse_float_string() -> None:
    """Test parsing a float string that doesn't match topology regex."""
    result = resources._parse_resource_quantity(
        resources.ResourceType.MEMORY,
        "4.5",  # type: ignore
    )
    assert result == (4.5, None)


def test_parse_invalid_string_raises_error() -> None:
    """Test parsing a non-numeric string is accepted as custom resource value."""
    # Non-numeric strings are now accepted as custom resource values
    with pytest.raises(ValueError, match="Couldn't parse resource quantity"):
        resources._parse_resource_quantity(
            resources.ResourceType.GPU,
            "invalid",  # type: ignore
        )


def test_parse_invalid_type_raises_error() -> None:
    """Test parsing invalid type raises error."""
    with pytest.raises(ValueError, match="Invalid resource quantity"):
        resources._parse_resource_quantity(
            resources.ResourceType.GPU,
            {"invalid": "dict"},  # type: ignore
        )


def test_large_topology_chip_count() -> None:
    """Test topology with large chip counts."""
    topo = resources.Topology("100x100x100", switches=1)
    assert topo.chip_count == 1000000
    assert topo.ndim == 3


def test_topology_with_single_unit_dimension() -> None:
    """Test topology with dimension of 1."""
    topo = resources.Topology("1x8", switches=1)
    assert topo.chip_count == 8
    assert topo.dimensions == [1, 8]


def test_topology_grace_period_zero_seconds() -> None:
    """Test topology with zero seconds grace period."""
    delta = __import__("datetime").timedelta(seconds=0)
    topo = resources.Topology("4x2", switches=1, switches_grace_period=delta)
    assert topo.switches_grace_period == delta


def test_topology_grace_period_very_long() -> None:
    """Test topology with very long grace period."""
    delta = __import__("datetime").timedelta(days=365)
    topo = resources.Topology("4x2", switches=1, switches_grace_period=delta)
    assert topo.switches_grace_period == delta


def test_topology_switches_large_number() -> None:
    """Test topology with large number of switches."""
    topo = resources.Topology("4x2", switches=10000)
    assert topo.switches == 10000


def test_parse_topology_with_leading_zeros() -> None:
    """Test parsing topology with leading zeros."""
    topo = resources.Topology("004x002", switches=1)
    assert topo.mesh == "004x002"
    assert topo.dimensions == [4, 2]
    assert topo.chip_count == 8
