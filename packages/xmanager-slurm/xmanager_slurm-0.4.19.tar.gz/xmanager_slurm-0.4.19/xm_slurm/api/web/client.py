import dataclasses

import backoff
import httpx

from xm_slurm.api import models
from xm_slurm.api.abc import XManagerAPI

# Define which exceptions should trigger a retry
RETRY_EXCEPTIONS = (
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
    httpx.WriteTimeout,
    httpx.NetworkError,
)


# Common backoff decorator for all API calls
def with_backoff(f):
    return backoff.on_exception(
        backoff.expo,
        RETRY_EXCEPTIONS,
        max_tries=3,  # Maximum number of attempts
        max_time=30,  # Maximum total time to try in seconds
        jitter=backoff.full_jitter,  # Add jitter to prevent thundering herd
    )(f)


class XManagerWebAPI(XManagerAPI):
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(headers={"Authorization": f"Bearer {token}"}, verify=False)

    def _make_url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    @with_backoff
    def get_experiment(self, xid: int) -> models.Experiment:
        response = self.client.get(self._make_url(f"/experiment/{xid}"))
        response.raise_for_status()
        data = response.json()
        # Construct work units with nested jobs and artifacts
        work_units = []
        for wu_data in data.pop("work_units", []):
            # Build jobs for this work unit
            jobs = [
                models.SlurmJob(
                    name=job["name"],
                    slurm_job_id=job["slurm_job_id"],
                    slurm_ssh_config=job["slurm_ssh_config"],
                )
                for job in wu_data.pop("jobs", [])
            ]

            # Build artifacts for this work unit
            artifacts = [
                models.Artifact(name=artifact["name"], uri=artifact["uri"])
                for artifact in wu_data.pop("artifacts", [])
            ]

            # Create work unit with its jobs and artifacts
            wu_data["jobs"] = jobs
            wu_data["artifacts"] = artifacts
            work_units.append(models.WorkUnit(**wu_data))

        # Build experiment artifacts
        artifacts = [
            models.Artifact(name=artifact["name"], uri=artifact["uri"])
            for artifact in data.pop("artifacts", [])
        ]

        return models.Experiment(**data, work_units=work_units, artifacts=artifacts)

    @with_backoff
    def delete_experiment(self, experiment_id: int) -> None:
        response = self.client.delete(self._make_url(f"/experiment/{experiment_id}"))
        response.raise_for_status()

    @with_backoff
    def insert_experiment(self, experiment: models.ExperimentPatch) -> int:
        assert experiment.title is not None, "Title must be set in the experiment model."
        assert (
            experiment.description is None and experiment.note is None and experiment.tags is None
        ), "Only title should be set in the experiment model."

        response = self.client.put(
            self._make_url("/experiment"), json=dataclasses.asdict(experiment)
        )
        response.raise_for_status()
        return int(response.json()["xid"])

    @with_backoff
    def update_experiment(
        self, experiment_id: int, experiment_patch: models.ExperimentPatch
    ) -> None:
        response = self.client.patch(
            self._make_url(f"/experiment/{experiment_id}"),
            json=dataclasses.asdict(experiment_patch),
        )
        response.raise_for_status()

    @with_backoff
    def insert_work_unit(self, experiment_id: int, work_unit: models.WorkUnitPatch) -> None:
        response = self.client.put(
            self._make_url(f"/experiment/{experiment_id}/wu"),
            json=dataclasses.asdict(work_unit),
        )
        response.raise_for_status()

    @with_backoff
    def insert_job(self, experiment_id: int, work_unit_id: int, job: models.SlurmJob) -> None:
        response = self.client.put(
            self._make_url(f"/experiment/{experiment_id}/wu/{work_unit_id}/job"),
            json=dataclasses.asdict(job),
        )
        response.raise_for_status()

    @with_backoff
    def insert_work_unit_artifact(
        self, experiment_id: int, work_unit_id: int, artifact: models.Artifact
    ) -> None:
        response = self.client.put(
            self._make_url(f"/experiment/{experiment_id}/wu/{work_unit_id}/artifact"),
            json=dataclasses.asdict(artifact),
        )
        response.raise_for_status()

    @with_backoff
    def delete_work_unit_artifact(self, experiment_id: int, work_unit_id: int, name: str) -> None:
        response = self.client.delete(
            self._make_url(f"/experiment/{experiment_id}/wu/{work_unit_id}/artifact/{name}")
        )
        response.raise_for_status()

    @with_backoff
    def delete_experiment_artifact(self, experiment_id: int, name: str) -> None:
        response = self.client.delete(
            self._make_url(f"/experiment/{experiment_id}/artifact/{name}")
        )
        response.raise_for_status()

    @with_backoff
    def insert_experiment_artifact(self, experiment_id: int, artifact: models.Artifact) -> None:
        response = self.client.put(
            self._make_url(f"/experiment/{experiment_id}/artifact"),
            json=dataclasses.asdict(artifact),
        )
        response.raise_for_status()

    @with_backoff
    def insert_experiment_config_artifact(
        self, experiment_id: int, artifact: models.ConfigArtifact
    ) -> None:
        response = self.client.put(
            self._make_url(f"/experiment/{experiment_id}/config"), json=dataclasses.asdict(artifact)
        )
        response.raise_for_status()

    @with_backoff
    def delete_experiment_config_artifact(self, experiment_id: int, name: str) -> None:
        response = self.client.delete(self._make_url(f"/experiment/{experiment_id}/config/{name}"))
        response.raise_for_status()

    @with_backoff
    def update_work_unit(
        self, experiment_id: int, work_unit_id: int, patch: models.ExperimentUnitPatch
    ) -> None:
        response = self.client.patch(
            self._make_url(f"/experiment/{experiment_id}/wu/{work_unit_id}"),
            json=dataclasses.asdict(patch),
        )
        response.raise_for_status()
