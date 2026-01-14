import logging
import os
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from xm_slurm.api import models
from xm_slurm.api.abc import XManagerAPI

logger = logging.getLogger(__name__)

Base = declarative_base()


class ExperimentSqliteModel(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    note = Column(String)
    tags = Column(String)
    work_units = relationship(
        "WorkUnitSqliteModel", back_populates="experiment", cascade="all, delete-orphan"
    )
    artifacts = relationship(
        "ExperimentArtifactSqliteModel", back_populates="experiment", cascade="all, delete-orphan"
    )


class WorkUnitSqliteModel(Base):
    __tablename__ = "work_units"

    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    wid = Column(Integer)
    identity = Column(String)
    args = Column(String)
    experiment = relationship("ExperimentSqliteModel", back_populates="work_units")
    jobs = relationship(
        "SlurmJobSqliteModel", back_populates="work_unit", cascade="all, delete-orphan"
    )
    artifacts = relationship(
        "WorkUnitArtifactSqliteModel", back_populates="work_unit", cascade="all, delete-orphan"
    )


class SlurmJobSqliteModel(Base):
    __tablename__ = "slurm_jobs"

    id = Column(Integer, primary_key=True)
    work_unit_id = Column(Integer, ForeignKey("work_units.id"))
    name = Column(String)
    slurm_job_id = Column(Integer)
    slurm_ssh_config = Column(String)
    work_unit = relationship("WorkUnitSqliteModel", back_populates="jobs")


class ArtifactSqliteModel(Base):
    __tablename__ = "artifacts"
    __mapper_args__ = {"polymorphic_on": "type"}

    id = Column(Integer, primary_key=True)
    name = Column(String)
    uri = Column(String)
    type = Column(String)


class ExperimentArtifactSqliteModel(ArtifactSqliteModel):
    __tablename__ = "experiment_artifacts"
    __mapper_args__ = {"polymorphic_identity": "experiment"}

    id = Column(Integer, ForeignKey("artifacts.id"), primary_key=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    experiment = relationship("ExperimentSqliteModel", back_populates="artifacts")


class ConfigArtifactSqliteModel(ExperimentArtifactSqliteModel):
    __mapper_args__ = {"polymorphic_identity": "config"}


class WorkUnitArtifactSqliteModel(ArtifactSqliteModel):
    __tablename__ = "work_unit_artifacts"
    __mapper_args__ = {"polymorphic_identity": "work_unit"}

    id = Column(Integer, ForeignKey("artifacts.id"), primary_key=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    work_unit_id = Column(Integer, ForeignKey("work_units.id"))
    experiment = relationship("ExperimentSqliteModel", back_populates="artifacts")
    work_unit = relationship("WorkUnitSqliteModel", back_populates="artifacts")


class XManagerSqliteAPI(XManagerAPI):
    def __init__(self):
        if "XM_SLURM_STATE_DIR" in os.environ:
            db_path = Path(os.environ["XM_SLURM_STATE_DIR"]) / "db.sqlite3"
        else:
            db_path = Path.home() / ".local" / "state" / "xm-slurm" / "db.sqlite3"
        logger.debug("Looking for db at: %s", db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)  # type: ignore
        self.Session = sessionmaker(bind=engine)

    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def get_experiment(self, xid: int) -> models.Experiment:
        with self.session_scope() as session:
            experiment = (
                session.query(ExperimentSqliteModel).filter(ExperimentSqliteModel.id == xid).first()  # type: ignore
            )
            if not experiment:
                raise ValueError(f"Experiment with id {xid} not found")

            work_units = []
            for wu in experiment.work_units:
                jobs = [
                    models.SlurmJob(
                        name=job.name,
                        slurm_job_id=job.slurm_job_id,
                        slurm_ssh_config=job.slurm_ssh_config,
                    )
                    for job in wu.jobs
                ]
                artifacts = [
                    models.Artifact(name=artifact.name, uri=artifact.uri)
                    for artifact in wu.artifacts
                ]
                work_units.append(
                    models.WorkUnit(
                        wid=wu.wid,
                        identity=wu.identity,
                        args=wu.args,
                        jobs=jobs,
                        artifacts=artifacts,
                    )
                )

            # Combine regular experiment artifacts and config artifacts
            artifacts = [
                models.Artifact(name=artifact.name, uri=artifact.uri)
                for artifact in experiment.artifacts
            ]

            return models.Experiment(
                title=experiment.title,
                description=experiment.description,
                note=experiment.note,
                tags=experiment.tags.split(",") if experiment.tags else None,
                work_units=work_units,
                artifacts=artifacts,
            )

    def delete_experiment(self, experiment_id: int) -> None:
        with self.session_scope() as session:
            experiment = (
                session.query(ExperimentSqliteModel)
                .filter(ExperimentSqliteModel.id == experiment_id)
                .first()  # type: ignore
            )
            if experiment:
                session.delete(experiment)

    def insert_experiment(self, experiment: models.ExperimentPatch) -> int:
        with self.session_scope() as session:
            new_experiment = ExperimentSqliteModel(
                title=experiment.title,  # type: ignore
                description=experiment.description,  # type: ignore
                note=experiment.note,  # type: ignore
                tags=",".join(experiment.tags) if experiment.tags else None,  # type: ignore
            )
            session.add(new_experiment)
            session.flush()
            return new_experiment.id

    def update_experiment(
        self, experiment_id: int, experiment_patch: models.ExperimentPatch
    ) -> None:
        with self.session_scope() as session:
            experiment = (
                session.query(ExperimentSqliteModel)
                .filter(ExperimentSqliteModel.id == experiment_id)
                .first()  # type: ignore
            )
            if experiment:
                if experiment_patch.title is not None:
                    experiment.title = experiment_patch.title
                if experiment_patch.description is not None:
                    experiment.description = experiment_patch.description
                if experiment_patch.note is not None:
                    experiment.note = experiment_patch.note
                if experiment_patch.tags is not None:
                    experiment.tags = ",".join(experiment_patch.tags)

    def insert_job(self, experiment_id: int, work_unit_id: int, job: models.SlurmJob) -> None:
        with self.session_scope() as session:
            work_unit = (
                session.query(WorkUnitSqliteModel)
                .filter_by(experiment_id=experiment_id, wid=work_unit_id)
                .first()  # type: ignore
            )
            if work_unit:
                new_job = SlurmJobSqliteModel(
                    work_unit_id=work_unit.id,  # type: ignore
                    name=job.name,  # type: ignore
                    slurm_job_id=job.slurm_job_id,  # type: ignore
                    slurm_ssh_config=job.slurm_ssh_config,  # type: ignore
                )
                session.add(new_job)
            else:
                raise ValueError(
                    f"Work unit with id {work_unit_id} not found in experiment {experiment_id}"
                )

    def insert_work_unit(self, experiment_id: int, work_unit: models.WorkUnitPatch) -> None:
        with self.session_scope() as session:
            new_work_unit = WorkUnitSqliteModel(
                experiment_id=experiment_id,  # type: ignore
                wid=work_unit.wid,  # type: ignore
                identity=work_unit.identity,  # type: ignore
                args=work_unit.args,  # type: ignore
            )
            session.add(new_work_unit)

    def update_work_unit(
        self, experiment_id: int, work_unit_id: int, patch: models.ExperimentUnitPatch
    ) -> None:
        with self.session_scope() as session:
            work_unit = (
                session.query(WorkUnitSqliteModel)
                .filter(
                    WorkUnitSqliteModel.experiment_id == experiment_id,
                    WorkUnitSqliteModel.wid == work_unit_id,
                )
                .first()  # type: ignore
            )

            if work_unit:
                if patch.identity is not None:
                    work_unit.identity = patch.identity
                if patch.args is not None:
                    work_unit.args = patch.args
            else:
                raise ValueError(
                    f"Work unit with id {work_unit_id} not found in experiment {experiment_id}"
                )

    def delete_work_unit_artifact(self, experiment_id: int, work_unit_id: int, name: str) -> None:
        with self.session_scope() as session:
            artifact = (
                session.query(WorkUnitArtifactSqliteModel)
                .filter(
                    WorkUnitArtifactSqliteModel.experiment_id == experiment_id,
                    WorkUnitArtifactSqliteModel.work_unit_id == work_unit_id,
                    WorkUnitArtifactSqliteModel.name == name,
                )
                .first()  # type: ignore
            )
            if artifact:
                session.delete(artifact)

    def insert_work_unit_artifact(
        self, experiment_id: int, work_unit_id: int, artifact: models.Artifact
    ) -> None:
        with self.session_scope() as session:
            work_unit = (
                session.query(WorkUnitSqliteModel)
                .filter(
                    WorkUnitSqliteModel.experiment_id == experiment_id,
                    WorkUnitSqliteModel.wid == work_unit_id,
                )
                .first()  # type: ignore
            )
            if work_unit:
                new_artifact = WorkUnitArtifactSqliteModel(
                    experiment_id=experiment_id,  # type: ignore
                    work_unit_id=work_unit.id,  # type: ignore
                    name=artifact.name,  # type: ignore
                    uri=artifact.uri,  # type: ignore
                )
                session.add(new_artifact)
            else:
                raise ValueError(
                    f"Work unit with id {work_unit_id} not found in experiment {experiment_id}"
                )

    def delete_experiment_artifact(self, experiment_id: int, name: str) -> None:
        with self.session_scope() as session:
            # Try to find and delete either type of artifact
            artifact = (
                session.query(ArtifactSqliteModel)
                .filter(
                    ArtifactSqliteModel.name == name,
                    (
                        (ArtifactSqliteModel.type == "experiment")
                        | (ArtifactSqliteModel.type == "config")
                    ),
                )
                .join(ExperimentArtifactSqliteModel)  # type: ignore
                .filter(ExperimentArtifactSqliteModel.experiment_id == experiment_id)
                .first()
            )
            if artifact:
                session.delete(artifact)

    def insert_experiment_artifact(self, experiment_id: int, artifact: models.Artifact) -> None:
        with self.session_scope() as session:
            # Determine if this should be a config artifact based on name
            if artifact.name in ("PYTHON", "GRAPHVIZ"):
                new_artifact = ConfigArtifactSqliteModel(
                    experiment_id=experiment_id,  # type: ignore
                    name=artifact.name,  # type: ignore
                    uri=artifact.uri,  # type: ignore
                )
            else:
                new_artifact = ExperimentArtifactSqliteModel(
                    experiment_id=experiment_id,  # type: ignore
                    name=artifact.name,  # type: ignore
                    uri=artifact.uri,  # type: ignore
                )
            session.add(new_artifact)

    def insert_experiment_config_artifact(
        self, experiment_id: int, artifact: models.ConfigArtifact
    ) -> None:
        with self.session_scope() as session:
            new_artifact = ConfigArtifactSqliteModel(
                experiment_id=experiment_id,  # type: ignore
                name=artifact.name,  # type: ignore
                uri=artifact.uri,  # type: ignore
            )
            session.add(new_artifact)

    def delete_experiment_config_artifact(self, experiment_id: int, name: str) -> None:
        with self.session_scope() as session:
            artifact = (
                session.query(ConfigArtifactSqliteModel)
                .filter(
                    ConfigArtifactSqliteModel.experiment_id == experiment_id,
                    ConfigArtifactSqliteModel.name == name,
                )
                .first()  # type: ignore
            )
            if artifact:
                session.delete(artifact)
