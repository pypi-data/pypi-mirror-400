import os
import typing as tp

from xm_slurm import config
from xm_slurm.resources import FeatureType, ResourceType

__all__ = [
    "fir",
    "narval",
    "nibi",
    "rorqual",
    "killarney",
    "tamia",
    "vulcan",
]


def _drac_cluster(
    *,
    name: str,
    host: str,
    port: int = 22,
    robot_host: str | None = None,
    robot_port: int | None = None,
    public_key: config.PublicKey,
    user: str | None = None,
    account: str | None = None,
    modules: list[str] | None = None,
    proxy: tp.Literal["submission-host"] | str | None = None,
    mounts: tp.Mapping[os.PathLike[str] | str, os.PathLike[str] | str] | None = None,
    resources: tp.Mapping[ResourceType, str] | None = None,
    features: tp.Mapping[FeatureType, str] | None = None,
) -> config.SlurmClusterConfig:
    """DRAC Cluster."""
    if mounts is None:
        mounts = {
            "/scratch/$USER": "/scratch",
            # TODO: move these somewhere common to all cluster configs.
            "/home/$USER/.ssh": "/home/$USER/.ssh",
            "/home/$USER/.local/state/xm-slurm": "/xm-slurm-state",
        }
    mounts = dict(mounts) | {"/dev/infiniband": "/dev/infiniband"}

    endpoints = []
    if robot_host is not None and robot_host != host:
        endpoints.append(config.Endpoint(robot_host, robot_port))
    endpoints.append(config.Endpoint(host, port))
    endpoints = tuple(endpoints)

    return config.SlurmClusterConfig(
        name=name,
        ssh=config.SSHConfig(user=user, endpoints=endpoints, public_key=public_key),
        account=account,
        proxy=proxy,
        runtime=config.ContainerRuntime.APPTAINER,
        prolog=f"module load apptainer {' '.join(modules) if modules else ''}".rstrip(),
        host_environment={
            "XDG_DATA_HOME": "$SLURM_TMPDIR/.local",
            "APPTAINER_CACHEDIR": "$SCRATCH/.apptainer",
            "APPTAINER_TMPDIR": "$SLURM_TMPDIR",
            "APPTAINER_LOCALCACHEDIR": "$SLURM_TMPDIR",
        },
        container_environment={
            "SCRATCH": "/scratch",
            "XM_SLURM_STATE_DIR": "/xm-slurm-state",
        },
        mounts=mounts,
        resources=resources or {},
        features=features or {},
    )


def narval(
    *,
    user: str | None = None,
    account: str | None = None,
    proxy: tp.Literal["submission-host"] | str | None = None,
    mounts: tp.Mapping[os.PathLike[str] | str, os.PathLike[str] | str] | None = None,
) -> config.SlurmClusterConfig:
    """DRAC Narval Cluster (https://docs.alliancecan.ca/wiki/Narval/en)."""
    modules = []
    if proxy != "submission-host":
        modules.append("httpproxy")

    return _drac_cluster(
        name="narval",
        host="narval.alliancecan.ca",
        robot_host="robot.narval.alliancecan.ca",
        public_key=config.PublicKey(
            "ssh-ed25519",
            "AAAAC3NzaC1lZDI1NTE5AAAAILFxB0spH5RApc43sBx0zOxo1ARVH0ezU+FbQH95FW+h",
        ),
        user=user,
        account=account,
        mounts=mounts,
        proxy=proxy,
        modules=modules,
        resources={ResourceType.A100: "a100"},
        features={
            FeatureType.NVIDIA_MIG: "a100mig",
            FeatureType.NVIDIA_NVLINK: "nvlink",
        },
    )


def rorqual(
    *,
    user: str | None = None,
    account: str | None = None,
    proxy: tp.Literal["submission-host"] | str | None = None,
    mounts: tp.Mapping[os.PathLike[str] | str, os.PathLike[str] | str] | None = None,
) -> config.SlurmClusterConfig:
    """DRAC Rorqual Cluster (https://docs.alliancecan.ca/wiki/Rorqual/en)."""
    modules = []
    if proxy != "submission-host":
        modules.append("httpproxy")

    return _drac_cluster(
        name="rorqual",
        host="rorqual.alliancecan.ca",
        robot_host="robot.rorqual.alliancecan.ca",
        public_key=config.PublicKey(
            "ssh-ed25519",
            "AAAAC3NzaC1lZDI1NTE5AAAAINME5e9bifKZbuKKOQSpe3xrvC4g1b0QLMYj+AXBQGJe",
        ),
        user=user,
        account=account,
        mounts=mounts,
        proxy=proxy,
        modules=modules,
        resources={ResourceType.H100: "h100"},
        features={
            FeatureType.NVIDIA_NVLINK: "nvlink",
        },
    )


def fir(
    *,
    user: str | None = None,
    account: str | None = None,
    mounts: tp.Mapping[os.PathLike[str] | str, os.PathLike[str] | str] | None = None,
) -> config.SlurmClusterConfig:
    """DRAC Fir Cluster (https://docs.alliancecan.ca/wiki/Fir/en)."""
    return _drac_cluster(
        name="fir",
        host="fir.alliancecan.ca",
        robot_host="robot.fir.alliancecan.ca",
        public_key=config.PublicKey(
            "ssh-ed25519",
            "AAAAC3NzaC1lZDI1NTE5AAAAIJtenyJz+inwobvlJntWYFNu+ANcVWNcOHRKcEN6zmDo",
        ),
        user=user,
        account=account,
        mounts=mounts,
        resources={ResourceType.H100: "h100"},
    )


def nibi(
    *,
    user: str | None = None,
    account: str | None = None,
    mounts: tp.Mapping[os.PathLike[str] | str, os.PathLike[str] | str] | None = None,
) -> config.SlurmClusterConfig:
    """DRAC Nibi Cluster (https://docs.alliancecan.ca/wiki/Nibi/en)."""
    return _drac_cluster(
        name="nibi",
        host="nibi.alliancecan.ca",
        robot_host="robot.nibi.alliancecan.ca",
        public_key=config.PublicKey(
            "ssh-ed25519",
            "AAAAC3NzaC1lZDI1NTE5AAAAIEcmFoQZr6+KUHm/zm/BJpnNIlME7GytMxbHgfAUfoQX",
        ),
        user=user,
        account=account,
        mounts=mounts,
        resources={ResourceType.H100: "h100"},
    )


def killarney(
    *,
    user: str | None = None,
    account: str | None = None,
    mounts: tp.Mapping[os.PathLike[str] | str, os.PathLike[str] | str] | None = None,
) -> config.SlurmClusterConfig:
    """DRAC (PAICE) Killarney Cluster (https://docs.alliancecan.ca/wiki/Killarney/en)."""
    return _drac_cluster(
        name="killarney",
        host="killarney.alliancecan.ca",
        public_key=config.PublicKey(
            "ssh-ed25519",
            "AAAAC3NzaC1lZDI1NTE5AAAAIGlzaBBtvhJsSr23rMoY41gy8Svv1IOct8TBRH9CGuJf",
        ),
        user=user,
        account=account,
        mounts=mounts,
        resources={ResourceType.L40S: "l40s", ResourceType.H100: "h100"},
    )


def tamia(
    *,
    user: str | None = None,
    account: str | None = None,
    mounts: tp.Mapping[os.PathLike[str] | str, os.PathLike[str] | str] | None = None,
) -> config.SlurmClusterConfig:
    """DRAC (PAICE) Tamia Cluster (https://docs.alliancecan.ca/wiki/Tamia/en)."""
    return _drac_cluster(
        name="tamia",
        host="tamia.alliancecan.ca",
        public_key=config.PublicKey(
            "ssh-ed25519",
            "AAAAC3NzaC1lZDI1NTE5AAAAIN2wL9wOa0VveA/2l2ky/OhPsQfYtKuX99dyNnUTSYeU",
        ),
        user=user,
        account=account,
        mounts=mounts,
        resources={ResourceType.H100: "h100"},
    )


def vulcan(
    *,
    user: str | None = None,
    account: str | None = None,
    mounts: tp.Mapping[os.PathLike[str] | str, os.PathLike[str] | str] | None = None,
) -> config.SlurmClusterConfig:
    """DRAC (PAICE) Vulcan Cluster (https://docs.alliancecan.ca/wiki/Vulcan/en)."""
    return _drac_cluster(
        name="vulcan",
        host="vulcan.alliancecan.ca",
        public_key=config.PublicKey(
            "ssh-ed25519",
            "AAAAC3NzaC1lZDI1NTE5AAAAIMuIj6T45HqVeJgRotH9Qq46FzidekS2lXkD7FOTltnC",
        ),
        user=user,
        account=account,
        mounts=mounts,
        resources={ResourceType.L40S: "l40s"},
    )
