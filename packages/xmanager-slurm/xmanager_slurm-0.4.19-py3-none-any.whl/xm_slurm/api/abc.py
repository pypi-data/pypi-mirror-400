import abc

from xm_slurm.api import models


class XManagerAPI(abc.ABC):
    @abc.abstractmethod
    def get_experiment(self, xid: int) -> models.Experiment:
        pass

    @abc.abstractmethod
    def delete_experiment(self, experiment_id: int) -> None:
        pass

    @abc.abstractmethod
    def insert_experiment(self, experiment: models.ExperimentPatch) -> int:
        pass

    @abc.abstractmethod
    def update_experiment(
        self, experiment_id: int, experiment_patch: models.ExperimentPatch
    ) -> None:
        pass

    @abc.abstractmethod
    def insert_job(self, experiment_id: int, work_unit_id: int, job: models.SlurmJob) -> None:
        pass

    @abc.abstractmethod
    def insert_work_unit(self, experiment_id: int, work_unit: models.WorkUnitPatch) -> None:
        pass

    @abc.abstractmethod
    def update_work_unit(
        self, experiment_id: int, work_unit_id: int, patch: models.ExperimentUnitPatch
    ) -> None:
        pass

    @abc.abstractmethod
    def delete_work_unit_artifact(self, experiment_id: int, work_unit_id: int, name: str) -> None:
        pass

    @abc.abstractmethod
    def insert_work_unit_artifact(
        self, experiment_id: int, work_unit_id: int, artifact: models.Artifact
    ) -> None:
        pass

    @abc.abstractmethod
    def delete_experiment_artifact(self, experiment_id: int, name: str) -> None:
        pass

    @abc.abstractmethod
    def insert_experiment_artifact(self, experiment_id: int, artifact: models.Artifact) -> None:
        pass

    @abc.abstractmethod
    def insert_experiment_config_artifact(
        self, experiment_id: int, artifact: models.ConfigArtifact
    ) -> None:
        pass

    @abc.abstractmethod
    def delete_experiment_config_artifact(self, experiment_id: int, name: str) -> None:
        pass
