import logging
import os

from xm_slurm import config, resources
from xm_slurm.contrib.clusters import drac

# ComputeCanada alias
cc = drac

__all__ = ["drac", "mila", "cc"]

logger = logging.getLogger(__name__)


def mila(
    *,
    user: str | None = None,
    partition: str | None = None,
    mounts: dict[os.PathLike[str] | str, os.PathLike[str] | str] | None = None,
) -> config.SlurmClusterConfig:
    """Mila Cluster (https://docs.mila.quebec/)."""
    if mounts is None:
        mounts = {
            "/network/scratch/${USER:0:1}/$USER": "/scratch",
            # TODO: move these somewhere common to all cluster configs.
            "/home/mila/${USER:0:1}/$USER/.local/state/xm-slurm": "/xm-slurm-state",
            "/home/mila/${USER:0:1}/$USER/.ssh": "/home/mila/${USER:0:1}/$USER/.ssh",
        }
    mounts = dict(mounts) | {"/dev/infiniband": "/dev/infiniband"}

    return config.SlurmClusterConfig(
        name="mila",
        ssh=config.SSHConfig(
            user=user,
            endpoints=(config.Endpoint("login.server.mila.quebec", 2222),),
            public_key=config.PublicKey(
                "ssh-ed25519",
                "AAAAC3NzaC1lZDI1NTE5AAAAIBTPCzWRkwYDr/cFb4d2uR6rFlUtqfH3MoLMXPpJHK0n",
            ),
        ),
        runtime=config.ContainerRuntime.SINGULARITY,
        partition=partition,
        prolog="module load singularity",
        host_environment={
            "SINGULARITY_CACHEDIR": "$SCRATCH/.apptainer",
            "SINGULARITY_TMPDIR": "$SLURM_TMPDIR",
            "SINGULARITY_LOCALCACHEDIR": "$SLURM_TMPDIR",
        },
        container_environment={
            "SCRATCH": "/scratch",
            "XM_SLURM_STATE_DIR": "/xm-slurm-state",
        },
        mounts=mounts,
        resources={
            resources.ResourceType.RTX8000: "rtx8000",
            resources.ResourceType.V100: "v100",
            resources.ResourceType.A100: "a100",
            resources.ResourceType.A100_80GIB: "a100l",
            resources.ResourceType.A6000: "a6000",
            resources.ResourceType.L40S: "l40s",
            resources.ResourceType.H100: "h100",
        },
        features={
            resources.FeatureType.NVIDIA_MIG: "mig",
            resources.FeatureType.NVIDIA_NVLINK: "nvlink",
        },
    )
