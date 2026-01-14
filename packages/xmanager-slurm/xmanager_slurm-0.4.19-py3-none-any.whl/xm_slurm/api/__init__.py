import functools
import logging
import os

from xm_slurm.api import models
from xm_slurm.api.abc import XManagerAPI
from xm_slurm.api.sqlite import client as sqlite_client
from xm_slurm.api.web import client as web_client

logger = logging.getLogger(__name__)


@functools.cache
def client() -> XManagerAPI:
    backend = os.environ.get("XM_SLURM_API_BACKEND", "sqlite").lower()
    match backend:
        case "rest":
            if "XM_SLURM_REST_API_BASE_URL" not in os.environ:
                raise ValueError("XM_SLURM_REST_API_BASE_URL is not set")
            if "XM_SLURM_REST_API_TOKEN" not in os.environ:
                raise ValueError("XM_SLURM_REST_API_TOKEN is not set")

            return web_client.XManagerWebAPI(
                base_url=os.environ["XM_SLURM_REST_API_BASE_URL"],
                token=os.environ["XM_SLURM_REST_API_TOKEN"],
            )
        case "sqlite":
            return sqlite_client.XManagerSqliteAPI()
        case _:
            raise ValueError(f"Invalid XM_SLURM_API_BACKEND: {backend}")


__all__ = ["client", "XManagerAPI", "models"]
